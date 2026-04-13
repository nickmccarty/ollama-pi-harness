"""
github_skill.py — /github standalone skill.

Provides LLM-assisted GitHub operations via the `gh` CLI.

Supported operations (auto-detected from task string):
  push        — stage, commit, and push current branch
  pr create   — LLM-generated title + body from git diff, then gh pr create
  pr list     — list open PRs
  pr view     — view a specific PR (by number or current branch)
  pr merge    — merge a PR
  pr review   — add a review comment
  issue create — LLM-generated issue from task description
  issue list  — list open issues
  issue view  — view a specific issue
  repo view   — show repo info
  repo clone  — clone a repo by owner/name
  status      — git status + recent log summary

Usage (via agent.py):
    python agent.py "/github push add GitHub skill"
    python agent.py "/github pr create"
    python agent.py "/github pr list"
    python agent.py "/github issue create synthesis output is too long"
    python agent.py "/github repo view nickmccarty/harness-engineering"
    python agent.py "/github status"
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path

import ollama as _ollama_raw

HERE         = Path(__file__).parent
_KEEP_ALIVE  = int(os.environ.get("OLLAMA_KEEP_ALIVE", -1))
_DEFAULT_MODEL = os.environ.get("PRODUCER_MODEL", "llama3.2:3b")

# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], cwd: str = None, check: bool = False) -> tuple[int, str, str]:
    """Run a shell command, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd or str(HERE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _require_gh():
    """Exit with a helpful message if gh CLI is not installed."""
    rc, _, _ = _run(["gh", "--version"])
    if rc != 0:
        print("[github_skill] gh CLI not found.")
        print("  Install: https://cli.github.com/")
        print("  Then authenticate: gh auth login")
        sys.exit(1)


def _require_git():
    rc, _, _ = _run(["git", "rev-parse", "--git-dir"])
    if rc != 0:
        print("[github_skill] Not inside a git repository.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def _llm(system: str, user: str, model: str) -> str:
    resp = _ollama_raw.chat(
        model=model,
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ],
        options={"temperature": 0.3},
        keep_alive=_KEEP_ALIVE,
    )
    return resp["message"]["content"].strip()


_PR_SYSTEM = """\
You are a precise technical writer. Given git diff output and a task description, \
write a GitHub pull request title and body.

Output format (exactly):
TITLE: <one concise sentence, ≤72 chars>
BODY:
<2-4 sentence summary of what changed and why. Plain prose. No bullet points.>

Do not include any other text before TITLE or after the body.\
"""

_ISSUE_SYSTEM = """\
You are a precise technical writer. Given a description of a problem or request, \
write a GitHub issue title and body.

Output format (exactly):
TITLE: <one concise sentence, ≤72 chars>
BODY:
<2-4 sentences describing the problem, expected behaviour, and relevant context. Plain prose.>

Do not include any other text before TITLE or after the body.\
"""

_COMMIT_SYSTEM = """\
You are a precise technical writer. Given a git diff and optional task description, \
write a single git commit message.

Rules:
- One line only, ≤72 characters.
- Imperative mood ("Add", "Fix", "Update", not "Added", "Fixed").
- Be specific — name the file or function when it fits.
- Output ONLY the commit message text. Nothing else.\
"""


def _parse_title_body(text: str) -> tuple[str, str]:
    """Parse TITLE: / BODY: sections from LLM output."""
    title_m = re.search(r"^TITLE:\s*(.+)$", text, re.MULTILINE)
    body_m  = re.search(r"^BODY:\s*\n([\s\S]+)", text, re.MULTILINE)
    title   = title_m.group(1).strip() if title_m else text.splitlines()[0][:72]
    body    = body_m.group(1).strip()  if body_m  else text
    return title, body


# ---------------------------------------------------------------------------
# Operation implementations
# ---------------------------------------------------------------------------

def op_status(args: list[str], model: str) -> str:
    _require_git()
    _, status, _  = _run(["git", "status", "--short"])
    _, log, _     = _run(["git", "log", "--oneline", "-10"])
    _, branch, _  = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    out = [
        f"Branch: {branch}",
        "",
        "Recent commits:",
        log or "(none)",
        "",
        "Working tree:",
        status or "(clean)",
    ]
    return "\n".join(out)


def op_push(args: list[str], model: str) -> str:
    """Stage all, generate commit message via LLM, commit, push."""
    _require_git()

    _, branch, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, diff, _   = _run(["git", "diff", "--cached", "--stat"])

    # Stage everything not already staged
    _run(["git", "add", "-A"])
    _, diff_full, _ = _run(["git", "diff", "--cached"])

    if not diff_full.strip():
        return "[github] Nothing to commit — working tree is clean."

    task_hint = " ".join(args).strip()
    user_msg  = f"Task: {task_hint}\n\nDiff:\n{diff_full[:6000]}"
    commit_msg = _llm(_COMMIT_SYSTEM, user_msg, model)
    print(f"[github] commit message: {commit_msg}")

    rc, out, err = _run(["git", "commit", "-m", commit_msg])
    if rc != 0:
        return f"[github] commit failed:\n{err}"

    rc, out, err = _run(["git", "push", "--set-upstream", "origin", branch])
    if rc != 0:
        return f"[github] push failed:\n{err}"

    return f"[github] pushed branch '{branch}'\n{out}"


def op_pr_create(args: list[str], model: str) -> str:
    _require_gh()
    _require_git()

    _, branch, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, diff, _   = _run(["git", "diff", "origin/main...HEAD"])
    _, log, _    = _run(["git", "log", "origin/main...HEAD", "--oneline"])

    task_hint = " ".join(args).strip()
    user_msg  = (
        f"Task hint: {task_hint}\n\n"
        f"Commits:\n{log}\n\n"
        f"Diff (truncated to 6000 chars):\n{diff[:6000]}"
    )
    raw = _llm(_PR_SYSTEM, user_msg, model)
    title, body = _parse_title_body(raw)

    print(f"[github] PR title: {title}")
    print(f"[github] PR body:\n{body}\n")

    rc, out, err = _run([
        "gh", "pr", "create",
        "--title", title,
        "--body",  body,
    ])
    if rc != 0:
        return f"[github] pr create failed:\n{err}"
    return f"[github] PR created:\n{out}"


def op_pr_list(args: list[str], model: str) -> str:
    _require_gh()
    rc, out, err = _run(["gh", "pr", "list"])
    return out or "(no open PRs)"


def op_pr_view(args: list[str], model: str) -> str:
    _require_gh()
    pr_num = args[0] if args else ""
    cmd = ["gh", "pr", "view"] + ([pr_num] if pr_num else [])
    rc, out, err = _run(cmd)
    return out if rc == 0 else f"[github] pr view failed:\n{err}"


def op_pr_merge(args: list[str], model: str) -> str:
    _require_gh()
    pr_num = args[0] if args else ""
    cmd = ["gh", "pr", "merge", "--merge"] + ([pr_num] if pr_num else [])
    rc, out, err = _run(cmd)
    return out if rc == 0 else f"[github] pr merge failed:\n{err}"


def op_pr_review(args: list[str], model: str) -> str:
    """Add a review comment to a PR. Args: [pr_num] <comment text>"""
    _require_gh()
    if args and args[0].isdigit():
        pr_num, comment = args[0], " ".join(args[1:])
    else:
        pr_num, comment = "", " ".join(args)
    if not comment:
        return "[github] pr review requires a comment body"
    cmd = ["gh", "pr", "review", "--comment", "--body", comment] + ([pr_num] if pr_num else [])
    rc, out, err = _run(cmd)
    return out if rc == 0 else f"[github] pr review failed:\n{err}"


def op_issue_create(args: list[str], model: str) -> str:
    _require_gh()
    description = " ".join(args).strip()
    if not description:
        return "[github] issue create requires a description"

    raw = _llm(_ISSUE_SYSTEM, f"Problem description: {description}", model)
    title, body = _parse_title_body(raw)

    print(f"[github] issue title: {title}")
    print(f"[github] issue body:\n{body}\n")

    rc, out, err = _run([
        "gh", "issue", "create",
        "--title", title,
        "--body",  body,
    ])
    return out if rc == 0 else f"[github] issue create failed:\n{err}"


def op_issue_list(args: list[str], model: str) -> str:
    _require_gh()
    rc, out, err = _run(["gh", "issue", "list"])
    return out or "(no open issues)"


def op_issue_view(args: list[str], model: str) -> str:
    _require_gh()
    issue_num = args[0] if args else ""
    if not issue_num:
        return "[github] issue view requires an issue number"
    rc, out, err = _run(["gh", "issue", "view", issue_num])
    return out if rc == 0 else f"[github] issue view failed:\n{err}"


def op_repo_view(args: list[str], model: str) -> str:
    _require_gh()
    repo = args[0] if args else ""
    cmd  = ["gh", "repo", "view"] + ([repo] if repo else [])
    rc, out, err = _run(cmd)
    return out if rc == 0 else f"[github] repo view failed:\n{err}"


def op_repo_clone(args: list[str], model: str) -> str:
    _require_gh()
    repo = args[0] if args else ""
    if not repo:
        return "[github] repo clone requires owner/repo"
    rc, out, err = _run(["gh", "repo", "clone", repo])
    return out if rc == 0 else f"[github] repo clone failed:\n{err}"


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_OPS = {
    # git
    "status":       op_status,
    "push":         op_push,
    # PR
    "pr":           None,          # resolved via sub-command
    "pr create":    op_pr_create,
    "pr list":      op_pr_list,
    "pr view":      op_pr_view,
    "pr merge":     op_pr_merge,
    "pr review":    op_pr_review,
    # issues
    "issue":        None,
    "issue create": op_issue_create,
    "issue list":   op_issue_list,
    "issue view":   op_issue_view,
    # repo
    "repo":         None,
    "repo view":    op_repo_view,
    "repo clone":   op_repo_clone,
}


def _dispatch(tokens: list[str], model: str) -> str:
    """
    Match tokens to the longest known operation prefix.
    e.g. ["pr", "create", "fix", "bug"] -> op_pr_create(["fix", "bug"])
    """
    # Try two-word key first, then one-word
    if len(tokens) >= 2:
        two = f"{tokens[0]} {tokens[1]}"
        if two in _OPS and _OPS[two] is not None:
            return _OPS[two](tokens[2:], model)

    one = tokens[0] if tokens else ""
    if one in _OPS and _OPS[one] is not None:
        return _OPS[one](tokens[1:], model)

    # Unknown — list available operations
    ops = [k for k, v in _OPS.items() if v is not None]
    return (
        f"[github] Unknown operation: '{' '.join(tokens[:2])}'\n"
        f"Available: {', '.join(sorted(ops))}"
    )


# ---------------------------------------------------------------------------
# Entry point (called from agent.py dispatch)
# ---------------------------------------------------------------------------

def run_github_standalone(task: str, model: str = _DEFAULT_MODEL) -> str:
    """
    Parse the task string and dispatch to the appropriate GitHub operation.
    Returns a string result for agent.py to print/write.
    """
    tokens = task.strip().split()
    if not tokens:
        ops = [k for k, v in _OPS.items() if v is not None]
        return f"[github] No operation specified. Available: {', '.join(sorted(ops))}"

    result = _dispatch(tokens, model)
    print(result)
    return result


# ---------------------------------------------------------------------------
# CLI (standalone test)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "status"
    run_github_standalone(task)
