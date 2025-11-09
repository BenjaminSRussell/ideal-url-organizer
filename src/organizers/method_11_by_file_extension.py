"""
Method 11: Organization by File Extension
Groups URLs by file extension (.php, .html, .aspx, etc.) or "no_extension"
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByFileExtensionOrganizer:
    """Organize URLs by file extension"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def get_extension(self, url: str) -> str:
        """Extract file extension from URL path"""
        parsed = self.parser.parse(url)
        path = parsed.path

        # Remove query and fragment
        path = path.split('?')[0].split('#')[0]

        # Get extension
        if '.' in path:
            extension = path.rsplit('.', 1)[-1]
            # Only consider it an extension if it's short (< 6 chars) and alphanumeric
            if len(extension) <= 6 and extension.isalnum():
                return extension

        return '<no_extension>'

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by file extension

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping extension -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            extension = self.get_extension(record.url)
            organized[extension].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_file_extension',
            'total_extensions': len(organized_data),
            'extensions': {
                ext: len(records)
                for ext, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each extension's URLs to separate file
        for extension, records in organized_data.items():
            filename = extension.replace('<', '').replace('>', '') + '.jsonl'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 11] Organizing by file extension...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_extensions']} unique file extensions")
        for ext, count in summary['extensions'].items():
            print(f"    - .{ext}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_11_by_file_extension'
    organizer = ByFileExtensionOrganizer(output_dir)
    organizer.run(loader)
