"""
Method 02: Organization by Crawl Depth
Groups URLs by their crawl depth level
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord


class ByDepthOrganizer:
    """Organize URLs by crawl depth"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize(self, records: List[URLRecord]) -> Dict[int, List[URLRecord]]:
        """
        Group URLs by depth

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping depth -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            organized[record.depth].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[int, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_depth',
            'total_depth_levels': len(organized_data),
            'min_depth': min(organized_data.keys()),
            'max_depth': max(organized_data.keys()),
            'depth_distribution': {
                f'depth_{depth}': len(records)
                for depth, records in sorted(organized_data.items())
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each depth level to separate file
        for depth, records in organized_data.items():
            filepath = self.output_dir / f'depth_{depth}.jsonl'

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 02] Organizing by depth...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Depth range: {summary['min_depth']} to {summary['max_depth']}")
        for depth_key, count in summary['depth_distribution'].items():
            print(f"    - {depth_key}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_02_by_depth'
    organizer = ByDepthOrganizer(output_dir)
    organizer.run(loader)
