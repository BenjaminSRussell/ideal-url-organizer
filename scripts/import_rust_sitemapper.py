#!/usr/bin/env python3
"""
Import a rust-sitemapper crawl's sitemap.jsonl into url-organizer's
data/raw/urls.jsonl (the URLRecord/methods-1-21 pathway), then run the
full analysis pipeline against it.

Usage:
    python3 scripts/import_rust_sitemapper.py <path-to-sitemap.jsonl>
"""
import json
import subprocess
import sys
from pathlib import Path

# The exact field set url-organizer's URLRecord dataclass accepts
# (src/core/data_loader.py). URLRecord.from_dict does `cls(**data)`, so any
# key outside this set raises TypeError -- extra keys must be dropped, not
# passed through. Missing keys here become None, matching URLRecord's
# defaults for every field except the first 8 (which rust-sitemapper always
# populates, even if only with null, so they're never actually missing).
URL_RECORD_FIELDS = [
    "schema_version",
    "url",
    "url_normalized",
    "depth",
    "parent_url",
    "fragments",
    "discovered_at",
    "queued_at",
    "crawled_at",
    "response_time_ms",
    "status_code",
    "content_type",
    "content_length",
    "title",
    "link_count",
]


def filter_record(raw: dict) -> dict:
    """Keep only the fields URLRecord expects; anything missing defaults to None."""
    return {field: raw.get(field) for field in URL_RECORD_FIELDS}


def convert_file(input_path: Path, output_path: Path) -> dict:
    """
    Stream-convert a rust-sitemapper sitemap.jsonl file into url-organizer's
    URLRecord JSONL shape, one line at a time (memory-safe for large crawls).

    Lines that are blank, invalid JSON, or missing a "url" key are skipped
    and counted rather than aborting the whole conversion.

    Returns {"written": int, "skipped": int}.
    """
    written = 0
    skipped = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            if not isinstance(raw, dict) or "url" not in raw:
                skipped += 1
                continue

            filtered = filter_record(raw)
            outfile.write(json.dumps(filtered) + "\n")
            written += 1

    return {"written": written, "skipped": skipped}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/import_rust_sitemapper.py <path-to-sitemap.jsonl>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)
    if input_path.stat().st_size == 0:
        print(f"Error: input file is empty: {input_path}")
        sys.exit(1)

    project_root = Path(__file__).parent.parent
    output_path = project_root / "data" / "raw" / "urls.jsonl"

    print(f"Importing {input_path} -> {output_path}")
    stats = convert_file(input_path, output_path)
    print(f"Imported {stats['written']} records ({stats['skipped']} skipped)")

    if stats["written"] == 0:
        print("Error: no valid records imported, aborting pipeline run")
        sys.exit(1)

    print("\nRunning url-organizer pipeline (./run.sh --all)...")
    run_sh = project_root / "run.sh"
    result = subprocess.run([str(run_sh), "--all"], cwd=str(project_root))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
