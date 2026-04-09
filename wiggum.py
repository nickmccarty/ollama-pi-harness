"""
wiggum.py — verification loop for agent outputs

Flow per round:
  1. Normalize output to markdown via markitdown
  2. If HTML, render with playwright and extract clean text
  3. Evaluate normalized content against task criteria using an ollama evaluator model
  4. PASS: done. FAIL: revise with producer model, write, loop back.

Max 3 rounds — rounds 1-2 capture ~75% of reachable improvement (Yang et al., EMNLP 2025).

Usage (standalone):
    python wiggum.py "<task>" <output_path>

Usage (as module):
    from wiggum import loop
    result = loop(task, output_path, producer_model="pi-qwen")

Environment:
    conda activate ollama-pi
"""

import sys
import os
import json
import subprocess
import re
import ollama

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

PRODUCER_MODEL = "pi-qwen"
EVALUATOR_MODEL = "Qwen3-Coder:30b"
MAX_ROUNDS = 3
PASS_THRESHOLD = 8.0


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(path: str) -> str:
    """Convert any file format to plain markdown text for evaluation."""
    expanded = os.path.expanduser(path)

    if not os.path.exists(expanded):
        return f"[error] file not found: {expanded}"

    ext = os.path.splitext(expanded)[1].lower()

    # HTML: render with playwright for clean text extraction
    if ext in (".html", ".htm") and PLAYWRIGHT_AVAILABLE:
        print("  [normalize] rendering HTML with playwright")
        return _playwright_extract(expanded)

    # PDF, DOCX, etc: convert via markitdown
    if MARKITDOWN_AVAILABLE and ext in (".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm"):
        print(f"  [normalize] converting {ext} via markitdown")
        md = MarkItDown()
        result = md.convert(expanded)
        return result.text_content

    # Markdown or plain text: read directly
    with open(expanded, "r", encoding="utf-8") as f:
        return f.read()


def _playwright_extract(html_path: str) -> str:
    """Render HTML file in headless Chromium and return visible text."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{html_path.replace(os.sep, '/')}")
        text = page.inner_text("body")
        browser.close()
    return text


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

EVAL_PROMPT = """You are a strict evaluator. Score this output across five dimensions, then compute a weighted composite.

Task:
{task}

Output:
{content}

Score each dimension 0-10 as an integer:
- relevance (weight 0.20): Does the output address the correct topic and complete the task as specified?
- completeness (weight 0.25): Are all required items or practices present, with nothing important missing?
- depth (weight 0.30): Does each item have a concrete example or implementation note specific enough to act on?
- specificity (weight 0.15): Are claims precise and actionable, or vague and generic?
- structure (weight 0.10): Is the document clearly organized and readable?

Dimension score guide (apply to each dimension independently):
- 9-10: exceptional — no meaningful gaps; content a domain expert would be satisfied with
- 7-8: good — addresses the dimension but has at least one concrete gap you can name
- 5-6: surface-level — present but shallow, generic, or missing key parts
- 3-4: weak — significant problems; a practitioner could not act on this
- 1-2: failing — this dimension is essentially absent

Calibration anchors:
- A document that correctly lists N items but gives only one-line descriptions per item: depth=5, specificity=5
- A document where every section has a code snippet or step-by-step example: depth may reach 8-9
- A document that covers the topic broadly but omits 2+ major subtopics an expert would expect: completeness=6
- Do not score 9+ on any dimension unless you cannot identify a single concrete improvement

Task-type criteria:
{task_criteria}

Compute composite = round(0.20*relevance + 0.25*completeness + 0.30*depth + 0.15*specificity + 0.10*structure, 1)

Respond with valid JSON only — no preamble, no explanation:
{{
  "relevance": integer 0-10,
  "completeness": integer 0-10,
  "depth": integer 0-10,
  "specificity": integer 0-10,
  "structure": integer 0-10,
  "score": composite as a number with one decimal place,
  "passed": true if composite >= 8.0 else false,
  "issues": ["issue naming section and what is missing"],
  "feedback": "one paragraph of specific, actionable feedback for the producer"
}}

Universal rules:
- A bullet list of one-liners with no implementation detail: depth <= 5.
- issues must name the specific section and what is missing (e.g. "Section 2 has no implementation note")
- feedback must tell the producer exactly what to add or change, not just that improvement is possible
- Do not give 10 on any dimension unless it is genuinely exceptional — find at least one thing that could be improved
- For every dimension you scored 8 or below, include at least one specific issue describing exactly what would raise the score
- Be a strict grader. When in doubt, score lower rather than higher."""


# Task-type-specific criteria injected into EVAL_PROMPT
TASK_CRITERIA = {
    "enumerated": (
        "This is an enumerated list task (e.g. 'top N' or 'N most common').\n"
        "- The output must contain exactly the requested number of items. More or fewer is an automatic score cap of 5 and passed=false.\n"
        "- Each item must have a distinct name, a concrete example of it in practice, and a specific implementation note.\n"
        "- Items that restate the same concept in different words count as duplicates — flag them."
    ),
    "best_practices": (
        "This is a best practices task (open-ended, no count constraint).\n"
        "- Evaluate completeness: the practices should cover multiple distinct dimensions of the topic, not cluster around one angle.\n"
        "- Each practice must be actionable — it should tell a practitioner exactly what to do, not just describe a concept.\n"
        "- Flag any major practices that a domain expert would expect to see but are absent.\n"
        "- More practices is not better if they are shallow — depth over breadth."
    ),
    "research": (
        "This is a research synthesis task.\n"
        "- The output should synthesize findings, not just list facts — explain why each point matters and how a practitioner would apply it.\n"
        "- Each section should have enough context that a reader unfamiliar with the topic could act on it.\n"
        "- Flag missing nuance or important caveats that affect how the information should be used."
    ),
}


def detect_task_type(task: str) -> str:
    """Classify the task into one of three types for criteria selection."""
    if re.search(r'\btop\s+\d+\b|\b\d+\s+most\b|\b\d+\s+(?:best|key|common|main)\b', task, re.IGNORECASE):
        return "enumerated"
    if re.search(r'\bbest practices?\b|\bhow to\b|\bstrategies? for\b|\bguide\b|\btips?\b', task, re.IGNORECASE):
        return "best_practices"
    return "research"


def evaluate(task: str, content: str, prior_issues: list[str] = None, _trace=None) -> dict:
    """Call the evaluator model. Returns parsed result dict."""
    task_type = detect_task_type(task)
    print(f"  [evaluate] task_type={task_type}  scoring output...")

    prompt = EVAL_PROMPT.format(
        task=task,
        content=content[:6000],
        task_criteria=TASK_CRITERIA[task_type],
    )

    response = ollama.chat(
        model=EVALUATOR_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.0},
    )
    if _trace is not None:
        _trace.log_usage(response, stage="wiggum_eval")

    raw = response["message"]["content"].strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  [warn] evaluator returned non-JSON: {raw[:200]}")
        return {"passed": False, "score": 0.0, "issues": ["evaluator parse error"], "feedback": raw}

    # Recompute composite from dimension scores in Python — don't trust model arithmetic
    dims = {
        "relevance":    (result.get("relevance", 0),    0.20),
        "completeness": (result.get("completeness", 0), 0.25),
        "depth":        (result.get("depth", 0),        0.30),
        "specificity":  (result.get("specificity", 0),  0.15),
        "structure":    (result.get("structure", 0),    0.10),
    }
    composite = round(sum(score * weight for score, weight in dims.values()), 1)
    result["score"] = composite
    result["dims"] = {k: v[0] for k, v in dims.items()}

    # Enforce threshold
    result["passed"] = composite >= PASS_THRESHOLD
    return result


# ---------------------------------------------------------------------------
# Revision
# ---------------------------------------------------------------------------

REVISE_PROMPT = """You produced the following output for this task:

Task: {task}

Your output:
{content}

The evaluator found these issues:
{issues}

Evaluator feedback:
{feedback}

Produce a corrected version. Output ONLY the revised markdown starting with # — no preamble, no commentary."""


def revise(task: str, content: str, eval_result: dict, _trace=None) -> str:
    """Ask the producer model to revise the output given evaluator feedback."""
    print("  [revise] asking producer to fix issues...")

    issues_text = "\n".join(f"- {i}" for i in eval_result.get("issues", []))
    prompt = REVISE_PROMPT.format(
        task=task,
        content=content,
        issues=issues_text,
        feedback=eval_result.get("feedback", ""),
    )

    response = ollama.chat(
        model=PRODUCER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )
    if _trace is not None:
        _trace.log_usage(response, stage="wiggum_revise")

    return response["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def loop(task: str, output_path: str, producer_model: str = PRODUCER_MODEL, evaluator_model: str = EVALUATOR_MODEL) -> dict:
    """
    Run the Wiggum verification loop on an existing output file.

    Returns a trace dict with round-by-round results, final status, and token stats.
    """
    import time as _time
    from logger import RunTrace as _RunTrace

    global PRODUCER_MODEL, EVALUATOR_MODEL
    PRODUCER_MODEL = producer_model
    EVALUATOR_MODEL = evaluator_model

    expanded = os.path.expanduser(output_path)
    task_type = detect_task_type(task)

    # Lightweight local trace just for token accumulation — not written to disk
    _local_trace = _RunTrace(task=task, producer_model=producer_model, evaluator_model=evaluator_model)

    trace = {"task": task, "task_type": task_type, "output_path": expanded, "rounds": [], "final": None}

    print(f"\n[wiggum] starting verification loop")
    print(f"  file:  {expanded}")
    print(f"  task_type: {task_type}")
    print(f"  model: evaluator={evaluator_model} producer={producer_model}")
    print(f"  max rounds: {MAX_ROUNDS}\n")

    for round_num in range(1, MAX_ROUNDS + 1):
        print(f"--- round {round_num} ---")

        # 1. Normalize
        content = normalize(expanded)

        # 2. Evaluate
        result = evaluate(task, content, _trace=_local_trace)
        score = result.get("score", 0.0)
        passed = result.get("passed", False)
        issues = [i for i in result.get("issues", []) if i and str(i).strip().lower() not in ("none", "n/a", "")]
        feedback = result.get("feedback", "")
        dims = result.get("dims", {})

        abbrev = {"relevance": "rel", "completeness": "cmp", "depth": "dep", "specificity": "spc", "structure": "str"}
        dim_str = "  ".join(f"{abbrev.get(k, k)}={v}" for k, v in dims.items()) if dims else ""
        print(f"  score: {score}/10  passed: {passed}  [{dim_str}]")
        if issues:
            for issue in issues:
                print(f"    - {issue}")

        round_record = {
            "round": round_num,
            "score": score,
            "dims": dims,
            "passed": passed,
            "issues": issues,
            "feedback": feedback,
        }
        trace["rounds"].append(round_record)

        if passed:
            print(f"\n[wiggum] PASS on round {round_num} (score {score}/10)")
            trace["final"] = "PASS"
            _attach_token_stats(trace, _local_trace)
            return trace

        if round_num == MAX_ROUNDS:
            print(f"\n[wiggum] FAIL — max rounds reached without passing")
            trace["final"] = "FAIL"
            _attach_token_stats(trace, _local_trace)
            return trace

        # 3. Revise
        revised_content = revise(task, content, result, _trace=_local_trace)

        if not revised_content.strip():
            print("  [warn] producer returned empty revision, stopping loop")
            trace["final"] = "FAIL"
            return trace

        # Write revised content back to disk
        with open(expanded, "w", encoding="utf-8") as f:
            f.write(revised_content)
        print(f"  [write] revision saved to {expanded}")

    trace["final"] = "FAIL"
    _attach_token_stats(trace, _local_trace)
    return trace


def _attach_token_stats(trace: dict, local_trace):
    """Copy accumulated token stats from local_trace into the wiggum trace dict."""
    trace["input_tokens"]    = local_trace.data["input_tokens"]
    trace["output_tokens"]   = local_trace.data["output_tokens"]
    trace["tokens_by_stage"] = local_trace.data["tokens_by_stage"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_trace(trace: dict):
    print("\n==============================")
    print(" Wiggum Loop Trace")
    print("==============================")
    for r in trace["rounds"]:
        print(f"  Round {r['round']}: score={r['score']}/10 passed={r['passed']}")
    print(f"  Final: {trace['final']}")
    print("==============================\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: python wiggum.py "<task>" <output_path>')
        sys.exit(1)

    task_arg = sys.argv[1]
    path_arg = sys.argv[2]

    result = loop(task_arg, path_arg)
    print_trace(result)
    sys.exit(0 if result["final"] == "PASS" else 1)
