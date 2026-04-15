"""
memory.py — persistent observation store for the agent pipeline.

Inspired by claude-mem's architecture but runs fully locally via Ollama.
Storage:   SQLite + FTS5 (source of truth, metadata, fallback retrieval)
Retrieval: ChromaDB + sentence-transformers (semantic cosine similarity)
Compression: glm4:9b

Lifecycle:
  1. run() start  → get_context(task)       → inject into synthesize()
  2. run() end    → compress_and_store(...)  → write to SQLite + ChromaDB

Usage:
    from memory import MemoryStore, assess_novelty
    store   = MemoryStore()
    context = store.get_context(task)           # call before synthesis
    store.compress_and_store(task, ...)         # call after run completes

    # For gather_research novelty gating:
    score = assess_novelty(new_results, knowledge_state)   # 0–10
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone

import ollama

COMPRESSION_MODEL   = "glm4:9b"
DB_PATH             = os.path.join(os.path.dirname(__file__), "memory.db")
CHROMA_PATH         = os.path.join(os.path.dirname(__file__), "chroma_memory")
CHROMA_COLLECTION   = "observations_vec"
EMBED_MODEL         = "all-MiniLM-L6-v2"   # ~22MB, local, no API key
MAX_CONTEXT_OBSERVATIONS = 4    # observations injected per run
MAX_EXCERPT_CHARS   = 600       # output excerpt sent to compression model
SEMANTIC_CANDIDATES = 12        # over-fetch from ChromaDB before re-ranking


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
            items = re.findall(r'"([^"]+)"', facts_m.group(1))
            result["facts"] = items

    if not result["title"]:
        result["title"] = text.splitlines()[0][:80] if text else "unknown"
    if not result["narrative"]:
        result["narrative"] = text[:300]

    return result


# ---------------------------------------------------------------------------
# ChromaDB helpers
# ---------------------------------------------------------------------------

def _get_chroma_ef():
    from chromadb.utils import embedding_functions
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        device="cuda" if _cuda_available() else "cpu",
    )


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _obs_embed_text(row) -> str:
    """Build the text that gets embedded for a single observation row."""
    parts = [row["title"] or "", row["narrative"] or ""]
    if row["facts"]:
        try:
            facts = json.loads(row["facts"])
            parts.extend(str(f) for f in facts)
        except (json.JSONDecodeError, TypeError):
            pass
    return " ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------

class MemoryStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._chroma_client = None
        self._chroma_col = None
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    # ------------------------------------------------------------------
    # ChromaDB init + migration
    # ------------------------------------------------------------------

    def _get_chroma(self):
        """Lazy-init ChromaDB client and collection. Auto-migrates if needed."""
        if self._chroma_col is not None:
            return self._chroma_col
        try:
            import chromadb
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            ef = _get_chroma_ef()
            col = client.get_or_create_collection(
                name=CHROMA_COLLECTION,
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"},
            )
            # Auto-migrate any observations not yet in ChromaDB
            sqlite_count = self.count()
            chroma_count = col.count()
            if chroma_count < sqlite_count:
                self._migrate_to_chroma(col)
            self._chroma_client = client
            self._chroma_col = col
            return col
        except Exception as e:
            print(f"  [memory] ChromaDB unavailable: {e} — using FTS5 fallback")
            return None

    def _migrate_to_chroma(self, col):
        """Backfill ChromaDB from existing SQLite observations."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, narrative, facts FROM observations ORDER BY id"
            ).fetchall()

        existing = set(col.get(include=[])["ids"])
        to_add = [r for r in rows if str(r["id"]) not in existing]
        if not to_add:
            return

        print(f"  [memory] migrating {len(to_add)} observation(s) to ChromaDB...")
        batch_size = 50
        for i in range(0, len(to_add), batch_size):
            batch = to_add[i:i + batch_size]
            col.upsert(
                ids=[str(r["id"]) for r in batch],
                documents=[_obs_embed_text(r) for r in batch],
                metadatas=[{"task_type": "unknown", "final_score": 0.0,
                            "timestamp": ""} for r in batch],
            )
        print(f"  [memory] migration done")

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

        # Write to SQLite
        with self._connect() as conn:
            cursor = conn.execute(
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
            rowid = cursor.lastrowid

        # Index in ChromaDB
        col = self._get_chroma()
        if col is not None:
            try:
                embed_text = _obs_embed_text({
                    "title": obs["title"],
                    "narrative": obs["narrative"],
                    "facts": facts_json,
                })
                col.upsert(
                    ids=[str(rowid)],
                    documents=[embed_text],
                    metadatas=[{
                        "task_type": task_type or "unknown",
                        "final_score": score or 0.0,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }],
                )
            except Exception as e:
                print(f"  [memory] ChromaDB upsert failed (non-fatal): {e}")

        return obs

    def store_direct(
        self,
        task: str,
        task_type: str,
        title: str,
        narrative: str,
        facts: list[str],
        timestamp: str = None,
        final_score: float = None,
        final: str = "PASS",
        output_path: str = None,
    ) -> int:
        """
        Write a pre-built observation directly to SQLite + ChromaDB,
        bypassing LLM compression. Used for bulk imports (e.g. paper corpus).
        Returns the new SQLite rowid, or -1 if the task is already indexed.
        """
        # Idempotency check — skip if this task is already stored
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM observations WHERE task = ?", (task,)
            ).fetchone()
            if existing:
                return -1

        facts_json = json.dumps(facts) if facts else None
        ts = timestamp or datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO observations
                   (timestamp, task, task_type, title, narrative, facts, output_path, final_score, final)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ts, task, task_type, title, narrative, facts_json, output_path, final_score, final),
            )
            rowid = cursor.lastrowid

        col = self._get_chroma()
        if col is not None:
            try:
                embed_text = _obs_embed_text({
                    "title": title,
                    "narrative": narrative,
                    "facts": facts_json,
                })
                col.upsert(
                    ids=[str(rowid)],
                    documents=[embed_text],
                    metadatas=[{
                        "task_type": task_type,
                        "final_score": final_score or 0.0,
                        "timestamp": ts,
                    }],
                )
            except Exception as e:
                print(f"  [memory] ChromaDB upsert failed (non-fatal): {e}")

        return rowid

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

    def search(self, task: str, n: int = 10) -> list[sqlite3.Row]:
        """Public alias for _search — semantic + quality ranked retrieval."""
        return self._search(task, n)

    def _search(self, task: str, n: int) -> list[sqlite3.Row]:
        """
        Semantic retrieval via ChromaDB with SQLite metadata join.
        Re-ranks by blending similarity + quality score.
        Falls back to FTS5 if ChromaDB unavailable.
        """
        col = self._get_chroma()
        if col is not None and col.count() > 0:
            try:
                results = col.query(
                    query_texts=[task],
                    n_results=min(SEMANTIC_CANDIDATES, col.count()),
                    include=["distances", "metadatas"],
                )
                ids       = results["ids"][0]
                distances = results["distances"][0]

                if ids:
                    rowids = [int(i) for i in ids]
                    placeholders = ",".join("?" * len(rowids))
                    with self._connect() as conn:
                        rows_by_id = {
                            row["id"]: row
                            for row in conn.execute(
                                f"SELECT id, timestamp, task, task_type, title, "
                                f"narrative, facts, final_score "
                                f"FROM observations WHERE id IN ({placeholders})",
                                rowids,
                            ).fetchall()
                        }

                    scored = []
                    for rowid, dist in zip(rowids, distances):
                        row = rows_by_id.get(rowid)
                        if not row:
                            continue
                        sim   = 1.0 - (dist / 2.0)          # cosine sim [0, 1]
                        qual  = (row["final_score"] or 5.0) / 10.0
                        rank  = 0.7 * sim + 0.3 * qual
                        scored.append((rank, row))

                    scored.sort(key=lambda x: x[0], reverse=True)
                    return [row for _, row in scored[:n]]
            except Exception as e:
                print(f"  [memory] semantic search error ({e}) — falling back to FTS5")

        return self._search_fts(task, n)

    def _search_fts(self, task: str, n: int) -> list[sqlite3.Row]:
        """FTS5 keyword search with recency tie-breaking. Fallback only."""
        query_terms = _fts_query(task)
        with self._connect() as conn:
            if query_terms:
                try:
                    rows = conn.execute(
                        """SELECT o.id, o.timestamp, o.task, o.task_type, o.title,
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
                    pass

            return conn.execute(
                """SELECT id, timestamp, task, task_type, title, narrative, facts, final_score
                   FROM observations
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (n,),
            ).fetchall()

    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]


# ---------------------------------------------------------------------------
# Novelty scoring — for gather_research() marginal value search
# ---------------------------------------------------------------------------

def assess_novelty(new_results: list[dict], knowledge_state: str) -> int:
    """
    Score 0–10 how much new_results adds beyond knowledge_state.
    10 = entirely new information, 0 = completely redundant.

    Uses ChromaDB ephemeral collection + sentence-transformers cosine similarity.
    Falls back to word-overlap heuristic if ChromaDB unavailable.
    """
    if not knowledge_state or not new_results:
        return 10

    try:
        import chromadb
        ef = _get_chroma_ef()
        client = chromadb.EphemeralClient()
        col = client.get_or_create_collection(
            name="novelty_session",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        # Index knowledge state as sentence-level chunks
        chunks = [s.strip() for s in re.split(r'[.\n]', knowledge_state)
                  if len(s.strip()) > 20]
        if not chunks:
            return 10

        col.upsert(
            ids=[f"k{i}" for i in range(len(chunks))],
            documents=chunks,
        )

        # Query with each new result body; find minimum distance to known chunks
        new_bodies = [r.get("body", "") for r in new_results if r.get("body", "").strip()]
        if not new_bodies:
            return 10

        results = col.query(
            query_texts=new_bodies,
            n_results=1,
            include=["distances"],
        )
        min_distances = [r[0] for r in results["distances"] if r]
        if not min_distances:
            return 10

        # cosine distance: 0.0 = identical → novelty 0
        #                  1.0 = orthogonal → novelty 5
        #                  2.0 = opposite   → novelty 10
        avg_dist = sum(min_distances) / len(min_distances)
        return min(10, round(avg_dist * 5))

    except Exception as e:
        print(f"  [novelty] chroma unavailable ({e}) — using heuristic")
        return _novelty_heuristic(new_results, knowledge_state)


def _novelty_heuristic(new_results: list[dict], knowledge_state: str) -> int:
    """Word overlap fallback."""
    new_words   = set(w for r in new_results for w in r.get("body", "").lower().split())
    known_words = set(knowledge_state.lower().split())
    if not new_words:
        return 0
    return round(len(new_words - known_words) / len(new_words) * 10)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fts_query(task: str) -> str:
    """Build a safe FTS5 MATCH query from a task string."""
    STOP = {
        "the", "a", "an", "and", "or", "for", "to", "of", "in", "on",
        "at", "by", "is", "are", "was", "be", "with", "from", "that",
        "this", "it", "as", "not", "use", "save", "search", "find",
        "best", "most", "top", "how", "what", "which", "about",
    }
    words = re.findall(r'\b[a-zA-Z]{3,}\b', task)
    terms = [w.lower() for w in words if w.lower() not in STOP]
    seen, unique = set(), []
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
    device = "GPU" if _cuda_available() else "CPU"
    print(f"Memory store:  {store.db_path}")
    print(f"Observations:  {store.count()}")
    print(f"Embed device:  {device} ({EMBED_MODEL})")

    col = store._get_chroma()
    if col:
        print(f"ChromaDB:      {col.count()} vectors  ({CHROMA_PATH})")
    else:
        print("ChromaDB:      unavailable — FTS5 fallback active")

    print()

    if "--search" in sys.argv:
        idx   = sys.argv.index("--search")
        query = " ".join(sys.argv[idx + 1:])
        print(f"Query: {query!r}\n")
        ctx = store.get_context(query)
        print(ctx if ctx else "(no matches)")
    else:
        with store._connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, title, task_type, final_score, final "
                "FROM observations ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()
        for r in rows:
            score = f"{r['final_score']:.1f}" if r["final_score"] else "n/a"
            print(f"  [{r['timestamp'][:10]}] {r['title']!r}  "
                  f"({r['task_type']}, {score}/10, {r['final']})")
