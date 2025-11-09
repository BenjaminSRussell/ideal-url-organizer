"""
Method 19: Network Graph Visualization
Creates a network graph of parent-child URL relationships
"""
from pathlib import Path
from typing import List, Dict, Any
import json

from src.core.data_loader import DataLoader, URLRecord


class NetworkGraphOrganizer:
    """Create network graph of URL relationships"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_graph(self, records: List[URLRecord]) -> Dict[str, Any]:
        """
        Create network graph structure

        Args:
            records: List of URL records

        Returns:
            Graph data structure
        """
        nodes = []
        edges = []
        node_ids = {}

        # Create nodes
        for idx, record in enumerate(records):
            node_id = idx
            node_ids[record.url] = node_id

            nodes.append({
                'id': node_id,
                'url': record.url,
                'depth': record.depth,
                'crawled': record.is_crawled()
            })

        # Create edges (parent -> child relationships)
        for record in records:
            if record.parent_url:
                parent_id = node_ids.get(record.parent_url)
                child_id = node_ids.get(record.url)

                if parent_id is not None and child_id is not None:
                    edges.append({
                        'source': parent_id,
                        'target': child_id,
                        'depth': record.depth
                    })

        graph = {
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }

        return graph

    def save(self, graph_data: Dict[str, Any]):
        """Save graph data"""
        # Save full graph
        with open(self.output_dir / 'graph.json', 'w') as f:
            json.dump(graph_data, f, indent=2)

        # Save summary
        summary = {
            'method': 'network_graph',
            'node_count': graph_data['node_count'],
            'edge_count': graph_data['edge_count'],
            'avg_connections': graph_data['edge_count'] / graph_data['node_count'] if graph_data['node_count'] > 0 else 0
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 19] Creating network graph...")
        records = data_loader.load()
        graph = self.create_graph(records)
        summary = self.save(graph)

        print(f"  ✓ Created graph with {summary['node_count']} nodes")
        print(f"  ✓ Created {summary['edge_count']} edges")
        print(f"  ✓ Average connections: {summary['avg_connections']:.2f}")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_19_network_graph'
    organizer = NetworkGraphOrganizer(output_dir)
    organizer.run(loader)
