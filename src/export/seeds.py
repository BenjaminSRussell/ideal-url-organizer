"""Seed-url JSONL export for Scrapy / Rust-sitemap handoff.

Schema (one JSON object per line):
  {
    "url": "https://example.com/path",
    "labels": ["by_domain:example.com", ...],
    "priority": 1.0,
    "method": "by_domain",
    "bucket": "example.com"
  }

Rust-sitemap can consume via `--start-url` lists (url field).
Scrapy seed_manager can read url + priority + labels.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SEED_SCHEMA_DOC = __doc__


def seeds_from_organized(
    organized: Dict[str, list],
    *,
    method: str,
    url_attr: str = "url",
) -> List[Dict[str, Any]]:
    """Flatten organizer output `{bucket: [PageContent|dict|str]}` to seed rows."""
    rows: List[Dict[str, Any]] = []
    # Higher priority for smaller buckets (more specific)
    sizes = {k: len(v or []) for k, v in organized.items()}
    max_size = max(sizes.values()) if sizes else 1
    for bucket, pages in organized.items():
        size = sizes.get(bucket, 0) or 1
        priority = round(max(0.1, 1.0 - (size / (max_size + 1)) * 0.5), 4)
        for page in pages or []:
            if isinstance(page, str):
                url = page
            elif isinstance(page, dict):
                url = page.get(url_attr) or page.get("final_url") or ""
            else:
                url = getattr(page, url_attr, None) or getattr(page, "final_url", "") or ""
            if not url:
                continue
            rows.append(
                {
                    "url": url,
                    "labels": [f"{method}:{bucket}"],
                    "priority": priority,
                    "method": method,
                    "bucket": bucket,
                }
            )
    return rows


def write_seeds_jsonl(rows: Iterable[Dict[str, Any]], out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def load_organized_json(path: Path) -> Dict[str, list]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "buckets" in data:
        return data["buckets"]
    if isinstance(data, dict):
        return data
    raise ValueError(f"Unsupported organized JSON shape: {path}")
