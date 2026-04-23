"""
mcp_server.py — MCP server exposing the harness as a callable agent.

Makes the harness interoperable with any MCP-compatible client:
  - Claude Code (add to .mcp.json or mcp_config.json)
  - External orchestrators via streamable-http
  - Other harness instances routing subtasks cross-team

Tools exposed:
  run_task(task)         — run agent.py, return markdown output content
  run_orchestrated(task) — run orchestrator.py for multi-subtask tasks
  get_run(run_id)        — fetch a runs.jsonl record by run_id

Resources exposed:
  runs://recent          — last N runs summary (scores, status, task preview)

Transports:
  stdio  (default) — for Claude Code / local MCP clients
    python mcp_server.py
  streamable-http  — for remote cross-team dispatch
    python mcp_server.py --http [--port 8766] [--host 0.0.0.0]
  sse              — legacy SSE transport
    python mcp_server.py --sse

Claude Code config (.mcp.json or ~/.claude/mcp_config.json):
  {
    "mcpServers": {
      "harness": {
        "command": "python",
        "args": ["C:/Users/nicho/Desktop/harness-engineering/mcp_server.py"],
        "cwd": "C:/Users/nicho/Desktop/harness-engineering"
      }
    }
  }

Remote dispatch via HARNESS_MCP_ENDPOINTS:
  HARNESS_MCP_ENDPOINTS='{"security":  "http://team-b-harness:8766/mcp"}'
  python orchestrator.py "Research X (security aspects) and Y and save to out.md"
  → "security aspects" subtask dispatched to team-b-harness via MCP

Environment:
  MCP_SERVER_PORT   — HTTP port (default: 8766)
  MCP_SERVER_HOST   — HTTP host (default: 127.0.0.1)
  MCP_RECENT_RUNS   — number of recent runs to include in runs://recent (default: 10)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import argparse

from mcp.server.fastmcp import FastMCP
from security import check_output_path, scan_for_injection

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENT_SCRIPT = os.path.join(_BASE_DIR, "agent.py")
_ORCH_SCRIPT  = os.path.join(_BASE_DIR, "orchestrator.py")
_RUNS_PATH    = os.path.join(_BASE_DIR, "runs.jsonl")
_RECENT_N     = int(os.environ.get("MCP_RECENT_RUNS", 10))

# Security limits
_TASK_MAX_CHARS   = int(os.environ.get("MCP_TASK_MAX_CHARS", 2000))
_MAX_CONCURRENCY  = int(os.environ.get("MCP_MAX_CONCURRENCY", 2))
_API_KEY          = os.environ.get("MCP_API_KEY", "")      # empty = no auth required
_semaphore        = threading.Semaphore(_MAX_CONCURRENCY)


def _validate_task(task: str) -> tuple[bool, str]:
    """
    Gate all MCP tool inputs: length cap, UNC block, injection scan, output path check.
    Returns (ok, error_message).
    """
    if len(task) > _TASK_MAX_CHARS:
        return False, f"task too long: {len(task)} chars (max {_TASK_MAX_CHARS})"

    # Block UNC paths (\\server\share) which could reach network shares
    if "\\\\" in task or task.lstrip().startswith("//"):
        return False, "UNC/network paths are not permitted in task strings"

    clean, matches = scan_for_injection(task, source="mcp_task")
    if not clean:
        return False, f"task rejected (injection pattern): {matches[0]}"

    # Validate any output path embedded in the task
    import re as _re
    m = _re.search(
        r"(~[\w/\\.\\-]+\.md|[A-Za-z]:[\w/\\.\-]+\.md|/[\w/.\-]+\.md|[\w./\\\-]+\.md)",
        task,
    )
    if m:
        ok, reason = check_output_path(m.group(1))
        if not ok:
            return False, f"output path rejected: {reason}"

    return True, ""


def _check_api_key(provided: str) -> bool:
    """Return True if auth is not configured or the key matches."""
    if not _API_KEY:
        return True
    return provided == _API_KEY

mcp = FastMCP(
    "harness-engineering",
    instructions=(
        "Research and synthesis agent harness. "
        "Use run_task() to execute a research task and get back a markdown document. "
        "Include a .md output path in the task string (e.g. 'save to ~/Desktop/out.md'). "
        "Use get_run() to retrieve details about a previous run by run_id."
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_temp_path(suffix: str = ".md") -> str:
    """Generate a temp output path if the task doesn't specify one."""
    fd, path = tempfile.mkstemp(suffix=suffix, dir=_BASE_DIR)
    os.close(fd)
    return path


def _ensure_output_path(task: str) -> tuple[str, str]:
    """
    Return (task_with_path, output_path).
    Injects a temp path if none is present in the task string.
    """
    import re
    m = re.search(r"(~[\w/\\.\\-]+\.md|[A-Za-z]:[\w/\\.\-]+\.md|/[\w/.\-]+\.md|[\w./\\\-]+\.md)", task)
    if m:
        return task, os.path.expanduser(m.group(1))
    tmp = _make_temp_path()
    return f"{task} save to {tmp}", tmp


def _run_subprocess(script: str, task: str, timeout: int = 600) -> dict:
    """Run agent.py or orchestrator.py and return {content, ok, run_id, elapsed}."""
    task_with_path, output_path = _ensure_output_path(task)
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script, task_with_path],
        cwd=_BASE_DIR,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ.copy(),
    )
    elapsed = round(time.time() - t0, 1)

    content = ""
    expanded = os.path.expanduser(output_path)
    if os.path.exists(expanded):
        with open(expanded, "r", encoding="utf-8") as f:
            content = f.read()

    # Extract run_id from stdout if available
    import re as _re
    run_id_m = _re.search(r"run_id[=:\s]+([0-9T Z\-a-f]+)", result.stdout)
    run_id = run_id_m.group(1).strip() if run_id_m else ""

    return {
        "content":  content,
        "ok":       result.returncode == 0 and bool(content.strip()),
        "run_id":   run_id,
        "elapsed":  elapsed,
        "stdout":   result.stdout[-2000:] if result.stdout else "",
        "stderr":   result.stderr[-500:]  if result.stderr else "",
    }


def _load_recent_runs(n: int = _RECENT_N) -> list[dict]:
    runs = []
    try:
        with open(_RUNS_PATH, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        runs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except FileNotFoundError:
        pass
    return runs[-n:]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def run_task(task: str, api_key: str = "") -> str:
    """
    Run a research or synthesis task through the harness agent pipeline.

    The task string should describe what to research and where to save the output,
    e.g.: "Search for best practices for prompt injection defense and save to ~/Desktop/out.md"

    If no output path is included, a temporary path is used and the content is
    returned directly.

    api_key: required when MCP_API_KEY is set on the server.

    Returns the markdown document content produced by the agent.
    """
    if not _check_api_key(api_key):
        return "[error] invalid or missing api_key"
    ok, err = _validate_task(task)
    if not ok:
        return f"[error] {err}"

    # Block until a slot is free — callers queue here rather than getting an error
    _semaphore.acquire(blocking=True)
    try:
        result = _run_subprocess(_AGENT_SCRIPT, task)
    finally:
        _semaphore.release()

    if not result["ok"]:
        error_hint = result["stderr"] or result["stdout"] or "unknown error"
        return f"[error] Agent run failed after {result['elapsed']}s.\n{error_hint}"
    return result["content"]


@mcp.tool()
def run_orchestrated(task: str, api_key: str = "") -> str:
    """
    Run a complex multi-subtask research task through the orchestrator.

    Use this for tasks that span multiple topics or require cross-referencing
    multiple research threads, e.g.:
    "Research X and Y and Z, synthesize into a guide and save to ~/Desktop/out.md"

    The orchestrator decomposes the task into parallel subtasks, assembles the
    results, and runs wiggum verification on the final output.

    api_key: required when MCP_API_KEY is set on the server.

    Returns the assembled markdown document.
    """
    if not _check_api_key(api_key):
        return "[error] invalid or missing api_key"
    ok, err = _validate_task(task)
    if not ok:
        return f"[error] {err}"

    _semaphore.acquire(blocking=True)
    try:
        result = _run_subprocess(_ORCH_SCRIPT, task, timeout=1800)
    finally:
        _semaphore.release()

    if not result["ok"]:
        error_hint = result["stderr"] or result["stdout"] or "unknown error"
        return f"[error] Orchestration failed after {result['elapsed']}s.\n{error_hint}"
    return result["content"]


@mcp.tool()
def get_run(run_id: str) -> str:
    """
    Retrieve a run record from runs.jsonl by run_id.

    Returns a JSON summary of the run: task, scores, status, duration, model info.
    """
    try:
        with open(_RUNS_PATH, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if r.get("run_id") == run_id:
                        summary = {
                            "run_id":        r.get("run_id"),
                            "task":          r.get("task", "")[:200],
                            "final":         r.get("final"),
                            "wiggum_scores": r.get("wiggum_scores", []),
                            "output_bytes":  r.get("output_bytes"),
                            "run_duration_s": r.get("run_duration_s"),
                            "producer_model": r.get("producer_model"),
                            "task_type":     r.get("task_type"),
                            "timestamp":     r.get("timestamp"),
                        }
                        return json.dumps(summary, indent=2)
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        pass
    return json.dumps({"error": f"run_id {run_id!r} not found"})


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("runs://recent")
def recent_runs() -> str:
    """Summary of the most recent agent runs: task, score, status, duration."""
    runs = _load_recent_runs()
    if not runs:
        return "No runs found."
    lines = [f"Recent {len(runs)} run(s):\n"]
    for r in reversed(runs):
        scores = r.get("wiggum_scores", [])
        score_str = f"  score={scores[-1]}" if scores else "  no-wiggum"
        lines.append(
            f"  [{r.get('timestamp','')[:16]}] {r.get('final','?'):4s}{score_str}"
            f"  {r.get('run_duration_s',0):.0f}s  {r.get('task','')[:80]}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harness MCP server")
    parser.add_argument("--http",   action="store_true", help="Streamable HTTP transport")
    parser.add_argument("--sse",    action="store_true", help="Legacy SSE transport")
    parser.add_argument("--port",   type=int, default=int(os.environ.get("MCP_SERVER_PORT", 8766)))
    parser.add_argument("--host",   default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"))
    args = parser.parse_args()

    if args.http:
        os.environ.setdefault("FASTMCP_PORT", str(args.port))
        os.environ.setdefault("FASTMCP_HOST", args.host)
        print(f"[mcp_server] streamable-http on {args.host}:{args.port}")
        mcp.run(transport="streamable-http")
    elif args.sse:
        os.environ.setdefault("FASTMCP_PORT", str(args.port))
        os.environ.setdefault("FASTMCP_HOST", args.host)
        print(f"[mcp_server] SSE on {args.host}:{args.port}")
        mcp.run(transport="sse")
    else:
        print("[mcp_server] stdio transport (for Claude Code / local clients)")
        mcp.run(transport="stdio")
