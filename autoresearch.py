"""
autoresearch.py — autonomous harness improvement loop.

Applies Karpathy's autoresearch pattern to the synthesis instruction in agent.py.

Loop (runs indefinitely until killed):
  1. Read current SYNTH_INSTRUCTION from agent.py
  2. Gather context: experiment history + evaluator feedback from last run
  3. Ask Qwen3-Coder:30b to propose a new instruction (one specific change)
  4. Apply the change to agent.py
  5. git commit
  6. Run eval_suite --score --tasks <EVAL_TASKS> → composite float
  7. If score improved by > DELTA_THRESHOLD: keep (advance), update baseline
     Else: git checkout -- agent.py (discard), log as discard
  8. Log to autoresearch.tsv
  9. GOTO 1

Mutable scope: SYNTH_INSTRUCTION and SYNTH_INSTRUCTION_COUNT in agent.py only.
Fixed metric:  eval_suite composite (wiggum r1 score + criteria rate).
Immutable:     eval_suite task definitions, wiggum evaluator, PASS_THRESHOLD.

Usage:
    conda activate ollama-pi
    python autoresearch.py                  # use defaults
    python autoresearch.py --tasks T_A,T_B  # fast: 2 tasks per experiment (~25 min/loop)
    python autoresearch.py --delta 0.2      # require larger improvement to keep

Environment:
    conda activate ollama-pi
"""

import json
import os
import re
import subprocess
import sys
import time

import ollama

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROPOSER_MODEL  = "Qwen3-Coder:30b"   # stronger than producer — proposes improvements
EVAL_TASKS      = ["T_A", "T_B"]      # subset for speed; T_A (enumerated) + T_B (open)
DELTA_THRESHOLD = 0.1                  # minimum score improvement to keep a change
TSV_PATH        = "autoresearch.tsv"
AGENT_PATH      = "agent.py"
RUNS_JSONL      = "runs.jsonl"

# Sentinel markers in agent.py (do not change without updating agent.py too)
BEGIN_MARKER = "# AUTORESEARCH:SYNTH_INSTRUCTION:BEGIN"
END_MARKER   = "# AUTORESEARCH:SYNTH_INSTRUCTION:END"
BEGIN_MARKER_COUNT = "# AUTORESEARCH:SYNTH_INSTRUCTION_COUNT:BEGIN"
END_MARKER_COUNT   = "# AUTORESEARCH:SYNTH_INSTRUCTION_COUNT:END"


# ---------------------------------------------------------------------------
# Instruction read / write
# ---------------------------------------------------------------------------

def _extract_between(text: str, begin: str, end: str) -> str:
    """Extract text between two sentinel lines (exclusive)."""
    lines = text.splitlines()
    in_block = False
    block = []
    for line in lines:
        if line.strip() == begin:
            in_block = True
            continue
        if line.strip() == end:
            break
        if in_block:
            block.append(line)
    return "\n".join(block)


def _replace_between(text: str, begin: str, end: str, new_block: str) -> str:
    """Replace lines between two sentinel lines with new_block."""
    lines = text.splitlines(keepends=True)
    out = []
    in_block = False
    for line in lines:
        if line.strip() == begin:
            out.append(line)
            in_block = True
            out.append(new_block + "\n")
            continue
        if line.strip() == end:
            in_block = False
            out.append(line)
            continue
        if not in_block:
            out.append(line)
    return "".join(out)


def _parse_instruction_value(block: str) -> str:
    """Extract the string value from a SYNTH_INSTRUCTION = (...) block.
    Handles implicit string concatenation (adjacent quoted literals).
    """
    fragments = re.findall(r'"((?:[^"\\]|\\.)*)"', block)
    return "".join(fragments)  # fragments already include trailing spaces


def _build_instruction_block(var_name: str, value: str) -> str:
    """Build a SYNTH_INSTRUCTION = (...) block from a plain string value."""
    # Escape any double quotes in the value
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'{var_name} = (\n    "{escaped}"\n)'


def read_instructions() -> dict:
    """Read current SYNTH_INSTRUCTION and SYNTH_INSTRUCTION_COUNT string values from agent.py."""
    with open(AGENT_PATH, encoding="utf-8") as f:
        text = f.read()
    synth_block       = _extract_between(text, BEGIN_MARKER, END_MARKER).strip()
    synth_count_block = _extract_between(text, BEGIN_MARKER_COUNT, END_MARKER_COUNT).strip()
    return {
        "synth":       _parse_instruction_value(synth_block),
        "synth_count": _parse_instruction_value(synth_count_block),
    }


def write_instructions(synth: str, synth_count: str):
    """Write new SYNTH_INSTRUCTION and SYNTH_INSTRUCTION_COUNT values into agent.py."""
    with open(AGENT_PATH, encoding="utf-8") as f:
        text = f.read()
    text = _replace_between(
        text, BEGIN_MARKER, END_MARKER,
        _build_instruction_block("SYNTH_INSTRUCTION", synth),
    )
    text = _replace_between(
        text, BEGIN_MARKER_COUNT, END_MARKER_COUNT,
        _build_instruction_block("SYNTH_INSTRUCTION_COUNT", synth_count),
    )
    with open(AGENT_PATH, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# TSV logging
# ---------------------------------------------------------------------------

TSV_HEADER = "experiment\tscore\tbaseline\tdelta\tstatus\tdescription\n"

def init_tsv():
    if not os.path.exists(TSV_PATH):
        with open(TSV_PATH, "w", encoding="utf-8") as f:
            f.write(TSV_HEADER)


def log_experiment(experiment: int, score: float, baseline: float, status: str, description: str):
    delta = round(score - baseline, 3)
    sign = "+" if delta >= 0 else ""
    with open(TSV_PATH, "a", encoding="utf-8") as f:
        f.write(f"{experiment}\t{score:.3f}\t{baseline:.3f}\t{sign}{delta:.3f}\t{status}\t{description}\n")
    print(f"  [tsv] exp {experiment}: score={score:.3f} baseline={baseline:.3f} "
          f"delta={sign}{delta:.3f} status={status}")


def read_history() -> str:
    """Return TSV contents as a string for the proposer prompt."""
    if not os.path.exists(TSV_PATH):
        return "(no experiments yet)"
    with open(TSV_PATH, encoding="utf-8") as f:
        return f.read().strip()


# ---------------------------------------------------------------------------
# Evaluator feedback extraction
# ---------------------------------------------------------------------------

def get_recent_eval_feedback(task_ids: list[str], n_before: int) -> str:
    """
    Read runs.jsonl entries added since n_before and extract evaluator feedback
    for runs matching the eval task fingerprints.
    """
    FINGERPRINTS = {
        "T_A": "top 5 context engineering",
        "T_B": "cost envelope management",
        "T_C": "3 most common failure modes",
        "T_D": "context window management strategies",
        "T_E": "prompt injection defense",
    }
    try:
        with open(RUNS_JSONL, encoding="utf-8") as f:
            all_runs = [json.loads(l) for l in f if l.strip()]
    except FileNotFoundError:
        return "(no runs.jsonl)"

    new_runs = all_runs[n_before:]
    feedback_lines = []
    for run in new_runs:
        task_str = run.get("task", "").lower()
        matched_id = None
        for tid in task_ids:
            if FINGERPRINTS.get(tid, "").lower() in task_str:
                matched_id = tid
                break
        if not matched_id:
            continue
        eval_log = run.get("wiggum_eval_log", [])
        for entry in eval_log:
            score = entry.get("score", "?")
            dims = entry.get("dims", {})
            issues = entry.get("issues", [])
            feedback = entry.get("feedback", "")
            dim_str = " ".join(f"{k[:3]}={v}" for k, v in dims.items())
            feedback_lines.append(f"[{matched_id} round {entry.get('round',1)} score={score} {dim_str}]")
            for issue in issues:
                feedback_lines.append(f"  issue: {issue}")
            if feedback:
                feedback_lines.append(f"  feedback: {feedback[:300]}")

    return "\n".join(feedback_lines) if feedback_lines else "(no eval feedback found)"


def get_run_count() -> int:
    try:
        with open(RUNS_JSONL, encoding="utf-8") as f:
            return sum(1 for l in f if l.strip())
    except FileNotFoundError:
        return 0


# ---------------------------------------------------------------------------
# Proposer
# ---------------------------------------------------------------------------

PROPOSE_PROMPT = """You are improving the synthesis instruction for a local LLM research agent.

The agent researches topics via web search and synthesizes findings into markdown documents.
The evaluator (Qwen3-Coder:30b) scores outputs on 5 dimensions (weights in parens):
  - relevance (0.20)
  - completeness (0.25)
  - depth (0.30)       ← most important; scored low when items lack concrete implementation steps
  - specificity (0.15) ← scored low when claims are generic rather than actionable
  - structure (0.10)

The synthesis instruction is the final sentence(s) appended to every synthesis prompt,
telling the producer model how to format and structure its output. It must:
  - Tell the model to output ONLY markdown starting with #
  - Not mention file paths
  - Be clear and direct

Current SYNTH_INSTRUCTION:
{synth}

Current SYNTH_INSTRUCTION_COUNT (used when task has a count constraint like "top 5"):
{synth_count}

Experiment history (tab-separated: experiment, score, baseline, delta, status, description):
{history}

Latest evaluator feedback from the most recent eval run:
{eval_feedback}

Your task: propose ONE specific change to the synthesis instruction(s) that might improve
the composite eval score (0.7 * mean_wiggum_r1 + 0.3 * criteria_rate * 10).

Focus on the weakest dimensions (depth, specificity). Common effective changes:
  - Adding explicit requirements for code snippets or step-by-step examples
  - Requiring a specific sub-structure within each item (e.g. "what / why / how")
  - Asking the model to name specific tools, versions, or libraries
  - Requiring a comparison or trade-off where relevant

Rules:
  - Output complete replacement strings — not patches
  - Both instructions must still say "output ONLY the markdown starting with #"
  - Make one focused change; don't try to fix everything at once
  - If history shows a change was DISCARDed, don't repeat it

Output ONLY valid JSON (no preamble, no markdown fences):
{{
  "synth": "complete replacement for SYNTH_INSTRUCTION (the Python string value, not the assignment)",
  "synth_count": "complete replacement for SYNTH_INSTRUCTION_COUNT",
  "description": "one line: what changed and why"
}}"""


def propose_instructions(current: dict, history: str, eval_feedback: str) -> dict | None:
    """Ask proposer model to suggest new synthesis instructions. Returns dict or None on failure."""
    prompt = PROPOSE_PROMPT.format(
        synth=current["synth"],
        synth_count=current["synth_count"],
        history=history,
        eval_feedback=eval_feedback,
    )
    print("  [propose] asking proposer for new instruction...")
    try:
        response = ollama.chat(
            model=PROPOSER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3},
        )
    except Exception as e:
        print(f"  [propose] ollama error: {e}")
        return None

    raw = response["message"]["content"].strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE)
    # Strip <think>...</think> if present
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  [propose] parse error, raw: {raw[:300]}")
        return None

    for key in ("synth", "synth_count", "description"):
        if key not in result:
            print(f"  [propose] missing key '{key}' in response")
            return None

    return result


# ---------------------------------------------------------------------------
# Eval
# ---------------------------------------------------------------------------

def run_eval(task_ids: list[str]) -> float:
    """Run eval_suite --score --tasks <tasks> and return composite float."""
    tasks_arg = ",".join(task_ids)
    print(f"  [eval] running eval_suite on {tasks_arg}...")
    result = subprocess.run(
        [sys.executable, "eval_suite.py", "--score", "--tasks", tasks_arg],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    stdout = result.stdout.strip()
    try:
        score = float(stdout.split("\n")[-1].strip())
        print(f"  [eval] composite score: {score:.3f}")
        return score
    except (ValueError, IndexError):
        print(f"  [eval] parse error, stdout: {stdout[:200]!r}")
        return 0.0


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_commit(message: str):
    subprocess.run(["git", "add", AGENT_PATH], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)


def git_discard():
    """Restore agent.py to last committed state."""
    subprocess.run(["git", "checkout", "--", AGENT_PATH], check=True)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    # Parse args
    args = sys.argv[1:]
    task_ids = EVAL_TASKS[:]
    if "--tasks" in args:
        idx = args.index("--tasks")
        if idx + 1 < len(args):
            task_ids = [t.strip() for t in args[idx + 1].split(",")]
    delta_threshold = DELTA_THRESHOLD
    if "--delta" in args:
        idx = args.index("--delta")
        if idx + 1 < len(args):
            delta_threshold = float(args[idx + 1])

    print("\n" + "=" * 60)
    print(" autoresearch — autonomous synthesis instruction improvement")
    print(f" proposer:  {PROPOSER_MODEL}")
    print(f" eval tasks: {task_ids}")
    print(f" delta threshold: {delta_threshold}")
    print("=" * 60 + "\n")

    init_tsv()

    # Establish baseline if not present
    history = read_history()
    if history == "(no experiments yet)" or not any("baseline" in l for l in history.splitlines()):
        print("[baseline] running initial eval to establish baseline...")
        baseline_score = run_eval(task_ids)
        log_experiment(0, baseline_score, baseline_score, "baseline", "initial baseline")
        print(f"[baseline] score: {baseline_score:.3f}\n")
    else:
        # Extract best score from history
        scores = []
        for line in history.splitlines()[1:]:  # skip header
            parts = line.split("\t")
            if len(parts) >= 2:
                try:
                    scores.append(float(parts[1]))
                except ValueError:
                    pass
        baseline_score = max(scores) if scores else 0.0
        print(f"[resume] best score from history: {baseline_score:.3f}\n")

    experiment = sum(1 for l in history.splitlines() if l and not l.startswith("experiment")) + 1

    # LOOP FOREVER
    while True:
        print(f"\n{'=' * 60}")
        print(f" Experiment {experiment}")
        print(f" Baseline: {baseline_score:.3f}")
        print(f"{'=' * 60}")

        # 1. Get context
        current = read_instructions()
        history = read_history()
        n_before = get_run_count()

        # Get eval feedback from most recent runs of our eval tasks
        eval_feedback = get_recent_eval_feedback(task_ids, max(0, n_before - len(task_ids) * 2))
        if not eval_feedback or eval_feedback == "(no eval feedback found)":
            eval_feedback = "(no prior eval feedback — first experiment)"

        # 2. Propose
        proposal = propose_instructions(current, history, eval_feedback)
        if proposal is None:
            print("  [warn] proposer failed — skipping experiment")
            time.sleep(5)
            continue

        description = proposal["description"]
        print(f"  [proposal] {description}")
        print(f"  [proposal] synth instruction (first 120 chars): {proposal['synth'][:120]!r}")

        # 3. Apply
        write_instructions(
            synth=proposal["synth"],
            synth_count=proposal["synth_count"],
        )

        # 4. Git commit
        commit_msg = f"autoresearch exp {experiment}: {description}"
        try:
            git_commit(commit_msg)
        except subprocess.CalledProcessError as e:
            print(f"  [warn] git commit failed: {e} — continuing anyway")

        # 5. Eval
        n_before_eval = get_run_count()
        score = run_eval(task_ids)

        # 6. Keep or discard
        delta = score - baseline_score
        if delta > delta_threshold:
            status = "keep"
            baseline_score = score
            print(f"  [KEEP] {score:.3f} (+{delta:.3f}) — new baseline: {baseline_score:.3f}")
        else:
            status = "discard"
            print(f"  [DISCARD] {score:.3f} (delta={delta:+.3f} <= threshold {delta_threshold})")
            try:
                git_discard()
                # Amend the commit to mark as discarded, or just leave it — git log shows the experiment
                # For cleanliness, reset the commit too
                subprocess.run(["git", "reset", "HEAD~1", "--soft"], check=True)
                subprocess.run(["git", "checkout", "--", AGENT_PATH], check=True)
            except subprocess.CalledProcessError as e:
                print(f"  [warn] git discard failed: {e}")

        # 7. Log
        log_experiment(experiment, score, baseline_score if status == "keep" else baseline_score, status, description)

        # Refresh eval feedback for next round
        # (new runs were just logged; next iteration will pick them up)

        experiment += 1
        print(f"\n  [loop] experiment {experiment - 1} done. Starting {experiment}...")


if __name__ == "__main__":
    main()
