---
title: ChromaDB Memory Migration
updated: 2026-04-09
sources: [memory.py, marginal-value-search.md]
tags: [memory, chromadb, retrieval, design, roadmap]
---

# ChromaDB Memory Migration

Design spec for upgrading `memory.py` retrieval from SQLite FTS5 (BM25 keyword
search) to ChromaDB (embedding-based cosine similarity), and reusing the same
ChromaDB instance for novelty scoring in `gather_research()`.

## Problem

`memory.py` retrieves past observations via FTS5 MATCH with BM25 ranking.
BM25 is keyword frequency — it finds observations that share words with the
current task. It misses semantically related observations that use different
terminology:

```
Task:    "Search for RAG chunking strategies for long documents"
FTS5 hit: "context window management: sliding window, token budgeting"  ← same concept, different words
FTS5 miss: ← BM25 sees no "RAG" or "chunking" tokens in that record
```

This matters because `memory_hits: 4` fires on every run and those observations
influence planning and synthesis. Poor retrieval = stale or irrelevant context
injected into every prompt.

## Scope

**What changes**: `_search()` in `MemoryStore` — retrieval layer only.

**What stays the same**: 
- `compress_and_store()` signature and behavior
- `get_context()` return format
- SQLite schema — kept as source of truth for metadata
- `compress()` using glm4:9b
- All callers in agent.py, autoresearch.py

**New capability added**: `assess_novelty()` global function reusing the same
ChromaDB instance for marginal value search (Option C from that spec).

---

## Architecture

```
                    WRITE PATH
compress_and_store()
    │
    ├──▶ SQLite (observations table)   ← source of truth, metadata, FTS5 kept
    └──▶ ChromaDB (observations_vec)   ← embedding index, keyed by SQLite rowid

                    READ PATH
get_context(task)
    │
    ├── ChromaDB.query(embed(task), n_results=8)  → candidate rowids + distances
    └── SQLite SELECT WHERE id IN (rowids)         → full observation rows
         └──▶ format and return top N

                    NOVELTY SCORING (new, for gather_research)
assess_novelty(new_results, knowledge_state)
    │
    ├── embed(knowledge_state)   → query vector
    ├── embed(new_result_bodies) → result vectors
    └── max cosine_sim(query, results) → convert to 0–10 novelty score
         (high similarity = low novelty; low similarity = high novelty)
```

SQLite stays the authoritative store. ChromaDB is a pure index — if the collection
is deleted or corrupted, it can be rebuilt from SQLite (see Migration section).

---

## Implementation

### Config (new constants in memory.py)

```python
CHROMA_PATH       = os.path.join(os.path.dirname(__file__), "chroma_memory")
CHROMA_COLLECTION = "observations_vec"
EMBED_MODEL       = "all-MiniLM-L6-v2"   # sentence-transformers, local, ~22MB
SEMANTIC_CANDIDATES = 12   # over-fetch from ChromaDB, then rank by recency+score
```

`all-MiniLM-L6-v2` is ChromaDB's default embedding model — no API key, no Ollama
call, runs in ~5ms per embed on CPU. First use downloads ~22MB once.

---

### ChromaDB client init (new method on MemoryStore)

```python
def _get_chroma(self):
    """Lazy-init ChromaDB client and collection. Auto-migrates if needed."""
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Auto-migrate: if SQLite has observations ChromaDB hasn't indexed, add them
    sqlite_count = self.count()
    chroma_count = collection.count()
    if chroma_count < sqlite_count:
        self._migrate_to_chroma(collection)

    return collection
```

---

### Embed text (what goes into ChromaDB per observation)

```python
def _obs_embed_text(self, row) -> str:
    """Build the text that gets embedded for an observation."""
    parts = [row["title"], row["narrative"]]
    if row["facts"]:
        try:
            facts = json.loads(row["facts"])
            parts.extend(str(f) for f in facts)
        except (json.JSONDecodeError, TypeError):
            pass
    return " ".join(parts)
```

The task string is also stored as metadata for filtering (e.g. task_type).

---

### Updated write path (dual-write)

`compress_and_store()` gains one extra block after the SQLite insert:

```python
# After SQLite insert — get the new rowid
with self._connect() as conn:
    cursor = conn.execute("INSERT INTO observations ...", (...))
    rowid = cursor.lastrowid

# Index in ChromaDB
collection = self._get_chroma()
embed_text = self._obs_embed_text({
    "title": obs["title"],
    "narrative": obs["narrative"],
    "facts": facts_json,
})
collection.upsert(
    ids=[str(rowid)],
    documents=[embed_text],
    metadatas=[{
        "task_type": task_type or "unknown",
        "final_score": score or 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }],
)
```

---

### Updated `_search()` — semantic retrieval

```python
def _search(self, task: str, n: int) -> list[sqlite3.Row]:
    """
    Semantic retrieval via ChromaDB, with SQLite metadata join.
    Falls back to FTS5 then recency if ChromaDB unavailable.
    """
    try:
        collection = self._get_chroma()
        if collection.count() == 0:
            raise RuntimeError("empty collection")

        # Over-fetch candidates, re-rank by score
        results = collection.query(
            query_texts=[task],
            n_results=min(SEMANTIC_CANDIDATES, collection.count()),
            include=["distances", "metadatas"],
        )
        ids       = results["ids"][0]           # list of str rowids
        distances = results["distances"][0]     # cosine distances (0=identical, 2=opposite)

        if not ids:
            raise RuntimeError("no results")

        # Join SQLite for full rows, preserving semantic rank
        rowids = [int(i) for i in ids]
        placeholders = ",".join("?" * len(rowids))
        with self._connect() as conn:
            rows_by_id = {
                row["id"]: row
                for row in conn.execute(
                    f"SELECT id, timestamp, task, task_type, title, narrative, facts, final_score "
                    f"FROM observations WHERE id IN ({placeholders})",
                    rowids,
                ).fetchall()
            }

        # Re-rank: blend semantic similarity + final_score, pick top n
        scored = []
        for rowid, dist in zip(rowids, distances):
            row = rows_by_id.get(rowid)
            if not row:
                continue
            sim   = 1 - (dist / 2)          # cosine similarity [0, 1]
            score = (row["final_score"] or 5.0) / 10.0
            rank  = 0.7 * sim + 0.3 * score  # weight: similarity > quality
            scored.append((rank, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [row for _, row in scored[:n]]

    except Exception as e:
        print(f"  [memory] chroma unavailable ({e}) — falling back to FTS5")
        return self._search_fts(task, n)   # existing FTS5 logic, renamed


def _search_fts(self, task: str, n: int) -> list[sqlite3.Row]:
    """Original FTS5 search — fallback only."""
    # ... existing _search() implementation unchanged, just renamed ...
```

The re-rank formula `0.7 * semantic_similarity + 0.3 * quality_score` means:
- A past run scoring 9.5/10 on a closely related task ranks above a tangential 6/10 run
- Semantic relevance is still the primary signal

---

### `assess_novelty()` — reusing ChromaDB for marginal value search

Global function, not a method on MemoryStore. Uses a **separate** ChromaDB collection
(`research_vec`) that is session-local (not persisted to disk, or persisted with short TTL).

```python
NOVELTY_COLLECTION = "research_vec"

def assess_novelty(new_results: list[dict], knowledge_state: str) -> int:
    """
    Score 0–10 how much new_results adds beyond knowledge_state.
    10 = entirely new, 0 = completely redundant.
    Uses embedding cosine similarity — no model call.
    """
    if not knowledge_state or not new_results:
        return 10  # no knowledge yet → everything is novel

    try:
        import chromadb
        from chromadb.utils import embedding_functions

        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        # In-memory collection for this session
        client = chromadb.EphemeralClient()
        col = client.get_or_create_collection(
            name=NOVELTY_COLLECTION,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        # Index knowledge state as chunks (split by sentence/bullet)
        chunks = [s.strip() for s in re.split(r'[.\n]', knowledge_state) if len(s.strip()) > 20]
        if not chunks:
            return 10
        col.upsert(
            ids=[f"k{i}" for i in range(len(chunks))],
            documents=chunks,
        )

        # Query with each new result body; take min distance (most similar)
        new_bodies = [r.get("body", "") for r in new_results if r.get("body")]
        if not new_bodies:
            return 10

        results = col.query(query_texts=new_bodies, n_results=1, include=["distances"])
        min_distances = [r[0] for r in results["distances"] if r]
        if not min_distances:
            return 10

        # Convert cosine distance to novelty score
        # distance 0.0 (identical) → novelty 0
        # distance 1.0 (orthogonal) → novelty 7
        # distance 2.0 (opposite) → novelty 10
        avg_dist = sum(min_distances) / len(min_distances)
        novelty = min(10, round(avg_dist * 5))
        return novelty

    except Exception as e:
        print(f"  [novelty] chroma unavailable ({e}) — using heuristic")
        return _assess_novelty_heuristic(new_results, knowledge_state)


def _assess_novelty_heuristic(new_results: list[dict], knowledge_state: str) -> int:
    """Word overlap fallback when ChromaDB unavailable."""
    new_words   = set(w for r in new_results for w in r.get("body","").lower().split())
    known_words = set(knowledge_state.lower().split())
    if not new_words:
        return 0
    novel_fraction = len(new_words - known_words) / len(new_words)
    return round(novel_fraction * 10)
```

`EphemeralClient` keeps the novelty collection in memory only — no disk writes,
no cleanup needed, automatically freed at process exit.

---

### Migration (SQLite → ChromaDB backfill)

```python
def _migrate_to_chroma(self, collection):
    """Backfill ChromaDB from existing SQLite observations."""
    with self._connect() as conn:
        rows = conn.execute(
            "SELECT id, title, narrative, facts FROM observations ORDER BY id"
        ).fetchall()

    existing_ids = set(collection.get(include=[])["ids"])
    to_add = [r for r in rows if str(r["id"]) not in existing_ids]

    if not to_add:
        return

    print(f"  [memory] migrating {len(to_add)} observations to ChromaDB...")
    batch_size = 50
    for i in range(0, len(to_add), batch_size):
        batch = to_add[i:i + batch_size]
        collection.upsert(
            ids=[str(r["id"]) for r in batch],
            documents=[self._obs_embed_text(r) for r in batch],
            metadatas=[{"task_type": "unknown", "final_score": 0.0,
                        "timestamp": ""} for r in batch],
        )
    print(f"  [memory] migration done — {len(to_add)} observations indexed")
```

Migration runs automatically on first `get_context()` call after upgrade.
No manual step required. Runs once, then ChromaDB stays in sync.

---

## New dependency

```bash
pip install chromadb sentence-transformers
```

`chromadb` pulls in `hnswlib` (HNSW index) and `sentence-transformers` pulls in
`torch` (CPU-only is fine). First use of `all-MiniLM-L6-v2` downloads ~22MB to
`~/.cache/torch/sentence_transformers/`. Subsequent uses are instant.

Add to AGENTS.md under environment setup.

---

## Rollout

| Step | Action | Verifiable |
|------|--------|------------|
| 1 | `pip install chromadb sentence-transformers` | `python -c "import chromadb"` |
| 2 | Apply changes to memory.py | `python memory.py` shows observation count |
| 3 | Run one agent task | Check `  [memory] migrating N observations` in output |
| 4 | Run `python memory.py --search "context window"` | Compare results to current FTS5 hits |
| 5 | Run autoresearch session | Verify `memory_hits` still fires; check retrieved obs quality |
| 6 | Implement `assess_novelty()` in agent.py | Add logging of novelty scores to runs.jsonl |

---

## What stays the same

- `MemoryStore` public API — no changes to callers
- `compress_and_store()` signature
- `get_context()` return format
- SQLite schema — observations table and FTS5 index remain (FTS5 is now fallback)
- `memory.db` file — not replaced, still authoritative
- glm4:9b compression model
- `MAX_CONTEXT_OBSERVATIONS = 4`

---

## Open questions

- **Embedding model size vs quality**: `all-MiniLM-L6-v2` (22MB) is fast but small.
  `all-mpnet-base-v2` (420MB) is higher quality. Worth testing both once the store
  has 50+ observations.
- **Re-rank weights**: `0.7 * similarity + 0.3 * quality` is a guess. May want to
  tune after running a few sessions and manually inspecting retrieved observations.
- **Novelty collection scope**: Currently `EphemeralClient` (per-process). If
  `gather_research()` is called multiple times in the same agent run (it isn't
  currently), the novelty state should persist within the run but not across runs.
  Present design handles this correctly.
- **Should knowledge_state be passed to synthesis?**: Out of scope for this spec
  but tracked in marginal-value-search.md.
