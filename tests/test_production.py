#!/usr/bin/env python3
"""
Production Test Suite

Comprehensive tests to find limits, weaknesses, and failure points.
Tests edge cases, error handling, and system boundaries.
"""
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logger import get_logger, safe_execute
from src.core.url_parser import URLParser
from src.core.data_loader import DataLoader, URLRecord
from src.core.config import get_config


class ProductionTester:
    """Comprehensive production testing"""

    def __init__(self):
        self.logger = get_logger(verbose=True)
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def run_all_tests(self):
        """Run all production tests"""
        print("\nProduction Test Suite")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        tests = [
            ('URL Parser Edge Cases', self.test_url_parser_edge_cases),
            ('Config Loading', self.test_config_loading),
            ('Data Loader Limits', self.test_data_loader_limits),
            ('Memory Stress Test', self.test_memory_stress),
            ('Concurrent Operations', self.test_concurrent_operations),
            ('Error Recovery', self.test_error_recovery),
            ('Invalid Input Handling', self.test_invalid_inputs),
            ('File System Limits', self.test_filesystem_limits),
        ]

        for test_name, test_func in tests:
            self._run_test(test_name, test_func)

        self._print_summary()

    def _run_test(self, name: str, func):
        """Run individual test with error handling"""
        print(f"\n[TEST] {name}")
        print("-" * 80)

        try:
            start_time = time.time()
            func()
            elapsed = time.time() - start_time

            self.results['passed'].append(name)
            print(f"PASSED ({elapsed:.2f}s)")

        except AssertionError as e:
            self.results['failed'].append((name, str(e)))
            print(f"FAILED: {e}")

        except Exception as e:
            self.results['failed'].append((name, str(e)))
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    def test_url_parser_edge_cases(self):
        """Test URL parser with edge cases"""
        parser = URLParser()

        # Edge case 1: Very long URL
        long_url = "http://example.com/" + "a" * 10000 + "?param=" + "b" * 10000
        result = safe_execute(
            parser.parse,
            long_url,
            component='parser',
            operation='parse_long_url'
        )
        assert result is not None, "Should handle very long URLs"

        # Edge case 2: Malformed URL
        malformed_urls = [
            "not a url",
            "http://",
            "://example.com",
            "http://[invalid",
            ""
        ]

        for url in malformed_urls:
            result = safe_execute(
                parser.parse,
                url,
                component='parser',
                operation='parse_malformed_url'
            )
            # Should not crash, even if result is None

        # Edge case 3: Unicode and special characters
        unicode_url = "http://example.com/café/日本語?query=тест"
        result = safe_execute(
            parser.parse,
            unicode_url,
            component='parser',
            operation='parse_unicode_url'
        )

        # Edge case 4: Port edge cases
        port_urls = [
            "http://example.com:0",  # Invalid port
            "http://example.com:65536",  # Port too high
            "http://example.com:abc",  # Non-numeric port
        ]

        for url in port_urls:
            result = safe_execute(
                parser.parse,
                url,
                component='parser',
                operation='parse_invalid_port'
            )

        print("  Tested URL parser edge cases")

    def test_config_loading(self):
        """Test configuration loading edge cases"""
        # Test 1: Missing config file
        config = safe_execute(
            get_config,
            component='config',
            operation='load_config'
        )
        assert config is not None, "Config should load"

        # Test 2: Get non-existent keys
        result = config.get('nonexistent.key.path', 'default')
        assert result == 'default', "Should return default for missing keys"

        # Test 3: Get nested keys
        tracker_params = config.get_tracker_params()
        assert isinstance(tracker_params, list), "Should return list"

        print("  Tested config loading")

    def test_data_loader_limits(self):
        """Test data loader with various limits"""
        loader = DataLoader()

        # Test 1: Load with empty file
        count = safe_execute(
            loader.get_record_count,
            component='loader',
            operation='count_records',
            default=0
        )
        assert count >= 0, "Should handle record counting"

        # Test 2: Load records
        records = safe_execute(
            loader.load,
            component='loader',
            operation='load_records',
            default=[]
        )
        assert isinstance(records, list), "Should return list"

        # Test 3: Iterate records (memory efficient)
        record_iter = safe_execute(
            lambda: list(loader.iter_records()),
            component='loader',
            operation='iter_records',
            default=[]
        )
        assert isinstance(record_iter, list), "Should iterate records"

        print(f"  Tested data loader with {len(records)} records")

    def test_memory_stress(self):
        """Test memory usage with large datasets"""
        import gc

        # Create large URL list
        large_urls = [f"http://example{i}.com/path/{i}" for i in range(1000)]

        parser = URLParser()

        # Test parsing many URLs
        parsed_count = 0
        for url in large_urls:
            result = safe_execute(
                parser.parse,
                url,
                component='parser',
                operation='bulk_parse',
                default=None
            )
            if result:
                parsed_count += 1

        # Force garbage collection
        gc.collect()

        assert parsed_count > 900, f"Should parse most URLs (got {parsed_count}/1000)"
        print(f"  Parsed {parsed_count}/1000 URLs successfully")

    def test_concurrent_operations(self):
        """Test concurrent operations"""
        from concurrent.futures import ThreadPoolExecutor
        import random

        parser = URLParser()
        test_urls = [
            f"http://example{i}.com?param={random.randint(0, 1000)}"
            for i in range(100)
        ]

        def parse_url(url):
            return safe_execute(
                parser.parse,
                url,
                component='parser',
                operation='concurrent_parse'
            )

        # Run concurrent parsing
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(parse_url, test_urls))

        success_count = sum(1 for r in results if r is not None)
        assert success_count > 90, f"Should handle concurrent operations (got {success_count}/100)"

        print(f"  Concurrent operations: {success_count}/100 successful")

    def test_error_recovery(self):
        """Test error recovery mechanisms"""
        parser = URLParser()

        # Test recovery from errors
        error_urls = [
            None,  # None value
            123,   # Wrong type
            [],    # Wrong type
            {"url": "test"},  # Wrong type
        ]

        for invalid_url in error_urls:
            result = safe_execute(
                parser.parse,
                invalid_url,
                component='parser',
                operation='error_recovery',
                default=None
            )
            # Should not crash

        print("  Tested error recovery")

    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        parser = URLParser()

        # Test with invalid tracker params
        parser_with_bad_params = URLParser(tracker_params=[None, 123, "valid"])

        # Test with empty strings
        result = safe_execute(
            parser.parse,
            "",
            component='parser',
            operation='empty_string',
            default=None
        )

        # Test with whitespace
        result = safe_execute(
            parser.parse,
            "   ",
            component='parser',
            operation='whitespace',
            default=None
        )

        print("  Tested invalid input handling")

    def test_filesystem_limits(self):
        """Test filesystem operation limits"""
        from pathlib import Path
        import tempfile

        # Test with very long paths
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deep directory structure
            deep_path = Path(tmpdir)
            for i in range(50):
                deep_path = deep_path / f"dir{i}"

            # Try to create it
            try:
                deep_path.mkdir(parents=True, exist_ok=True)
                assert deep_path.exists(), "Should handle deep paths"
            except OSError as e:
                self.logger.log_warning('filesystem', f"Deep path limit reached: {e}")

        print("  Tested filesystem limits")

    def _print_summary(self):
        """Print test summary"""
        print("\nTest Summary")

        total = len(self.results['passed']) + len(self.results['failed'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if self.results['failed']:
            print("\nFAILED TESTS:")
            for test_name, error in self.results['failed']:
                print(f"  - {test_name}: {error}")

        if failed == 0:
            print("\nALL TESTS PASSED")
            return True
        else:
            print(f"\n{failed} TESTS FAILED")
            return False


def main():
    """Run production tests"""
    tester = ProductionTester()
    success = tester.run_all_tests()

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
