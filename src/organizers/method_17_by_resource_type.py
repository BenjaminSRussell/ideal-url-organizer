"""
Method 17: Organization by Resource Type
Categorizes URLs by resource type (repositories, courses, programs, etc.)
based on URL patterns
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByResourceTypeOrganizer:
    """Organize URLs by resource type"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

        # Define resource type patterns (based on URL path)
        self.resource_patterns = {
            'repository': 'repositories',
            'course': 'course',
            'program': 'program',
            'entity': 'entity',
            'catalog_home': 'catalog.hartford.edu/',
            'archives': 'archives.hartford.edu',
            'libguides': 'libguides.hartford.edu',
            'academics': 'academics',
            'music': 'music',
            'education': 'education'
        }

    def get_resource_type(self, url: str) -> str:
        """Determine resource type from URL"""
        url_lower = url.lower()

        for resource_type, pattern in self.resource_patterns.items():
            if pattern in url_lower:
                return resource_type

        return '<other>'

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by resource type

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping resource type -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            resource_type = self.get_resource_type(record.url)
            organized[resource_type].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_resource_type',
            'total_resource_types': len(organized_data),
            'resource_types': {
                rt: len(records)
                for rt, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each resource type's URLs to separate file
        for resource_type, records in organized_data.items():
            filename = resource_type.replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 17] Organizing by resource type...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_resource_types']} resource types")
        for rt, count in summary['resource_types'].items():
            print(f"    - {rt}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_17_by_resource_type'
    organizer = ByResourceTypeOrganizer(output_dir)
    organizer.run(loader)
