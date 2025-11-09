"""
Method 15: Organization by Crawl Status
Groups URLs by whether they've been crawled or not
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord


class ByCrawlStatusOrganizer:
    """Organize URLs by crawl status"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by crawl status

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping status -> list of records
        """
        organized = {
            'crawled': [],
            'not_crawled': []
        }

        for record in records:
            if record.is_crawled():
                organized['crawled'].append(record)
            else:
                organized['not_crawled'].append(record)

        return organized

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_crawl_status',
            'crawled': len(organized_data['crawled']),
            'not_crawled': len(organized_data['not_crawled']),
            'total': len(organized_data['crawled']) + len(organized_data['not_crawled']),
            'crawl_percentage': (len(organized_data['crawled']) /
                                (len(organized_data['crawled']) + len(organized_data['not_crawled'])) * 100
                                if (len(organized_data['crawled']) + len(organized_data['not_crawled'])) > 0 else 0)
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each status's URLs to separate file
        for status, records in organized_data.items():
            filepath = self.output_dir / f'{status}.jsonl'

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 15] Organizing by crawl status...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Crawled: {summary['crawled']} URLs ({summary['crawl_percentage']:.1f}%)")
        print(f"  ✓ Not crawled: {summary['not_crawled']} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_15_by_crawl_status'
    organizer = ByCrawlStatusOrganizer(output_dir)
    organizer.run(loader)
