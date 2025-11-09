"""
Chart Generator
Creates visual charts and graphs for URL data analysis
"""
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import json

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Warning: matplotlib/seaborn not available. Install with: pip install matplotlib seaborn")

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ChartGenerator:
    """Generate visual charts and graphs"""

    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'visualizations' / 'charts'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

        if PLOTTING_AVAILABLE:
            sns.set_style("whitegrid")
            plt.rcParams['figure.figsize'] = (12, 8)
            plt.rcParams['figure.dpi'] = 100

    def generate_all(self, records: List[URLRecord]):
        """Generate all charts"""
        if not PLOTTING_AVAILABLE:
            print("Plotting libraries not available. Skipping chart generation.")
            return

        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)

        self._generate_depth_distribution(records)
        self._generate_domain_distribution(records)
        self._generate_protocol_pie_chart(records)
        self._generate_url_length_histogram(records)
        self._generate_crawl_status_chart(records)

        print(f"\n✓ All charts saved to: {self.output_dir}")

    def _generate_depth_distribution(self, records: List[URLRecord]):
        """Bar chart of URL distribution by depth"""
        print("  Creating depth distribution chart...")

        depths = [r.depth for r in records]
        depth_counts = Counter(depths)

        fig, ax = plt.subplots()
        sorted_depths = sorted(depth_counts.items())
        x = [d[0] for d in sorted_depths]
        y = [d[1] for d in sorted_depths]

        ax.bar(x, y, color='steelblue', edgecolor='black')
        ax.set_xlabel('Crawl Depth', fontsize=12)
        ax.set_ylabel('Number of URLs', fontsize=12)
        ax.set_title('URL Distribution by Crawl Depth', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'depth_distribution.png')
        plt.close()

    def _generate_domain_distribution(self, records: List[URLRecord]):
        """Bar chart of URL distribution by domain"""
        print("  Creating domain distribution chart...")

        domains = [self.parser.parse(r.url).hostname for r in records]
        domain_counts = Counter(domains)

        fig, ax = plt.subplots()
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        x = [d[0] for d in sorted_domains]
        y = [d[1] for d in sorted_domains]

        ax.barh(x, y, color='coral', edgecolor='black')
        ax.set_xlabel('Number of URLs', fontsize=12)
        ax.set_ylabel('Domain', fontsize=12)
        ax.set_title('URL Distribution by Domain', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'domain_distribution.png', bbox_inches='tight')
        plt.close()

    def _generate_protocol_pie_chart(self, records: List[URLRecord]):
        """Pie chart of protocol usage"""
        print("  Creating protocol distribution chart...")

        protocols = [self.parser.parse(r.url).scheme for r in records]
        protocol_counts = Counter(protocols)

        fig, ax = plt.subplots()
        ax.pie(
            protocol_counts.values(),
            labels=protocol_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=['#ff9999', '#66b3ff']
        )
        ax.set_title('Protocol Distribution (HTTP vs HTTPS)', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'protocol_distribution.png')
        plt.close()

    def _generate_url_length_histogram(self, records: List[URLRecord]):
        """Histogram of URL lengths"""
        print("  Creating URL length histogram...")

        lengths = [len(r.url) for r in records]

        fig, ax = plt.subplots()
        ax.hist(lengths, bins=20, color='mediumseagreen', edgecolor='black')
        ax.set_xlabel('URL Length (characters)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('URL Length Distribution', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'url_length_distribution.png')
        plt.close()

    def _generate_crawl_status_chart(self, records: List[URLRecord]):
        """Pie chart of crawl status"""
        print("  Creating crawl status chart...")

        crawled = sum(1 for r in records if r.is_crawled())
        not_crawled = len(records) - crawled

        fig, ax = plt.subplots()
        ax.pie(
            [crawled, not_crawled],
            labels=['Crawled', 'Not Crawled'],
            autopct='%1.1f%%',
            startangle=90,
            colors=['#90EE90', '#FFB6C1']
        )
        ax.set_title('Crawl Status', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'crawl_status.png')
        plt.close()

    def run(self, data_loader: DataLoader):
        """Run chart generation"""
        records = data_loader.load()
        self.generate_all(records)


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    generator = ChartGenerator()
    generator.run(loader)
