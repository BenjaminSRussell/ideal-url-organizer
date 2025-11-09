"""
Method 05: Organization by Query Parameters
Groups URLs by presence and type of query parameters
"""
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByQueryParamsOrganizer:
    """Organize URLs by query parameters"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by query parameter signature

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping param signature -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            components = self.parser.extract_components(record.url)
            query_params = components['query_params']

            if query_params:
                # Create signature from sorted param keys
                param_keys = sorted(query_params.keys())
                signature = ','.join(param_keys)
            else:
                signature = '<no_params>'

            organized[signature].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_query_params',
            'total_signatures': len(organized_data),
            'signatures': {
                sig: len(records)
                for sig, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each signature's URLs to separate file
        for signature, records in organized_data.items():
            # Sanitize signature for filename
            filename = signature.replace(',', '_').replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 05] Organizing by query parameters...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_signatures']} unique parameter signatures")
        for signature, count in summary['signatures'].items():
            print(f"    - {signature}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_05_by_query_params'
    organizer = ByQueryParamsOrganizer(output_dir)
    organizer.run(loader)
