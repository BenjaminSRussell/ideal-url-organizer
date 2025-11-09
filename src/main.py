#!/usr/bin/env python3
"""
Main Orchestrator for URL Organizer
Run individual methods or all methods together
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.data_loader import DataLoader
from src.core.config import get_config
from src.analyzers.data_quality_analyzer import DataQualityAnalyzer
from src.visualizers.chart_generator import ChartGenerator

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
    """Main orchestrator for running organization methods"""

    def __init__(self):
        self.config = get_config()
        self.data_loader = DataLoader()
        self.project_root = Path(__file__).parent.parent

        # Map method names to organizer classes
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
        output_dir = self.project_root / 'data' / 'processed' / method_name

        print(f"\n{'='*80}")
        print(f"Running: {description}")
        print(f"{'='*80}")

        try:
            organizer = organizer_class(output_dir)
            organizer.run(self.data_loader)
            print(f"✓ Completed successfully")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_methods(self):
        """Run all organization methods"""
        print("\n" + "="*80)
        print("RUNNING ALL ORGANIZATION METHODS")
        print("="*80)

        start_time = datetime.now()
        results = {}

        for method_name in self.methods.keys():
            success = self.run_method(method_name)
            results[method_name] = 'success' if success else 'failed'

        # Print summary
        elapsed = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results.values() if r == 'success')
        total_count = len(results)

        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Completed {success_count}/{total_count} methods in {elapsed:.2f}s")

        if success_count < total_count:
            print("\nFailed methods:")
            for method, result in results.items():
                if result == 'failed':
                    print(f"  ✗ {method}")

    def run_analysis(self):
        """Run data quality analysis"""
        print("\n" + "="*80)
        print("RUNNING DATA QUALITY ANALYSIS")
        print("="*80)

        analyzer = DataQualityAnalyzer()
        analyzer.run(self.data_loader)

    def run_visualization(self):
        """Generate visualizations"""
        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)

        generator = ChartGenerator()
        generator.run(self.data_loader)

    def list_methods(self):
        """List all available methods"""
        print("\n" + "="*80)
        print("AVAILABLE ORGANIZATION METHODS")
        print("="*80)

        for method_name, (_, description) in self.methods.items():
            print(f"  • {method_name}: {description}")

        print(f"\nTotal: {len(self.methods)} methods")

    def run_full_pipeline(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*80)
        print("FULL ANALYSIS PIPELINE")
        print("="*80)
        print("This will run:")
        print("  1. Data quality analysis")
        print("  2. All organization methods")
        print("  3. Visualization generation")
        print("="*80)

        start_time = datetime.now()

        # Run analysis
        self.run_analysis()

        # Run all methods
        self.run_all_methods()

        # Run visualizations
        self.run_visualization()

        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()
        print("\n" + "="*80)
        print("PIPELINE COMPLETE")
        print("="*80)
        print(f"Total time: {elapsed:.2f}s")
        print(f"\nResults saved to: {self.project_root / 'data'}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='URL Organizer - Comprehensive URL data organization and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all methods
  python src/main.py --all

  # Run specific method
  python src/main.py --method method_01_by_domain

  # Run data quality analysis
  python src/main.py --analyze

  # Generate visualizations
  python src/main.py --visualize

  # Run full pipeline
  python src/main.py --full

  # List all methods
  python src/main.py --list
        """
    )

    parser.add_argument('--all', action='store_true',
                        help='Run all organization methods')
    parser.add_argument('--method', type=str,
                        help='Run specific organization method')
    parser.add_argument('--analyze', action='store_true',
                        help='Run data quality analysis')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate visualizations')
    parser.add_argument('--full', action='store_true',
                        help='Run full pipeline (analysis + all methods + visualization)')
    parser.add_argument('--list', action='store_true',
                        help='List all available methods')

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = URLOrganizerOrchestrator()

    # Handle commands
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
    elif args.visualize:
        orchestrator.run_visualization()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
