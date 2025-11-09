"""
Method 13: Hierarchical Tree Structure
Creates a hierarchical tree structure based on parent-child relationships
"""
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord


class HierarchicalTreeOrganizer:
    """Create hierarchical tree structure"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_tree(self, records: List[URLRecord]) -> Dict[str, Any]:
        """
        Build hierarchical tree structure

        Args:
            records: List of URL records

        Returns:
            Tree structure as nested dictionary
        """
        # Create URL -> record mapping
        url_map = {record.url: record for record in records}

        # Create parent -> children mapping
        children_map = defaultdict(list)
        root_urls = []

        for record in records:
            if record.parent_url and record.parent_url in url_map:
                children_map[record.parent_url].append(record.url)
            else:
                root_urls.append(record.url)

        # Build tree recursively
        def build_node(url: str) -> Dict[str, Any]:
            record = url_map.get(url)
            if not record:
                return None

            node = {
                'url': url,
                'depth': record.depth,
                'crawled': record.is_crawled(),
                'children': []
            }

            # Add children
            for child_url in children_map.get(url, []):
                child_node = build_node(child_url)
                if child_node:
                    node['children'].append(child_node)

            return node

        # Build tree from roots
        tree = {
            'roots': [build_node(url) for url in root_urls],
            'total_urls': len(records),
            'total_roots': len(root_urls)
        }

        return tree

    def save(self, tree_data: Dict[str, Any]):
        """Save tree data"""
        # Save full tree
        with open(self.output_dir / 'tree.json', 'w') as f:
            json.dump(tree_data, f, indent=2)

        # Save summary
        summary = {
            'method': 'hierarchical_tree',
            'total_urls': tree_data['total_urls'],
            'total_roots': tree_data['total_roots'],
            'tree_depth': self._get_max_depth(tree_data['roots'])
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def _get_max_depth(self, nodes: List[Dict[str, Any]], current_depth: int = 0) -> int:
        """Get maximum depth of tree"""
        if not nodes:
            return current_depth

        max_depth = current_depth
        for node in nodes:
            if node and 'children' in node:
                child_depth = self._get_max_depth(node['children'], current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 13] Creating hierarchical tree...")
        records = data_loader.load()
        tree = self.build_tree(records)
        summary = self.save(tree)

        print(f"  ✓ Built tree with {summary['total_roots']} root nodes")
        print(f"  ✓ Maximum tree depth: {summary['tree_depth']}")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_13_hierarchical_tree'
    organizer = HierarchicalTreeOrganizer(output_dir)
    organizer.run(loader)
