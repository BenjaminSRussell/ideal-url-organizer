"""Eval harness: precision/recall-style label accuracy vs golden JSONL (#4)."""
from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from src.core.data_loader import URLRecord
from src.organizers.method_01_by_domain import ByDomainOrganizer
from src.organizers.method_07_by_tld import ByTLDOrganizer
from src.organizers.method_08_by_protocol import ByProtocolOrganizer

PRIMARY_METHOD = "method_01_by_domain"
PRIMARY_MIN_ACCURACY = 0.99

METHOD_CLASSES = {
    "method_01_by_domain": ByDomainOrganizer,
    "method_07_by_tld": ByTLDOrganizer,
    "method_08_by_protocol": ByProtocolOrganizer,
}


def _record(url: str) -> URLRecord:
    return URLRecord(
        schema_version=1,
        url=url,
        url_normalized=url,
        depth=0,
        parent_url="",
        fragments=[],
        discovered_at=0,
        queued_at=0,
    )


def load_golden(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _labels_for(method: str, urls: list[str]) -> dict[str, str]:
    Cls = METHOD_CLASSES[method]
    with TemporaryDirectory() as tmp:
        org = Cls(Path(tmp))
        organized = org.organize([_record(u) for u in urls])
    inv: dict[str, str] = {}
    for label, records in organized.items():
        for r in records:
            inv[r.url] = str(label)
    return inv


@dataclass
class MethodMetrics:
    method: str
    n: int
    correct: int
    accuracy: float
    disagreements: list[dict[str, str]]


def evaluate_methods(
    golden_path: Path,
    methods: list[str] | None = None,
) -> dict[str, Any]:
    rows = load_golden(golden_path)
    urls = [r["url"] for r in rows]
    methods = methods or list(METHOD_CLASSES)
    metrics: list[MethodMetrics] = []
    per_url: dict[str, dict[str, str]] = {u: {} for u in urls}

    for method in methods:
        if method not in METHOD_CLASSES:
            raise SystemExit(f"unknown method: {method}")
        predicted = _labels_for(method, urls)
        correct = 0
        disagreements = []
        for row in rows:
            url = row["url"]
            expected_map = row.get("expected") or {}
            if method not in expected_map:
                continue
            exp = str(expected_map[method])
            pred = predicted.get(url, "")
            per_url[url][method] = pred
            if pred == exp:
                correct += 1
            else:
                disagreements.append({"url": url, "expected": exp, "predicted": pred})
        n = sum(1 for r in rows if method in (r.get("expected") or {}))
        acc = (correct / n) if n else 0.0
        metrics.append(
            MethodMetrics(
                method=method, n=n, correct=correct, accuracy=acc, disagreements=disagreements
            )
        )

    # Cross-method disagreement: URLs where method labels differ across methods
    cross: list[dict[str, Any]] = []
    for url, labels in per_url.items():
        if len(set(labels.values())) > 1:
            cross.append({"url": url, "labels": labels})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "golden": str(golden_path),
        "metrics": [asdict(m) for m in metrics],
        "per_url": per_url,
        "cross_method_disagreements": cross,
    }


def write_sqlite(report: dict[str, Any], db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS eval_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generated_at TEXT,
                method TEXT,
                n INTEGER,
                correct INTEGER,
                accuracy REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS eval_disagreements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generated_at TEXT,
                method TEXT,
                url TEXT,
                expected TEXT,
                predicted TEXT
            )
            """
        )
        ts = report["generated_at"]
        for m in report["metrics"]:
            conn.execute(
                "INSERT INTO eval_metrics (generated_at, method, n, correct, accuracy) VALUES (?,?,?,?,?)",
                (ts, m["method"], m["n"], m["correct"], m["accuracy"]),
            )
            for d in m["disagreements"]:
                conn.execute(
                    "INSERT INTO eval_disagreements (generated_at, method, url, expected, predicted) VALUES (?,?,?,?,?)",
                    (ts, m["method"], d["url"], d["expected"], d["predicted"]),
                )
        conn.commit()
    finally:
        conn.close()


def write_disagreement_html(report: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for url, labels in report["per_url"].items():
        cells = "".join(f"<td><code>{labels.get(m,'')}</code></td>" for m in METHOD_CLASSES)
        rows.append(f"<tr><td><code>{url}</code></td>{cells}</tr>")
    header = "".join(f"<th>{m}</th>" for m in METHOD_CLASSES)
    metrics_rows = "".join(
        f"<tr><td>{m['method']}</td><td>{m['correct']}/{m['n']}</td>"
        f"<td>{m['accuracy']:.3f}</td></tr>"
        for m in report["metrics"]
    )
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>Method disagreement explorer</title>
<style>
body{{font-family:system-ui,sans-serif;margin:1.5rem;background:#0b0f14;color:#e7ecf3}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{border:1px solid #2a3340;padding:.4rem .6rem;text-align:left;font-size:13px}}
th{{background:#151b24}}
code{{color:#9ecbff}}
h1,h2{{font-weight:600}}
</style></head><body>
<h1>Method eval + disagreement explorer</h1>
<p>Generated {report['generated_at']}</p>
<h2>Metrics</h2>
<table><tr><th>method</th><th>correct</th><th>accuracy</th></tr>{metrics_rows}</table>
<h2>Per-URL labels</h2>
<table><tr><th>url</th>{header}</tr>{''.join(rows)}</table>
</body></html>"""
    out.write_text(html)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m src.eval.harness")
    p.add_argument(
        "--golden",
        type=Path,
        default=Path("tests/fixtures/urls.jsonl"),
        help="Labeled golden JSONL",
    )
    p.add_argument("--method", action="append", dest="methods", help="Method id (repeatable) or 'all'")
    p.add_argument("--db", type=Path, default=Path("data/processed/eval.sqlite"))
    p.add_argument("--html", type=Path, default=Path("data/processed/disagreement.html"))
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument(
        "--fail-under",
        type=float,
        default=PRIMARY_MIN_ACCURACY,
        help="Fail if primary method accuracy is below this",
    )
    args = p.parse_args(argv)
    methods = None
    if args.methods:
        if any(m == "all" for m in args.methods):
            methods = list(METHOD_CLASSES)
        else:
            methods = args.methods
    report = evaluate_methods(args.golden, methods)
    write_sqlite(report, args.db)
    write_disagreement_html(report, args.html)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2))
    print("method\tcorrect\tn\taccuracy")
    for m in report["metrics"]:
        print(f"{m['method']}\t{m['correct']}\t{m['n']}\t{m['accuracy']:.4f}")
    print(f"wrote {args.db}")
    print(f"wrote {args.html}")
    primary = next((m for m in report["metrics"] if m["method"] == PRIMARY_METHOD), None)
    if primary and primary["accuracy"] < args.fail_under:
        print(
            f"PRIMARY REGRESSION: {PRIMARY_METHOD} accuracy {primary['accuracy']:.4f} "
            f"< {args.fail_under}",
            flush=True,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
