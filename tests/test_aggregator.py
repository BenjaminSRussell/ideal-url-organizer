"""Tests for server/aggregator.py"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.aggregator import aggregate_site, aggregate_all


def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _make_full_site(site_dir: Path, total_records=100, unique_domains=1,
                     crawl_rate=50.0, avg_len=40.0, total_original=100,
                     total_duplicates=20, generated_date="2026-08-08T00:00:00"):
    _write_json(site_dir / "analysis" / "data_quality_report.json", {
        "overview": {"total_records": total_records, "unique_domains": unique_domains},
        "temporal_analysis": {"crawl_rate": crawl_rate},
        "url_quality": {"url_length": {"avg": avg_len}},
    })
    _write_json(site_dir / "reports" / "comprehensive_intelligence_report.json", {
        "metadata": {"generated_date": generated_date},
    })
    _write_json(site_dir / "methods" / "method_16_canonical_deduplication" / "summary.json", {
        "total_original_urls": total_original,
        "total_duplicates": total_duplicates,
    })


def test_aggregate_site_full_data():
    tmp_dir = Path(tempfile.mkdtemp())
    site_dir = tmp_dir / "example-site"
    _make_full_site(site_dir)
    result = aggregate_site(site_dir)
    assert result["name"] == "example-site"
    assert result["total_urls"] == 100
    assert result["unique_domains"] == 1
    assert result["success_rate_pct"] == 50.0
    assert result["duplication_rate_pct"] == 20.0
    assert result["avg_url_length"] == 40.0
    assert result["generated_at"] == "2026-08-08T00:00:00"
    assert result["partial"] is False
    assert result["missing_files"] == []
    print("PASS")


def test_aggregate_site_missing_dedup_summary_is_partial():
    tmp_dir = Path(tempfile.mkdtemp())
    site_dir = tmp_dir / "example-site"
    _write_json(site_dir / "analysis" / "data_quality_report.json", {
        "overview": {"total_records": 10, "unique_domains": 1},
        "temporal_analysis": {"crawl_rate": 100.0},
        "url_quality": {"url_length": {"avg": 20.0}},
    })
    _write_json(site_dir / "reports" / "comprehensive_intelligence_report.json", {
        "metadata": {"generated_date": "2026-08-08T00:00:00"},
    })
    result = aggregate_site(site_dir)
    assert result["partial"] is True
    assert "methods/method_16_canonical_deduplication/summary.json" in result["missing_files"]
    assert result["duplication_rate_pct"] is None
    assert result["total_urls"] == 10
    print("PASS")


def test_aggregate_site_completely_empty_dir():
    tmp_dir = Path(tempfile.mkdtemp())
    site_dir = tmp_dir / "empty-site"
    site_dir.mkdir()
    result = aggregate_site(site_dir)
    assert result["partial"] is True
    assert len(result["missing_files"]) == 3
    assert result["total_urls"] is None
    print("PASS")


def test_aggregate_all_rolls_up_multiple_sites():
    tmp_dir = Path(tempfile.mkdtemp())
    _make_full_site(tmp_dir / "site-a", total_records=100, unique_domains=1,
                     total_original=100, total_duplicates=20)
    _make_full_site(tmp_dir / "site-b", total_records=200, unique_domains=2,
                     total_original=200, total_duplicates=180)
    result = aggregate_all(tmp_dir)
    assert result["rollup"]["site_count"] == 2
    assert result["rollup"]["total_urls"] == 300
    assert result["rollup"]["unique_domains_total"] == 3
    # (20 + 180) / (100 + 200) * 100
    assert abs(result["rollup"]["aggregate_duplication_rate_pct"] - (200 / 300 * 100)) < 1e-9
    print("PASS")


def test_aggregate_all_empty_results_dir():
    tmp_dir = Path(tempfile.mkdtemp()) / "does-not-exist"
    result = aggregate_all(tmp_dir)
    assert result["sites"] == []
    assert result["rollup"]["site_count"] == 0
    assert result["rollup"]["aggregate_duplication_rate_pct"] is None
    print("PASS")


def run_all_tests():
    print("\nserver.aggregator Test Suite")
    tests = [
        test_aggregate_site_full_data,
        test_aggregate_site_missing_dedup_summary_is_partial,
        test_aggregate_site_completely_empty_dir,
        test_aggregate_all_rolls_up_multiple_sites,
        test_aggregate_all_empty_results_dir,
    ]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\nFAIL: {test.__name__}\n  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    print(f"\nPassed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
