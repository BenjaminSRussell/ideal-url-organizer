"""HTTP content cache (#7)."""
from __future__ import annotations

import time
from pathlib import Path

from src.core.http_cache import HttpContentCache


def test_second_get_is_hit(tmp_path: Path):
    cache = HttpContentCache(root=tmp_path / "http", ttl_seconds=60)
    url = "https://example.com/a"
    assert cache.get(url) is None
    assert cache.misses == 1
    cache.put(url, b"<html>hi</html>", headers={"status_code": 200})
    hit = cache.get(url)
    assert hit is not None
    assert hit["body"] == b"<html>hi</html>"
    assert cache.hits == 1


def test_ttl_expiry_refetches(tmp_path: Path):
    cache = HttpContentCache(root=tmp_path / "http", ttl_seconds=1)
    url = "https://example.com/b"
    cache.put(url, b"x")
    assert cache.get(url) is not None
    time.sleep(1.1)
    assert cache.get(url) is None
