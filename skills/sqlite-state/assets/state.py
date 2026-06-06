"""Durable run-state between scheduled runs, backed by one SQLite file.

Scheduled scripts are stateless by default: every run re-scrapes from scratch
and re-alerts on items already seen. This gives three primitives over a single
file - a seen-set (dedup), a key/value cursor (resume where you left off), and
order-preserving new-item filtering - so a cron job remembers what it already
did. SQLite is stdlib, file-locked, and safe for one writer; no server, no deps.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY, ts REAL DEFAULT (julianday('now')));
CREATE TABLE IF NOT EXISTS cursor (name TEXT PRIMARY KEY, value TEXT);
"""


@contextmanager
def _conn(path: str | Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(path, timeout=30)
    try:
        conn.execute("PRAGMA journal_mode=WAL")  # concurrent readers, durable writes
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def mark_seen(path: str | Path, *keys: str) -> int:
    """Record keys as seen; return how many were NEW this call."""
    with _conn(path) as conn:
        before = conn.total_changes
        conn.executemany("INSERT OR IGNORE INTO seen(key) VALUES (?)", [(k,) for k in keys])
        return conn.total_changes - before


def is_seen(path: str | Path, key: str) -> bool:
    with _conn(path) as conn:
        row = conn.execute("SELECT 1 FROM seen WHERE key = ?", (key,)).fetchone()
        return row is not None


def filter_new(path: str | Path, keys: list[str]) -> list[str]:
    """Return only the keys not yet seen, in order (does not mark them)."""
    with _conn(path) as conn:
        seen = {r[0] for r in conn.execute("SELECT key FROM seen").fetchall()}
    return [k for k in keys if k not in seen]


def get_cursor(path: str | Path, name: str, default: str | None = None) -> str | None:
    with _conn(path) as conn:
        row = conn.execute("SELECT value FROM cursor WHERE name = ?", (name,)).fetchone()
        return row[0] if row else default


def set_cursor(path: str | Path, name: str, value: str) -> None:
    with _conn(path) as conn:
        conn.execute(
            "INSERT INTO cursor(name, value) VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET value = excluded.value",
            (name, value),
        )


if __name__ == "__main__":
    import os
    import tempfile

    db = os.path.join(tempfile.gettempdir(), "sqlite_state_demo.db")
    try:
        print("new:", mark_seen(db, "a", "b"))            # 2
        print("new again:", mark_seen(db, "a", "c"))      # 1 (only 'c' is new)
        print("unseen of [a,b,c,d]:", filter_new(db, ["a", "b", "c", "d"]))  # ['d']
        set_cursor(db, "last_id", "12345")
        print("cursor:", get_cursor(db, "last_id"))        # 12345
    finally:
        if os.path.exists(db):
            os.remove(db)
