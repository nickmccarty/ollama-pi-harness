"""
skills.py — skill registry and invocation layer for the harness agent.

Skills extend the agent pipeline at defined hook points:

  pre_research   — modify search behaviour (e.g. force deep search)
  pre_synthesis  — inject additional instructions into the synthesis prompt
  post_synthesis — transform or augment the synthesized output
  post_wiggum    — run additional evaluation after the verification loop

Invocation — explicit slash commands in the task string:
    python agent.py "/annotate /cite Search for RAG papers and save to output.md"

Invocation — automatic, via per-skill trigger predicates:
    Planner complexity="high"   → panel auto-activates
    Task mentions "paper"       → annotate auto-activates
    Task mentions "exhaustive"  → deep auto-activates

Skills are loaded lazily — importing skills.py does not import kg_gen, panel, etc.
"""

import os
import re

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
# Each entry:
#   description  — shown in /skills listing
#   hook         — pipeline stage: pre_research | pre_synthesis | post_synthesis | post_wiggum
#   prompt       — text injected into synthesis prompt (pre_synthesis only); None otherwise
#   auto         — callable(task: str, plan) -> bool; None = explicit-only
# ---------------------------------------------------------------------------

REGISTRY: dict[str, dict] = {

    "annotate": {
        "description": "Standalone: read a paper (local or URL) and output a Nanda Annotated Abstract",
        "hook":        "standalone",
        "prompt":      None,
        "auto":        None,   # explicit only — /annotate bypasses the whole pipeline
    },

    "kg": {
        "description": "Generate a D3.js knowledge graph from the synthesized content",
        "hook":        "post_synthesis",
        "prompt":      None,
        "auto": lambda task, plan: bool(re.search(
            r"knowledge graph|\bkg\b|visuali[sz]e", task, re.IGNORECASE
        )),
    },

    "panel": {
        "description": "Run the 3-persona evaluation panel (Domain Practitioner, Critical Reviewer, Informed Newcomer)",
        "hook":        "post_wiggum",
        "prompt":      None,
        "auto": lambda task, plan: plan.complexity == "high",
    },

    "deep": {
        "description": "Force MAX_SEARCH_ROUNDS, disable novelty saturation gate",
        "hook":        "pre_research",
        "prompt":      None,
        "auto": lambda task, plan: bool(re.search(
            r"\bcomprehensive\b|\bthorough\b|\bexhaustive\b|\bin.depth\b|\bdeep.dive\b",
            task, re.IGNORECASE
        )),
    },

    "cite": {
        "description": "Require source attribution and citations for each claim",
        "hook":        "pre_synthesis",
        "prompt": (
            "For each significant claim, technique, or recommendation, include a source reference "
            "in parentheses (e.g. the URL or publication name from the research context). "
            "If a claim cannot be attributed to the provided sources, flag it explicitly as inferred."
        ),
        "auto": None,   # explicit only — too broad to auto-trigger
    },

    "annotated-abstract": {
        "description": "Alias for /annotate",
        "hook":        "standalone",
        "prompt":      None,   # resolved to "annotate" at parse time
        "auto":        None,
    },

    "wiggum": {
        "description": "Run the wiggum evaluation+revision loop on the output (combine with /annotate for annotation eval)",
        "hook":        "modifier",
        "prompt":      None,
        "auto":        None,   # explicit only — always opt-in
    },

    "email": {
        "description": "Generate personalized .eml drafts from a CSV of contacts + a stated goal",
        "hook":        "standalone",
        "prompt":      None,
        "auto":        None,   # explicit only
    },

    "github": {
        "description": (
            "GitHub operations via gh CLI: push, pr create/list/view/merge/review, "
            "issue create/list/view, repo view/clone, status"
        ),
        "hook":        "standalone",
        "prompt":      None,
        "auto":        None,   # explicit only — always opt-in
    },

}

# Aliases — resolved during parse
_ALIASES = {"annotated-abstract": "annotate"}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_skills(task: str) -> tuple[str, list[str]]:
    """
    Extract /skill_name tokens from the task string.
    Returns (clean_task, deduplicated_list_of_skill_names).
    Tokens not in REGISTRY are left in the task string unchanged.
    """
    parts      = task.split()
    skill_names: list[str] = []
    clean      = []

    for part in parts:
        if part.startswith("/"):
            raw  = part[1:]
            name = _ALIASES.get(raw, raw)
            if name in REGISTRY:
                if name not in skill_names:
                    skill_names.append(name)
                continue   # strip from task
        clean.append(part)

    return " ".join(clean), skill_names


def auto_activate(task: str, plan) -> list[str]:
    """
    Return skill names whose auto-trigger fires for this task + plan.
    Safe — never raises; trigger errors are silently skipped.
    """
    active = []
    for name, skill in REGISTRY.items():
        if name in _ALIASES.values() and name != name:   # skip alias targets
            continue
        trigger = skill.get("auto")
        if not trigger:
            continue
        try:
            if trigger(task, plan):
                active.append(name)
        except Exception:
            pass
    return active


def merge_skills(explicit: list[str], auto: list[str]) -> list[str]:
    """Deduplicate, preserving explicit-first order."""
    seen   = set(explicit)
    merged = list(explicit)
    for s in auto:
        if s not in seen:
            seen.add(s)
            merged.append(s)
    return merged


# ---------------------------------------------------------------------------
# Hook helpers
# ---------------------------------------------------------------------------

def get_prompt_injections(active_skills: list[str], hook: str) -> str:
    """
    Concatenate prompt injections for all active skills at the given hook.
    Returns an empty string if none match.
    """
    parts = []
    for name in active_skills:
        skill = REGISTRY.get(name, {})
        if skill.get("hook") == hook and skill.get("prompt"):
            parts.append(skill["prompt"])
    return "\n\n".join(parts)


def skills_at_hook(active_skills: list[str], hook: str) -> list[str]:
    """Return the subset of active_skills that fire at the given hook."""
    return [n for n in active_skills if REGISTRY.get(n, {}).get("hook") == hook]


# ---------------------------------------------------------------------------
# Post-synthesis handler
# ---------------------------------------------------------------------------

def run_post_synthesis(
    active_skills: list[str],
    content:       str,
    task:          str,
    output_path:   str,
    producer_model: str,
) -> dict:
    """
    Run all post_synthesis skill handlers.
    Returns a dict of results keyed by skill name (e.g. {"kg": "/path/to/graph.html"}).
    """
    results = {}
    for name in skills_at_hook(active_skills, "post_synthesis"):
        if name == "kg":
            results["kg"] = _handle_kg(content, task, output_path, producer_model)
    return results


def _handle_kg(content: str, task: str, output_path: str, producer_model: str) -> str | None:
    """Generate a D3.js knowledge graph from synthesized content."""
    try:
        from kg_gen import generate_kg, render_html
        from pathlib import Path
        from datetime import datetime

        article = content[:4000]
        graph_data = generate_kg(article, producer_model, num_nodes=12, max_edge_density=3)

        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir   = Path(output_path).parent if output_path else Path("graphs")
        kg_path   = out_dir / f"kg_{ts}.html"

        render_html(graph_data, kg_path, title=task[:60], model=producer_model, article_snippet=article)
        print(f"  [skill:kg] graph → {kg_path.resolve()}")
        return str(kg_path.resolve())
    except Exception as e:
        print(f"  [skill:kg] failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Standalone skill handler — /annotate
# ---------------------------------------------------------------------------

# The 8 rhetorical moves in Nanda's Annotated Abstract framework
_ANNOTATE_LABELS = [
    "Topic",
    "Motivation",
    "Contribution",
    "Detail/Nuance",
    "Evidence/Contribution 2",
    "Weaker result",
    "Narrow impact",
    "Broad impact",
]

_ANNOTATE_SYSTEM = (
    "You are a research-paper analyst. Given paper content, produce an annotated abstract "
    "using the Nanda framework with EXACTLY these eight bold section headers, in this order:\n\n"
    "**Topic**\n"
    "**Motivation**\n"
    "**Contribution**\n"
    "**Detail / Nuance**\n"
    "**Evidence / Contribution 2**\n"
    "**Weaker result**\n"
    "**Narrow impact**\n"
    "**Broad impact**\n\n"
    "Rules:\n"
    "- Each header must appear on its own line, bold, exactly as shown above.\n"
    "- After each header write 1-2 sentences of plain prose synthesized from the paper. Be concise.\n"
    "- Use only information from the provided text. Do not invent results.\n"
    "- If a section is not clearly evidenced, write a brief inference grounded in what IS present.\n"
    "- Output NOTHING before **Topic** and NOTHING after the **Broad impact** prose.\n\n"
    "Section definitions:\n"
    "  Topic                    — what subject area / problem this paper addresses\n"
    "  Motivation               — why this problem matters; the gap or need being addressed\n"
    "  Contribution             — the main new artifact, method, or claim ('We introduce/propose X')\n"
    "  Detail / Nuance          — key technical specifics of how the contribution works\n"
    "  Evidence / Contribution 2 — benchmark results or empirical evidence; secondary findings\n"
    "  Weaker result            — limitations, conditions where the approach underperforms, or open problems\n"
    "  Narrow impact            — specific, bounded applications or immediate takeaways\n"
    "  Broad impact             — wider implications for the field or community (e.g. open-source release)\n"
)

_ANNOTATE_PROMPT = (
    "Here is the paper content. Produce the annotated abstract.\n\n"
    "Start your output with:\n"
    "# Annotated Abstract: <paper title>\n\n"
    "Then output each of the eight section headers followed immediately by 1-2 sentences.\n\n"
    "PAPER CONTENT:\n"
)


_ANNOTATE_SECTION_PATTERNS = [
    ("Abstract",     r"(?i)^#+\s*abstract|^abstract\s*:",          2_000),
    ("Conclusion",   r"(?i)^#+\s*conclusions?",                     2_500),
    ("Introduction", r"(?i)^#+\s*\d*\.?\s*introduction",           2_500),
    ("Results",      r"(?i)^#+\s*\d*\.?\s*(results?|experiments?|evaluation)", 2_500),
    ("Discussion",   r"(?i)^#+\s*\d*\.?\s*discussion",              1_500),
]
_ANNOTATE_CHAR_BUDGET = 10_000

_ANNOTATE_LABELS = [
    "**Topic**",
    "**Motivation**",
    "**Contribution**",
    "**Detail / Nuance**",
    "**Evidence / Contribution 2**",
    "**Weaker result**",
    "**Narrow impact**",
    "**Broad impact**",
]


def _extract_sections(text: str) -> str:
    """
    Extract key sections (Abstract, Conclusion, Introduction, Results, Discussion)
    in priority order within a char budget. Falls back to truncated full text if
    no section headings are found (e.g. arxiv abstract-only pages).
    """
    lines = text.splitlines()
    heading_re = re.compile(r"^#+\s")

    section_starts = []
    for label, pattern, max_chars in _ANNOTATE_SECTION_PATTERNS:
        for idx, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                section_starts.append((label, idx, max_chars))
                break

    if not section_starts:
        # No headings — likely an abstract-only page. Return as-is.
        return text[:_ANNOTATE_CHAR_BUDGET]

    extracted = {}
    for label, start_idx, max_chars in section_starts:
        chunk_lines = []
        for line in lines[start_idx:]:
            if chunk_lines and heading_re.match(line):
                break
            chunk_lines.append(line)
        extracted[label] = "\n".join(chunk_lines)[:max_chars]

    priority = ["Abstract", "Conclusion", "Introduction", "Results", "Discussion"]
    parts = []
    remaining = _ANNOTATE_CHAR_BUDGET
    for label in priority:
        if label not in extracted or remaining <= 0:
            continue
        chunk = extracted[label][:remaining]
        parts.append(f"=== {label} ===\n{chunk}")
        remaining -= len(chunk)

    if not parts:
        return text[:_ANNOTATE_CHAR_BUDGET]

    return "\n\n".join(parts)


def _is_valid_annotation(text: str) -> bool:
    """Return True if annotation has a heading and at least 6 of 8 Nanda sections."""
    if not re.search(r"^#\s", text, re.MULTILINE):
        return False
    hits = sum(1 for lbl in _ANNOTATE_LABELS if lbl in text)
    return hits >= 6


def _clean_pdf_text(text: str) -> str:
    """
    Clean garbled PDF extraction output.

    MarkItDown's pdfminer backend sometimes produces single-character-per-line
    output for PDFs with unusual font encoding (common in arXiv papers).
    This collapses those runs back into readable text before feeding to the model.
    """
    lines = text.split("\n")
    cleaned = []
    i = 0
    while i < len(lines):
        # Detect a run of >=5 single-char (or 2-char) lines — garbled PDF artifact
        run_start = i
        while i < len(lines) and len(lines[i].strip()) <= 2:
            i += 1
        run_len = i - run_start
        if run_len >= 5:
            # Collapse: join non-blank single chars, skip pure whitespace lines
            joined = "".join(l.strip() for l in lines[run_start:i] if l.strip())
            if joined:
                cleaned.append(joined)
        else:
            cleaned.extend(lines[run_start:i])
            if i < len(lines):
                cleaned.append(lines[i])
                i += 1
    return "\n".join(cleaned)


def run_annotate_standalone(
    paper_context: str,
    producer_model: str,
    max_retries: int = 3,
) -> str:
    """
    Standalone /annotate handler.

    Reads the paper content (already fetched by agent.py — local PDF or URL),
    extracts key sections (Abstract, Conclusion, Introduction, Results),
    and returns a Nanda-annotated abstract with retry logic.

    Bypasses the normal research → synthesize → wiggum pipeline entirely.
    """
    import ollama as _ollama_raw
    import os

    keep_alive = int(os.environ.get("OLLAMA_KEEP_ALIVE", -1))

    if not paper_context.strip():
        return ""

    cleaned_context = _clean_pdf_text(paper_context)
    context = _extract_sections(cleaned_context)
    print(f"  [annotate] paper context: {len(paper_context)} chars raw → {len(context)} chars extracted")

    # Append /no_think for Qwen3 models — more reliable than the think:false option
    model_lower = producer_model.lower()
    system = _ANNOTATE_SYSTEM
    if "qwen3" in model_lower:
        system = system + "\n/no_think"

    prompt = system + "\n\n" + _ANNOTATE_PROMPT + context

    for attempt in range(1, max_retries + 1):
        resp = _ollama_raw.chat(
            model=producer_model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 2048, "num_ctx": 8192},
            keep_alive=keep_alive,
        )
        result = resp["message"]["content"].strip()
        # Strip Qwen3 chain-of-thought blocks if present
        result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()
        # Strip Qwen2.5 end-of-turn tokens and anything after
        result = re.split(r"<\|im_end\|>|<\|endoftext\|>", result)[0].strip()

        # Strip preamble before the annotation heading or first section
        preamble_m = re.search(r"(#\s*Annotated Abstract|\*\*Topic\*\*)", result)
        if preamble_m:
            result = result[preamble_m.start():].strip()

        # Truncate after the Broad impact paragraph.
        # Strategy: take at most 600 chars of content after the header line,
        # then cut at the last sentence-ending punctuation in that window.
        # This avoids dependence on blank lines or stop markers the model may not emit.
        broad_idx = result.find("**Broad impact**")
        if broad_idx != -1:
            header_end = result.find("\n", broad_idx)
            if header_end != -1:
                content_start = header_end + 1
                window = result[content_start : content_start + 600]
                last_sent = max(window.rfind("."), window.rfind("!"), window.rfind("?"))
                if last_sent != -1:
                    result = result[: content_start + last_sent + 1].strip()

        if _is_valid_annotation(result):
            return result

        print(f"  [annotate] attempt {attempt}/{max_retries} — invalid output, retrying...")

    return result  # return last attempt even if invalid; wiggum will catch it


# ---------------------------------------------------------------------------
# CLI — list available skills
# ---------------------------------------------------------------------------

def _print_registry():
    print("\nAvailable skills (prefix task with /name to activate):\n")
    for name, skill in REGISTRY.items():
        if name in _ALIASES:
            continue
        hook  = skill["hook"]
        desc  = skill["description"]
        auto  = "auto" if skill.get("auto") else "explicit"
        print(f"  /{name:<22} [{hook:<15}] [{auto}]  {desc}")
    print()


if __name__ == "__main__":
    _print_registry()
