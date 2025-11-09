"""
Method 24: Organization by Page Authority (PageRank)
Groups URLs by their PageRank score (importance in link structure)

This separates cornerstone content from leaf pages
"""
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import json

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from src.core.web_crawler import PageContent


class ByPageAuthorityOrganizer:
    """Organize URLs by PageRank authority"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx required for PageRank")

    def organize(self, pages: List[PageContent]) -> Dict[str, List[PageContent]]:
        """Group pages by PageRank authority level"""
        # Build graph
        G = self._build_graph(pages)

        # Compute PageRank
        pagerank = nx.pagerank(G) if G.number_of_nodes() > 0 else {}

        # Create page map
        page_map = {p.url: p for p in pages}

        # Categorize by authority level
        organized = {
            'very_high': [],    # Top 10%
            'high': [],         # Top 10-25%
            'medium': [],       # Top 25-50%
            'low': [],          # Bottom 50%
        }

        if pagerank:
            scores = sorted(pagerank.values(), reverse=True)
            threshold_very_high = scores[int(len(scores) * 0.10)] if len(scores) > 10 else 0
            threshold_high = scores[int(len(scores) * 0.25)] if len(scores) > 4 else 0
            threshold_medium = scores[int(len(scores) * 0.50)] if len(scores) > 2 else 0

            for url, score in pagerank.items():
                page = page_map.get(url)
                if page:
                    if score >= threshold_very_high:
                        organized['very_high'].append(page)
                    elif score >= threshold_high:
                        organized['high'].append(page)
                    elif score >= threshold_medium:
                        organized['medium'].append(page)
                    else:
                        organized['low'].append(page)

        return organized

    def _build_graph(self, pages: List[PageContent]) -> nx.DiGraph:
        """Build link graph"""
        G = nx.DiGraph()
        page_map = {p.url: p for p in pages}

        for page in pages:
            G.add_node(page.url)

        for page in pages:
            for link in page.internal_links:
                if link in page_map:
                    G.add_edge(page.url, link)

        return G

    def save(self, organized_data: Dict[str, List[PageContent]]):
        """Save organized data"""
        summary = {
            'method': 'by_page_authority',
            'authority_distribution': {
                level: len(pages)
                for level, pages in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each authority level
        for level, pages in organized_data.items():
            filepath = self.output_dir / f'{level}.json'
            with open(filepath, 'w') as f:
                json.dump([p.to_dict() for p in pages], f, indent=2)

        return summary

    def run(self, pages: List[PageContent]):
        """Run the organization method"""
        print(f"[Method 24] Organizing by page authority (PageRank)...")
        organized = self.organize(pages)
        summary = self.save(organized)

        print(f"  ✓ Authority distribution:")
        for level, count in summary['authority_distribution'].items():
            print(f"    - {level}: {count} pages")

        return summary
