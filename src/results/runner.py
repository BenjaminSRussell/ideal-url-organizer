"""Unified organize run CLI into results DB (#3 + #5)."""
from __future__ import annotations

import argparse
import importlib
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.data_loader import DataLoader
from src.results.db import ResultsDB

# Curated subset matching src/main.py organizers (avoid importing analyzers).
METHOD_IMPORTS: Dict[str, Tuple[str, str]] = {
    "method_01_by_domain": ("src.organizers.method_01_by_domain", "ByDomainOrganizer"),
    "method_02_by_depth": ("src.organizers.method_02_by_depth", "ByDepthOrganizer"),
    "method_03_by_subdomain": ("src.organizers.method_03_by_subdomain", "BySubdomainOrganizer"),
    "method_07_by_tld": ("src.organizers.method_07_by_tld", "ByTLDOrganizer"),
    "method_08_by_protocol": ("src.organizers.method_08_by_protocol", "ByProtocolOrganizer"),
    "method_11_by_file_extension": (
        "src.organizers.method_11_by_file_extension",
        "ByFileExtensionOrganizer",
    ),
}


def _load_urls(path: Path) -> List[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _write_fixture_jsonl(urls: List[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for i, u in enumerate(urls):
            f.write(
                json.dumps(
                    {
                        "schema_version": 1,
                        "url": u,
                        "url_normalized": u,
                        "depth": i % 3,
                        "parent_url": "",
                        "fragments": [],
                        "discovered_at": i,
                        "queued_at": i,
                    }
                )
                + "\n"
            )


def _load_organizer(method_id: str) -> Type:
    if method_id not in METHOD_IMPORTS:
        raise KeyError(method_id)
    mod_name, cls_name = METHOD_IMPORTS[method_id]
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)


def run_methods(
    urls: List[str],
    method_ids: List[str],
    db_path: Path,
    *,
    export_fs: bool = True,
    project_root: Path | None = None,
) -> dict:
    root = project_root or ROOT
    db = ResultsDB(db_path)
    run_id = uuid.uuid4().hex[:12]
    db.start_run(run_id, method_ids)

    fixture = root / "data" / "tmp" / f"run_{run_id}.jsonl"
    _write_fixture_jsonl(urls, fixture)
    loader = DataLoader(str(fixture))
    records = loader.load()

    results = {}
    for mid in method_ids:
        try:
            cls = _load_organizer(mid)
            out = root / "data" / "results" / "methods" / mid
            if not export_fs:
                out = root / "data" / "tmp" / "methods" / mid
            organizer = cls(out)
            organized = organizer.organize(records)
            organizer.save(organized)
            if isinstance(organized, dict):
                for label, recs in organized.items():
                    for rec in recs:
                        db.add_assignment(
                            mid,
                            rec.url,
                            label=str(label),
                            payload={"label": str(label)},
                            run_id=run_id,
                            url_normalized=rec.url_normalized,
                        )
            results[mid] = "success"
        except Exception as exc:
            results[mid] = f"error:{exc}"
            for u in urls:
                db.add_assignment(
                    mid, u, label="error", payload={"error": str(exc)}, run_id=run_id
                )

    status = "ok" if all(v == "success" for v in results.values()) else "partial"
    db.finish_run(run_id, status=status)
    n = db.count_assignments()
    db.close()
    return {"run_id": run_id, "results": results, "assignments": n, "db": str(db_path)}


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="python -m src.results.runner")
    p.add_argument("--urls", type=Path, required=True)
    p.add_argument("--methods", default="method_01_by_domain,method_08_by_protocol")
    p.add_argument("--out", type=Path, default=Path("data/results/results.db"))
    p.add_argument("--no-export-fs", action="store_true")
    p.add_argument("--limit-methods", type=int, default=0)
    args = p.parse_args(argv)

    urls = _load_urls(args.urls)
    if not urls:
        print("no URLs", file=sys.stderr)
        return 1

    if args.methods.strip() == "all":
        method_ids = list(METHOD_IMPORTS.keys())
    else:
        method_ids = [m.strip() for m in args.methods.split(",") if m.strip()]
    if args.limit_methods > 0:
        method_ids = method_ids[: args.limit_methods]

    summary = run_methods(
        urls, method_ids, args.out, export_fs=not args.no_export_fs
    )
    print(json.dumps(summary, indent=2))
    return 0 if any(v == "success" for v in summary["results"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
