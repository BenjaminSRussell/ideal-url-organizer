"""
Method 04: Organization by Path Structure
Groups URLs by their top-level path (first path segment)
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json
import hashlib

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByPathStructureOrganizer:
    """Organize URLs by path structure"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def safe_filename(self, name: str, max_length: int = 200) -> str:
        """
        Create a safe filename from a path segment.
        Handles extremely long paths by truncating and adding hash.

        Args:
            name: The path segment
            max_length: Maximum filename length (default 200, well under OS limit of 255)

        Returns:
            Safe filename string
        """
        # Sanitize special characters
        safe_name = name.replace('/', '_').replace('.', '_').replace('<', '').replace('>', '')

        # If within limit, return as-is
        if len(safe_name) <= max_length:
            return safe_name + '.jsonl'

        # For very long names, truncate and add hash for uniqueness
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:8]
        truncated = safe_name[:max_length-9]  # Leave room for hash and underscore
        return f"{truncated}_{hash_suffix}.jsonl"

    def organize(self, records: List[URLRecord]) -> Dict[str, List[URLRecord]]:
        """
        Group URLs by first path segment

        Args:
            records: List of URL records

        Returns:
            Dictionary mapping path -> list of records
        """
        organized = defaultdict(list)

        for record in records:
            components = self.parser.extract_components(record.url)
            path_segments = components['path_segments']

            if path_segments:
                # Use first path segment
                key = path_segments[0]
            else:
                # Root path
                key = '<root>'

            organized[key].append(record)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[URLRecord]]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_path_structure',
            'total_paths': len(organized_data),
            'paths': {
                path: len(records)
                for path, records in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each path's URLs to separate file
        for path, records in organized_data.items():
            # Use safe filename generation (handles very long paths)
            filename = self.safe_filename(path)
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 04] Organizing by path structure...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_paths']} unique path structures")
        for path, count in summary['paths'].items():
            print(f"    - /{path}: {count} URLs")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_04_by_path_structure'
    organizer = ByPathStructureOrganizer(output_dir)
    organizer.run(loader)
