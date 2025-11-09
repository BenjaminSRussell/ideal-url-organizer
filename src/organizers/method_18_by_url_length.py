"""
Method 18: Organization by URL Length
Groups URLs by length categories (short, medium, long, very long)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord


class ByURLLengthOrganizer:
    """Organize URLs by length"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Define length categories
        self.categories = [
            (0, 50, 'very_short'),
            (50, 100, 'short'),
            (100, 150, 'medium'),
            (150, 200, 'long'),
            (200, float('inf'), 'very_long')
        ]

    def get_length_category(self, url: str) -> str:
        """Get length category for URL"""
        length = len(url)

        for min_len, max_len, category in self.categories:
            if min_len <= length < max_len:
                return f'{category}_{min_len}-{max_len if max_len != float("inf") else "plus"}'

        return 'unknown'

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by length

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping length category -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            category = self.get_length_category(record.url)
            organized[category].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Calculate statistics
        all_lengths = []
        for records in organized_data.values():
            all_lengths.extend([len(r.url) for r in records])

        # Save summary
        summary = {
            'method': 'by_url_length',
            'total_categories': len(organized_data),
            'categories': {
                cat: len(records)
                for cat, records in organized_data.items()
            },
            'statistics': {
                'min_length': min(all_lengths) if all_lengths else 0,
                'max_length': max(all_lengths) if all_lengths else 0,
                'avg_length': sum(all_lengths) / len(all_lengths) if all_lengths else 0
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each category's URLs to separate file
        for category, records in organized_data.items():
            filepath = self.output_dir / f'{category}.jsonl'

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 18] Organizing by URL length...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Length range: {summary['statistics']['min_length']} to {summary['statistics']['max_length']}")
        print(f"  ✓ Average length: {summary['statistics']['avg_length']:.1f}")
        for cat, count in summary['categories'].items():
            print(f"    - {cat}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_18_by_url_length'
    organizer = ByURLLengthOrganizer(output_dir)
    organizer.run(loader)
