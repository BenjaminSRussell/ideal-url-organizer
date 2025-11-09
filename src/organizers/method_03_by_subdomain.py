"""
Method 03: Organization by Subdomain
Groups URLs by subdomain (archives, catalog, libguides, www, etc.)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class BySubdomainOrganizer:
    """Organize URLs by subdomain"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by subdomain

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping subdomain -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            subdomain, domain, tld = self.parser.get_domain_parts(record.url)

            # Use subdomain if present, otherwise use "root"
            key = subdomain if subdomain else f"<root>.{domain}.{tld}"
            organized[key].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_subdomain',
            'total_subdomains': len(organized_data),
            'subdomains': {
                subdomain: len(records)
                for subdomain, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each subdomain's URLs to separate file
        for subdomain, records in organized_data.items():
            # Sanitize subdomain for filename
            filename = subdomain.replace('.', '_').replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 03] Organizing by subdomain...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_subdomains']} unique subdomains")
        for subdomain, count in summary['subdomains'].items():
            print(f"    - {subdomain}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_03_by_subdomain'
    organizer = BySubdomainOrganizer(output_dir)
    organizer.run(loader)
