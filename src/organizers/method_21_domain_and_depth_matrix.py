"""
Method 21: Domain and Depth Matrix
Creates a 2D matrix showing how URLs are distributed across domains and depths
"""
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class DomainDepthMatrixOrganizer:
    """Create domain-depth matrix"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Create domain-depth matrix"""
        matrix = defaultdict(lambda: defaultdict(list))

        for record in records:
            parsed = self.parser.parse(record.url)
            domain = parsed.hostname
            depth = record.depth

            matrix[domain][depth].append(record)

        return {'matrix': {d: dict(depths) for d, depths in matrix.items()}}

    def save(self, organized_data: Dict[str, Any]):
        """Save matrix data"""
        matrix = organized_data['matrix']

        # Create summary with counts
        summary_matrix = {}
        for domain, depths in matrix.items():
            summary_matrix[domain] = {depth: len(records) for depth, records in depths.items()}

        summary = {
            'method': 'domain_depth_matrix',
            'matrix': summary_matrix,
            'domains': list(matrix.keys()),
            'depths': sorted(set(d for depths in matrix.values() for d in depths.keys()))
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        with open(self.output_dir / 'matrix.json', 'w') as f:
            json.dump({'matrix': summary_matrix}, f, indent=2)

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 21] Creating domain-depth matrix...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Matrix: {len(summary['domains'])} domains × {len(summary['depths'])} depths")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_21_domain_and_depth_matrix'
    organizer = DomainDepthMatrixOrganizer(output_dir)
    organizer.run(loader)
