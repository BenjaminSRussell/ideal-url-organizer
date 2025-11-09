"""
Method 14: Organization by Discovery Time
Groups URLs by discovery time buckets (hour, day, etc.)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime
import json

from src.core.data_loader import DataLoader, URLRecord


class ByDiscoveryTimeOrganizer:
    """Organize URLs by discovery time"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by discovery time (by hour)

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping time bucket -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            if record.discovered_at:
                dt = datetime.fromtimestamp(record.discovered_at)
                # Group by hour
                time_bucket = dt.strftime('%Y-%m-%d_%H:00')
            else:
                time_bucket = '<no_discovery_time>'

            organized[time_bucket].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_discovery_time',
            'total_time_buckets': len(organized_data),
            'time_buckets': {
                bucket: len(records)
                for bucket, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each time bucket's URLs to separate file
        for bucket, records in organized_data.items():
            filename = bucket.replace('<', '').replace('>', '').replace(':', '_') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 14] Organizing by discovery time...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_time_buckets']} unique time buckets")
        for bucket, count in sorted(summary['time_buckets'].items())[:5]:
            print(f"    - {bucket}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_14_by_discovery_time'
    organizer = ByDiscoveryTimeOrganizer(output_dir)
    organizer.run(loader)
