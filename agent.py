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
import warnings
from pathlib import Path

# Load .env from project root if present
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# Suppress pydub's ffmpeg-not-found warning — ffmpeg is not used in this pipeline
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg", category=RuntimeWarning)

import ollama as _ollama_raw
from inference import OllamaLike as _OllamaLike

# Keep models hot between calls — avoids 30-60s cold reload between pipeline stages.
# OLLAMA_KEEP_ALIVE env var pins keep_alive globally (e.g. -1 to force always-on).
# If unset, _estimate_keep_alive() computes a per-run value from historical data.
# When INFERENCE_BACKEND=vllm, keep_alive is silently ignored (vLLM manages lifetime).
_KEEP_ALIVE_OVERRIDE = os.environ.get("OLLAMA_KEEP_ALIVE")
_KEEP_ALIVE = int(_KEEP_ALIVE_OVERRIDE) if _KEEP_ALIVE_OVERRIDE is not None else None


def _estimate_keep_alive(task_type: str, explicit_skills: set, use_wiggum: bool) -> int:
    """
    Estimate keep_alive (seconds) for this run.

    Strategy:
      1. Read last 100 runs from runs.jsonl, filter to matching task type.
      2. Take the 90th-percentile run_duration_s + 20% buffer.
      3. Fall back to skill-aware heuristics if history is thin (< 5 matching runs).

    The env var OLLAMA_KEEP_ALIVE always wins if set — this function is never
    called in that case.
    """
    # Standalone skills with short, bounded durations
    if explicit_skills & {"github", "email", "review", "recall", "queue"}:
        return 90
    if explicit_skills & {"lit-review"}:
        return -1   # keep alive indefinitely — pipeline runs for minutes to hours

    # Try historical data
    try:
        import json as _json
        _log = os.path.join(os.path.dirname(__file__), "runs.jsonl")
        durations = []
        with open(_log, encoding="utf-8") as _f:
            lines = _f.readlines()
        for line in lines[-100:]:
            line = line.strip()
            if not line:
                continue
            try:
                r = _json.loads(line)
            except _json.JSONDecodeError:
                continue
            dur = r.get("run_duration_s")
            # Match on task_type if known; otherwise use all runs
            if dur and dur > 0:
                if task_type and r.get("task_type") == task_type:
                    durations.append(dur)
        # Fall back to all task types if too few matching
        if len(durations) < 5:
            durations = []
            for line in lines[-100:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = _json.loads(line)
                except _json.JSONDecodeError:
                    continue
                dur = r.get("run_duration_s")
                if dur and dur > 0:
                    durations.append(dur)
        if len(durations) >= 5:
            durations.sort()
            p90 = durations[int(len(durations) * 0.9)]
            return int(p90 * 1.2)
    except Exception:
        pass

    # Heuristic fallback
    base = 300
    if use_wiggum:
        base += 150
    if "panel" in explicit_skills:
        base += 200
    if "deep" in explicit_skills:
        base = int(base * 1.5)
    if "annotate" in explicit_skills:
        base = max(base, 240)
    return base


ollama = _OllamaLike(keep_alive=_KEEP_ALIVE)

from ddgs import DDGS
from wiggum import loop as wiggum_loop
from logger import RunTrace
from vision import extract_image_context, detect_image_paths
from security import check_python_code, check_file_path, check_output_path, scan_for_injection, strip_injection_candidates
from memory import MemoryStore, assess_novelty
from planner import make_plan, Plan
from skills import parse_skills, auto_activate, merge_skills, get_prompt_injections, skills_at_hook, run_post_synthesis, run_annotate_standalone

try:
    from markitdown import MarkItDown
    _md_converter = MarkItDown(enable_plugins=False)
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

MODEL = "pi-qwen-32b"
COMPRESS_MODEL = os.environ.get("COMPRESS_MODEL", MODEL)  # lighter model for compress_knowledge / plan_query

# ---------------------------------------------------------------------------
# Synthesis instruction — the text appended to every synthesis prompt.
# This is the primary target for autoresearch.py experiments.
# autoresearch.py reads and rewrites SYNTH_INSTRUCTION between the sentinels.
# Do not rename the sentinels or move them off their own lines.
# ---------------------------------------------------------------------------
# AUTORESEARCH:SYNTH_INSTRUCTION:BEGIN
SYNTH_INSTRUCTION = (
    "Output ONLY the markdown starting with #. Structure each section with 'What', 'Why', 'How' subsections using numbered steps and inline code blocks. Write at least 150 words per subsection with concrete implementation details, ensuring every code snippet is complete, executable with specific tool versions, and includes error handling. Every section MUST include a complete runnable code example with both opening and closing triple-backtick fences — never leave a code block unclosed. Include edge case notes, trade-offs, and library recommendations. For each strategy, state when NOT to use it, identify input boundaries, and specify exact numerical values for all configuration parameters with workload-based justification."
)
# AUTORESEARCH:SYNTH_INSTRUCTION:END

# AUTORESEARCH:SYNTH_INSTRUCTION_COUNT:BEGIN
SYNTH_INSTRUCTION_COUNT = (
    "Output ONLY the markdown starting with #. List strategies as a numbered list with working code examples. Write at least 150 words per strategy with concrete implementation details, ensuring code is complete, executable with specific tool versions, and includes error handling. Every section MUST include a complete runnable code example with opening and closing triple-backtick fences — never leave code blocks unclosed. Use 'What', 'Why', 'How' subsections with numbered steps. Include edge case notes, trade-offs, and library recommendations. For each strategy, state when NOT to use it, identify input boundaries, and specify exact numerical values for configuration parameters with workload-based justification."
)
# AUTORESEARCH:SYNTH_INSTRUCTION_COUNT:END
SEARCHES_PER_TASK = 2        # minimum searches before novelty gating kicks in
SEARCH_QUALITY_FLOOR = 1800  # total merged chars — below this, run one more search
MAX_SEARCH_ROUNDS   = 5      # hard cap regardless of novelty
NOVELTY_THRESHOLD   = 3      # 0–10; stop if new results score below this
KNOWLEDGE_MAX_CHARS = 1500   # cap on rolling knowledge state fed to novelty scoring
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
    """Return raw result dicts from DDGS, using SQLite cache (24 h TTL)."""
    try:
        from search_cache import cached_search
        def _ddgs(q: str, n: int) -> list[dict]:
            with DDGS() as ddgs:
                return list(ddgs.text(q, max_results=n))
        return cached_search(query, _ddgs, max_results=max_results)
    except Exception as e:
        print(f"  [web_search error] {e}")
        return []


def format_results(results: list[dict]) -> str:
    lines = []
    for r in results:
        lines.append(f"**{r['title']}**\n{r['href']}\n{r['body']}\n")
    return "\n".join(lines)


def detect_task_urls(task: str) -> list[str]:
    """Find http(s):// URLs in the task string (excluding the .md output path)."""
    return re.findall(r'https?://[^\s"\'<>]+', task)


def fetch_task_url_context(urls: list[str]) -> str:
    """Fetch and concatenate content from task-level URLs using MarkItDown."""
    if not MARKITDOWN_AVAILABLE or not urls:
        return ""
    blocks = []
    for url in urls:
        print(f"  [fetch_url] {url[:80]}...")
        content = fetch_url_content(url)
        if content:
            blocks.append(f"--- Source: {url} ---\n{content}")
            print(f"  [fetch_url] {len(content)} chars")
        else:
            print(f"  [fetch_url] failed or empty — skipping")
    return "\n\n".join(blocks)


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


def read_file_context(paths: list[str], task: str = "") -> str:
    """Read files and return concatenated content blocks.
    Rich documents (PDF, DOCX, XLSX, etc.) are converted to markdown via MarkItDown.
    Plain text files are read directly.
    Large files (> LARGE_FILE_THRESHOLD chars) are context-extracted via chunker."""
    from chunker import extract_paper_context, LARGE_FILE_THRESHOLD
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
            # OCR fallback: if MarkItDown output is sparse (scanned/image-heavy PDF),
            # try PyMuPDF then vision model for a better extraction
            if ext.lower() == ".pdf":
                try:
                    from ocr import is_sparse, ocr_pdf
                    if is_sparse(content, p):
                        print(f"  [ocr] {os.path.basename(p)} is sparse — attempting OCR fallback")
                        content = ocr_pdf(p, task=task, markitdown_content=content)
                except Exception as e:
                    print(f"  [ocr] fallback failed (non-fatal): {e}")
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
        # Large file: extract most relevant context within budget
        if len(content) > LARGE_FILE_THRESHOLD:
            content = extract_paper_context(content, task=task, source=os.path.basename(p))
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


def enrich_with_page_content(results: list[dict], count: int, knowledge_state: str = "") -> str:
    """Fetch full page content for the top `count` search results.
    Skips URLs whose snippet is already well-covered in knowledge_state (>60% word overlap).
    Returns a context block."""
    if not MARKITDOWN_AVAILABLE or count == 0:
        return ""
    known_words = set(knowledge_state.lower().split()) if knowledge_state else set()
    blocks = []
    fetched = 0
    for r in results:
        if fetched >= count:
            break
        url = r.get("href", "")
        if not url.startswith("http"):
            continue
        if known_words:
            snippet_words = set(r.get("body", "").lower().split())
            overlap = len(snippet_words & known_words) / max(len(snippet_words), 1)
            if overlap > 0.6:
                print(f"  [markitdown] skipping {url[:50]} — {overlap:.0%} covered")
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


COMPRESS_PROMPT = """\
Current knowledge summary:
{current_state}

New search results to incorporate:
{new_results}

Update the summary to include the new information. Be concise — 5–8 bullet points, \
each starting with a key fact. Do not exceed {max_chars} characters total.
Output ONLY the bullet points, nothing else."""


def compress_knowledge(current_state: str, new_results: list[dict],
                       producer_model: str = MODEL, trace=None) -> str:
    """
    Compress accumulated search results into a rolling bullet-point knowledge state.
    Round 1 (empty current_state): returns raw body text — no model call.
    Round 2+: model call with num_predict=400 cap so it stays fast.
    """
    new_text = " ".join(r.get("body", "") for r in new_results)

    if not current_state:
        # First round — skip model call, just seed with raw bodies
        return new_text[:KNOWLEDGE_MAX_CHARS]

    prompt = COMPRESS_PROMPT.format(
        current_state=current_state,
        new_results=new_text[:800],
        max_chars=KNOWLEDGE_MAX_CHARS,
    )
    response = ollama.chat(
        model=COMPRESS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1, "num_predict": 400},
    )
    if trace is not None:
        trace.log_usage(response, stage="compress_knowledge")
    return response["message"]["content"].strip()[:KNOWLEDGE_MAX_CHARS]


def plan_query(task: str, knowledge_state: str, round_num: int, producer_model: str = MODEL, trace=None) -> str:
    """
    Generate a search query for the given round.
    Round 1: derives query directly from task (no model call).
    Round 2+: targets gaps in knowledge_state via model call.
    Replaces generate_second_query() — knowledge-state-aware for all rounds.
    """
    if round_num == 1 or not knowledge_state:
        return re.sub(r"(?i)^search\s+(for\s+)?", "", task.split("save to")[0].strip()).strip().rstrip("and ,.")

    prompt = (
        f"Task: {task}\n\n"
        f"What is already known:\n{knowledge_state}\n\n"
        "Generate ONE search query to find important information about the task NOT yet covered above. "
        "Output ONLY the query string, nothing else."
    )
    response = ollama.chat(
        model=COMPRESS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.3},
    )
    if trace is not None:
        trace.log_usage(response, stage="search_query")
    return response["message"]["content"].strip().strip('"')


def gather_research(task: str, trace: RunTrace, planned_queries: list[str] = None, producer_model: str = MODEL, force_deep: bool = False, task_type: str = "") -> str:
    """
    Saturation-based search loop: runs up to MAX_SEARCH_ROUNDS searches, stopping
    early when new results score below NOVELTY_THRESHOLD against the accumulated
    knowledge state. Minimum SEARCHES_PER_TASK rounds always run before gating.

    force_deep=True (set by /deep skill) disables novelty gating and runs all rounds.
    planned_queries are used for rounds 1–N before switching to plan_query().
    Returns a merged context string ready for synthesis.

    When RESEARCH_CACHE=1 (set by autoresearch.py), the full output is cached in
    research_cache table (24 h TTL). Cache hits skip the entire search + compress loop.
    Disabled for force_deep runs to ensure fresh results.
    """
    # Research cache — opt-in, autoresearch only (avoids stale results in interactive use)
    _research_cache_enabled = os.environ.get("RESEARCH_CACHE") == "1" and not force_deep
    if _research_cache_enabled:
        try:
            from search_cache import get_research, put_research
            _rc_hit = get_research(task, task_type)
            if _rc_hit:
                trace.data["novelty_scores"] = _rc_hit["novelty_scores"]
                trace.data["search_rounds"]  = _rc_hit["search_rounds"]
                print(f"  [rcache] research context served from cache ({len(_rc_hit['context'])} chars, {_rc_hit['search_rounds']} rounds skipped)")
                return _rc_hit["context"]
        except Exception as _e:
            print(f"  [rcache] cache lookup failed: {_e} — running search normally")

    all_result_sets  = []
    queries_used     = []
    knowledge_state  = ""
    novelty_scores   = []
    novelty_gate     = NOVELTY_THRESHOLD if not force_deep else -1   # -1 = never gate

    for round_num in range(1, MAX_SEARCH_ROUNDS + 1):
        # Query selection: planned first, then gap-targeted model call
        if planned_queries and round_num <= len(planned_queries):
            query = planned_queries[round_num - 1]
            print(f"  [web_search {round_num}] {query}  (planned)")
        else:
            query = plan_query(task, knowledge_state, round_num, producer_model=producer_model, trace=trace)
            suffix = "" if round_num == 1 else "  (gap-targeted)"
            print(f"  [web_search {round_num}] {query}{suffix}")

        results = web_search_raw(query)
        trace.log_tool_call("web_search", query, len(format_results(results)))

        # Novelty gate — only after minimum rounds have run (skipped when force_deep)
        if round_num > SEARCHES_PER_TASK:
            novelty = assess_novelty(results, knowledge_state)
            novelty_scores.append(novelty)
            gate_label = " (deep — no gate)" if force_deep else ""
            print(f"  [novelty] round {round_num}: {novelty}/10{gate_label}")
            if novelty < novelty_gate:
                print(f"  [novelty] saturation — stopping search")
                break
        elif round_num > 1:
            # Log novelty for rounds inside the minimum window (informational only)
            novelty = assess_novelty(results, knowledge_state)
            novelty_scores.append(novelty)
            print(f"  [novelty] round {round_num}: {novelty}/10  (below gate minimum — continuing)")

        all_result_sets.append(results)
        queries_used.append(query)
        knowledge_state = compress_knowledge(knowledge_state, results, producer_model=producer_model, trace=trace)

    # Log to trace
    trace.data["novelty_scores"]  = novelty_scores
    trace.data["search_rounds"]   = len(queries_used)

    # Merge and check quality floor
    merged      = merge_results(all_result_sets)
    merged_text = format_results(merged)
    total_chars = len(merged_text)
    print(f"  [research] merged {len(merged)} results, {total_chars} chars ({len(queries_used)} rounds)")
    trace.log_search_quality(total_chars)

    if total_chars < SEARCH_QUALITY_FLOOR:
        print(f"  [quality floor] {total_chars} < {SEARCH_QUALITY_FLOOR} — running fallback search")
        fallback_query = f"{queries_used[0]} examples implementation best practices"
        print(f"  [web_search fallback] {fallback_query}")
        results_fallback = web_search_raw(fallback_query)
        all_result_sets.append(results_fallback)
        queries_used.append(fallback_query)
        merged      = merge_results(all_result_sets)
        merged_text = format_results(merged)
        total_chars = len(merged_text)
        trace.log_tool_call("web_search", fallback_query, len(format_results(results_fallback)))
        trace.log_search_quality(total_chars)
        print(f"  [research] after fallback: {len(merged)} results, {total_chars} chars")

    # URL enrichment — disabled for enumerated tasks: full-page context causes
    # the model to produce flat lists instead of H2 sections, triggering count_check_retry.
    # Traces show this adds 300-1000s overhead (29-56% on top of synthesis) with no score gain.
    enrich_count = 0 if task_type == "enumerated" else URL_ENRICH_COUNT

    # URL enrichment — fetch full page content for top results via MarkItDown
    if enrich_count > 0 and MARKITDOWN_AVAILABLE:
        print(f"  [markitdown] enriching top {enrich_count} URL(s)...")
        page_content = enrich_with_page_content(merged, enrich_count, knowledge_state=knowledge_state)
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

    # Store in research cache for future autoresearch experiments on the same task
    if _research_cache_enabled:
        try:
            put_research(task, task_type, merged_text,
                         search_rounds=len(queries_used),
                         novelty_scores=novelty_scores)
        except Exception as _e:
            print(f"  [rcache] store failed: {_e}")

    return merged_text


def synthesize(task: str, research_context: str, vision_context: str = "", file_context: str = "", code_context: str = "", memory_context: str = "", skill_context: str = "", producer_model: str = MODEL, trace=None) -> str:
    """Ask the model to synthesize research (and optional contexts) into a markdown document."""
    vision_block = f"\nImage analysis:\n{vision_context}\n" if vision_context else ""
    file_block = f"\nFile contents:\n{file_context}\n" if file_context else ""
    code_block = f"\nCode execution results:\n{code_context}\n" if code_context else ""
    memory_block = f"\n{memory_context}\n" if memory_context else ""
    skill_block  = f"\nAdditional requirements:\n{skill_context}\n" if skill_context else ""
    prompt = (
        f"Task: {task}\n\n"
        f"Research findings:\n{research_context}\n"
        f"{vision_block}{file_block}{code_block}{memory_block}{skill_block}\n"
        f"{SYNTH_INSTRUCTION}"
    )
    response = ollama.chat(
        model=producer_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1, "num_predict": 8192},
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


def clean_synthesis_output(content: str) -> str:
    """
    Strip artefacts that models sometimes wrap around markdown output:
      - Any preamble before the first H1 heading (bash setup blocks, ```markdown fences, etc.)
      - Trailing ```  that closes an outer fence, plus any verification/commentary after it
      - Standalone trailing Verification sections and file-write epilogues
      - Leading and trailing blank lines
    """
    content = content.strip()

    # Anchor to the first H1 — discard everything before it (preamble, fences, bash blocks)
    h1_match = re.search(r'(?:^|\n)(# .+)', content)
    if h1_match:
        content = content[h1_match.start(1):]

    # Strip a trailing closing ``` fence + any epilogue that follows it
    # Only if what follows the fence looks like a verification block, not real content
    outer_close = re.search(r'\n```\s*\n(.+)$', content, re.DOTALL)
    if outer_close and re.search(
        r'Verification|was created|has been|cat ~|display the contents',
        outer_close.group(1), re.IGNORECASE
    ):
        content = content[:outer_close.start()]

    # Strip trailing verification / file-write commentary
    epilogue_re = re.compile(
        r'\n+(?:#{1,4}\s*)?(?:Verification|Verify)[:\s].*$'
        r'|\n+The (?:markdown )?file .{0,120} (?:was created|has been).*$'
        r'|\n+This command will (?:display|show|confirm).*$'
        # Trailing --- divider followed by meta-commentary about saving / file paths
        r'|\n+---\s*\n+(?:This (?:synthesized|guide|document|markdown)|Ensure you have|Save this|Note:|The above).{0,400}$',
        re.DOTALL | re.IGNORECASE,
    )
    content = epilogue_re.sub('', content)

    # Close any unclosed code fences (odd number of ``` markers = fence left open)
    fence_count = len(re.findall(r'^```', content, re.MULTILINE))
    if fence_count % 2 != 0:
        content = content.rstrip() + '\n```'

    return content.strip()


def count_output_items(content: str) -> int:
    """Count H2-level content sections in markdown, ignoring structural headers."""
    structural = {"introduction", "conclusion", "summary", "overview", "background", "references"}
    headers = re.findall(r'^##\s+(.+)', content, re.MULTILINE)
    return sum(
        1 for h in headers
        if re.sub(r'^[\d.\s]+', '', h).strip().lower() not in structural
    )


def synthesize_with_count(task: str, research_context: str, expected_count: int, vision_context: str = "", file_context: str = "", code_context: str = "", memory_context: str = "", skill_context: str = "", producer_model: str = MODEL, trace=None) -> str:
    """Re-synthesize with an explicit count constraint injected into the prompt."""
    vision_block = f"\nImage analysis:\n{vision_context}\n" if vision_context else ""
    file_block = f"\nFile contents:\n{file_context}\n" if file_context else ""
    code_block = f"\nCode execution results:\n{code_context}\n" if code_context else ""
    memory_block = f"\n{memory_context}\n" if memory_context else ""
    skill_block  = f"\nAdditional requirements:\n{skill_context}\n" if skill_context else ""
    prompt = (
        f"Task: {task}\n\n"
        f"Research findings:\n{research_context}\n"
        f"{vision_block}{file_block}{code_block}{memory_block}{skill_block}\n"
        f"IMPORTANT: You must produce EXACTLY {expected_count} numbered sections "
        f"(## 1. ... through ## {expected_count}. ...) — no more, no fewer. "
        f"{SYNTH_INSTRUCTION}"
    )
    response = ollama.chat(
        model=producer_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1, "num_predict": 8192},
    )
    if trace is not None:
        trace.log_usage(response, stage="synth_count")
    return response["message"]["content"].strip()


def extract_path(task: str) -> str | None:
    match = re.search(r"(~[\w/\\.\-]+\.md|[A-Za-z]:[\w/\\.\-]+\.md|/[\w/.\-]+\.md|[\w./\\\-]+\.md)", task)
    return match.group(1) if match else None


def write_output(content: str, path: str, trace: RunTrace):
    print("\n[turn 2] writing file...\n")

    # Validate output path against sandbox before writing
    ok, reason = check_output_path(path)
    if not ok:
        print(f"[security] write blocked: {reason}")
        print("[error] output path is outside allowed directories — aborting write")
        trace.finish("ERROR")
        sys.exit(1)

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


def run(task: str, use_wiggum: bool = True, producer_model: str = MODEL, evaluator_model: str = None):
    global _KEEP_ALIVE
    from wiggum import EVALUATOR_MODEL, ANNOTATE_EVALUATOR_MODEL
    _eval_model    = evaluator_model or EVALUATOR_MODEL
    _ann_eval_model = evaluator_model or ANNOTATE_EVALUATOR_MODEL
    trace = RunTrace(task=task, producer_model=producer_model, evaluator_model=_eval_model)
    memory = MemoryStore()

    try:
        # Skill parsing — extract /skill tokens before anything else touches the task
        task, explicit_skills = parse_skills(task)

        # Set dynamic keep_alive unless overridden by OLLAMA_KEEP_ALIVE env var
        if _KEEP_ALIVE_OVERRIDE is None:
            _KEEP_ALIVE = _estimate_keep_alive(
                task_type=None,           # task_type not known yet; refined below after planning
                explicit_skills=set(explicit_skills),
                use_wiggum=use_wiggum,
            )
            print(f"[agent] keep_alive={_KEEP_ALIVE}s (dynamic)")
        mode = "+".join(explicit_skills) if explicit_skills else "research"
        print(f"[agent] model={producer_model}  mode={mode}")

        # Standalone skills that produce their own output don't require a .md path
        _path_optional = {"email", "github", "review", "lit-review", "recall", "queue"}
        path = extract_path(task)
        if not path and not (set(explicit_skills) & _path_optional):
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
            file_context = read_file_context(text_files, task=task)
            print(f"  [read_file] injecting {len(file_context)} chars of file context")

        # URL fetch — inject content of any http(s):// URLs referenced in the task
        task_urls = detect_task_urls(task)
        has_url_content = False
        if task_urls:
            print(f"\n[fetch_url] {len(task_urls)} URL(s) in task — fetching...")
            url_context = fetch_task_url_context(task_urls)
            if url_context:
                file_context = (file_context + "\n\n" + url_context).strip()
                has_url_content = True
                print(f"  [fetch_url] injecting {len(url_context)} chars of URL content")

        # ---------------------------------------------------------------------------
        # Standalone skill dispatch
        # Each handler closes over local variables (trace, task, path, etc.).
        # Must be defined after file/URL context is assembled.
        # Add new standalone skills here — one function, one entry in _STANDALONE.
        # ---------------------------------------------------------------------------

        def _handle_annotate():
            print("\n[skill:annotate] standalone mode — annotating paper abstract...")
            trace.data["task_type"] = "annotate"
            if not file_context.strip():
                print("[error] /annotate requires a paper URL or local file path in the task")
                trace.finish("ERROR")
                sys.exit(1)
            with trace.span("synthesize", model=producer_model):
                content = run_annotate_standalone(file_context, producer_model)
            content = content.strip()
            if not content:
                print("[error] annotation model returned empty output")
                trace.finish("ERROR")
                return
            print("\n" + content + "\n")
            write_output(content, path, trace)
            if "wiggum" in explicit_skills:
                from wiggum import loop_annotate
                wiggum_result = loop_annotate(
                    task=task,
                    output_path=path,
                    paper_context=file_context,
                    producer_model=producer_model,
                    evaluator_model=_ann_eval_model,
                    parent_trace=trace,
                )
                trace.log_wiggum(wiggum_result)
                trace.finish(wiggum_result.get("final", "FAIL"))
            else:
                trace.finish("PASS")
            _store_memory(memory, task, "annotate", trace.data, content)

        def _handle_email():
            print("\n[skill:email] standalone mode — generating email drafts...")
            from email_skill import run_email_standalone
            tokens     = task.split()
            csv_token  = next((t for t in tokens if t.endswith(".csv")), "")
            out_token  = next((t for t in reversed(tokens) if "/" in t or t.endswith("/")), "email_drafts/")
            goal       = " ".join(t for t in tokens if t not in (csv_token, out_token)).strip() or task
            if not csv_token:
                print("[error] /email requires a .csv path in the task string")
                trace.finish("ERROR")
                return
            with trace.span("email_drafts", model=producer_model):
                results = run_email_standalone(
                    csv_path=csv_token,
                    goal=goal,
                    output_dir=out_token,
                    producer_model=producer_model,
                    sender_name=os.environ.get("SENDER_NAME", ""),
                    sender_email=os.environ.get("SENDER_EMAIL", ""),
                )
            print(f"\nGenerated {len(results)} email drafts -> {out_token}")
            tok_in  = results[0].get("_tokens_in",  0) if results else 0
            tok_out = results[0].get("_tokens_out", 0) if results else 0
            trace.data.update({"task_type": "email", "email_drafts": len(results),
                               "email_output_dir": out_token,
                               "input_tokens": tok_in, "output_tokens": tok_out})
            trace.finish("PASS")

        def _handle_github():
            print("\n[skill:github] standalone mode...")
            from github_skill import run_github_standalone
            result, tok_in, tok_out = run_github_standalone(task, model=producer_model)
            if path:
                write_output(result, path, trace)
            trace.data["task_type"]     = "github"
            trace.data["input_tokens"]  = tok_in
            trace.data["output_tokens"] = tok_out
            trace.finish("PASS")

        def _handle_review():
            print("\n[skill:review] standalone mode — reviewing diff...")
            from review_skill import run_review_standalone
            result = run_review_standalone(task, model=producer_model)
            if path:
                write_output(result["text"], path, trace)
            trace.data["task_type"]        = "review"
            trace.data["input_tokens"]     = result["tokens_in"]
            trace.data["output_tokens"]    = result["tokens_out"]
            trace.data["review_scope"]     = result["scope"]
            trace.data["review_diff_chars"] = result["diff_chars"]
            trace.data["review_warnings"]  = result["warnings"]
            trace.data["review_warnings_count"] = result["warnings_count"]
            trace.data["review_summary"]   = result["summary"]
            if result["thinking"]:
                trace.data["review_thinking"] = result["thinking"]
            trace.finish("PASS")

        def _handle_lit_review():
            from lit_review_skill import run_lit_review
            import re as _re
            # Parse flags from task string
            no_fetch   = "--no-fetch"   in task
            no_curate  = "--no-curate"  in task
            no_wiggum  = "--no-wiggum"  in task
            no_s2      = "--no-s2"      in task
            after_m    = _re.search(r"--after\s+(\S+)",        task)
            before_m   = _re.search(r"--before\s+(\S+)",       task)
            csv_m      = _re.search(r"--csv\s+(\S+)",          task)
            max_f_m    = _re.search(r"--max-fetch\s+(\d+)",    task)
            max_a_m    = _re.search(r"--max-annotate\s+(\d+)", task)
            tmpl_m     = _re.search(r"--template\s+(\S+)",     task)
            after      = after_m.group(1)  if after_m  else None
            before     = before_m.group(1) if before_m else None
            csv_path   = Path(csv_m.group(1)) if csv_m else None
            max_fetch  = int(max_f_m.group(1)) if max_f_m else 100
            max_ann    = int(max_a_m.group(1)) if max_a_m else 20
            template   = tmpl_m.group(1) if tmpl_m else "survey"
            out        = Path(path) if path else Path("lit_review.md")
            # Strip known flags from task to get query
            query = _re.sub(
                r"(/lit-review|--no-fetch|--no-curate|--no-wiggum|--no-s2"
                r"|--after\s+\S+|--before\s+\S+|--csv\s+\S+"
                r"|--max-fetch\s+\d+|--max-annotate\s+\d+"
                r"|--template\s+\S+|save\s+to\s+\S+|\S+\.md)",
                "", task, flags=_re.IGNORECASE,
            ).strip()
            trace.data["task_type"] = "lit-review"
            result = run_lit_review(
                query=query,
                out_path=out,
                max_fetch=max_fetch,
                max_annotate=max_ann,
                after=after,
                before=before,
                csv_path=csv_path if (no_fetch or csv_path) else None,
                no_curate=no_curate,
                no_wiggum=no_wiggum,
                no_s2=no_s2,
                template=template,
                producer_model=producer_model,
                evaluator_model=evaluator_model,
            )
            trace.data["output_path"]  = result.get("out_path", "")
            trace.data["output_bytes"] = Path(result.get("out_path","")).stat().st_size if result.get("out_path") and Path(result["out_path"]).exists() else 0
            trace.data["lit_review_papers"]   = result.get("papers", 0)
            trace.data["lit_review_clusters"] = result.get("clusters", 0)
            trace.finish("PASS")

        def _handle_recall():
            import re as _re
            import json as _json

            # Parse: /recall <query> [--n N] [--facts] [--scores]
            raw = task.strip()
            n_match = _re.search(r"--n\s+(\d+)", raw)
            n = int(n_match.group(1)) if n_match else 10
            show_facts  = "--facts"  in raw
            show_scores = "--scores" in raw
            query = _re.sub(r"--n\s+\d+|--facts|--scores", "", raw).strip()

            if not query:
                print("[recall] usage: /recall <query> [--n N] [--facts] [--scores]")
                trace.finish("ERROR")
                return

            print(f"\n[recall] searching memory for: {query!r}  (top {n})")
            hits = memory.search(query, n=n)

            if not hits:
                print("[recall] no matching observations found.")
                trace.finish("PASS")
                return

            for i, row in enumerate(hits, 1):
                score_str = f"  score={row['final_score']:.1f}" if show_scores and row["final_score"] else ""
                date = (row["timestamp"] or "")[:10]
                print(f"\n{'─'*60}")
                print(f"[{i}] {row['title']}")
                print(f"     {date}{score_str}")
                print(f"     {row['narrative']}")
                if show_facts and row["facts"]:
                    try:
                        facts = _json.loads(row["facts"]) if isinstance(row["facts"], str) else row["facts"]
                        for f in (facts or []):
                            print(f"     • {f}")
                    except Exception:
                        print(f"     {row['facts']}")

            print(f"\n{'─'*60}")
            print(f"[recall] {len(hits)} result(s) for {query!r}")
            trace.finish("PASS")

        def _handle_queue():
            import urllib.request as _urllib
            import json as _json

            # tasks separated by ;; in the task string
            subtasks = [t.strip() for t in task.split(";;") if t.strip()]
            if not subtasks:
                print("[queue] usage: /queue <task1> ;; <task2> ;; ...")
                trace.finish("ERROR")
                return

            server_url = os.environ.get("HARNESS_SERVER", "http://127.0.0.1:8765")
            queued = []
            for i, subtask in enumerate(subtasks, 1):
                body = _json.dumps({"task": subtask}).encode()
                req  = _urllib.Request(
                    f"{server_url}/api/queue",
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with _urllib.urlopen(req, timeout=10) as resp:
                        d = _json.loads(resp.read())
                    print(f"[queue] [{i}/{len(subtasks)}] position={d.get('position')}  id={d.get('queue_id')}  {subtask[:60]}")
                    queued.append(d)
                except Exception as exc:
                    print(f"[queue] [{i}/{len(subtasks)}] FAILED: {exc}  task={subtask[:60]}")

            print(f"[queue] {len(queued)}/{len(subtasks)} task(s) enqueued.")
            trace.finish("PASS")

        _STANDALONE = {
            "annotate":   _handle_annotate,
            "email":      _handle_email,
            "github":     _handle_github,
            "review":     _handle_review,
            "lit-review": _handle_lit_review,
            "recall":     _handle_recall,
            "queue":      _handle_queue,
        }

        for _skill in explicit_skills:
            if _skill in _STANDALONE:
                _STANDALONE[_skill]()
                return

        # Memory retrieval — before planning so the planner can use prior context
        with trace.span("memory_retrieval"):
            memory_context = memory.get_context(task)
        if memory_context:
            memory_hits = memory_context.count("**[")
            print(f"\n  [memory] injecting {memory_hits} past observation(s)")
            trace.log_memory_hits(memory_hits)
        else:
            print("\n  [memory] no relevant history")

        # Planning — analyse task + memory; produces search queries and synthesis notes
        print("  [planner] generating plan...")
        with trace.span("planner"):
            plan, _planner_resp = make_plan(task, memory_context)
        trace.log_plan(plan.to_dict())
        if _planner_resp is not None:
            trace.log_usage(_planner_resp, stage="planner")
        print(f"  [planner] {plan.task_type} / {plan.complexity}"
              + (f" / {plan.expected_sections} sections" if plan.expected_sections else "")
              + (f"\n  [planner] note: {plan.notes}" if plan.notes else ""))

        # Skill activation — merge explicit + auto-triggered
        auto_skills    = auto_activate(task, plan)
        active_skills  = merge_skills(explicit_skills, auto_skills)

        # Refine keep_alive now that task_type and active_skills are known
        if _KEEP_ALIVE_OVERRIDE is None:
            _KEEP_ALIVE = _estimate_keep_alive(
                task_type=plan.task_type,
                explicit_skills=set(active_skills),
                use_wiggum=use_wiggum,
            )
            print(f"  [agent] keep_alive refined to {_KEEP_ALIVE}s ({plan.task_type})")
        if auto_skills:
            print(f"  [skills] auto-activated: {auto_skills}")
        if active_skills:
            print(f"  [skills] active: {active_skills}")

        # Combined synthesis context: memory observations + planner notes
        plan_ctx = plan.synthesis_context()
        full_memory_context = "\n\n".join(filter(None, [memory_context, plan_ctx]))

        print("\n[turn 1] researching...\n")
        trace.name_thread("main")
        force_deep = "deep" in active_skills
        if force_deep:
            print("  [skill:deep] novelty gate disabled — running all search rounds")
        if has_url_content:
            print("  [fetch_url] document already fetched — skipping web search")
            context = ""
        else:
            with trace.span("gather_research"):
                context = gather_research(task, trace, planned_queries=plan.search_queries or None, producer_model=producer_model, force_deep=force_deep, task_type=plan.task_type or "")

        # run_python tool loop — skip for pure research tasks (never use code)
        code_context = ""
        if plan.task_type in ("research", "best_practices"):
            print("\n  [tool loop] skipped for research task")
        else:
            print("\n  [tool loop] checking for code execution needs...")
            with trace.span("tool_loop"):
                code_context = run_tool_loop(task, context, trace, producer_model=producer_model)
            if code_context:
                print(f"  [tool loop] {len(code_context)} chars of execution output")
            else:
                print("  [tool loop] no code needed")

        # Pre-synthesis skill injections
        skill_context = get_prompt_injections(active_skills, "pre_synthesis")
        if skill_context:
            skill_names = [s for s in active_skills if s in ("annotate", "cite")]
            print(f"  [skills] injecting pre_synthesis prompts: {skill_names}")

        # Count constraint: detect before synthesis so we can use the count-aware prompt directly
        expected_count = plan.expected_sections or extract_count_constraint(task)

        print("\n  [synth] synthesizing from merged results...")
        if expected_count is not None:
            print(f"  [count] detected count constraint: {expected_count} — using count-aware synthesis")
            with trace.span("synthesize", model=producer_model):
                content = synthesize_with_count(task, context, expected_count, vision_context=vision_context, file_context=file_context, code_context=code_context, memory_context=full_memory_context, skill_context=skill_context, producer_model=producer_model, trace=trace)
        else:
            with trace.span("synthesize", model=producer_model):
                content = synthesize(task, context, vision_context=vision_context, file_context=file_context, code_context=code_context, memory_context=full_memory_context, skill_context=skill_context, producer_model=producer_model, trace=trace)

        # Clean fences and trailing epilogues before any downstream processing
        content = clean_synthesis_output(content)

        # Count verification (safety net — synthesis should already comply)
        if expected_count is not None:
            actual_count = count_output_items(content)
            if actual_count != expected_count:
                print(f"\n[count check] expected {expected_count} items, got {actual_count} — retrying synthesis")
                trace.log_count_retry()
                content = synthesize_with_count(task, context, expected_count, vision_context=vision_context, file_context=file_context, code_context=code_context, memory_context=full_memory_context, skill_context=skill_context, producer_model=producer_model, trace=trace)
                content = clean_synthesis_output(content)
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

        # Post-synthesis skill handlers (e.g. /kg)
        if skills_at_hook(active_skills, "post_synthesis"):
            with trace.span("post_synthesis_skills"):
                run_post_synthesis(active_skills, content, task, path, producer_model)

        if use_wiggum:
            # /panel skill activates the 3-persona panel inside wiggum
            if "panel" in active_skills:
                os.environ["WIGGUM_PANEL"] = "1"
                print("  [skill:panel] panel evaluation enabled")
            with trace.span("wiggum"):
                wiggum_trace = wiggum_loop(task, path, producer_model=producer_model, parent_trace=trace)
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

    evaluator = None
    if "--evaluator" in args:
        idx = args.index("--evaluator")
        if idx + 1 < len(args):
            evaluator = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

    if "--from-env" in args:
        task = os.environ.get("AGENT_TASK", "").strip()
        if not task:
            print("[error] --from-env specified but AGENT_TASK env var is empty")
            sys.exit(1)
        # Parse --producer / --evaluator / --no-wiggum out of the task string too,
        # since the server bundles everything into AGENT_TASK to avoid MSYS2 path conversion.
        task_parts = task.split()
        clean_parts = []
        i = 0
        while i < len(task_parts):
            tok = task_parts[i]
            if tok == "--producer" and i + 1 < len(task_parts):
                producer = task_parts[i + 1]; i += 2
            elif tok == "--evaluator" and i + 1 < len(task_parts):
                evaluator = task_parts[i + 1]; i += 2
            elif tok == "--no-wiggum":
                no_wiggum = True; i += 1
            else:
                clean_parts.append(tok); i += 1
        task = " ".join(clean_parts)
    else:
        task_args = [a for a in args if a not in ("--no-wiggum", "--from-env")]
        task = " ".join(task_args)

    run(task, use_wiggum=not no_wiggum, producer_model=producer, evaluator_model=evaluator)
