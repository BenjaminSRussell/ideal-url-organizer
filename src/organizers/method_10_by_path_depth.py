"""
Method 10: Organization by Path Depth
Groups URLs by the depth of their path (number of path segments)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByPathDepthOrganizer:
    """Organize URLs by path depth"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[int, List[URLRecord]]:
        """
        Group URLs by path depth

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping path depth -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            components = self.parser.extract_components(record.url)
            path_depth = components['path_depth']
            organized[path_depth].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[int, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_path_depth',
            'total_depth_levels': len(organized_data),
            'min_path_depth': min(organized_data.keys()) if organized_data else 0,
            'max_path_depth': max(organized_data.keys()) if organized_data else 0,
            'path_depth_distribution': {
                f'path_depth_{depth}': len(records)
                for depth, records in sorted(organized_data.items())
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each depth level to separate file
        for depth, records in organized_data.items():
            filepath = self.output_dir / f'path_depth_{depth}.jsonl'

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 10] Organizing by path depth...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Path depth range: {summary['min_path_depth']} to {summary['max_path_depth']}")
        for depth_key, count in summary['path_depth_distribution'].items():
            print(f"    - {depth_key}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_10_by_path_depth'
    organizer = ByPathDepthOrganizer(output_dir)
    organizer.run(loader)
