#!/usr/bin/env python3
"""
Comprehensive Test Suite for All 25 Organization Methods

Tests each method with:
- Normal data
- Edge cases
- Stress tests
- Error conditions
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.data_loader import DataLoader, URLRecord
from src.core.logger import get_logger, safe_execute

# Import all 25 organizers
from src.organizers.method_01_by_domain import ByDomainOrganizer
from src.organizers.method_02_by_depth import ByDepthOrganizer
from src.organizers.method_03_by_subdomain import BySubdomainOrganizer
from src.organizers.method_04_by_path_structure import ByPathStructureOrganizer
from src.organizers.method_05_by_query_params import ByQueryParamsOrganizer
from src.organizers.method_06_by_parent_domain import ByParentDomainOrganizer
from src.organizers.method_07_by_tld import ByTLDOrganizer
from src.organizers.method_08_by_protocol import ByProtocolOrganizer
from src.organizers.method_09_by_port import ByPortOrganizer
from src.organizers.method_10_by_path_depth import ByPathDepthOrganizer
from src.organizers.method_11_by_file_extension import ByFileExtensionOrganizer
from src.organizers.method_12_by_content_type import ByContentTypeOrganizer
from src.organizers.method_13_hierarchical_tree import HierarchicalTreeOrganizer
from src.organizers.method_14_by_discovery_time import ByDiscoveryTimeOrganizer
from src.organizers.method_15_by_crawl_status import ByCrawlStatusOrganizer
from src.organizers.method_16_canonical_deduplication import CanonicalDeduplicationOrganizer
from src.organizers.method_17_by_resource_type import ByResourceTypeOrganizer
from src.organizers.method_18_by_url_length import ByURLLengthOrganizer
from src.organizers.method_19_network_graph import NetworkGraphOrganizer
from src.organizers.method_20_by_param_patterns import ByParamPatternsOrganizer
from src.organizers.method_21_domain_and_depth_matrix import DomainDepthMatrixOrganizer


class ComprehensiveMethodTester:
    """Comprehensive testing for all organization methods"""

    def __init__(self):
        self.logger = get_logger(verbose=True)
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

        # Define all methods to test (methods 1-21 for now, 22-25 require actual web content)
        self.methods = {
            'method_01_by_domain': (ByDomainOrganizer, 'Group by Domain'),
            'method_02_by_depth': (ByDepthOrganizer, 'Group by Depth'),
            'method_03_by_subdomain': (BySubdomainOrganizer, 'Group by Subdomain'),
            'method_04_by_path_structure': (ByPathStructureOrganizer, 'Group by Path Structure'),
            'method_05_by_query_params': (ByQueryParamsOrganizer, 'Group by Query Parameters'),
            'method_06_by_parent_domain': (ByParentDomainOrganizer, 'Group by Parent Domain'),
            'method_07_by_tld': (ByTLDOrganizer, 'Group by TLD'),
            'method_08_by_protocol': (ByProtocolOrganizer, 'Group by Protocol'),
            'method_09_by_port': (ByPortOrganizer, 'Group by Port'),
            'method_10_by_path_depth': (ByPathDepthOrganizer, 'Group by Path Depth'),
            'method_11_by_file_extension': (ByFileExtensionOrganizer, 'Group by File Extension'),
            'method_12_by_content_type': (ByContentTypeOrganizer, 'Group by Content Type'),
            'method_13_hierarchical_tree': (HierarchicalTreeOrganizer, 'Hierarchical Tree'),
            'method_14_by_discovery_time': (ByDiscoveryTimeOrganizer, 'Group by Discovery Time'),
            'method_15_by_crawl_status': (ByCrawlStatusOrganizer, 'Group by Crawl Status'),
            'method_16_canonical_deduplication': (CanonicalDeduplicationOrganizer, 'Canonical Deduplication'),
            'method_17_by_resource_type': (ByResourceTypeOrganizer, 'Group by Resource Type'),
            'method_18_by_url_length': (ByURLLengthOrganizer, 'Group by URL Length'),
            'method_19_network_graph': (NetworkGraphOrganizer, 'Network Graph'),
            'method_20_by_param_patterns': (ByParamPatternsOrganizer, 'Group by Parameter Patterns'),
            'method_21_domain_and_depth_matrix': (DomainDepthMatrixOrganizer, 'Domain-Depth Matrix'),
        }

    def create_test_data_loader(self, urls: List[Dict[str, Any]]) -> DataLoader:
        """Create a data loader with test data"""
        class TestDataLoader(DataLoader):
            def __init__(self, test_urls):
                super().__init__()
                self.test_urls = test_urls

            def load(self) -> List[URLRecord]:
                records = []
                for url_data in self.test_urls:
                    record = URLRecord(**url_data)
                    records.append(record)
                return records

        return TestDataLoader(urls)

    def generate_normal_test_data(self) -> List[Dict[str, Any]]:
        """Generate normal test data"""
        return [
            {
                'schema_version': 1,
                'url': 'http://example.com/page1',
                'url_normalized': 'http://example.com/page1',
                'depth': 1,
                'parent_url': None,
                'fragments': [],
                'discovered_at': 1704067200,
                'queued_at': 1704067200,
                'crawled_at': 1704067300,
                'response_time_ms': 150,
                'status_code': 200,
                'content_type': 'text/html',
                'content_length': 5000,
                'title': 'Page 1',
                'link_count': 10
            },
            {
                'schema_version': 1,
                'url': 'http://example.com/page2',
                'url_normalized': 'http://example.com/page2',
                'depth': 2,
                'parent_url': 'http://example.com/page1',
                'fragments': [],
                'discovered_at': 1704067300,
                'queued_at': 1704067300,
                'crawled_at': None,
                'response_time_ms': None,
                'status_code': None,
                'content_type': None,
                'content_length': None,
                'title': None,
                'link_count': None
            },
            {
                'schema_version': 1,
                'url': 'https://subdomain.example.com/path/to/page.html',
                'url_normalized': 'https://subdomain.example.com/path/to/page.html',
                'depth': 3,
                'parent_url': 'http://example.com/page2',
                'fragments': [],
                'discovered_at': 1704067400,
                'queued_at': 1704067400,
                'crawled_at': 1704067500,
                'response_time_ms': 200,
                'status_code': 200,
                'content_type': 'text/html',
                'content_length': 8000,
                'title': 'Subdomain Page',
                'link_count': 15
            }
        ]

    def generate_edge_case_data(self) -> List[Dict[str, Any]]:
        """Generate edge case test data"""
        return [
            # Very long URL
            {
                'schema_version': 1,
                'url': 'http://example.com/' + 'a' * 1000 + '?param=' + 'b' * 1000,
                'url_normalized': 'http://example.com/' + 'a' * 1000,
                'depth': 1,
                'parent_url': None,
                'fragments': [],
                'discovered_at': 1704067200,
                'queued_at': 1704067200,
                'crawled_at': None,
                'response_time_ms': None,
                'status_code': None,
                'content_type': None,
                'content_length': None,
                'title': None,
                'link_count': None
            },
            # Unicode URL
            {
                'schema_version': 1,
                'url': 'http://example.com/café/日本語',
                'url_normalized': 'http://example.com/café/日本語',
                'depth': 2,
                'parent_url': 'http://example.com/',
                'fragments': [],
                'discovered_at': 1704067300,
                'queued_at': 1704067300,
                'crawled_at': None,
                'response_time_ms': None,
                'status_code': None,
                'content_type': None,
                'content_length': None,
                'title': None,
                'link_count': None
            },
            # Custom port
            {
                'schema_version': 1,
                'url': 'http://example.com:8080/page',
                'url_normalized': 'http://example.com:8080/page',
                'depth': 1,
                'parent_url': None,
                'fragments': [],
                'discovered_at': 1704067400,
                'queued_at': 1704067400,
                'crawled_at': None,
                'response_time_ms': None,
                'status_code': None,
                'content_type': None,
                'content_length': None,
                'title': None,
                'link_count': None
            },
            # Many query parameters
            {
                'schema_version': 1,
                'url': 'http://example.com/page?a=1&b=2&c=3&d=4&e=5&f=6&g=7&h=8&i=9&j=10',
                'url_normalized': 'http://example.com/page?a=1&b=2&c=3&d=4&e=5',
                'depth': 1,
                'parent_url': None,
                'fragments': [],
                'discovered_at': 1704067500,
                'queued_at': 1704067500,
                'crawled_at': None,
                'response_time_ms': None,
                'status_code': None,
                'content_type': None,
                'content_length': None,
                'title': None,
                'link_count': None
            }
        ]

    def generate_stress_test_data(self, count: int = 1000) -> List[Dict[str, Any]]:
        """Generate large dataset for stress testing"""
        urls = []
        domains = ['example.com', 'test.com', 'site.org', 'domain.edu', 'web.net']
        paths = ['page', 'article', 'post', 'content', 'doc']

        for i in range(count):
            domain = domains[i % len(domains)]
            path = paths[i % len(paths)]
            depth = (i % 10) + 1

            urls.append({
                'schema_version': 1,
                'url': f'http://{domain}/{path}/{i}',
                'url_normalized': f'http://{domain}/{path}/{i}',
                'depth': depth,
                'parent_url': f'http://{domain}/' if i > 0 else None,
                'fragments': [],
                'discovered_at': 1704067200 + i,
                'queued_at': 1704067200 + i,
                'crawled_at': 1704067300 + i if i % 2 == 0 else None,
                'response_time_ms': 100 + (i % 500),
                'status_code': 200 if i % 10 != 0 else 404,
                'content_type': 'text/html' if i % 3 == 0 else 'application/json',
                'content_length': 5000 + (i % 10000),
                'title': f'Page {i}' if i % 2 == 0 else None,
                'link_count': i % 50
            })

        return urls

    def test_method_with_data(self, method_name: str, organizer_class, data_loader: DataLoader) -> bool:
        """Test a single method with given data"""
        output_dir = Path(__file__).parent.parent / 'data' / 'test_output' / method_name
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            organizer = organizer_class(output_dir)
            organizer.run(data_loader)
            return True
        except Exception as e:
            self.logger.log_failure(
                'organizer',
                f'test_{method_name}',
                e,
                {'method': method_name, 'data_type': 'test'}
            )
            return False

    def run_test(self, method_name: str):
        """Run comprehensive test for a single method"""
        organizer_class, description = self.methods[method_name]

        print(f"\nTesting: {description} ({method_name})")

        start_time = time.time()
        test_results = {
            'normal': False,
            'edge_cases': False,
            'stress_test': False
        }

        # Test 1: Normal data
        print("\n  [1/3] Testing with normal data...")
        normal_data = self.generate_normal_test_data()
        loader = self.create_test_data_loader(normal_data)
        test_results['normal'] = safe_execute(
            self.test_method_with_data,
            method_name, organizer_class, loader,
            component='organizer',
            operation='normal_test',
            default=False
        )
        print(f"        {'PASS' if test_results['normal'] else 'FAIL'}")

        # Test 2: Edge cases
        print("  [2/3] Testing with edge cases...")
        edge_data = self.generate_edge_case_data()
        loader = self.create_test_data_loader(edge_data)
        test_results['edge_cases'] = safe_execute(
            self.test_method_with_data,
            method_name, organizer_class, loader,
            component='organizer',
            operation='edge_case_test',
            default=False
        )
        print(f"        {'PASS' if test_results['edge_cases'] else 'FAIL'}")

        # Test 3: Stress test
        print("  [3/3] Stress testing with 1000 URLs...")
        stress_data = self.generate_stress_test_data(1000)
        loader = self.create_test_data_loader(stress_data)
        test_results['stress_test'] = safe_execute(
            self.test_method_with_data,
            method_name, organizer_class, loader,
            component='organizer',
            operation='stress_test',
            default=False
        )
        print(f"        {'PASS' if test_results['stress_test'] else 'FAIL'}")

        elapsed = time.time() - start_time
        all_passed = all(test_results.values())

        if all_passed:
            self.results['passed'].append(method_name)
            print(f"\nRESULT: PASSED ({elapsed:.2f}s)")
        else:
            self.results['failed'].append((method_name, test_results))
            print(f"\nRESULT: FAILED ({elapsed:.2f}s)")
            failed_tests = [k for k, v in test_results.items() if not v]
            print(f"Failed tests: {', '.join(failed_tests)}")

        return all_passed

    def run_all_tests(self):
        """Run all tests"""
        print("\nComprehensive Test Suite")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing {len(self.methods)} methods\n")

        overall_start = time.time()

        for method_name in self.methods.keys():
            self.run_test(method_name)

        self._print_summary(overall_start)

    def _print_summary(self, start_time: float):
        """Print test summary"""
        elapsed = time.time() - start_time

        print("\nTest Summary")

        total = len(self.methods)
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])

        print(f"\nTotal Methods Tested: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total Time: {elapsed:.2f}s")
        print(f"Average Time per Method: {elapsed/total:.2f}s")

        if self.results['failed']:
            print("\nFAILED METHODS:")
            for method_name, test_results in self.results['failed']:
                failed_tests = [k for k, v in test_results.items() if not v]
                print(f"  - {method_name}: {', '.join(failed_tests)}")

        if failed == 0:
            print("\nALL TESTS PASSED")
            return True
        else:
            print(f"\n{failed} METHODS FAILED")
            return False


def main():
    """Run comprehensive tests"""
    tester = ComprehensiveMethodTester()
    success = tester.run_all_tests()

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
