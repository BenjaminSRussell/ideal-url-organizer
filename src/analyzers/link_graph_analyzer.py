"""
Link Graph Analyzer - PageRank and HITS algorithms

This is THE KEY to finding authoritative and important pages
"""
from typing import Dict, List, Tuple, Any
import json
from pathlib import Path
from collections import defaultdict

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Warning: networkx not available. Install with: pip install networkx")

from src.core.web_crawler import PageContent


class LinkGraphAnalyzer:
    """
    Analyze link graph structure using PageRank and HITS algorithms

    PageRank: Finds the most "important" pages (linked to by other important pages)
    HITS: Finds "hubs" (pages that link to many authorities) and "authorities" (pages linked to by many hubs)
    """

    def __init__(self, output_dir: Path = None):
        """Initialize link graph analyzer"""
        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx not installed")

        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'analysis' / 'link_graph'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_graph(self, pages: List[PageContent]) -> nx.DiGraph:
        """
        Build directed graph from page links

        Args:
            pages: List of PageContent objects

        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()

        # Create URL -> PageContent mapping
        page_map = {page.url: page for page in pages}
        page_map.update({page.final_url: page for page in pages})  # Include final URLs

        # Add all pages as nodes
        for page in pages:
            G.add_node(page.url, title=page.title, status_code=page.status_code)

        # Add edges for internal links
        for page in pages:
            source = page.url

            for link in page.internal_links:
                # Only add edge if target is in our dataset
                if link in page_map or link in G.nodes:
                    G.add_edge(source, link)

        return G

    def compute_pagerank(self, G: nx.DiGraph, damping: float = 0.85) -> Dict[str, float]:
        """
        Compute PageRank scores

        PageRank measures the importance of pages based on the link structure.
        A page is important if it's linked to by other important pages.

        Args:
            G: NetworkX directed graph
            damping: Damping factor (probability of following a link vs. random jump)

        Returns:
            Dictionary mapping URL -> PageRank score
        """
        try:
            pagerank = nx.pagerank(G, alpha=damping)
            return pagerank
        except:
            return {}

    def compute_hits(self, G: nx.DiGraph) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Compute HITS (Hyperlink-Induced Topic Search) scores

        HITS identifies two types of pages:
        - Hubs: Pages that link to many authorities
        - Authorities: Pages that are linked to by many hubs

        Args:
            G: NetworkX directed graph

        Returns:
            Tuple of (hubs, authorities) dictionaries
        """
        try:
            hubs, authorities = nx.hits(G)
            return hubs, authorities
        except:
            return {}, {}

    def find_central_pages(self, G: nx.DiGraph) -> Dict[str, Any]:
        """
        Find central/important pages using various centrality measures

        Args:
            G: NetworkX directed graph

        Returns:
            Dictionary of centrality measures
        """
        centrality = {}

        # In-degree: How many pages link TO this page
        centrality['in_degree'] = dict(G.in_degree())

        # Out-degree: How many pages this page links TO
        centrality['out_degree'] = dict(G.out_degree())

        # Betweenness: How often this page lies on shortest paths
        if G.number_of_nodes() > 1:
            try:
                centrality['betweenness'] = nx.betweenness_centrality(G)
            except:
                centrality['betweenness'] = {}

        return centrality

    def identify_page_types(self, G: nx.DiGraph) -> Dict[str, List[str]]:
        """
        Categorize pages by their link patterns

        Args:
            G: NetworkX directed graph

        Returns:
            Dictionary mapping page type -> list of URLs
        """
        page_types = defaultdict(list)

        for node in G.nodes():
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)

            # Cornerstone content: High in-degree, moderate out-degree
            if in_degree >= 5 and out_degree >= 3:
                page_types['cornerstone'].append(node)

            # Hub pages: High out-degree
            elif out_degree >= 10:
                page_types['hub'].append(node)

            # Authority pages: High in-degree
            elif in_degree >= 5:
                page_types['authority'].append(node)

            # Leaf pages: No outgoing links
            elif out_degree == 0:
                page_types['leaf'].append(node)

            # Orphan pages: No incoming links
            elif in_degree == 0:
                page_types['orphan'].append(node)

            # Normal pages
            else:
                page_types['normal'].append(node)

        return dict(page_types)

    def analyze(self, pages: List[PageContent]) -> Dict[str, Any]:
        """
        Perform comprehensive link graph analysis

        Args:
            pages: List of PageContent objects

        Returns:
            Analysis results
        """
        print("\nLink Graph Analysis")

        # Build graph
        print("\nBuilding link graph...")
        G = self.build_graph(pages)
        print(f"  ✓ Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        analysis = {
            'graph_stats': {
                'num_nodes': G.number_of_nodes(),
                'num_edges': G.number_of_edges(),
                'density': nx.density(G),
                'is_connected': nx.is_weakly_connected(G)
            }
        }

        # PageRank
        print("\nComputing PageRank...")
        pagerank = self.compute_pagerank(G)
        if pagerank:
            top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
            analysis['pagerank'] = {
                'top_10': [{'url': url, 'score': score} for url, score in top_pagerank]
            }
            print(f"  ✓ Top page: {top_pagerank[0][0]} (score: {top_pagerank[0][1]:.4f})")

        # HITS
        print("\nComputing HITS (hubs and authorities)...")
        hubs, authorities = self.compute_hits(G)
        if hubs and authorities:
            top_hubs = sorted(hubs.items(), key=lambda x: x[1], reverse=True)[:10]
            top_authorities = sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:10]

            analysis['hits'] = {
                'top_hubs': [{'url': url, 'score': score} for url, score in top_hubs],
                'top_authorities': [{'url': url, 'score': score} for url, score in top_authorities]
            }
            print(f"  ✓ Top hub: {top_hubs[0][0]}")
            print(f"  ✓ Top authority: {top_authorities[0][0]}")

        # Centrality measures
        print("\nComputing centrality measures...")
        centrality = self.find_central_pages(G)
        if centrality.get('in_degree'):
            top_in_degree = sorted(centrality['in_degree'].items(), key=lambda x: x[1], reverse=True)[:10]
            analysis['centrality'] = {
                'top_in_degree': [{'url': url, 'degree': deg} for url, deg in top_in_degree]
            }

        # Page types
        print("\nCategorizing pages by link patterns...")
        page_types = self.identify_page_types(G)
        analysis['page_types'] = {
            ptype: len(urls)
            for ptype, urls in page_types.items()
        }

        print("\nPage Type Distribution:")
        for ptype, count in analysis['page_types'].items():
            print(f"  • {ptype}: {count} pages")

        # Save analysis
        analysis_file = self.output_dir / 'link_graph_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        # Export graph for visualization
        graph_file = self.output_dir / 'graph.gexf'
        nx.write_gexf(G, graph_file)

        print(f"\n✓ Link graph analysis saved to: {analysis_file}")
        print(f"✓ Graph exported to: {graph_file} (open with Gephi)")

        return analysis


if __name__ == '__main__':
    print("Link Graph Analyzer - Install networkx:")
    print("  pip install networkx")
