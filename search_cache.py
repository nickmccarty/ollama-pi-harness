"""
search_cache.py — SQLite-backed TTL cache for DDGS web search results.

Schema:
    key        TEXT PRIMARY KEY   SHA-256 of normalised query
    query      TEXT               original query string
    results    TEXT               JSON-encoded list[dict]
    created_at REAL               unix timestamp
    expires_at REAL               unix timestamp (created_at + ttl)

Usage:
    from search_cache import cached_search

    results = cached_search(
        query="best practices for RAG pipelines",
        search_fn=lambda q, n: list(DDGS().text(q, max_results=n)),
        ttl=86400,
        max_results=10,
    )

CLI:
    python search_cache.py            # print stats
    python search_cache.py --clear    # delete all cached entries
    python search_cache.py --expired  # delete only expired entries
"""

import hashlib
import json
import os
import sqlite3
import sys
import time
from typing import Callable

DB_PATH   = os.path.join(os.path.dirname(__file__), "search_cache.db")
DEFAULT_TTL = 86_400   # 24 hours in seconds


# ---------------------------------------------------------------------------
# DB init
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_cache (
            key        TEXT PRIMARY KEY,
            query      TEXT NOT NULL,
            results    TEXT NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON search_cache(expires_at)")
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def _cache_key(query: str) -> str:
    """SHA-256 of lower-cased, whitespace-normalised query."""
    normalised = " ".join(query.lower().split())
    return hashlib.sha256(normalised.encode()).hexdigest()


def get(query: str) -> list[dict] | None:
    """Return cached results for query, or None if missing/expired."""
    key  = _cache_key(query)
    now  = time.time()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT results, expires_at FROM search_cache WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        results_json, expires_at = row
        if expires_at < now:
            conn.execute("DELETE FROM search_cache WHERE key = ?", (key,))
            conn.commit()
            return None
        return json.loads(results_json)
    finally:
        conn.close()


def put(query: str, results: list[dict], ttl: int = DEFAULT_TTL) -> None:
    """Store results for query with given TTL; also evict expired rows."""
    key  = _cache_key(query)
    now  = time.time()
    conn = _connect()
    try:
        # Upsert
        conn.execute(
            """
            INSERT INTO search_cache (key, query, results, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                results    = excluded.results,
                created_at = excluded.created_at,
                expires_at = excluded.expires_at
            """,
            (key, query, json.dumps(results, ensure_ascii=False), now, now + ttl),
        )
        # Lazy eviction of expired entries (cheap: uses index)
        conn.execute("DELETE FROM search_cache WHERE expires_at < ?", (now,))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# High-level helper
# ---------------------------------------------------------------------------

def cached_search(
    query: str,
    search_fn: Callable[[str, int], list[dict]],
    ttl: int = DEFAULT_TTL,
    max_results: int = 10,
) -> list[dict]:
    """
    Return cached results for query if available, otherwise call search_fn,
    store the results, and return them.

    Args:
        query:       search query string
        search_fn:   callable(query, max_results) -> list[dict]
        ttl:         cache lifetime in seconds (default 24 h)
        max_results: passed to search_fn on cache miss

    Returns:
        list of result dicts (same shape as DDGS().text() output)
    """
    cached = get(query)
    if cached is not None:
        print(f"[cache HIT ] {query[:60]}")
        return cached

    print(f"[cache MISS] {query[:60]}")
    results = search_fn(query, max_results)
    if results:
        put(query, results, ttl=ttl)
    return results


# ---------------------------------------------------------------------------
# Management helpers
# ---------------------------------------------------------------------------

def stats() -> dict:
    """Return cache statistics."""
    now  = time.time()
    conn = _connect()
    try:
        total   = conn.execute("SELECT COUNT(*) FROM search_cache").fetchone()[0]
        expired = conn.execute(
            "SELECT COUNT(*) FROM search_cache WHERE expires_at < ?", (now,)
        ).fetchone()[0]
        size_kb = os.path.getsize(DB_PATH) // 1024 if os.path.exists(DB_PATH) else 0
        return {"total": total, "expired": expired, "live": total - expired, "size_kb": size_kb}
    finally:
        conn.close()


def clear_all() -> int:
    """Delete all cached entries. Returns count deleted."""
    conn = _connect()
    try:
        n = conn.execute("DELETE FROM search_cache").rowcount
        conn.commit()
        return n
    finally:
        conn.close()


def clear_expired() -> int:
    """Delete only expired entries. Returns count deleted."""
    now  = time.time()
    conn = _connect()
    try:
        n = conn.execute(
            "DELETE FROM search_cache WHERE expires_at < ?", (now,)
        ).rowcount
        conn.commit()
        return n
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--clear" in args:
        n = clear_all()
        print(f"[search_cache] cleared {n} entries")
    elif "--expired" in args:
        n = clear_expired()
        print(f"[search_cache] cleared {n} expired entries")
    else:
        s = stats()
        print(f"[search_cache] {s['live']} live / {s['expired']} expired / {s['total']} total  ({s['size_kb']} KB)")
