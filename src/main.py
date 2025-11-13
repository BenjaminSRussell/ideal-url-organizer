#!/usr/bin/env python3
"""
URL Organizer - Main orchestrator for running organization methods
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.data_loader import DataLoader
from src.core.config import get_config
from src.core.web_crawler import WebCrawler
from src.analyzers.data_quality_analyzer import DataQualityAnalyzer
from src.analyzers.link_graph_analyzer import LinkGraphAnalyzer
from src.analyzers.semantic_analyzer import SemanticAnalyzer
from src.analyzers.advanced_analytics import AdvancedAnalytics
from src.analyzers.comprehensive_report_generator import ComprehensiveReportGenerator
from src.visualizers.chart_generator import ChartGenerator
from src.generators.unified_report_generator import UnifiedReportGenerator

# Import all organizers
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


class URLOrganizerOrchestrator:
    """Orchestrates URL organization methods"""

    def __init__(self):
        self.config = get_config()
        self.data_loader = DataLoader()
        self.project_root = Path(__file__).parent.parent

        self.methods = {
            'method_01_by_domain': (ByDomainOrganizer, 'Organize by Domain'),
            'method_02_by_depth': (ByDepthOrganizer, 'Organize by Crawl Depth'),
            'method_03_by_subdomain': (BySubdomainOrganizer, 'Organize by Subdomain'),
            'method_04_by_path_structure': (ByPathStructureOrganizer, 'Organize by Path Structure'),
            'method_05_by_query_params': (ByQueryParamsOrganizer, 'Organize by Query Parameters'),
            'method_06_by_parent_domain': (ByParentDomainOrganizer, 'Organize by Parent Domain'),
            'method_07_by_tld': (ByTLDOrganizer, 'Organize by TLD'),
            'method_08_by_protocol': (ByProtocolOrganizer, 'Organize by Protocol'),
            'method_09_by_port': (ByPortOrganizer, 'Organize by Port'),
            'method_10_by_path_depth': (ByPathDepthOrganizer, 'Organize by Path Depth'),
            'method_11_by_file_extension': (ByFileExtensionOrganizer, 'Organize by File Extension'),
            'method_12_by_content_type': (ByContentTypeOrganizer, 'Organize by Content Type'),
            'method_13_hierarchical_tree': (HierarchicalTreeOrganizer, 'Create Hierarchical Tree'),
            'method_14_by_discovery_time': (ByDiscoveryTimeOrganizer, 'Organize by Discovery Time'),
            'method_15_by_crawl_status': (ByCrawlStatusOrganizer, 'Organize by Crawl Status'),
            'method_16_canonical_deduplication': (CanonicalDeduplicationOrganizer, 'Canonical URL Deduplication'),
            'method_17_by_resource_type': (ByResourceTypeOrganizer, 'Organize by Resource Type'),
            'method_18_by_url_length': (ByURLLengthOrganizer, 'Organize by URL Length'),
            'method_19_network_graph': (NetworkGraphOrganizer, 'Create Network Graph'),
            'method_20_by_param_patterns': (ByParamPatternsOrganizer, 'Organize by Parameter Patterns'),
            'method_21_domain_and_depth_matrix': (DomainDepthMatrixOrganizer, 'Create Domain-Depth Matrix'),
        }

    def run_method(self, method_name: str):
        """Run a single organization method"""
        if method_name not in self.methods:
            print(f"Error: Unknown method '{method_name}'")
            print(f"Available methods: {', '.join(self.methods.keys())}")
            return False

        organizer_class, description = self.methods[method_name]
        output_dir = self.project_root / 'data' / 'results' / 'methods' / method_name

        print(f"\n{description}")

        try:
            organizer = organizer_class(output_dir)
            organizer.run(self.data_loader)
            print(f"Completed successfully")
            return True
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_methods(self):
        """Run all organization methods"""
        print("\nRunning all organization methods")

        start_time = datetime.now()
        results = {}

        for method_name in self.methods.keys():
            success = self.run_method(method_name)
            results[method_name] = 'success' if success else 'failed'

        elapsed = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results.values() if r == 'success')
        total_count = len(results)

        print(f"\nCompleted {success_count}/{total_count} methods in {elapsed:.2f}s")

        if success_count < total_count:
            print("\nFailed methods:")
            for method, result in results.items():
                if result == 'failed':
                    print(f"  {method}")

    def run_analysis(self):
        """Run data quality analysis"""
        print("\nRunning data quality analysis")

        analyzer = DataQualityAnalyzer()
        analyzer.run(self.data_loader)

    def run_advanced_analysis(self):
        """Run advanced analytics (link graph, semantic, temporal, etc.)"""
        print("\nRunning advanced analysis")

        data_loader = DataLoader()
        records = data_loader.load()

        # Try to get crawled pages
        pages = []
        try:
            # Check if crawled data exists
            crawler = WebCrawler()
            crawled_data_file = self.project_root / 'data' / 'crawled' / 'pages.jsonl'
            if crawled_data_file.exists():
                with open(crawled_data_file, 'r') as f:
                    import json
                    for line in f:
                        try:
                            page_data = json.loads(line)
                            # Convert to PageContent if possible
                            from src.core.web_crawler import PageContent
                            page = PageContent(**page_data)
                            pages.append(page)
                        except Exception:
                            pass
            if pages:
                print(f"  ✓ Loaded {len(pages)} crawled pages")
        except Exception as e:
            print(f"  Warning: Could not load page content: {e}")
            pages = []

        # Run link graph analysis
        if pages:
            print("\n  [1/4] Link Graph Analysis")
            try:
                link_analyzer = LinkGraphAnalyzer()
                link_analyzer.analyze(pages)
            except Exception as e:
                print(f"    Error: {e}")

        # Run semantic analysis
        if pages:
            print("\n  [2/4] Semantic Analysis")
            try:
                semantic_analyzer = SemanticAnalyzer()
                semantic_analyzer.analyze(pages)
            except Exception as e:
                print(f"    Error: {e}")

        # Run advanced analytics
        print("\n  [3/4] Advanced Analytics")
        try:
            advanced_analytics = AdvancedAnalytics()
            advanced_analytics.analyze(pages, records)
        except Exception as e:
            print(f"    Error: {e}")

        # Generate comprehensive report
        print("\n  [4/4] Generating Comprehensive Report")
        try:
            report_gen = ComprehensiveReportGenerator()
            report_gen.run()
        except Exception as e:
            print(f"    Error: {e}")

    def run_visualization(self):
        """Generate visualizations"""
        print("\nGenerating visualizations")

        generator = ChartGenerator()
        generator.run(self.data_loader)

    def run_unified_report(self):
        """Generate unified HTML report"""
        print("\nGenerating unified HTML report")

        generator = UnifiedReportGenerator()
        report_path = generator.generate_report()

        if report_path:
            print(f"\n[+] Unified report generated successfully")
            print(f"[+] Open in browser: file://{report_path.absolute()}")
        else:
            print("\n[-] Failed to generate unified report")

    def list_methods(self):
        """List all available methods"""
        print("\nAvailable organization methods:")

        for method_name, (_, description) in self.methods.items():
            print(f"  {method_name}: {description}")

        print(f"\nTotal: {len(self.methods)} methods")

    def run_full_pipeline(self):
        """Run complete analysis pipeline"""
        print("\nFull pipeline: analysis, advanced analytics, methods, visualization, and unified report")

        start_time = datetime.now()

        self.run_analysis()
        self.run_advanced_analysis()
        self.run_all_methods()
        self.run_visualization()
        self.run_unified_report()

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\nPipeline complete in {elapsed:.2f}s")
        print(f"Results: {self.project_root / 'data' / 'results'}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='URL Organizer')
    parser.add_argument('--all', action='store_true', help='Run all organization methods')
    parser.add_argument('--method', type=str, help='Run specific organization method')
    parser.add_argument('--analyze', action='store_true', help='Run data quality analysis')
    parser.add_argument('--advanced', action='store_true', help='Run advanced analytics (link graph, semantic, temporal)')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    parser.add_argument('--unified-report', action='store_true', help='Generate unified HTML report')
    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    parser.add_argument('--list', action='store_true', help='List all available methods')

    args = parser.parse_args()
    orchestrator = URLOrganizerOrchestrator()

    if args.list:
        orchestrator.list_methods()
    elif args.full:
        orchestrator.run_full_pipeline()
    elif args.all:
        orchestrator.run_all_methods()
    elif args.method:
        orchestrator.run_method(args.method)
    elif args.analyze:
        orchestrator.run_analysis()
    elif args.advanced:
        orchestrator.run_advanced_analysis()
    elif args.visualize:
        orchestrator.run_visualization()
    elif args.unified_report:
        orchestrator.run_unified_report()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
