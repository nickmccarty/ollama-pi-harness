"""
eval_suite.py — regression harness for the agent pipeline.

Runs a fixed set of representative tasks and checks content criteria beyond
file existence: minimum size, section count, absence of placeholders, and
presence of implementation notes.

Run after any model swap, Modelfile change, or harness modification to detect
regressions before they accumulate.

Usage:
    python eval_suite.py              # run all tasks then check criteria
    python eval_suite.py --fast       # check existing output files only (no re-runs)
    python eval_suite.py --no-wiggum  # run tasks but skip wiggum loop (faster)

Environment:
    conda activate ollama-pi
"""

import os
import re
import sys
import subprocess

# ---------------------------------------------------------------------------
# Criterion factories
# ---------------------------------------------------------------------------

def min_bytes(n: int):
    def check(content: str):
        b = len(content.encode("utf-8"))
        ok = b >= n
        return ok, f"{b} bytes (need >= {n})"
    check.__name__ = f"min_bytes({n})"
    return check


def min_lines(n: int):
    def check(content: str):
        lines = content.count("\n") + 1
        ok = lines >= n
        return ok, f"{lines} lines (need >= {n})"
    check.__name__ = f"min_lines({n})"
    return check


def exact_sections(n: int):
    """Exactly n H2-level content sections (excluding structural headers)."""
    structural = {"introduction", "conclusion", "summary", "overview", "background", "references"}
    def check(content: str):
        headers = re.findall(r'^##\s+(.+)', content, re.MULTILINE)
        items = [h for h in headers if re.sub(r'^[\d.\s]+', '', h).strip().lower() not in structural]
        ok = len(items) == n
        return ok, f"{len(items)} content sections (need exactly {n})"
    check.__name__ = f"exact_sections({n})"
    return check


def min_sections(n: int):
    """At least n H2-level sections (any)."""
    def check(content: str):
        headers = re.findall(r'^##\s+\S', content, re.MULTILINE)
        ok = len(headers) >= n
        return ok, f"{len(headers)} H2 sections (need >= {n})"
    check.__name__ = f"min_sections({n})"
    return check


def no_placeholders():
    """Output must not contain placeholder text."""
    BAD = [
        "[placeholder]", "TODO", "brief implementation note", "add example here",
        "implementation note here", "your example here",
    ]
    def check(content: str):
        found = [b for b in BAD if b.lower() in content.lower()]
        ok = len(found) == 0
        return ok, ("clean" if ok else f"placeholder text found: {found}")
    check.__name__ = "no_placeholders"
    return check


def has_impl_notes():
    """Output must contain at least one implementation note or code example."""
    MARKERS = ["implementation note", "example:", "```", "**example", "**implementation"]
    def check(content: str):
        found = any(m.lower() in content.lower() for m in MARKERS)
        return found, ("has implementation notes/examples" if found else "no implementation notes or examples found")
    check.__name__ = "has_impl_notes"
    return check


def no_file_path_refs():
    """Output must not mention file save paths (producer artifact)."""
    def check(content: str):
        # Common producer artifact: "This document is saved to ~/..."
        patterns = [r'saved to ~/\S+\.md', r'save.*~/\S+\.md', r'written to ~/\S+\.md']
        found = any(re.search(p, content, re.IGNORECASE) for p in patterns)
        return not found, ("clean" if not found else "output contains file path reference (producer artifact)")
    check.__name__ = "no_file_path_refs"
    return check


# ---------------------------------------------------------------------------
# Task registry
# ---------------------------------------------------------------------------

BASE = "~/Desktop/harness-engineering"

SUITE = [
    {
        "id": "T_A",
        "desc": "top 5, context engineering",
        "task": f"Search for the top 5 context engineering techniques used in production LLM agents and save to {BASE}/eval-context-engineering.md",
        "output": f"{BASE}/eval-context-engineering.md",
        "criteria": [
            min_bytes(800),
            min_lines(15),
            exact_sections(5),
            no_placeholders(),
            has_impl_notes(),
            no_file_path_refs(),
        ],
    },
    {
        "id": "T_B",
        "desc": "open-ended, cost management",
        "task": f"Search for best practices for cost envelope management in production AI agents and save to {BASE}/eval-cost-management.md",
        "output": f"{BASE}/eval-cost-management.md",
        "criteria": [
            min_bytes(800),
            min_lines(15),
            min_sections(3),
            no_placeholders(),
            has_impl_notes(),
            no_file_path_refs(),
        ],
    },
    {
        "id": "T_C",
        "desc": "top 3, agent failure modes",
        "task": f"Search for the 3 most common failure modes in multi-agent AI systems and save to {BASE}/eval-agent-failure-modes.md",
        "output": f"{BASE}/eval-agent-failure-modes.md",
        "criteria": [
            min_bytes(600),
            min_lines(10),
            exact_sections(3),
            no_placeholders(),
            has_impl_notes(),
            no_file_path_refs(),
        ],
    },
    {
        "id": "T_D",
        "desc": "top 3, context window management",
        "task": f"Search for the top 3 context window management strategies for production LLM applications and save to {BASE}/eval-context-window.md",
        "output": f"{BASE}/eval-context-window.md",
        "criteria": [
            min_bytes(600),
            min_lines(10),
            exact_sections(3),
            no_placeholders(),
            has_impl_notes(),
            no_file_path_refs(),
        ],
    },
    {
        "id": "T_E",
        "desc": "open-ended, prompt injection defense",
        "task": f"Search for best practices for prompt injection defense in production AI systems and save to {BASE}/eval-prompt-injection.md",
        "output": f"{BASE}/eval-prompt-injection.md",
        "criteria": [
            min_bytes(800),
            min_lines(15),
            min_sections(3),
            no_placeholders(),
            has_impl_notes(),
            no_file_path_refs(),
        ],
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_task(task_def: dict, use_wiggum: bool = True) -> bool:
    """Run agent.py for a task. Returns True if agent exited cleanly."""
    cmd = [sys.executable, "agent.py"]
    if not use_wiggum:
        cmd.append("--no-wiggum")
    cmd.append(task_def["task"])

    print(f"  [run] {task_def['id']}: {task_def['desc']}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def check_task(task_def: dict) -> list[dict]:
    """Check all criteria for a task's output. Returns list of result dicts."""
    output_path = os.path.expanduser(task_def["output"])
    results = []

    if not os.path.exists(output_path):
        return [{"criterion": "file_exists", "passed": False, "detail": f"not found: {output_path}"}]

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return [{"criterion": "file_not_empty", "passed": False, "detail": "file is empty"}]

    for criterion_fn in task_def["criteria"]:
        passed, detail = criterion_fn(content)
        results.append({
            "criterion": criterion_fn.__name__,
            "passed": passed,
            "detail": detail,
        })

    return results


def print_results(task_def: dict, results: list[dict]):
    passed_all = all(r["passed"] for r in results)
    status = "PASS" if passed_all else "FAIL"
    print(f"\n  {task_def['id']} ({task_def['desc']}) — {status}")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        print(f"    {mark} {r['criterion']}: {r['detail']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fast = "--fast" in sys.argv
    no_wiggum = "--no-wiggum" in sys.argv

    print("\n======================================")
    print(" Eval Suite")
    print(f" mode: {'fast (criteria check only)' if fast else 'full (run + check)'}")
    print("======================================\n")

    total_tasks = len(SUITE)
    passed_tasks = 0
    total_criteria = 0
    passed_criteria = 0

    for task_def in SUITE:
        if not fast:
            ok = run_task(task_def, use_wiggum=not no_wiggum)
            if not ok:
                print(f"  [warn] agent.py exited with error for {task_def['id']}")

        results = check_task(task_def)
        print_results(task_def, results)

        task_passed = all(r["passed"] for r in results)
        if task_passed:
            passed_tasks += 1
        total_criteria += len(results)
        passed_criteria += sum(1 for r in results if r["passed"])

    print(f"\n======================================")
    print(f" Tasks:    {passed_tasks}/{total_tasks} passed")
    print(f" Criteria: {passed_criteria}/{total_criteria} passed")
    print(f" Overall:  {'PASS' if passed_tasks == total_tasks else 'FAIL'}")
    print(f"======================================\n")

    sys.exit(0 if passed_tasks == total_tasks else 1)
