#!/usr/bin/env python3
"""
Tests for scripts/import_rust_sitemapper.py
"""
import dataclasses
import json
import sys
import tempfile
from pathlib import Path

# Add project root so `scripts.import_rust_sitemapper` resolves, matching
# the existing tests/ convention of inserting project root then importing
# with an absolute `src.`-style path (see tests/test_all_methods.py).
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.import_rust_sitemapper import URL_RECORD_FIELDS, filter_record, convert_file
from src.core.data_loader import URLRecord


def test_filter_record_keeps_only_expected_fields():
    """A rust-sitemapper record has many extra fields beyond URLRecord's 15 --
    they must be dropped, not passed through (URLRecord(**data) raises
    TypeError on any unexpected keyword)."""
    print("\nTest 1: filter_record drops extra fields")

    raw = {
        "schema_version": 5,
        "url": "https://example.com/",
        "url_normalized": "https://example.com/",
        "depth": 0,
        "parent_url": None,
        "fragments": [],
        "discovered_at": 111,
        "queued_at": 111,
        "crawled_at": 112,
        "response_time_ms": 50,
        "status_code": 200,
        "content_type": "text/html",
        "content_length": 1234,
        "title": "Example",
        "link_count": 3,
        # rust-sitemapper-only extra fields that must NOT survive:
        "description": "some description",
        "metadata_json": "{}",
        "privacy_metadata_json": "{}",
        "tech_profile": "Unknown",
    }

    result = filter_record(raw)

    assert set(result.keys()) == set(URL_RECORD_FIELDS), (
        f"expected exactly {URL_RECORD_FIELDS}, got {sorted(result.keys())}"
    )
    assert "description" not in result
    assert "metadata_json" not in result
    assert result["url"] == "https://example.com/"
    assert result["title"] == "Example"
    print("PASS")


def test_filter_record_missing_optional_field_defaults_to_none():
    """A record missing an optional field (e.g. no title yet -- URL discovered
    but not crawled) must fill in None, not omit the key or raise."""
    print("\nTest 2: filter_record defaults missing optional fields to None")

    raw = {
        "schema_version": 5,
        "url": "https://example.com/page",
        "url_normalized": "https://example.com/page",
        "depth": 1,
        "parent_url": "https://example.com/",
        "fragments": [],
        "discovered_at": 111,
        "queued_at": 111,
        # crawled_at, response_time_ms, status_code, content_type,
        # content_length, title, link_count all intentionally absent.
    }

    result = filter_record(raw)

    assert result["crawled_at"] is None
    assert result["status_code"] is None
    assert result["title"] is None
    assert result["url"] == "https://example.com/page"
    print("PASS")


def test_convert_file_normal_case():
    """Two valid records in, two filtered records out, correct stats."""
    print("\nTest 3: convert_file writes filtered records with correct stats")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "sitemap.jsonl"
        output_path = tmp_path / "data" / "raw" / "urls.jsonl"

        records = [
            {
                "schema_version": 5, "url": "https://a.example/", "url_normalized": "https://a.example/",
                "depth": 0, "parent_url": None, "fragments": [], "discovered_at": 1, "queued_at": 1,
                "crawled_at": 2, "response_time_ms": 10, "status_code": 200, "content_type": "text/html",
                "content_length": 100, "title": "A", "link_count": 5, "extra_field": "dropped",
            },
            {
                "schema_version": 5, "url": "https://b.example/", "url_normalized": "https://b.example/",
                "depth": 1, "parent_url": "https://a.example/", "fragments": [], "discovered_at": 3,
                "queued_at": 3, "crawled_at": None, "response_time_ms": None, "status_code": None,
                "content_type": None, "content_length": None, "title": None, "link_count": None,
            },
        ]
        with open(input_path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        stats = convert_file(input_path, output_path)

        assert stats == {"written": 2, "skipped": 0}, stats
        assert output_path.exists()

        with open(output_path) as f:
            lines = [json.loads(line) for line in f]

        assert len(lines) == 2
        assert lines[0]["url"] == "https://a.example/"
        assert "extra_field" not in lines[0]
        assert lines[1]["status_code"] is None
        print("PASS")


def test_convert_file_skips_malformed_lines_not_fatal():
    """Invalid JSON and records missing 'url' are skipped and counted, and
    do not stop processing of the valid lines around them."""
    print("\nTest 4: convert_file skips malformed lines without aborting")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "sitemap.jsonl"
        output_path = tmp_path / "urls.jsonl"

        valid = {
            "schema_version": 5, "url": "https://a.example/", "url_normalized": "https://a.example/",
            "depth": 0, "parent_url": None, "fragments": [], "discovered_at": 1, "queued_at": 1,
            "crawled_at": 2, "response_time_ms": 10, "status_code": 200, "content_type": "text/html",
            "content_length": 100, "title": "A", "link_count": 5,
        }

        with open(input_path, "w") as f:
            f.write(json.dumps(valid) + "\n")
            f.write("{not valid json\n")
            f.write(json.dumps({"no_url_field": True}) + "\n")
            f.write("\n")  # blank line, also skipped silently, not counted
            f.write(json.dumps(valid) + "\n")

        stats = convert_file(input_path, output_path)

        assert stats == {"written": 2, "skipped": 2}, stats

        with open(output_path) as f:
            lines = [json.loads(line) for line in f]
        assert len(lines) == 2
        print("PASS")


def test_convert_file_skips_non_dict_json_not_fatal():
    """Valid JSON that isn't a dict (e.g., null, number, boolean, list) must be
    skipped and counted, not crash the conversion. The key check must be
    dict-aware: `not isinstance(raw, dict) or "url" not in raw`."""
    print("\nTest 5: convert_file skips non-dict JSON values without crashing")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "sitemap.jsonl"
        output_path = tmp_path / "urls.jsonl"

        valid = {
            "schema_version": 5, "url": "https://a.example/", "url_normalized": "https://a.example/",
            "depth": 0, "parent_url": None, "fragments": [], "discovered_at": 1, "queued_at": 1,
            "crawled_at": 2, "response_time_ms": 10, "status_code": 200, "content_type": "text/html",
            "content_length": 100, "title": "A", "link_count": 5,
        }

        with open(input_path, "w") as f:
            f.write(json.dumps(valid) + "\n")
            f.write("null\n")  # valid JSON but not a dict
            f.write("42\n")  # valid JSON but not a dict
            f.write("true\n")  # valid JSON but not a dict
            f.write(json.dumps(["list", "of", "items"]) + "\n")  # valid JSON but not a dict
            f.write(json.dumps(valid) + "\n")

        stats = convert_file(input_path, output_path)

        assert stats == {"written": 2, "skipped": 4}, stats

        with open(output_path) as f:
            lines = [json.loads(line) for line in f]
        assert len(lines) == 2
        print("PASS")


def test_url_record_fields_matches_url_record_dataclass():
    """Guard against URL_RECORD_FIELDS drifting from url-organizer's actual
    URLRecord dataclass (src/core/data_loader.py). If a field is ever added,
    renamed, or removed on URLRecord without updating URL_RECORD_FIELDS to
    match, filter_record would silently drop/misalign data instead of
    raising -- this test catches that at test time instead."""
    print("\nTest 6: URL_RECORD_FIELDS matches URLRecord dataclass fields")

    expected = [f.name for f in dataclasses.fields(URLRecord)]

    assert URL_RECORD_FIELDS == expected, (
        f"URL_RECORD_FIELDS {URL_RECORD_FIELDS} has drifted from "
        f"URLRecord's actual fields {expected}"
    )
    print("PASS")


def run_all_tests():
    print("\nimport_rust_sitemapper Test Suite")

    tests = [
        test_filter_record_keeps_only_expected_fields,
        test_filter_record_missing_optional_field_defaults_to_none,
        test_convert_file_normal_case,
        test_convert_file_skips_malformed_lines_not_fatal,
        test_convert_file_skips_non_dict_json_not_fatal,
        test_url_record_fields_matches_url_record_dataclass,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\nFAIL: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nPassed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
