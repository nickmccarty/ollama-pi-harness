"""
Agentic research + write + verify harness for qwen2.5 via Ollama.

Turn 1: vision preprocessing (if images detected) + 2 web searches + synthesis
Turn 2: Python writes output directly to disk
Turn 3: Wiggum loop — evaluate, revise, verify until PASS or max rounds

Usage:
    python agent.py "Search for X and save to ~/Desktop/harness-engineering/output.md"
    python agent.py "Analyze ~/Desktop/chart.png and save to ~/Desktop/analysis.md"
    python agent.py --no-wiggum "..."   # skip verification loop

Environment:
    conda activate ollama-pi
"""

import sys
import re
import os
import subprocess
import textwrap
import ollama as _ollama_raw

# Keep models hot between calls — avoids 30-60s cold reload between pipeline stages.
# OLLAMA_KEEP_ALIVE env var overrides the default; -1 means keep loaded forever.
_KEEP_ALIVE = int(os.environ.get("OLLAMA_KEEP_ALIVE", -1))

def _ollama_chat(*args, **kwargs):
    kwargs.setdefault("keep_alive", _KEEP_ALIVE)
    return _ollama_raw.chat(*args, **kwargs)

ollama = type("_OllamaShim", (), {"chat": staticmethod(_ollama_chat)})()

from ddgs import DDGS
from wiggum import loop as wiggum_loop
from logger import RunTrace
from vision import extract_image_context, detect_image_paths
from security import check_python_code, check_file_path, scan_for_injection, strip_injection_candidates
from memory import MemoryStore
from planner import make_plan, Plan

try:
    from markitdown import MarkItDown
    _md_converter = MarkItDown(enable_plugins=False)
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

MODEL = "pi-qwen-32b"

# ---------------------------------------------------------------------------
# Synthesis instruction — the text appended to every synthesis prompt.
# This is the primary target for autoresearch.py experiments.
# autoresearch.py reads and rewrites SYNTH_INSTRUCTION between the sentinels.
# Do not rename the sentinels or move them off their own lines.
# ---------------------------------------------------------------------------
# AUTORESEARCH:SYNTH_INSTRUCTION:BEGIN
SYNTH_INSTRUCTION = (
    "Output ONLY the markdown starting with #. For each section, include 'What', 'Why', 'How' with specific tool names, versions, and code examples. Require at least one working code snippet or step-by-step process per section. Explicitly structure each 'How' section with numbered steps and inline code blocks where applicable. For each strategy, include a concrete implementation note that addresses potential edge cases or practical challenges, and explicitly mention at least one production-ready library or framework (e.g., LangChain, HuggingFace Transformers, Prometheus, ELK stack) where relevant to improve depth and specificity. Ensure all sections include a practical example or implementation detail that demonstrates how the concept would be applied in a real-world system, especially for areas like chunk overlap, prompt templating, anomaly detection, and response verification."
)
# AUTORESEARCH:SYNTH_INSTRUCTION:END

# AUTORESEARCH:SYNTH_INSTRUCTION_COUNT:BEGIN
SYNTH_INSTRUCTION_COUNT = (
    "Output ONLY the markdown starting with #. For each of the 5 sections, include 'What', 'Why', 'How' with specific tool names, versions, and code examples. Require at least one working code snippet or step-by-step process per section. Explicitly structure each 'How' section with numbered steps and inline code blocks where applicable. For each strategy, include a concrete implementation note that addresses potential edge cases or practical challenges, and explicitly mention at least one production-ready library or framework (e.g., LangChain, HuggingFace Transformers, Prometheus, ELK stack) where relevant to improve depth and specificity. Ensure all sections include a practical example or implementation detail that demonstrates how the concept would be applied in a real-world system, especially for areas like chunk overlap, prompt templating, anomaly detection, and response verification."
)
# AUTORESEARCH:SYNTH_INSTRUCTION_COUNT:END
SEARCHES_PER_TASK = 2       # always run this many searches before synthesizing
SEARCH_QUALITY_FLOOR = 1800  # total merged chars — below this, run one more search
MAX_RESULTS_PER_SEARCH = 5
PYTHON_TOOL_ROUNDS = 3       # max rounds in the run_python tool loop
PYTHON_TIMEOUT = 10          # seconds before code execution is killed

TEXT_EXTENSIONS = {".txt", ".py", ".json", ".csv", ".tsv", ".yaml", ".yml", ".toml", ".xml", ".html"}
RICH_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".epub", ".htm"}
URL_ENRICH_COUNT = 2        # how many search-result URLs to fetch full content for (0 = disabled)
URL_ENRICH_MAX_CHARS = 8000 # cap per URL to avoid context bloat

PYTHON_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code and return stdout/stderr. Use for data processing, computation, or analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        }
    }
]


def web_search_raw(query: str, max_results: int = MAX_RESULTS_PER_SEARCH) -> list[dict]:
    """Return raw result dicts from DDGS."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"  [web_search error] {e}")
        return []


def format_results(results: list[dict]) -> str:
    lines = []
    for r in results:
        lines.append(f"**{r['title']}**\n{r['href']}\n{r['body']}\n")
    return "\n".join(lines)


def detect_text_files(task: str, exclude_path: str = None) -> list[str]:
    """Find readable file paths referenced in the task (non-image, non-output).
    Returns both plain-text and rich-document paths; caller uses extension to route."""
    pattern = r'(~[\w/\\.\-]+|[A-Za-z]:[\w/\\.\-]+|/[\w/.\-]+)'
    candidates = re.findall(pattern, task)
    found = []
    for c in candidates:
        expanded = os.path.expanduser(c)
        _, ext = os.path.splitext(expanded)
        if ext.lower() not in TEXT_EXTENSIONS and ext.lower() not in RICH_EXTENSIONS:
            continue
        if exclude_path and os.path.abspath(expanded) == os.path.abspath(os.path.expanduser(exclude_path)):
            continue
        if os.path.isfile(expanded):
            found.append(expanded)
    return found


def read_file_context(paths: list[str]) -> str:
    """Read files and return concatenated content blocks.
    Rich documents (PDF, DOCX, XLSX, etc.) are converted to markdown via MarkItDown.
    Plain text files are read directly."""
    blocks = []
    for p in paths:
        ok, reason = check_file_path(p)
        if not ok:
            print(f"  [security] read_file blocked: {reason}")
            continue
        _, ext = os.path.splitext(p)
        if ext.lower() in RICH_EXTENSIONS and MARKITDOWN_AVAILABLE:
            try:
                result = _md_converter.convert(p)
                content = result.text_content or ""
                print(f"  [markitdown] {os.path.basename(p)} → {len(content)} chars")
            except Exception as e:
                print(f"  [markitdown error] {os.path.basename(p)}: {e} — skipping")
                continue
        else:
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                print(f"  [read_file] {p} ({len(content)} chars)")
            except Exception as e:
                print(f"  [read_file error] {p}: {e}")
                continue
        # Injection scan applies to all sources
        clean, matches = scan_for_injection(content, source=os.path.basename(p))
        if not clean:
            print(f"  [security] injection pattern in {os.path.basename(p)} ({len(matches)} match(es)) — stripping")
            content, removed = strip_injection_candidates(content)
            print(f"  [security] removed {removed} line(s) from file")
        blocks.append(f"--- {os.path.basename(p)} ---\n{content}")
    return "\n\n".join(blocks)


def execute_python(code: str) -> str:
    """Run Python code in a subprocess. Returns stdout + stderr (truncated to 4000 chars)."""
    ok, reason = check_python_code(code)
    if not ok:
        print(f"  [security] run_python blocked: {reason}")
        return f"[blocked] {reason}"
    try:
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(code)],
            capture_output=True, text=True, timeout=PYTHON_TIMEOUT,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output[:4000] if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return f"[timeout] code exceeded {PYTHON_TIMEOUT}s"
    except Exception as e:
        return f"[error] {e}"


def run_tool_loop(task: str, research_context: str, trace: RunTrace, producer_model: str = MODEL) -> str:
    """
    Optional pre-synthesis tool loop: lets the model call run_python for data tasks.
    Returns accumulated execution output (empty string if model doesn't call tools).
    """
    messages = [{
        "role": "user",
        "content": (
            f"Task: {task}\n\n"
            f"Research context:\n{research_context}\n\n"
            "If this task requires data processing, computation, or analysis that "
            "would benefit from running Python code, use the run_python tool. "
            "Otherwise respond with exactly: no code needed"
        )
    }]

    execution_log = []
    for _ in range(PYTHON_TOOL_ROUNDS):
        response = ollama.chat(
            model=producer_model,
            messages=messages,
            tools=PYTHON_TOOLS,
            options={"temperature": 0.1},
        )
        trace.log_usage(response, stage="tool_loop")
        msg = response["message"]
        messages.append({"role": "assistant", "content": msg.get("content", ""), "tool_calls": msg.get("tool_calls", [])})

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            break

        for tc in tool_calls:
            fn = tc.get("function", {})
            if fn.get("name") == "run_python":
                code = fn.get("arguments", {}).get("code", "")
                print(f"  [run_python] executing ({len(code)} chars)...")
                result = execute_python(code)
                execution_log.append(f"```python\n{code}\n```\nOutput:\n```\n{result}\n```")
                trace.log_tool_call("run_python", code[:80], len(result))
                messages.append({"role": "tool", "content": result, "name": "run_python"})

    return "\n\n".join(execution_log)


def fetch_url_content(url: str) -> str:
    """Fetch a URL and convert its HTML to markdown via MarkItDown. Returns empty string on failure."""
    if not MARKITDOWN_AVAILABLE:
        return ""
    try:
        result = _md_converter.convert(url)
        text = (result.text_content or "").strip()
        if len(text) > URL_ENRICH_MAX_CHARS:
            text = text[:URL_ENRICH_MAX_CHARS] + "\n[truncated]"
        return text
    except Exception:
        return ""


def enrich_with_page_content(results: list[dict], count: int) -> str:
    """Fetch full page content for the top `count` search results. Returns a context block."""
    if not MARKITDOWN_AVAILABLE or count == 0:
        return ""
    blocks = []
    fetched = 0
    for r in results:
        if fetched >= count:
            break
        url = r.get("href", "")
        if not url.startswith("http"):
            continue
        print(f"  [markitdown] fetching {url[:60]}...")
        content = fetch_url_content(url)
        if content:
            blocks.append(f"**Full page: {r.get('title', url)}**\n{url}\n\n{content}")
            fetched += 1
            print(f"    → {len(content)} chars")
        else:
            print(f"    → failed or empty")
    return "\n\n---\n\n".join(blocks)


def merge_results(sets: list[list[dict]]) -> list[dict]:
    """Merge multiple result sets, deduplicating by URL."""
    seen = set()
    merged = []
    for result_set in sets:
        for r in result_set:
            url = r.get("href", "")
            if url not in seen:
                seen.add(url)
                merged.append(r)
    return merged


def generate_second_query(task: str, first_query: str, first_results: str, producer_model: str = MODEL, trace=None) -> str:
    """Ask the model to produce a complementary search query."""
    prompt = (
        f"Original task: {task}\n\n"
        f"First search query used: {first_query}\n\n"
        f"First search returned {len(first_results)} characters of results.\n\n"
        "Generate ONE alternative search query that would find complementary or more specific "
        "information not covered by the first query. Output ONLY the query string, nothing else."
    )
    response = ollama.chat(
        model=producer_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.3},
    )
    if trace is not None:
        trace.log_usage(response, stage="search_query")
    return response["message"]["content"].strip().strip('"')


def gather_research(task: str, trace: RunTrace, planned_queries: list[str] = None, producer_model: str = MODEL) -> str:
    """
    Run SEARCHES_PER_TASK searches, merge results, check quality floor.
    Uses planned_queries when provided; falls back to auto-generation otherwise.
    Returns a single merged context string ready for synthesis.
    """
    all_result_sets = []
    queries_used = []

    # First query
    if planned_queries and len(planned_queries) >= 1:
        first_query = planned_queries[0]
        print(f"  [web_search 1] {first_query}  (planned)")
    else:
        first_query = re.sub(r"(?i)^search\s+(for\s+)?", "", task.split("save to")[0].strip()).strip().rstrip("and ,.")
        print(f"  [web_search 1] {first_query}")
    results_1 = web_search_raw(first_query)
    all_result_sets.append(results_1)
    queries_used.append(first_query)
    trace.log_tool_call("web_search", first_query, len(format_results(results_1)))

    # Second query
    if planned_queries and len(planned_queries) >= 2:
        second_query = planned_queries[1]
        print(f"  [web_search 2] {second_query}  (planned)")
    else:
        formatted_1 = format_results(results_1)
        second_query = generate_second_query(task, first_query, formatted_1, producer_model=producer_model, trace=trace)
        print(f"  [web_search 2] {second_query}")
    results_2 = web_search_raw(second_query)
    all_result_sets.append(results_2)
    queries_used.append(second_query)
    trace.log_tool_call("web_search", second_query, len(format_results(results_2)))

    # Merge and check quality floor
    merged = merge_results(all_result_sets)
    merged_text = format_results(merged)
    total_chars = len(merged_text)
    print(f"  [research] merged {len(merged)} results, {total_chars} chars")
    trace.log_search_quality(total_chars)

    if total_chars < SEARCH_QUALITY_FLOOR:
        print(f"  [quality floor] {total_chars} < {SEARCH_QUALITY_FLOOR} — running fallback search")
        fallback_query = f"{first_query} examples implementation best practices"
        print(f"  [web_search fallback] {fallback_query}")
        results_fallback = web_search_raw(fallback_query)
        all_result_sets.append(results_fallback)
        queries_used.append(fallback_query)
        merged = merge_results(all_result_sets)
        merged_text = format_results(merged)
        total_chars = len(merged_text)
        trace.log_tool_call("web_search", fallback_query, len(format_results(results_fallback)))
        trace.log_search_quality(total_chars)
        print(f"  [research] after fallback: {len(merged)} results, {total_chars} chars")

    # URL enrichment — fetch full page content for top results via MarkItDown
    if URL_ENRICH_COUNT > 0 and MARKITDOWN_AVAILABLE:
        print(f"  [markitdown] enriching top {URL_ENRICH_COUNT} URL(s)...")
        page_content = enrich_with_page_content(merged, URL_ENRICH_COUNT)
        if page_content:
            merged_text = merged_text + "\n\n## Full page content\n\n" + page_content
            print(f"  [markitdown] added {len(page_content)} chars of page content")

    # Injection scan — strip suspicious lines from search results before synthesis
    clean, injection_matches = scan_for_injection(merged_text, source="web_search")
    if not clean:
        print(f"  [security] prompt injection detected in search results ({len(injection_matches)} match(es)) — stripping")
        for m in injection_matches:
            print(f"    {m}")
        merged_text, removed = strip_injection_candidates(merged_text)
        print(f"  [security] removed {removed} line(s)")
        trace.log_injection_stripped(len(injection_matches))

    return merged_text


def synthesize(task: str, research_context: str, vision_context: str = "", file_context: str = "", code_context: str = "", memory_context: str = "", producer_model: str = MODEL, trace=None) -> str:
    """Ask the model to synthesize research (and optional contexts) into a markdown document."""
    vision_block = f"\nImage analysis:\n{vision_context}\n" if vision_context else ""
    file_block = f"\nFile contents:\n{file_context}\n" if file_context else ""
    code_block = f"\nCode execution results:\n{code_context}\n" if code_context else ""
    memory_block = f"\n{memory_context}\n" if memory_context else ""
    prompt = (
        f"Task: {task}\n\n"
        f"Research findings:\n{research_context}\n"
        f"{vision_block}{file_block}{code_block}{memory_block}\n"
        f"{SYNTH_INSTRUCTION}"
    )
    response = ollama.chat(
        model=producer_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )
    if trace is not None:
        trace.log_usage(response, stage="synth")
    return response["message"].get("content", "")


def research(task: str, trace: RunTrace) -> str:
    print("\n[turn 1] researching...\n")
    context = gather_research(task, trace)
    print("\n  [synth] synthesizing from merged results...")
    return synthesize(task, context)


def extract_count_constraint(task: str) -> int | None:
    """Return the numeric count constraint from a task string, e.g. 'top 5' -> 5."""
    match = re.search(
        r'\btop\s+(\d+)\b|\b(\d+)\s+most\b|\b(\d+)\s+(?:best|key|common|main)\b',
        task,
        re.IGNORECASE,
    )
    if match:
        return int(next(g for g in match.groups() if g is not None))
    return None


def count_output_items(content: str) -> int:
    """Count H2-level content sections in markdown, ignoring structural headers."""
    structural = {"introduction", "conclusion", "summary", "overview", "background", "references"}
    headers = re.findall(r'^##\s+(.+)', content, re.MULTILINE)
    return sum(
        1 for h in headers
        if re.sub(r'^[\d.\s]+', '', h).strip().lower() not in structural
    )


def synthesize_with_count(task: str, research_context: str, expected_count: int, vision_context: str = "", file_context: str = "", code_context: str = "", memory_context: str = "", producer_model: str = MODEL, trace=None) -> str:
    """Re-synthesize with an explicit count constraint injected into the prompt."""
    vision_block = f"\nImage analysis:\n{vision_context}\n" if vision_context else ""
    file_block = f"\nFile contents:\n{file_context}\n" if file_context else ""
    code_block = f"\nCode execution results:\n{code_context}\n" if code_context else ""
    memory_block = f"\n{memory_context}\n" if memory_context else ""
    prompt = (
        f"Task: {task}\n\n"
        f"Research findings:\n{research_context}\n"
        f"{vision_block}{file_block}{code_block}{memory_block}\n"
        f"IMPORTANT: You must produce EXACTLY {expected_count} numbered sections "
        f"(## 1. ... through ## {expected_count}. ...) — no more, no fewer. "
        f"{SYNTH_INSTRUCTION_COUNT}"
    )
    response = ollama.chat(
        model=producer_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )
    if trace is not None:
        trace.log_usage(response, stage="synth_count")
    return response["message"]["content"].strip()


def extract_path(task: str) -> str | None:
    match = re.search(r"(~[\w/\\.\-]+\.md|[A-Za-z]:[\w/\\.\-]+\.md|/[\w/.\-]+\.md|[\w./\\\-]+\.md)", task)
    return match.group(1) if match else None


def write_output(content: str, path: str, trace: RunTrace):
    print("\n[turn 2] writing file...\n")

    expanded = os.path.expanduser(path)
    dir_path = os.path.dirname(expanded)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(expanded, "w", encoding="utf-8") as f:
        f.write(content)

    trace.log_write(path, content)

    if os.path.exists(expanded):
        size = os.path.getsize(expanded)
        lines = content.count("\n") + 1
        print(f"[eval] PASS — {expanded}")
        print(f"       {lines} lines, {size} bytes\n")
        print("--- preview (first 20 lines) ---")
        print("\n".join(content.splitlines()[:20]))
        print("--------------------------------")
    else:
        print(f"[eval] FAIL — {expanded} not found")


def _store_memory(memory: MemoryStore, task: str, task_type: str, trace_data: dict, content: str):
    """Compress a completed run and write it to the memory store."""
    print("\n  [memory] compressing run...")
    try:
        obs = memory.compress_and_store(
            task=task,
            task_type=task_type,
            tool_calls=trace_data.get("tool_calls", []),
            output_content=content,
            output_lines=trace_data.get("output_lines"),
            output_bytes=trace_data.get("output_bytes"),
            output_path=trace_data.get("output_path"),
            wiggum_scores=trace_data.get("wiggum_scores", []),
            final=trace_data.get("final", "PASS"),
        )
        print(f"  [memory] stored: {obs['title']!r}")
    except Exception as e:
        print(f"  [memory] compression failed (non-fatal): {e}")


def run(task: str, use_wiggum: bool = True, producer_model: str = MODEL):
    from wiggum import EVALUATOR_MODEL
    trace = RunTrace(task=task, producer_model=producer_model, evaluator_model=EVALUATOR_MODEL)
    memory = MemoryStore()

    try:
        path = extract_path(task)
        if not path:
            print("[error] no .md output path found in task — include a file path ending in .md")
            trace.finish("ERROR")
            sys.exit(1)

        # Vision preprocessing — extract context from any images referenced in the task
        vision_context = ""
        image_paths = detect_image_paths(task)
        if image_paths:
            print(f"\n[vision] {len(image_paths)} image(s) detected — extracting context...")
            trace.log_vision(image_paths)
            for img_path in image_paths:
                print(f"  [vision] processing {os.path.basename(img_path)}...")
                desc = extract_image_context(img_path, task)
                vision_context += f"\n--- {os.path.basename(img_path)} ---\n{desc}\n"
            print(f"  [vision] extracted {len(vision_context)} chars of image context")

        # read_file — inject content of any text files referenced in the task
        file_context = ""
        text_files = detect_text_files(task, exclude_path=path)
        if text_files:
            print(f"\n[read_file] {len(text_files)} file(s) detected — reading...")
            trace.log_files_read(text_files)
            file_context = read_file_context(text_files)
            print(f"  [read_file] injecting {len(file_context)} chars of file context")

        # Memory retrieval — before planning so the planner can use prior context
        memory_context = memory.get_context(task)
        if memory_context:
            memory_hits = memory_context.count("**[")
            print(f"\n  [memory] injecting {memory_hits} past observation(s)")
            trace.log_memory_hits(memory_hits)
        else:
            print("\n  [memory] no relevant history")

        # Planning — analyse task + memory; produces search queries and synthesis notes
        print("  [planner] generating plan...")
        plan = make_plan(task, memory_context)
        trace.log_plan(plan.to_dict())
        print(f"  [planner] {plan.task_type} / {plan.complexity}"
              + (f" / {plan.expected_sections} sections" if plan.expected_sections else "")
              + (f"\n  [planner] note: {plan.notes}" if plan.notes else ""))

        # Combined synthesis context: memory observations + planner notes
        plan_ctx = plan.synthesis_context()
        full_memory_context = "\n\n".join(filter(None, [memory_context, plan_ctx]))

        print("\n[turn 1] researching...\n")
        context = gather_research(task, trace, planned_queries=plan.search_queries or None, producer_model=producer_model)

        # run_python tool loop — optional pre-synthesis code execution
        code_context = ""
        print("\n  [tool loop] checking for code execution needs...")
        code_context = run_tool_loop(task, context, trace, producer_model=producer_model)
        if code_context:
            print(f"  [tool loop] {len(code_context)} chars of execution output")
        else:
            print("  [tool loop] no code needed")

        print("\n  [synth] synthesizing from merged results...")
        content = synthesize(task, context, vision_context=vision_context, file_context=file_context, code_context=code_context, memory_context=full_memory_context, producer_model=producer_model, trace=trace)

        # Count constraint: planner takes precedence over regex
        expected_count = plan.expected_sections or extract_count_constraint(task)
        if expected_count is not None:
            actual_count = count_output_items(content)
            if actual_count != expected_count:
                print(f"\n[count check] expected {expected_count} items, got {actual_count} — retrying synthesis")
                trace.log_count_retry()
                content = synthesize_with_count(task, context, expected_count, vision_context=vision_context, file_context=file_context, code_context=code_context, memory_context=full_memory_context, producer_model=producer_model, trace=trace)
                actual_count = count_output_items(content)
                if actual_count == expected_count:
                    print(f"  [count check] OK — {actual_count} items after retry")
                else:
                    print(f"  [count check] still {actual_count} after retry — proceeding anyway")
            else:
                print(f"\n[count check] OK — {actual_count} items match constraint ({expected_count})")

        if not content.strip():
            print("[error] model returned empty content — check model and tool setup")
            trace.finish("ERROR")
            sys.exit(1)

        print("\n" + content + "\n")
        write_output(content, path, trace)

        if use_wiggum:
            wiggum_trace = wiggum_loop(task, path, producer_model=producer_model)
            trace.log_wiggum(wiggum_trace)
            print(f"\n[wiggum] {wiggum_trace['final']} after {len(wiggum_trace['rounds'])} round(s)")
            for r in wiggum_trace["rounds"]:
                print(f"  round {r['round']}: score={r['score']}/10  passed={r['passed']}")
                for issue in r.get("issues", []):
                    print(f"    - {issue}")
            trace.finish()
            _store_memory(memory, task, wiggum_trace.get("task_type"), trace.data, content)
        else:
            trace.finish("PASS")
            from wiggum import detect_task_type
            _store_memory(memory, task, detect_task_type(task), trace.data, content)

    except Exception as e:
        print(f"[error] unhandled exception: {e}")
        trace.finish("ERROR")
        raise


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print('usage: python agent.py "<task>"')
        print('       python agent.py --no-wiggum "<task>"')
        sys.exit(1)

    no_wiggum = "--no-wiggum" in args

    producer = MODEL
    if "--producer" in args:
        idx = args.index("--producer")
        if idx + 1 < len(args):
            producer = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

    task_args = [a for a in args if a != "--no-wiggum"]
    run(" ".join(task_args), use_wiggum=not no_wiggum, producer_model=producer)
