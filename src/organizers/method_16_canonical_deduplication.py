"""
Method 16: Canonical URL Deduplication
Groups URLs by their canonical (normalized) form to find duplicates
"""
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser
from src.core.config import get_config


class CanonicalDeduplicationOrganizer:
    """Find duplicate URLs by canonical form"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get tracker params from config
        config = get_config()
        tracker_params = config.get_tracker_params()
        self.parser = URLParser(tracker_params)

    def organize(self, records: List[URLRecord]) -> Dict[str, Any]:
        """
        Group URLs by canonical form

        Args:
            records: List of URL records

        Returns:
            Dictionary with canonical URLs and duplicates
        """
        canonical_map = defaultdict(list)

        for record in records:
            canonical_url = self.parser.get_canonical_url(record.url)
            canonical_map[canonical_url].append(record)

        # Separate unique vs duplicates
        unique = {k: v for k, v in canonical_map.items() if len(v) == 1}
        duplicates = {k: v for k, v in canonical_map.items() if len(v) > 1}

        return {
            'canonical_map': dict(canonical_map),
            'unique': unique,
            'duplicates': duplicates
        }

    def save(self, organized_data: Dict[str, Any]):
        """Save organized data to files"""
        canonical_map = organized_data['canonical_map']
        unique = organized_data['unique']
        duplicates = organized_data['duplicates']

        # Save summary
        summary = {
            'method': 'canonical_deduplication',
            'total_original_urls': sum(len(records) for records in canonical_map.values()),
            'total_canonical_urls': len(canonical_map),
            'unique_urls': len(unique),
            'duplicate_groups': len(duplicates),
            'total_duplicates': sum(len(records) for records in duplicates.values()),
            'deduplication_savings': sum(len(records) - 1 for records in duplicates.values())
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save unique URLs
        with open(self.output_dir / 'unique.jsonl', 'w') as f:
            for canonical_url, records in unique.items():
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        # Save duplicates with details
        duplicates_details = []
        for canonical_url, records in duplicates.items():
            duplicates_details.append({
                'canonical_url': canonical_url,
                'count': len(records),
                'original_urls': [r.url for r in records],
                'records': [r.to_dict() for r in records]
            })

        with open(self.output_dir / 'duplicates.json', 'w') as f:
            json.dump(duplicates_details, f, indent=2)

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 16] Performing canonical deduplication...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Original URLs: {summary['total_original_urls']}")
        print(f"  ✓ Canonical URLs: {summary['total_canonical_urls']}")
        print(f"  ✓ Duplicate groups: {summary['duplicate_groups']}")
        print(f"  ✓ Deduplication savings: {summary['deduplication_savings']} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_16_canonical_deduplication'
    organizer = CanonicalDeduplicationOrganizer(output_dir)
    organizer.run(loader)
