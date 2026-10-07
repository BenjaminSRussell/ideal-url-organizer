"""HTTP content cache keyed by URL hash (#7)."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional


class HttpContentCache:
    def __init__(self, root: Path | str = "data/cache/http", ttl_seconds: int = 3600):
        self.root = Path(root)
        self.ttl = int(ttl_seconds)
        self.root.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _paths(self, url: str) -> tuple[Path, Path]:
        digest = self._key(url)
        base = self.root / digest[:2] / digest
        return base.with_suffix(".body"), base.with_suffix(".meta.json")

    def get(self, url: str) -> Optional[dict[str, Any]]:
        body_path, meta_path = self._paths(url)
        if not body_path.exists() or not meta_path.exists():
            self.misses += 1
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.misses += 1
            return None
        age = time.time() - float(meta.get("stored_at", 0))
        if age > self.ttl:
            self.misses += 1
            return None
        try:
            body = body_path.read_bytes()
        except OSError:
            self.misses += 1
            return None
        self.hits += 1
        return {"body": body, "meta": meta, "age_seconds": age}

    def put(self, url: str, body: bytes, headers: Optional[dict] = None) -> None:
        body_path, meta_path = self._paths(url)
        body_path.parent.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(body)
        meta = {
            "url": url,
            "stored_at": time.time(),
            "headers": headers or {},
            "sha256": hashlib.sha256(body).hexdigest(),
            "nbytes": len(body),
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
