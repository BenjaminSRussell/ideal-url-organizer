"""
Method 07: Organization by TLD (Top Level Domain)
Groups URLs by their TLD (.edu, .com, .org, etc.)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByTLDOrganizer:
    """Organize URLs by TLD"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by TLD

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping TLD -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            subdomain, domain, tld = self.parser.get_domain_parts(record.url)
            key = tld if tld else '<no_tld>'
            organized[key].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_tld',
            'total_tlds': len(organized_data),
            'tlds': {
                tld: len(records)
                for tld, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each TLD's URLs to separate file
        for tld, records in organized_data.items():
            filename = tld.replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 07] Organizing by TLD...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_tlds']} unique TLDs")
        for tld, count in summary['tlds'].items():
            print(f"    - .{tld}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_07_by_tld'
    organizer = ByTLDOrganizer(output_dir)
    organizer.run(loader)
