"""
memory.py — persistent observation store for the agent pipeline.

Inspired by claude-mem's architecture but runs fully locally via Ollama.
Uses SQLite + FTS5 for storage and retrieval; glm4:9b for compression.

Lifecycle:
  1. run() start  → get_context(task)       → inject into synthesize()
  2. run() end    → compress_and_store(...)  → write to SQLite

Usage:
    from memory import MemoryStore
    store = MemoryStore()
    context = store.get_context(task)           # call before synthesis
    store.compress_and_store(task, ...)         # call after run completes
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone

import ollama

COMPRESSION_MODEL = "glm4:9b"
DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")
MAX_CONTEXT_OBSERVATIONS = 4    # observations injected per run
MAX_EXCERPT_CHARS = 600         # output excerpt sent to compression model


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT    NOT NULL,
    task         TEXT    NOT NULL,
    task_type    TEXT,
    title        TEXT    NOT NULL,
    narrative    TEXT    NOT NULL,
    facts        TEXT,           -- JSON array of strings
    output_path  TEXT,
    final_score  REAL,
    final        TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts USING fts5(
    task,
    title,
    narrative,
    facts,
    content='observations',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS obs_ai AFTER INSERT ON observations BEGIN
    INSERT INTO observations_fts(rowid, task, title, narrative, facts)
    VALUES (new.id, new.task, new.title, new.narrative, COALESCE(new.facts, ''));
END;

CREATE TRIGGER IF NOT EXISTS obs_ad AFTER DELETE ON observations BEGIN
    INSERT INTO observations_fts(observations_fts, rowid, task, title, narrative, facts)
    VALUES ('delete', old.id, old.task, old.title, old.narrative, COALESCE(old.facts, ''));
END;
"""


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------

COMPRESS_PROMPT = """\
Summarize this completed AI agent run as a structured memory record.

Task: {task}
Task type: {task_type}
Searches: {queries}
Output: {lines} lines, {bytes} bytes
Wiggum score: {score}
Output excerpt:
{excerpt}

Respond with EXACTLY this format and nothing else:
Title: <one-line summary of what was researched and produced, max 80 chars>
Narrative: <2-3 sentences: what was researched, what the output contains, anything notable>
Facts: <JSON array of 3-5 specific factual strings worth remembering>
"""


def compress(task: str, task_type: str, queries: list[str], output_content: str,
             output_lines: int, output_bytes: int, wiggum_scores: list[float]) -> dict:
    """
    Ask the compression model to summarize a completed run.
    Returns dict with keys: title, narrative, facts (list).
    """
    score_str = f"{wiggum_scores[-1]}/10" if wiggum_scores else "n/a"
    excerpt = output_content[:MAX_EXCERPT_CHARS].strip()
    query_str = "; ".join(queries[:4]) if queries else "n/a"

    prompt = COMPRESS_PROMPT.format(
        task=task,
        task_type=task_type or "unknown",
        queries=query_str,
        lines=output_lines or 0,
        bytes=output_bytes or 0,
        score=score_str,
        excerpt=excerpt,
    )

    try:
        response = ollama.chat(
            model=COMPRESSION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1},
        )
        text = response["message"]["content"].strip()
        return _parse_compression(text)
    except Exception as e:
        # Fallback: store task as title, no narrative/facts
        return {
            "title": task[:80],
            "narrative": f"[compression failed: {e}]",
            "facts": [],
        }


def _parse_compression(text: str) -> dict:
    """Parse the fixed-format compression response."""
    result = {"title": "", "narrative": "", "facts": []}

    title_m = re.search(r'^Title:\s*(.+)', text, re.MULTILINE)
    if title_m:
        result["title"] = title_m.group(1).strip()[:80]

    narr_m = re.search(r'^Narrative:\s*(.+?)(?=^Facts:|$)', text, re.MULTILINE | re.DOTALL)
    if narr_m:
        result["narrative"] = narr_m.group(1).strip()

    facts_m = re.search(r'^Facts:\s*(\[.+?\])', text, re.MULTILINE | re.DOTALL)
    if facts_m:
        try:
            result["facts"] = json.loads(facts_m.group(1))
        except json.JSONDecodeError:
            # Fall back to line-by-line parsing
            raw = facts_m.group(1)
            items = re.findall(r'"([^"]+)"', raw)
            result["facts"] = items

    # If parsing failed, use the raw text as narrative
    if not result["title"]:
        result["title"] = text.splitlines()[0][:80] if text else "unknown"
    if not result["narrative"]:
        result["narrative"] = text[:300]

    return result


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------

class MemoryStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")  # safe for concurrent multi-process writes
            conn.executescript(SCHEMA)

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def compress_and_store(
        self,
        task: str,
        task_type: str,
        tool_calls: list[dict],
        output_content: str,
        output_lines: int,
        output_bytes: int,
        output_path: str,
        wiggum_scores: list[float],
        final: str,
    ) -> dict:
        """
        Compress a completed run into an observation and persist it.
        Returns the stored observation dict.
        """
        queries = [tc["query"] for tc in tool_calls if tc.get("name") == "web_search"]

        obs = compress(
            task=task,
            task_type=task_type,
            queries=queries,
            output_content=output_content or "",
            output_lines=output_lines or 0,
            output_bytes=output_bytes or 0,
            wiggum_scores=wiggum_scores or [],
        )

        score = wiggum_scores[-1] if wiggum_scores else None
        facts_json = json.dumps(obs["facts"]) if obs["facts"] else None

        with self._connect() as conn:
            conn.execute(
                """INSERT INTO observations
                   (timestamp, task, task_type, title, narrative, facts, output_path, final_score, final)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    task,
                    task_type,
                    obs["title"],
                    obs["narrative"],
                    facts_json,
                    output_path,
                    score,
                    final,
                ),
            )

        return obs

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def get_context(self, task: str, n: int = MAX_CONTEXT_OBSERVATIONS) -> str:
        """
        Retrieve the N most relevant past observations for a task.
        Returns a formatted string for injection into the synthesis prompt,
        or empty string if no relevant history exists.
        """
        rows = self._search(task, n)
        if not rows:
            return ""

        lines = ["## Relevant past research\n"]
        for row in rows:
            date = row["timestamp"][:10]
            score_str = f"{row['final_score']:.1f}/10" if row["final_score"] else "n/a"
            task_type = row["task_type"] or "unknown"
            lines.append(f"**[{date}] {row['title']}** ({task_type}, {score_str})")
            lines.append(row["narrative"])
            if row["facts"]:
                try:
                    facts = json.loads(row["facts"])
                    if facts:
                        lines.append("Facts: " + "; ".join(str(f) for f in facts))
                except (json.JSONDecodeError, TypeError):
                    pass
            lines.append("")

        return "\n".join(lines).strip()

    def _search(self, task: str, n: int) -> list[sqlite3.Row]:
        """FTS5 search with recency tie-breaking. Falls back to recency-only if no FTS matches."""
        query_terms = _fts_query(task)

        with self._connect() as conn:
            if query_terms:
                try:
                    rows = conn.execute(
                        """SELECT o.timestamp, o.task, o.task_type, o.title,
                                  o.narrative, o.facts, o.final_score
                           FROM observations_fts f
                           JOIN observations o ON o.id = f.rowid
                           WHERE observations_fts MATCH ?
                           ORDER BY bm25(observations_fts), o.timestamp DESC
                           LIMIT ?""",
                        (query_terms, n),
                    ).fetchall()
                    if rows:
                        return rows
                except sqlite3.OperationalError:
                    pass  # malformed FTS query — fall through to recency

            # Fallback: most recent N observations
            return conn.execute(
                """SELECT timestamp, task, task_type, title, narrative, facts, final_score
                   FROM observations
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (n,),
            ).fetchall()

    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fts_query(task: str) -> str:
    """
    Build a safe FTS5 MATCH query from a task string.
    Extracts meaningful words, strips FTS5 special characters.
    """
    STOP = {
        "the", "a", "an", "and", "or", "for", "to", "of", "in", "on",
        "at", "by", "is", "are", "was", "be", "with", "from", "that",
        "this", "it", "as", "not", "use", "save", "search", "find",
        "best", "most", "top", "how", "what", "which", "about",
    }
    words = re.findall(r'\b[a-zA-Z]{3,}\b', task)
    terms = [w.lower() for w in words if w.lower() not in STOP]
    # Deduplicate, keep order
    seen = set()
    unique = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return " OR ".join(unique[:8]) if unique else ""


# ---------------------------------------------------------------------------
# CLI — inspect the store
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    store = MemoryStore()
    print(f"Memory store: {store.db_path}")
    print(f"Observations: {store.count()}\n")

    if "--search" in sys.argv:
        idx = sys.argv.index("--search")
        query = " ".join(sys.argv[idx + 1:])
        ctx = store.get_context(query)
        print(ctx if ctx else "(no matches)")
    else:
        # Show most recent observations
        with store._connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, title, task_type, final_score, final FROM observations ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()
        for r in rows:
            score = f"{r['final_score']:.1f}" if r['final_score'] else "n/a"
            print(f"  [{r['timestamp'][:10]}] {r['title']!r}  ({r['task_type']}, {score}/10, {r['final']})")
