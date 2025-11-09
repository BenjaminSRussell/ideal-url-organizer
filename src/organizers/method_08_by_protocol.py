"""
Method 08: Organization by Protocol
Groups URLs by protocol (http, https)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByProtocolOrganizer:
    """Organize URLs by protocol"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by protocol

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping protocol -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            parsed = self.parser.parse(record.url)
            protocol = parsed.scheme if parsed.scheme else '<no_protocol>'
            organized[protocol].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_protocol',
            'total_protocols': len(organized_data),
            'protocols': {
                protocol: len(records)
                for protocol, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each protocol's URLs to separate file
        for protocol, records in organized_data.items():
            filename = protocol.replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 08] Organizing by protocol...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_protocols']} unique protocols")
        for protocol, count in summary['protocols'].items():
            print(f"    - {protocol}://: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_08_by_protocol'
    organizer = ByProtocolOrganizer(output_dir)
    organizer.run(loader)
