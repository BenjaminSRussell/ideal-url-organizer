"""SQLite sink for method assignments (#3)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    url_normalized TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS method_assignments (
    id INTEGER PRIMARY KEY,
    method_id TEXT NOT NULL,
    url_id INTEGER NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    label TEXT,
    payload_json TEXT,
    run_id TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ma_method ON method_assignments(method_id);
CREATE INDEX IF NOT EXISTS idx_ma_url ON method_assignments(url_id);
CREATE TABLE IF NOT EXISTS crawl_content (
    id INTEGER PRIMARY KEY,
    url_id INTEGER NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    title TEXT,
    text TEXT,
    status_code INTEGER,
    fetched_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY,
    url_id INTEGER NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    model TEXT,
    dim INTEGER,
    vector_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    started_at TEXT,
    finished_at TEXT,
    methods_json TEXT,
    status TEXT
);
"""


class ResultsDB:
    def __init__(self, path: str | Path = "data/results/results.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def upsert_url(self, url: str, url_normalized: str | None = None) -> int:
        self.conn.execute(
            "INSERT INTO urls(url, url_normalized) VALUES (?, ?) "
            "ON CONFLICT(url) DO UPDATE SET url_normalized=COALESCE(excluded.url_normalized, urls.url_normalized)",
            (url, url_normalized or url),
        )
        self.conn.commit()
        row = self.conn.execute("SELECT id FROM urls WHERE url=?", (url,)).fetchone()
        return int(row[0])

    def add_assignment(
        self,
        method_id: str,
        url: str,
        *,
        label: str | None = None,
        payload: Any = None,
        run_id: str | None = None,
        url_normalized: str | None = None,
    ) -> None:
        uid = self.upsert_url(url, url_normalized)
        self.conn.execute(
            "INSERT INTO method_assignments(method_id, url_id, label, payload_json, run_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                method_id,
                uid,
                label,
                json.dumps(payload) if payload is not None else None,
                run_id,
            ),
        )
        self.conn.commit()

    def start_run(self, run_id: str, methods: Iterable[str]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO runs(id, started_at, methods_json, status) "
            "VALUES (?, datetime('now'), ?, 'running')",
            (run_id, json.dumps(list(methods))),
        )
        self.conn.commit()

    def finish_run(self, run_id: str, status: str = "ok") -> None:
        self.conn.execute(
            "UPDATE runs SET finished_at=datetime('now'), status=? WHERE id=?",
            (status, run_id),
        )
        self.conn.commit()

    def count_assignments(self, method_id: str | None = None) -> int:
        if method_id:
            row = self.conn.execute(
                "SELECT COUNT(*) FROM method_assignments WHERE method_id=?",
                (method_id,),
            ).fetchone()
        else:
            row = self.conn.execute("SELECT COUNT(*) FROM method_assignments").fetchone()
        return int(row[0])
