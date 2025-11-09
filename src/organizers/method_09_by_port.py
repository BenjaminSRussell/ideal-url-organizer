"""
Method 09: Organization by Port Number
Groups URLs by port number (8081, 80, 443, etc.)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByPortOrganizer:
    """Organize URLs by port"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by port

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping port -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            parsed = self.parser.parse(record.url)

            if parsed.port:
                port_key = str(parsed.port)
            else:
                # Default ports based on scheme
                if parsed.scheme == 'http':
                    port_key = '80_default'
                elif parsed.scheme == 'https':
                    port_key = '443_default'
                else:
                    port_key = '<no_port>'

            organized[port_key].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_port',
            'total_ports': len(organized_data),
            'ports': {
                port: len(records)
                for port, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each port's URLs to separate file
        for port, records in organized_data.items():
            filename = f'port_{port}.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 09] Organizing by port...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_ports']} unique ports")
        for port, count in summary['ports'].items():
            print(f"    - Port {port}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_09_by_port'
    organizer = ByPortOrganizer(output_dir)
    organizer.run(loader)
