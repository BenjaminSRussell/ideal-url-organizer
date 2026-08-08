#!/usr/bin/env python3
"""
Import a rust-sitemapper crawl's sitemap.jsonl into url-organizer's
data/raw/urls.jsonl (the URLRecord/methods-1-21 pathway), then run the
full analysis pipeline against it.

Usage:
    python3 scripts/import_rust_sitemapper.py <path-to-sitemap.jsonl>

You do not need to activate a virtualenv first -- whichever `python3`
interpreter runs this script is also what the `./run.sh --all` subprocess
will use (its PATH is set up to match), so `.venv/bin/python3
scripts/import_rust_sitemapper.py ...` works directly.

Prerequisites (one-time setup, before first use):
    cp config/global.yaml.example config/global.yaml
    pip install -r requirements.txt
"""
import json
import os
import subprocess
import sys
import tempfile
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

    Lines that are blank, invalid JSON, or lack a valid string "url" are
    skipped and counted rather than aborting the whole conversion.

    Writes to a temp file in output_path's directory and only replaces
    output_path once the full loop has completed successfully, so a
    mid-stream read error (bad encoding, wrong file format entirely)
    can't truncate/destroy a pre-existing output_path.

    Returns {"written": int, "skipped": int}.
    """
    written = 0
    skipped = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path_str = tempfile.mkstemp(dir=str(output_path.parent), suffix=".tmp")
    tmp_path = Path(tmp_path_str)
    try:
        with open(input_path, "r", encoding="utf-8") as infile, \
                os.fdopen(fd, "w", encoding="utf-8") as outfile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue

                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    skipped += 1
                    continue

                if not isinstance(raw, dict) or not isinstance(raw.get("url"), str):
                    skipped += 1
                    continue

                filtered = filter_record(raw)
                outfile.write(json.dumps(filtered) + "\n")
                written += 1
        os.replace(tmp_path, output_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    return {"written": written, "skipped": skipped}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/import_rust_sitemapper.py <path-to-sitemap.jsonl>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
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

    # run.sh internally invokes bare `python3`, which resolves via PATH --
    # not necessarily the same interpreter running this script (e.g. when
    # invoked as `.venv/bin/python3 scripts/import_rust_sitemapper.py ...`
    # without the venv being activated). Prepend this interpreter's
    # directory to the subprocess's PATH so run.sh's `python3` resolves to
    # the same interpreter, and thus the same installed packages.
    env = os.environ.copy()
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")

    result = subprocess.run([str(run_sh), "--all"], cwd=str(project_root), env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
