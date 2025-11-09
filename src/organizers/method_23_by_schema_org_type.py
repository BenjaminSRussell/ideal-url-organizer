"""
Method 23: Organization by Schema.org Type
Groups URLs by their structured data types (Course, Person, Event, etc.)

This is the GOLDMINE for semantic categorization!
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.web_crawler import PageContent


class BySchemaOrgTypeOrganizer:
    """Organize URLs by Schema.org structured data types"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize(self, pages: List[PageContent]) -> Dict[str, List[PageContent]]:
        """Group pages by Schema.org types"""
        organized = defaultdict(list)

        for page in pages:
            if page.schema_org_types:
                for schema_type in page.schema_org_types:
                    organized[schema_type].append(page)
            else:
                organized['<no_structured_data>'].append(page)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[PageContent]]):
        """Save organized data"""
        summary = {
            'method': 'by_schema_org_type',
            'total_types': len(organized_data),
            'schema_org_types': {
                schema_type: len(pages)
                for schema_type, pages in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each type group
        for schema_type, pages in organized_data.items():
            filename = schema_type.replace('/', '_').replace('<', '').replace('>', '') + '.json'
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                json.dump([p.to_dict() for p in pages], f, indent=2)

        return summary

    def run(self, pages: List[PageContent]):
        """Run the organization method"""
        print(f"[Method 23] Organizing by Schema.org types...")
        organized = self.organize(pages)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_types']} unique Schema.org types")
        for schema_type, count in list(summary['schema_org_types'].items())[:10]:
            print(f"    - {schema_type}: {count} pages")

        return summary
