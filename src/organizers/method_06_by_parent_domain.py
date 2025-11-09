"""
Method 06: Organization by Parent URL Domain
Groups URLs by the domain of their parent URL
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByParentDomainOrganizer:
    """Organize URLs by parent domain"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by parent domain

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping parent domain -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            if record.parent_url:
                parsed = self.parser.parse(record.parent_url)
                parent_domain = parsed.hostname
            else:
                parent_domain = '<no_parent>'

            organized[parent_domain].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_parent_domain',
            'total_parent_domains': len(organized_data),
            'parent_domains': {
                domain: len(records)
                for domain, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each parent domain's URLs to separate file
        for domain, records in organized_data.items():
            # Sanitize domain for filename
            filename = domain.replace(':', '_').replace('/', '_').replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 06] Organizing by parent domain...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_parent_domains']} unique parent domains")
        for domain, count in summary['parent_domains'].items():
            print(f"    - {domain}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_06_by_parent_domain'
    organizer = ByParentDomainOrganizer(output_dir)
    organizer.run(loader)
