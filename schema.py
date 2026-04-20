"""
schema.py — harness data model.

Formal dataclass definitions for all persistent entities plus helpers for
ID generation, JSONL append, and project/session lifecycle management.

Entity hierarchy:
    Project > Session > Run > (Artifact, Message, Observation, Feedback)

All IDs use the format:  20260418T100000Z-a1b2c3d4e5f6
  └── UTC compact ISO 8601 ──┘ └─ uuid4 hex[:12] ─┘

ID properties:
  - Lexicographic sort == chronological sort
  - Human-readable date prefix (grep-friendly)
  - Fixed 27-char length
  - Shell/filename/URL-safe (no colons, spaces, slashes)

JSONL files (all gitignored):
    projects.jsonl   — project lifecycle events (create / update / archive)
    sessions.jsonl   — session start / end events
    artifacts.jsonl  — produced file registry (one record per file written)
    messages.jsonl   — LLM conversation log (one record per message/tool call)
    plans.jsonl      — orchestrator/agent plan records (written before execution)

Usage:
    # Resolve or create the active project
    project_id = resolve_project_id()

    # Start a session
    session = start_session(project_id, triggered_by="cli")

    # End a session
    end_session(session, runs=3, total_input_tokens=12000, ...)

    # Project management CLI
    python schema.py create-project --name "harness-engineering"
    python schema.py list-projects
    python schema.py set-project 20260418T100000Z-a1b2c3d4e5f6
    python schema.py project-stats 20260418T100000Z-a1b2c3d4e5f6
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

_BASE = os.path.dirname(os.path.abspath(__file__))

PROJECTS_PATH  = os.path.join(_BASE, "projects.jsonl")
SESSIONS_PATH  = os.path.join(_BASE, "sessions.jsonl")
ARTIFACTS_PATH = os.path.join(_BASE, "artifacts.jsonl")
MESSAGES_PATH  = os.path.join(_BASE, "messages.jsonl")
PLANS_PATH     = os.path.join(_BASE, "plans.jsonl")
DOTFILE        = os.path.join(_BASE, ".harness-project")


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def make_id() -> str:
    """Date-prefixed UUID: 20260418T100000Z-a1b2c3d4e5f6"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}-{uuid.uuid4().hex[:12]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: str, record: dict) -> None:
    """Append one JSON record to a JSONL file. Non-fatal on error."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"  [schema] JSONL write error ({path}): {e}")


def _read_jsonl(path: str) -> list[dict]:
    """Read all records from a JSONL file. Returns [] if missing."""
    if not os.path.exists(path):
        return []
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Project:
    project_id:  str       = field(default_factory=make_id)
    name:        str       = ""
    description: str       = ""
    status:      str       = "active"   # active | paused | archived
    tags:        list      = field(default_factory=list)
    created_at:  str       = field(default_factory=_now_iso)
    updated_at:  str       = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Session:
    session_id:          str            = field(default_factory=make_id)
    project_id:          str            = ""
    triggered_by:        str            = "cli"  # cli | server | orchestrator | schedule
    started_at:          str            = field(default_factory=_now_iso)
    ended_at:            Optional[str]  = None
    runs:                int            = 0
    total_input_tokens:  int            = 0
    total_output_tokens: int            = 0
    artifacts:           int            = 0
    duration_s:          Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Artifact:
    artifact_id:   str           = field(default_factory=make_id)
    run_id:        str           = ""
    session_id:    str           = ""
    project_id:    str           = ""
    type:          str           = "output"  # output | trace | kg | annotation | dataset | lit_review
    path:          str           = ""
    bytes:         int           = 0
    lines:         Optional[int] = None
    content_hash:  Optional[str] = None
    created_at:    str           = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Message:
    run_id:      str           = ""
    session_id:  str           = ""
    project_id:  str           = ""
    seq:         int           = 0
    role:        str           = ""        # system | user | assistant | tool
    content:     Optional[str] = None
    cot:         Optional[str] = None      # chain-of-thought / thinking text (thinking models only)
    tool_calls:  Optional[list] = None
    tool_name:   Optional[str] = None
    chars:       Optional[int] = None
    timestamp:   str           = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OrchestratorPlan:
    """Written to plans.jsonl before subtask execution begins."""
    plan_id:       str       = field(default_factory=make_id)
    run_id:        str       = ""
    session_id:    str       = ""
    project_id:    str       = ""
    parent_run_id: str       = ""   # populated when this plan is itself a subtask
    task:          str       = ""
    plan_type:     str       = "orchestrator"  # orchestrator | agent
    task_type:     str       = ""
    complexity:    str       = ""
    subtasks:      list      = field(default_factory=list)  # [{"desc": str, "path": str}]
    known_facts:   list      = field(default_factory=list)
    knowledge_gaps: list     = field(default_factory=list)
    search_queries: list     = field(default_factory=list)
    created_at:    str       = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Project lifecycle
# ---------------------------------------------------------------------------

def create_project(name: str, description: str = "", tags: list | None = None) -> Project:
    """Create a new project and append to projects.jsonl."""
    p = Project(name=name, description=description, tags=tags or [])
    _append_jsonl(PROJECTS_PATH, {"event": "project_create", **p.to_dict()})
    print(f"  [schema] project created: {p.project_id} ({name})")
    return p


def list_projects() -> list[dict]:
    """Return latest state per project from projects.jsonl."""
    records = _read_jsonl(PROJECTS_PATH)
    latest: dict[str, dict] = {}
    for r in records:
        pid = r.get("project_id")
        if pid:
            latest[pid] = r
    return list(latest.values())


def resolve_project_id() -> str:
    """
    Return the active project_id. Resolution order:
    1. HARNESS_PROJECT_ID env var
    2. .harness-project dotfile in _BASE
    3. Last active project in projects.jsonl
    4. Auto-create a default project
    """
    # 1. Env var
    pid = os.environ.get("HARNESS_PROJECT_ID")
    if pid:
        return pid

    # 2. Dotfile
    if os.path.exists(DOTFILE):
        pid = open(DOTFILE, encoding="utf-8").read().strip()
        if pid:
            return pid

    # 3. Last active project in projects.jsonl
    records = _read_jsonl(PROJECTS_PATH)
    last_active = None
    for r in records:
        if r.get("status") == "active" and r.get("project_id"):
            last_active = r["project_id"]
    if last_active:
        return last_active

    # 4. Auto-create default
    p = create_project(name="default", description="Auto-created default project")
    os.environ["HARNESS_PROJECT_ID"] = p.project_id
    return p.project_id


def set_project(project_id: str) -> None:
    """Write project_id to .harness-project dotfile and set env var."""
    with open(DOTFILE, "w", encoding="utf-8") as f:
        f.write(project_id + "\n")
    os.environ["HARNESS_PROJECT_ID"] = project_id
    print(f"  [schema] active project set: {project_id}")


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------

def start_session(project_id: str = "", triggered_by: str = "cli") -> Session:
    """Create and record a new session. Sets HARNESS_SESSION_ID env var."""
    if not project_id:
        project_id = resolve_project_id()
    s = Session(project_id=project_id, triggered_by=triggered_by)
    os.environ["HARNESS_SESSION_ID"] = s.session_id
    _append_jsonl(SESSIONS_PATH, {"event": "session_start", **s.to_dict()})
    return s


def end_session(
    session: Session,
    runs: int = 0,
    total_input_tokens: int = 0,
    total_output_tokens: int = 0,
    artifacts: int = 0,
) -> None:
    """Record session end event."""
    now = _now_iso()
    started = session.started_at
    try:
        dur = (datetime.fromisoformat(now) - datetime.fromisoformat(started)).total_seconds()
    except Exception:
        dur = None
    _append_jsonl(SESSIONS_PATH, {
        "event":               "session_end",
        "session_id":          session.session_id,
        "project_id":          session.project_id,
        "ended_at":            now,
        "runs":                runs,
        "total_input_tokens":  total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "artifacts":           artifacts,
        "duration_s":          dur,
    })


# ---------------------------------------------------------------------------
# Project-stats helper (used by CLI)
# ---------------------------------------------------------------------------

def project_stats(project_id: str) -> dict:
    """Aggregate stats for a project across all JSONL files."""
    runs      = [r for r in _read_jsonl(os.path.join(_BASE, "runs.jsonl"))
                 if r.get("project_id") == project_id]
    sessions  = [r for r in _read_jsonl(SESSIONS_PATH)
                 if r.get("project_id") == project_id and r.get("event") == "session_start"]
    artifacts = [r for r in _read_jsonl(ARTIFACTS_PATH)
                 if r.get("project_id") == project_id]

    total_in  = sum(r.get("input_tokens",  0) or 0 for r in runs)
    total_out = sum(r.get("output_tokens", 0) or 0 for r in runs)
    scores    = [r["wiggum_scores"][-1] for r in runs if r.get("wiggum_scores")]
    passes    = sum(1 for r in runs if r.get("final") == "PASS")

    return {
        "project_id":   project_id,
        "sessions":     len(sessions),
        "runs":         len(runs),
        "passes":       passes,
        "pass_rate":    round(passes / len(runs), 3) if runs else 0,
        "avg_score":    round(sum(scores) / len(scores), 2) if scores else None,
        "total_input_tokens":  total_in,
        "total_output_tokens": total_out,
        "artifacts":    len(artifacts),
        "artifact_types": {t: sum(1 for a in artifacts if a.get("type") == t)
                           for t in {a.get("type") for a in artifacts}},
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Harness project management")
    sub = parser.add_subparsers(dest="cmd")

    cp = sub.add_parser("create-project", help="Create a new project")
    cp.add_argument("--name",        required=True)
    cp.add_argument("--description", default="")
    cp.add_argument("--tags",        default="", help="Comma-separated tags")

    sub.add_parser("list-projects", help="List all projects")

    sp = sub.add_parser("set-project", help="Set active project (writes .harness-project)")
    sp.add_argument("project_id")

    ps = sub.add_parser("project-stats", help="Aggregate stats for a project")
    ps.add_argument("project_id", nargs="?", default=None)

    args = parser.parse_args()

    if args.cmd == "create-project":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        p = create_project(args.name, args.description, tags)
        print(json.dumps(p.to_dict(), indent=2))

    elif args.cmd == "list-projects":
        projects = list_projects()
        if not projects:
            print("No projects found.")
        else:
            for p in projects:
                status = p.get("status", "?")
                pid    = p.get("project_id", "?")
                name   = p.get("name", "?")
                print(f"  [{status}]  {pid}  {name}")

    elif args.cmd == "set-project":
        set_project(args.project_id)
        # Update env for this process
        with open(DOTFILE, "w", encoding="utf-8") as f:
            f.write(args.project_id + "\n")
        print(f"Active project: {args.project_id}")

    elif args.cmd == "project-stats":
        pid = args.project_id or resolve_project_id()
        stats = project_stats(pid)
        print(json.dumps(stats, indent=2))

    else:
        parser.print_help()
        sys.exit(1)
