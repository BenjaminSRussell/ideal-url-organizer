"""Data quality analysis for URL records"""
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import json

from src.core.data_loader import DataLoader, URLRecord
from src.core.url_parser import URLParser


class DataQualityAnalyzer:
    """Data quality analysis"""

    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'analysis'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = URLParser()

    def analyze(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Perform data quality analysis"""
        print("\nData Quality Analysis")

        analysis = {
            'overview': self._analyze_overview(records),
            'completeness': self._analyze_completeness(records),
            'url_quality': self._analyze_url_quality(records),
            'relationships': self._analyze_relationships(records),
            'temporal_analysis': self._analyze_temporal(records),
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

        analysis['strengths'], analysis['weaknesses'], analysis['recommendations'] = \
            self._identify_strengths_weaknesses(analysis, records)

        return analysis

    def _analyze_overview(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Basic overview statistics"""
        print("\n[Overview]")

        overview = {
            'total_records': len(records),
            'unique_urls': len(set(r.url for r in records)),
            'unique_normalized_urls': len(set(r.url_normalized for r in records)),
            'unique_domains': len(set(self.parser.parse(r.url).hostname for r in records)),
            'depth_range': {
                'min': min(r.depth for r in records) if records else 0,
                'max': max(r.depth for r in records) if records else 0,
                'avg': sum(r.depth for r in records) / len(records) if records else 0
            }
        }

        print(f"  Total records: {overview['total_records']}")
        print(f"  Unique URLs: {overview['unique_urls']}")
        print(f"  Unique domains: {overview['unique_domains']}")
        print(f"  Depth range: {overview['depth_range']['min']}-{overview['depth_range']['max']}")

        return overview

    def _analyze_completeness(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Analyze field completeness"""
        print("\n[Data Completeness]")

        fields = [
            'url', 'url_normalized', 'depth', 'parent_url', 'discovered_at',
            'queued_at', 'crawled_at', 'response_time_ms', 'status_code',
            'content_type', 'content_length', 'title', 'link_count'
        ]

        completeness = {}
        for field in fields:
            non_null = sum(1 for r in records if getattr(r, field) is not None and getattr(r, field) != [])
            percentage = (non_null / len(records) * 100) if records else 0
            completeness[field] = {
                'count': non_null,
                'percentage': percentage
            }

        # Print key completeness metrics
        for field in ['crawled_at', 'status_code', 'content_type', 'title']:
            print(f"  {field}: {completeness[field]['percentage']:.1f}% complete")

        return completeness

    def _analyze_url_quality(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Analyze URL quality"""
        print("\n[URL Quality]")

        protocols = Counter()
        ports = Counter()
        file_extensions = Counter()
        url_lengths = []

        for record in records:
            parsed = self.parser.parse(record.url)
            protocols[parsed.scheme] += 1
            ports[parsed.port or 'default'] += 1
            url_lengths.append(len(record.url))

            # Check file extension
            if '.' in parsed.path:
                ext = parsed.path.rsplit('.', 1)[-1].split('?')[0]
                if len(ext) <= 6 and ext.isalnum():
                    file_extensions[ext] += 1

        quality = {
            'protocols': dict(protocols),
            'ports': dict(ports),
            'file_extensions': dict(file_extensions.most_common(10)),
            'url_length': {
                'min': min(url_lengths) if url_lengths else 0,
                'max': max(url_lengths) if url_lengths else 0,
                'avg': sum(url_lengths) / len(url_lengths) if url_lengths else 0
            },
            'issues': []
        }

        # Check for issues
        http_count = protocols.get('http', 0)
        if http_count > 0:
            quality['issues'].append(f"{http_count} URLs use insecure HTTP protocol")

        print(f"  Protocols: {dict(protocols)}")
        print(f"  Average URL length: {quality['url_length']['avg']:.1f}")
        print(f"  Issues found: {len(quality['issues'])}")

        return quality

    def _analyze_relationships(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Analyze parent-child relationships"""
        print("\n[Relationships]")

        orphans = sum(1 for r in records if not r.parent_url)
        has_parent = len(records) - orphans

        # Build parent map
        parent_map = {}
        for record in records:
            if record.parent_url:
                parent_map[record.parent_url] = parent_map.get(record.parent_url, 0) + 1

        relationships = {
            'orphan_count': orphans,
            'has_parent_count': has_parent,
            'unique_parents': len(parent_map),
            'most_prolific_parents': sorted(
                [(url, count) for url, count in parent_map.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

        print(f"  Orphan URLs (no parent): {orphans}")
        print(f"  URLs with parent: {has_parent}")
        print(f"  Unique parent URLs: {relationships['unique_parents']}")

        return relationships

    def _analyze_temporal(self, records: List[URLRecord]) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        print("\n[Temporal Analysis]")

        discovered_times = [r.discovered_at for r in records if r.discovered_at]
        queued_times = [r.queued_at for r in records if r.queued_at]
        crawled_times = [r.crawled_at for r in records if r.crawled_at]

        temporal = {
            'discovery_span_seconds': (max(discovered_times) - min(discovered_times)) if discovered_times else 0,
            'crawled_count': len(crawled_times),
            'not_crawled_count': len(records) - len(crawled_times),
            'crawl_rate': (len(crawled_times) / len(records) * 100) if records else 0
        }

        print(f"  Crawled: {temporal['crawled_count']} ({temporal['crawl_rate']:.1f}%)")
        print(f"  Not crawled: {temporal['not_crawled_count']}")

        return temporal

    def _identify_strengths_weaknesses(self, analysis: Dict, records: List[URLRecord]) -> tuple:
        """Identify strengths and weaknesses"""
        print("\n[Analysis Summary]")

        strengths = []
        weaknesses = []
        recommendations = []

        # Strengths
        if analysis['completeness']['discovered_at']['percentage'] == 100:
            strengths.append("All URLs have discovery timestamps")

        if analysis['completeness']['queued_at']['percentage'] == 100:
            strengths.append("All URLs have queue timestamps")

        if analysis['overview']['unique_urls'] == analysis['overview']['total_records']:
            strengths.append("No duplicate URLs in dataset")

        if len(analysis['url_quality']['protocols']) == 1:
            strengths.append("Consistent protocol usage across all URLs")

        # Weaknesses
        if analysis['temporal_analysis']['crawl_rate'] == 0:
            weaknesses.append("No URLs have been crawled yet (all crawled_at timestamps are null)")
            recommendations.append("Begin crawling queued URLs to populate response data")

        if analysis['completeness']['content_type']['percentage'] < 10:
            weaknesses.append(f"Content-type data is {analysis['completeness']['content_type']['percentage']:.1f}% complete")

        if analysis['completeness']['title']['percentage'] < 10:
            weaknesses.append(f"Title data is {analysis['completeness']['title']['percentage']:.1f}% complete")
            recommendations.append("Extract page titles during crawling for better content analysis")

        if 'http' in analysis['url_quality']['protocols']:
            weaknesses.append("Some URLs use insecure HTTP protocol")
            recommendations.append("Consider upgrading HTTP URLs to HTTPS where possible")

        # Print summary
        print(f"\n✓ STRENGTHS ({len(strengths)}):")
        for strength in strengths:
            print(f"  • {strength}")

        print(f"\n✗ WEAKNESSES ({len(weaknesses)}):")
        for weakness in weaknesses:
            print(f"  • {weakness}")

        print(f"\n→ RECOMMENDATIONS ({len(recommendations)}):")
        for rec in recommendations:
            print(f"  • {rec}")

        return strengths, weaknesses, recommendations

    def save(self, analysis: Dict[str, Any]):
        """Save analysis results"""
        output_path = self.output_dir / 'data_quality_report.json'

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n✓ Analysis saved to: {output_path}")

        # Also save a human-readable report
        self._save_readable_report(analysis)

    def _save_readable_report(self, analysis: Dict[str, Any]):
        """Save human-readable markdown report"""
        output_path = self.output_dir / 'data_quality_report.md'

        with open(output_path, 'w') as f:
            f.write("# Data Quality Analysis Report\n\n")

            f.write("## Overview\n\n")
            for key, value in analysis['overview'].items():
                f.write(f"- **{key}**: {value}\n")

            f.write("\n## Strengths\n\n")
            for strength in analysis['strengths']:
                f.write(f"✓ {strength}\n\n")

            f.write("\n## Weaknesses\n\n")
            for weakness in analysis['weaknesses']:
                f.write(f"✗ {weakness}\n\n")

            f.write("\n## Recommendations\n\n")
            for rec in analysis['recommendations']:
                f.write(f"→ {rec}\n\n")

        print(f"✓ Readable report saved to: {output_path}")

    def run(self, data_loader: DataLoader):
        """Run full analysis"""
        records = data_loader.load()
        analysis = self.analyze(records)
        self.save(analysis)
        return analysis


if __name__ == '__main__':
    from src.core.data_loader import DataLoader

    loader = DataLoader()
    analyzer = DataQualityAnalyzer()
    analyzer.run(loader)
