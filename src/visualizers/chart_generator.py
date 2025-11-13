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
            # Modern, attractive styling
            sns.set_style("whitegrid")
            sns.set_palette("husl")
            plt.rcParams['figure.figsize'] = (14, 9)
            plt.rcParams['figure.dpi'] = 150
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
            plt.rcParams['axes.labelsize'] = 12
            plt.rcParams['axes.titlesize'] = 16
            plt.rcParams['axes.titleweight'] = 'bold'
            plt.rcParams['xtick.labelsize'] = 10
            plt.rcParams['ytick.labelsize'] = 10
            plt.rcParams['legend.fontsize'] = 11
            plt.rcParams['figure.titlesize'] = 18

    def generate_all(self, records: List[URLRecord]):
        """Generate all charts"""
        if not PLOTTING_AVAILABLE:
            print("Plotting libraries not available. Skipping chart generation.")
            return

        print("\nGenerating visualizations")

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

        fig, ax = plt.subplots(figsize=(14, 8))
        sorted_depths = sorted(depth_counts.items())
        x = [d[0] for d in sorted_depths]
        y = [d[1] for d in sorted_depths]

        # Modern gradient colors
        colors = plt.cm.viridis([i/len(x) for i in range(len(x))])

        bars = ax.bar(x, y, color=colors, edgecolor='white', linewidth=2, alpha=0.85)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_xlabel('Crawl Depth', fontsize=14, fontweight='600')
        ax.set_ylabel('Number of URLs', fontsize=14, fontweight='600')
        ax.set_title('URL Distribution by Crawl Depth', fontsize=18, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)

        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'depth_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def _generate_domain_distribution(self, records: List[URLRecord]):
        """Bar chart of URL distribution by domain"""
        print("  Creating domain distribution chart...")

        domains = [self.parser.parse(r.url).hostname for r in records]
        domain_counts = Counter(domains)

        fig, ax = plt.subplots(figsize=(14, max(8, len(domain_counts) * 0.5)))
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        x = [d[0] for d in sorted_domains]
        y = [d[1] for d in sorted_domains]

        # Modern gradient colors - reversed for horizontal bars
        colors = plt.cm.plasma([i/len(x) for i in range(len(x))])

        bars = ax.barh(x, y, color=colors, edgecolor='white', linewidth=2, alpha=0.85)

        # Add value labels at the end of bars
        for i, (bar, value) in enumerate(zip(bars, y)):
            ax.text(value + max(y) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{int(value)}',
                   ha='left', va='center', fontsize=10, fontweight='bold')

        ax.set_xlabel('Number of URLs', fontsize=14, fontweight='600')
        ax.set_ylabel('Domain', fontsize=14, fontweight='600')
        ax.set_title('URL Distribution by Domain', fontsize=18, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)

        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'domain_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def _generate_protocol_pie_chart(self, records: List[URLRecord]):
        """Pie chart of protocol usage"""
        print("  Creating protocol distribution chart...")

        protocols = [self.parser.parse(r.url).scheme for r in records]
        protocol_counts = Counter(protocols)

        fig, ax = plt.subplots(figsize=(12, 9))

        # Modern, attractive color scheme
        colors = ['#4ECDC4', '#FF6B6B', '#95E1D3', '#FFE66D'][:len(protocol_counts)]

        # Create explode effect for visual interest
        explode = [0.05] * len(protocol_counts)

        wedges, texts, autotexts = ax.pie(
            protocol_counts.values(),
            labels=protocol_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            shadow=True,
            wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'antialiased': True}
        )

        # Style the text
        for text in texts:
            text.set_fontsize(13)
            text.set_fontweight('bold')

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')

        ax.set_title('Protocol Distribution (HTTP vs HTTPS)', fontsize=18, fontweight='bold', pad=30)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'protocol_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def _generate_url_length_histogram(self, records: List[URLRecord]):
        """Histogram of URL lengths"""
        print("  Creating URL length histogram...")

        lengths = [len(r.url) for r in records]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Create histogram with modern styling
        n, bins, patches = ax.hist(lengths, bins=25, color='#3498DB', edgecolor='white',
                                    linewidth=2, alpha=0.85)

        # Color bars with gradient
        cm = plt.cm.cool
        for i, patch in enumerate(patches):
            patch.set_facecolor(cm(i / len(patches)))

        # Add mean line
        mean_length = sum(lengths) / len(lengths)
        ax.axvline(mean_length, color='#E74C3C', linestyle='--', linewidth=2.5,
                  label=f'Mean: {mean_length:.1f} chars', alpha=0.8)

        ax.set_xlabel('URL Length (characters)', fontsize=14, fontweight='600')
        ax.set_ylabel('Frequency', fontsize=14, fontweight='600')
        ax.set_title('URL Length Distribution', fontsize=18, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)

        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'url_length_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def _generate_crawl_status_chart(self, records: List[URLRecord]):
        """Pie chart of crawl status"""
        print("  Creating crawl status chart...")

        crawled = sum(1 for r in records if r.is_crawled())
        not_crawled = len(records) - crawled

        fig, ax = plt.subplots(figsize=(12, 9))

        # Modern, attractive color scheme
        colors = ['#2ECC71', '#E67E22']

        # Create explode effect - emphasize the larger segment
        sizes = [crawled, not_crawled]
        explode = [0.05 if crawled > not_crawled else 0, 0.05 if not_crawled > crawled else 0]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=['Crawled', 'Not Crawled'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            shadow=True,
            wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'antialiased': True}
        )

        # Style the text
        for text in texts:
            text.set_fontsize(13)
            text.set_fontweight('bold')

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')

        # Add count information
        total = crawled + not_crawled
        ax.text(0, -1.3, f'Total URLs: {total}', ha='center', fontsize=11,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))

        ax.set_title('Crawl Status', fontsize=18, fontweight='bold', pad=30)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'crawl_status.png', dpi=300, bbox_inches='tight', facecolor='white')
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
