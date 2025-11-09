#!/usr/bin/env python3
"""
Test Suite for URL Organizer
Tests all methods with the provided sample data
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.data_loader import DataLoader
from src.core.url_parser import URLParser
from src.core.config import get_config


def test_data_loading():
    """Test that sample data loads correctly"""
    print("\n" + "="*80)
    print("TEST 1: Data Loading")
    print("="*80)

    loader = DataLoader()
    records = loader.load()

    print(f"✓ Loaded {len(records)} records")
    assert len(records) > 0, "Should load sample data"

    # Verify first record
    first = records[0]
    print(f"✓ First record URL: {first.url}")
    assert first.url is not None
    assert first.depth is not None

    print("✓ Test passed\n")


def test_url_parsing():
    """Test URL parsing without regex"""
    print("="*80)
    print("TEST 2: URL Parsing (NO REGEX)")
    print("="*80)

    parser = URLParser()

    test_url = "http://catalog.hartford.edu/preview_program.php?catoid=20&poid=4445&returnto=1865"

    # Test parsing
    parsed = parser.parse(test_url)
    print(f"✓ Parsed URL: {test_url}")
    print(f"  - Scheme: {parsed.scheme}")
    print(f"  - Hostname: {parsed.hostname}")
    print(f"  - Path: {parsed.path}")
    print(f"  - Query params: {parsed.query_dict}")

    assert parsed.scheme == 'http'
    assert parsed.hostname == 'catalog.hartford.edu'
    assert 'catoid' in parsed.query_dict
    assert 'poid' in parsed.query_dict

    # Test component extraction
    components = parser.extract_components(test_url)
    print(f"✓ Extracted {len(components)} components")
    assert components['path_depth'] == 1  # preview_program.php

    # Test domain parts
    subdomain, domain, tld = parser.get_domain_parts(test_url)
    print(f"✓ Domain parts: subdomain='{subdomain}', domain='{domain}', tld='{tld}'")
    assert subdomain == 'catalog'
    assert domain == 'hartford'
    assert tld == 'edu'

    print("✓ Test passed\n")


def test_url_cleaning():
    """Test URL cleaning and normalization"""
    print("="*80)
    print("TEST 3: URL Cleaning & Normalization")
    print("="*80)

    config = get_config()
    tracker_params = config.get_tracker_params()
    parser = URLParser(tracker_params)

    messy_url = "http://catalog.hartford.edu/preview_program.php?catoid=20&poid=4445&utm_source=test&fbclid=123#section"

    print(f"Original: {messy_url}")

    # Clean URL
    clean = parser.clean(messy_url, normalize=True, remove_trackers=True)
    print(f"Cleaned:  {clean}")

    # Should remove trackers and fragment
    assert 'utm_source' not in clean
    assert 'fbclid' not in clean
    assert '#section' not in clean

    # Should keep important params
    assert 'catoid=20' in clean or 'catoid' in parser.parse(clean).query_dict
    assert 'poid=4445' in clean or 'poid' in parser.parse(clean).query_dict

    print("✓ Test passed\n")


def test_organization_methods():
    """Test that organization methods work"""
    print("="*80)
    print("TEST 4: Organization Methods")
    print("="*80)

    from src.organizers.method_01_by_domain import ByDomainOrganizer
    from src.organizers.method_02_by_depth import ByDepthOrganizer
    from src.organizers.method_16_canonical_deduplication import CanonicalDeduplicationOrganizer

    loader = DataLoader()

    # Test method 1: By Domain
    print("\n[Method 1: By Domain]")
    output_dir = Path(__file__).parent.parent / 'data' / 'processed' / 'test_method_01'
    organizer = ByDomainOrganizer(output_dir)
    records = loader.load()
    organized = organizer.organize(records)
    print(f"✓ Organized into {len(organized)} domains")
    assert len(organized) > 0

    # Test method 2: By Depth
    print("\n[Method 2: By Depth]")
    output_dir = Path(__file__).parent.parent / 'data' / 'processed' / 'test_method_02'
    organizer = ByDepthOrganizer(output_dir)
    organized = organizer.organize(records)
    print(f"✓ Organized into {len(organized)} depth levels")
    assert len(organized) > 0

    # Test method 16: Deduplication
    print("\n[Method 16: Canonical Deduplication]")
    output_dir = Path(__file__).parent.parent / 'data' / 'processed' / 'test_method_16'
    organizer = CanonicalDeduplicationOrganizer(output_dir)
    organized = organizer.organize(records)
    print(f"✓ Found {len(organized['canonical_map'])} canonical URLs")
    assert len(organized['canonical_map']) > 0

    print("\n✓ All organization methods working\n")


def test_data_quality_analysis():
    """Test data quality analyzer"""
    print("="*80)
    print("TEST 5: Data Quality Analysis")
    print("="*80)

    from src.analyzers.data_quality_analyzer import DataQualityAnalyzer

    loader = DataLoader()
    analyzer = DataQualityAnalyzer()
    records = loader.load()

    analysis = analyzer.analyze(records)

    print(f"✓ Analysis completed")
    print(f"  - Total records: {analysis['overview']['total_records']}")
    print(f"  - Unique domains: {analysis['overview']['unique_domains']}")
    print(f"  - Strengths found: {len(analysis['strengths'])}")
    print(f"  - Weaknesses found: {len(analysis['weaknesses'])}")

    assert analysis['overview']['total_records'] > 0
    assert len(analysis['strengths']) > 0 or len(analysis['weaknesses']) > 0

    print("✓ Test passed\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("URL ORGANIZER TEST SUITE")
    print("Testing with provided sample data")
    print("="*80)

    tests = [
        test_data_loading,
        test_url_parsing,
        test_url_cleaning,
        test_organization_methods,
        test_data_quality_analysis,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {failed} TESTS FAILED")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
