"""
Method 12: Organization by Content Type
Groups URLs by content-type (if available)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord


class ByContentTypeOrganizer:
    """Organize URLs by content type"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by content type

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping content type -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            content_type = record.content_type if record.content_type else '<not_crawled>'
            # Simplify content type (remove charset, etc.)
            if content_type != '<not_crawled>' and ';' in content_type:
                content_type = content_type.split(';')[0].strip()

            organized[content_type].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_content_type',
            'total_content_types': len(organized_data),
            'content_types': {
                ct: len(records)
                for ct, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each content type's URLs to separate file
        for content_type, records in organized_data.items():
            # Sanitize content type for filename
            filename = content_type.replace('/', '_').replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 12] Organizing by content type...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_content_types']} unique content types")
        for ct, count in summary['content_types'].items():
            print(f"    - {ct}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_12_by_content_type'
    organizer = ByContentTypeOrganizer(output_dir)
    organizer.run(loader)
