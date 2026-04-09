"""
search_cache.py — SQLite-backed cache for DDGS search results.

Keyed by normalized query fingerprint. TTL-based expiry (default 24h).
Zero external dependencies — same SQLite process as memory.db.

Usage (transparent — called by agent.py):
    from search_cache import cached_search
    results = cached_search(query, fallback_fn, ttl_hours=24)
"""

import json
import re
import sqlite3
import time
from pathlib import Path

CACHE_PATH = Path(__file__).parent / "search_cache.db"
DEFAULT_TTL_HOURS = 24


def _fingerprint(query: str) -> str:
    """Normalize query to a stable cache key."""
    return re.sub(r"\s+", " ", query.lower().strip())


def _get_db() -> sqlite3.Connection:
    db = sqlite3.connect(CACHE_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS search_cache (
            fingerprint TEXT PRIMARY KEY,
            query       TEXT NOT NULL,
            results_json TEXT NOT NULL,
            created_at  REAL NOT NULL,
            ttl_seconds REAL NOT NULL
        )
    """)
    db.commit()
    return db


def cached_search(
    query: str,
    fallback_fn,
    ttl_hours: float = DEFAULT_TTL_HOURS,
    max_results: int = 5,
) -> list[dict]:
    """
    Return cached results for `query` if fresh, else call fallback_fn(query, max_results)
    and cache the result.

    fallback_fn signature: (query: str, max_results: int) -> list[dict]
    """
    fp = _fingerprint(query)
    ttl_seconds = ttl_hours * 3600
    now = time.time()

    db = _get_db()
    try:
        row = db.execute(
            "SELECT results_json, created_at, ttl_seconds FROM search_cache WHERE fingerprint = ?",
            (fp,),
        ).fetchone()

        if row is not None:
            results_json, created_at, stored_ttl = row
            if now - created_at < stored_ttl:
                print(f"  [search_cache] HIT  {query[:60]!r}")
                return json.loads(results_json)
            else:
                print(f"  [search_cache] STALE {query[:60]!r} — refetching")
                db.execute("DELETE FROM search_cache WHERE fingerprint = ?", (fp,))
                db.commit()
        else:
            print(f"  [search_cache] MISS  {query[:60]!r}")

        results = fallback_fn(query, max_results)

        if results:
            db.execute(
                """INSERT OR REPLACE INTO search_cache
                   (fingerprint, query, results_json, created_at, ttl_seconds)
                   VALUES (?, ?, ?, ?, ?)""",
                (fp, query, json.dumps(results), now, ttl_seconds),
            )
            db.commit()

        return results
    finally:
        db.close()


def cache_stats() -> dict:
    """Return basic cache stats."""
    db = _get_db()
    try:
        total = db.execute("SELECT COUNT(*) FROM search_cache").fetchone()[0]
        now = time.time()
        fresh = db.execute(
            "SELECT COUNT(*) FROM search_cache WHERE ? - created_at < ttl_seconds", (now,)
        ).fetchone()[0]
        return {"total": total, "fresh": fresh, "stale": total - fresh}
    finally:
        db.close()


def clear_cache():
    """Delete all cached entries."""
    db = _get_db()
    db.execute("DELETE FROM search_cache")
    db.commit()
    db.close()
    print("[search_cache] cleared")


if __name__ == "__main__":
    stats = cache_stats()
    print(f"search_cache: {stats['fresh']} fresh, {stats['stale']} stale, {stats['total']} total entries")
    print(f"cache path: {CACHE_PATH}")
