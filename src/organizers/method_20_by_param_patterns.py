"""
Method 20: Organization by Query Parameter Patterns
Groups URLs by specific parameter patterns (catoid, poid, etc.)
"""
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class ByParamPatternsOrganizer:
    """Organize URLs by parameter patterns"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

        # Track specific parameters of interest
        self.tracked_params = ['catoid', 'poid', 'ent_oid', 'coid', 'returnto', 'hl']

    def get_param_pattern(self, url: str) -> Dict[str, str]:
        """Extract tracked parameter values"""
        components = self.parser.extract_components(url)
        query_params = components['query_params']

        pattern = {}
        for param in self.tracked_params:
            if param in query_params:
                values = query_params[param]
                # Use first value if multiple
                pattern[param] = values[0] if values else None

        return pattern

    def organize(self, records: List[URLRecord]) -> Dict[str, Any]:
        """
        Group URLs by parameter patterns

        Args:
            records: List of URL records

        Returns:
            Dictionary with various param-based groupings
        """
        # Group by presence of each param
        by_param_presence = defaultdict(list)

        # Group by param values
        by_catoid = defaultdict(list)
        by_poid = defaultdict(list)

        for record in records:
            pattern = self.get_param_pattern(record.url)

            # By presence
            present_params = sorted(pattern.keys())
            if present_params:
                key = ','.join(present_params)
            else:
                key = '<no_tracked_params>'
            by_param_presence[key].append(record)

            # By specific param values
            if 'catoid' in pattern:
                by_catoid[f'catoid_{pattern["catoid"]}'].append(record)

            if 'poid' in pattern:
                by_poid[f'poid_{pattern["poid"]}'].append(record)

        return {
            'by_param_presence': dict(by_param_presence),
            'by_catoid': dict(by_catoid),
            'by_poid': dict(by_poid)
        }

    def save(self, organized_data: Dict[str, Any]):
        """Save organized data to files"""
        # Save summary
        summary = {
            'method': 'by_param_patterns',
            'param_presence_groups': len(organized_data['by_param_presence']),
            'catoid_values': len(organized_data['by_catoid']),
            'poid_values': len(organized_data['by_poid'])
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save param presence groups
        param_presence_dir = self.output_dir / 'param_presence'
        param_presence_dir.mkdir(exist_ok=True)

        for pattern, records in organized_data['by_param_presence'].items():
            filename = pattern.replace(',', '_').replace('<', '').replace('>', '') + '.jsonl'
            with open(param_presence_dir / filename, 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        # Save catoid groups
        catoid_dir = self.output_dir / 'by_catoid'
        catoid_dir.mkdir(exist_ok=True)

        for catoid, records in organized_data['by_catoid'].items():
            with open(catoid_dir / f'{catoid}.jsonl', 'w') as f:
                for record in records:
                    f.write(json.dumps(record.to_dict()) + '\n')

        return summary

    def run(self, data_loader: DataLoader):
        """Run the organization method"""
        print(f"[Method 20] Organizing by parameter patterns...")
        records = data_loader.load()
        organized = self.organize(records)
        summary = self.save(organized)

        print(f"  ✓ Parameter presence groups: {summary['param_presence_groups']}")
        print(f"  ✓ Unique catoid values: {summary['catoid_values']}")
        print(f"  ✓ Unique poid values: {summary['poid_values']}")

        return summary


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'method_20_by_param_patterns'
    organizer = ByParamPatternsOrganizer(output_dir)
    organizer.run(loader)
