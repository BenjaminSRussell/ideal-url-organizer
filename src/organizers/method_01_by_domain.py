"""
Method 01: Organization by Domain
Groups URLs by their full domain (hostname)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByDomainOrganizer:
    """Organize URLs by domain"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by domain

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping domain -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            parsed = self.parser.parse(record.url)
            domain = parsed.hostname
            organized[domain].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_domain',
            'total_domains': len(organized_data),
            'domains': {
                domain: len(records)
                for domain, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each domain's URLs to separate file
        for domain, records in organized_data.items():
            # Sanitize domain for filename
            filename = domain.replace(':', '_').replace('/', '_') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 01] Organizing by domain...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_domains']} unique domains")
        for domain, count in summary['domains'].items():
            print(f"    - {domain}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_01_by_domain'
    organizer = ByDomainOrganizer(output_dir)
    organizer.run(loader)
