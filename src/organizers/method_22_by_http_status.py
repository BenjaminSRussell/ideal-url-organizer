"""
Method 22: Organization by HTTP Status Code
Groups URLs by their HTTP status code (200, 301, 404, 500, etc.)

This reveals link rot and site health issues
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

from src.core.web_crawler import PageContent


class ByHTTPStatusOrganizer:
    """Organize URLs by HTTP status code"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize(self, pages: List[PageContent]) -> Dict[str, List[PageContent]]:
        """Group pages by HTTP status code"""
        organized = defaultdict(list)

        for page in pages:
            status_code = page.status_code
            status_category = self._categorize_status(status_code)
            organized[status_category].append(page)

        return dict(organized)

    def _categorize_status(self, code: int) -> str:
        """Categorize status code"""
        if 200 <= code < 300:
            return f"2xx_success_{code}"
        elif 300 <= code < 400:
            return f"3xx_redirect_{code}"
        elif 400 <= code < 500:
            return f"4xx_client_error_{code}"
        elif 500 <= code < 600:
            return f"5xx_server_error_{code}"
        else:
            return f"other_{code}"

    def save(self, organized_data: Dict[str, List[PageContent]]):
        """Save organized data"""
        summary = {
            'method': 'by_http_status',
            'total_status_codes': len(organized_data),
            'status_distribution': {
                status: len(pages)
                for status, pages in organized_data.items()
            },
            'health_metrics': self._calculate_health_metrics(organized_data)
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each status group
        for status, pages in organized_data.items():
            filepath = self.output_dir / f'{status}.json'
            with open(filepath, 'w') as f:
                json.dump([p.to_dict() for p in pages], f, indent=2)

        return summary

    def _calculate_health_metrics(self, organized_data: Dict[str, List[PageContent]]) -> Dict:
        """Calculate site health metrics"""
        total = sum(len(pages) for pages in organized_data.values())

        success = sum(len(pages) for status, pages in organized_data.items() if status.startswith('2xx'))
        redirects = sum(len(pages) for status, pages in organized_data.items() if status.startswith('3xx'))
        client_errors = sum(len(pages) for status, pages in organized_data.items() if status.startswith('4xx'))
        server_errors = sum(len(pages) for status, pages in organized_data.items() if status.startswith('5xx'))

        return {
            'success_rate': (success / total * 100) if total > 0 else 0,
            'redirect_rate': (redirects / total * 100) if total > 0 else 0,
            'error_rate': ((client_errors + server_errors) / total * 100) if total > 0 else 0,
            'link_rot': client_errors,  # 404s indicate broken links
        }

    def run(self, pages: List[PageContent]):
        """Run the organization method"""
        print(f"[Method 22] Organizing by HTTP status...")
        organized = self.organize(pages)
        summary = self.save(organized)

        print(f"  ✓ Found {summary['total_status_codes']} unique status codes")
        print(f"  ✓ Site health: {summary['health_metrics']['success_rate']:.1f}% success")
        print(f"  ✓ Link rot: {summary['health_metrics']['link_rot']} broken links")

        return summary
