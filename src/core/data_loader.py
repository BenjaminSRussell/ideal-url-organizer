"""
Data loader for URL organizer
Loads JSONL data files and provides data access
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Iterator
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class URLRecord:
    """
    Data structure for a single URL record
    Matches the JSONL schema
    """
    schema_version: int
    url: str
    url_normalized: str
    depth: int
    parent_url: str
    fragments: List[str]
    discovered_at: int
    queued_at: int
    crawled_at: int = None
    response_time_ms: int = None
    status_code: int = None
    content_type: str = None
    content_length: int = None
    title: str = None
    link_count: int = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'URLRecord':
        """Create URLRecord from dictionary"""
        return cls(**data)

    def get_discovered_datetime(self) -> datetime:
        """Get discovery time as datetime object"""
        if self.discovered_at:
            return datetime.fromtimestamp(self.discovered_at)
        return None

    def get_queued_datetime(self) -> datetime:
        """Get queue time as datetime object"""
        if self.queued_at:
            return datetime.fromtimestamp(self.queued_at)
        return None

    def get_crawled_datetime(self) -> datetime:
        """Get crawl time as datetime object"""
        if self.crawled_at:
            return datetime.fromtimestamp(self.crawled_at)
        return None

    def is_crawled(self) -> bool:
        """Check if URL has been crawled"""
        return self.crawled_at is not None


class DataLoader:
    """
    Loader for URL data in JSONL format
    """

    def __init__(self, data_path: str = None):
        """
        Initialize data loader

        Args:
            data_path: Path to JSONL file, defaults to data/raw/urls.jsonl
        """
        if data_path is None:
            project_root = Path(__file__).parent.parent.parent
            data_path = project_root / "data" / "raw" / "urls.jsonl"

        self.data_path = Path(data_path)

    def load_raw(self) -> List[Dict[str, Any]]:
        """
        Load raw data as list of dictionaries

        Returns:
            List of URL records as dicts
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        data = []
        with open(self.data_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))

        return data

    def load(self) -> List[URLRecord]:
        """
        Load data as list of URLRecord objects

        Returns:
            List of URLRecord objects
        """
        raw_data = self.load_raw()
        return [URLRecord.from_dict(record) for record in raw_data]

    def iter_records(self) -> Iterator[URLRecord]:
        """
        Iterate over records (memory efficient for large files)

        Yields:
            URLRecord objects one at a time
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        with open(self.data_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield URLRecord.from_dict(json.loads(line))

    def get_record_count(self) -> int:
        """Get total number of records"""
        count = 0
        if self.data_path.exists():
            with open(self.data_path, 'r') as f:
                for line in f:
                    if line.strip():
                        count += 1
        return count

    def save(self, records: List[URLRecord], output_path: Path):
        """
        Save records to JSONL file

        Args:
            records: List of URLRecord objects
            output_path: Path to save file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            for record in records:
                f.write(json.dumps(record.to_dict()) + '\n')

    def save_json(self, data: Any, output_path: Path):
        """
        Save data as pretty-printed JSON

        Args:
            data: Data to save
            output_path: Path to save file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    # Test data loader
    loader = DataLoader()

    print(f"Loading data from: {loader.data_path}")
    print(f"Total records: {loader.get_record_count()}")

    records = loader.load()
    print(f"\nLoaded {len(records)} records")

    if records:
        print(f"\nFirst record:")
        print(f"  URL: {records[0].url}")
        print(f"  Depth: {records[0].depth}")
        print(f"  Parent: {records[0].parent_url}")
        print(f"  Discovered: {records[0].get_discovered_datetime()}")
