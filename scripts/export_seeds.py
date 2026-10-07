#!/usr/bin/env python3
"""organize export-seeds — write Scrapy/Rust-sitemap seed JSONL."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.export.seeds import load_organized_json, seeds_from_organized, write_seeds_jsonl, SEED_SCHEMA_DOC


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="organize export-seeds",
        description="Export organized URL buckets as seed JSONL for Scrapy/Rust-sitemap",
    )
    p.add_argument("--method", required=True, help="Method label stored on each seed row")
    p.add_argument("--input", type=Path, required=True, help="Organized JSON ({bucket: [pages]})")
    p.add_argument("--out", type=Path, required=True, help="Output seeds.jsonl path")
    p.add_argument("--schema", action="store_true", help="Print schema docs and exit")
    args = p.parse_args(argv)
    if args.schema:
        print(SEED_SCHEMA_DOC)
        return 0
    organized = load_organized_json(args.input)
    rows = seeds_from_organized(organized, method=args.method)
    n = write_seeds_jsonl(rows, args.out)
    print(f"Wrote {n} seeds to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
