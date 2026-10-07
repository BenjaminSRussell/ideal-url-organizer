"""Cross-site insight aggregator.

Reads the per-site JSON reports url-organizer's existing pipeline already
produces under data/results_by_site/<site>/, and produces per-site summaries
plus a global rollup. Nothing is cached -- every call re-reads the files
straight off disk, so results can never go stale relative to what's actually
in results_by_site/.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "data" / "results_by_site"

DATA_QUALITY_REPORT = "analysis/data_quality_report.json"
INTELLIGENCE_REPORT = "reports/comprehensive_intelligence_report.json"
DEDUP_SUMMARY = "methods/method_16_canonical_deduplication/summary.json"


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def aggregate_site(site_dir: Path) -> dict:
    """Read one site's reports, tolerating any of them being missing."""
    name = site_dir.name
    missing = []

    dq = _read_json(site_dir / DATA_QUALITY_REPORT)
    if dq is None:
        missing.append(DATA_QUALITY_REPORT)

    intel = _read_json(site_dir / INTELLIGENCE_REPORT)
    if intel is None:
        missing.append(INTELLIGENCE_REPORT)

    dedup = _read_json(site_dir / DEDUP_SUMMARY)
    if dedup is None:
        missing.append(DEDUP_SUMMARY)

    total_urls = dq["overview"]["total_records"] if dq else None
    unique_domains = dq["overview"]["unique_domains"] if dq else None
    success_rate_pct = dq["temporal_analysis"]["crawl_rate"] if dq else None
    avg_url_length = dq["url_quality"]["url_length"]["avg"] if dq else None

    duplication_rate_pct = None
    total_duplicates = None
    total_original_urls = None
    if dedup:
        total_duplicates = dedup["total_duplicates"]
        total_original_urls = dedup["total_original_urls"]
        if total_original_urls:
            duplication_rate_pct = (total_duplicates / total_original_urls) * 100

    generated_at = intel["metadata"]["generated_date"] if intel else None

    return {
        "name": name,
        "total_urls": total_urls,
        "unique_domains": unique_domains,
        "success_rate_pct": success_rate_pct,
        "duplication_rate_pct": duplication_rate_pct,
        "total_duplicates": total_duplicates,
        "total_original_urls": total_original_urls,
        "avg_url_length": avg_url_length,
        "generated_at": generated_at,
        "partial": bool(missing),
        "missing_files": missing,
    }


def aggregate_all(results_dir: Path) -> dict:
    """Scan every site directory under results_dir and roll it all up."""
    if not results_dir.exists():
        return {
            "sites": [],
            "rollup": {
                "site_count": 0,
                "total_urls": 0,
                "unique_domains_total": 0,
                "aggregate_duplication_rate_pct": None,
            },
        }

    site_dirs = sorted(p for p in results_dir.iterdir() if p.is_dir())
    sites = [aggregate_site(d) for d in site_dirs]

    total_urls = sum(s["total_urls"] for s in sites if s["total_urls"] is not None)
    unique_domains_total = sum(
        s["unique_domains"] for s in sites if s["unique_domains"] is not None
    )
    dup_num = sum(s["total_duplicates"] for s in sites if s["total_duplicates"] is not None)
    dup_den = sum(
        s["total_original_urls"] for s in sites if s["total_original_urls"] is not None
    )
    aggregate_duplication_rate_pct = (dup_num / dup_den * 100) if dup_den else None

    return {
        "sites": sites,
        "rollup": {
            "site_count": len(sites),
            "total_urls": total_urls,
            "unique_domains_total": unique_domains_total,
            "aggregate_duplication_rate_pct": aggregate_duplication_rate_pct,
        },
    }
