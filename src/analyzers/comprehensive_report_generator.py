"""
Comprehensive Report Generator

Creates a professional intelligence report combining all analyses
"""
from typing import Dict, List, Any
from pathlib import Path
import json
from datetime import datetime

from src.core.data_loader import DataLoader, URLRecord
from src.core.web_crawler import PageContent
from src.analyzers.data_quality_analyzer import DataQualityAnalyzer
from src.analyzers.link_graph_analyzer import LinkGraphAnalyzer
from src.analyzers.semantic_analyzer import SemanticAnalyzer
from src.analyzers.advanced_analytics import AdvancedAnalytics


class ComprehensiveReportGenerator:
    """
    Generate comprehensive website intelligence report
    """

    def __init__(self, output_dir: Path = None):
        """Initialize report generator"""
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'results' / 'reports'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_analysis_results(self, analysis_dir: Path) -> Dict[str, Any]:
        """Load analysis results from JSON files"""
        results = {}

        # Try to load each analysis type
        analysis_files = {
            'data_quality': 'data_quality_report.json',
            'link_graph': 'link_graph/link_graph_analysis.json',
            'semantic': 'semantic/semantic_analysis.json',
            'advanced': 'advanced/advanced_analytics.json'
        }

        for key, filename in analysis_files.items():
            filepath = analysis_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        results[key] = json.load(f)
                except Exception as e:
                    print(f"  Warning: Could not load {key} analysis: {e}")

        return results

    def _generate_executive_summary(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        summary = {
            'report_date': datetime.now().isoformat(),
            'analyses_included': list(analyses.keys()),
            'top_insights': [],
            'top_recommendations': []
        }

        # Extract insights from each analysis
        insights = []

        # Data quality insights
        if 'data_quality' in analyses:
            dq = analyses['data_quality']
            if dq.get('overview'):
                insights.append(f"Dataset contains {dq['overview'].get('total_records', 0)} URLs across {dq['overview'].get('unique_domains', 0)} domains")

            if dq.get('weaknesses'):
                for weakness in dq['weaknesses'][:2]:
                    insights.append(f"Data quality: {weakness}")

        # Link graph insights
        if 'link_graph' in analyses:
            lg = analyses['link_graph']
            if lg.get('graph_stats'):
                stats = lg['graph_stats']
                insights.append(f"Link structure: {stats.get('num_nodes', 0)} pages, {stats.get('num_edges', 0)} internal links")

            if lg.get('centrality', {}).get('top_betweenness'):
                insights.append(f"Identified {min(3, len(lg['centrality']['top_betweenness']))} critical bridge pages")

            if lg.get('communities', {}).get('total_communities'):
                insights.append(f"Found {lg['communities']['total_communities']} content communities/silos")

        # Semantic insights
        if 'semantic' in analyses:
            sem = analyses['semantic']
            if sem.get('clusters', {}).get('total_clusters'):
                insights.append(f"Detected {sem['clusters']['total_clusters']} semantic clusters indicating content redundancy")

            if sem.get('entities', {}).get('entity_types'):
                insights.append(f"Extracted {len(sem['entities']['entity_types'])} types of named entities")

            if sem.get('topics', {}).get('num_topics'):
                insights.append(f"Discovered {sem['topics']['num_topics']} main topics across content")

        # Advanced analytics insights
        if 'advanced' in analyses:
            adv = analyses['advanced']
            if adv.get('discovery_timeline'):
                trend = adv['discovery_timeline'].get('trend', 'unknown')
                insights.append(f"URL discovery trend: {trend}")

            if adv.get('page_classification', {}).get('type_distribution'):
                insights.append(f"Classified pages into {len(adv['page_classification']['type_distribution'])} types")

        # Generate recommendations
        recommendations = []

        # Link structure recommendations
        if 'link_graph' in analyses:
            lg = analyses['link_graph']
            if lg.get('page_types', {}).get('orphan'):
                recommendations.append(f"Found {lg['page_types'].get('orphan', 0)} orphan pages with no internal links - add internal linking")

            if lg.get('centrality', {}).get('top_betweenness'):
                recommendations.append("Prioritize updates to critical bridge pages identified by betweenness centrality")

        # Content recommendations
        if 'semantic' in analyses:
            sem = analyses['semantic']
            if sem.get('clusters', {}).get('clusters'):
                largest_clusters = sem['clusters']['clusters'][:3]
                for cluster in largest_clusters:
                    if cluster['size'] > 2:
                        recommendations.append(f"Consolidate semantic cluster {cluster['id']} ({cluster['size']} similar pages) into pillar page")

        # Add top insights and recommendations
        summary['top_insights'] = insights[:5]
        summary['top_recommendations'] = recommendations[:5]

        return summary

    def _generate_data_overview(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data and crawl overview section"""
        overview = {
            'basic_stats': {},
            'data_completeness': {},
            'temporal_analysis': {}
        }

        if 'data_quality' in analyses:
            dq = analyses['data_quality']
            if dq.get('overview'):
                overview['basic_stats'] = dq['overview']
            if dq.get('completeness'):
                # Select key completeness metrics
                key_fields = ['crawled_at', 'status_code', 'content_type', 'title']
                overview['data_completeness'] = {
                    field: dq['completeness'].get(field, {})
                    for field in key_fields
                }

        if 'advanced' in analyses:
            adv = analyses['advanced']
            if adv.get('discovery_timeline'):
                overview['temporal_analysis'] = adv['discovery_timeline']

        return overview

    def _generate_architecture_section(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate website architecture and link structure section"""
        architecture = {
            'key_hubs_authorities': {},
            'centrality_analysis': {},
            'community_structure': {}
        }

        if 'link_graph' in analyses:
            lg = analyses['link_graph']

            # HITS results
            if lg.get('hits'):
                architecture['key_hubs_authorities'] = {
                    'top_hubs': lg['hits'].get('top_hubs', [])[:5],
                    'top_authorities': lg['hits'].get('top_authorities', [])[:5]
                }

            # Centrality
            if lg.get('centrality'):
                architecture['centrality_analysis'] = {
                    'top_in_degree': lg['centrality'].get('top_in_degree', [])[:5],
                    'top_betweenness': lg['centrality'].get('top_betweenness', [])[:5],
                    'top_closeness': lg['centrality'].get('top_closeness', [])[:5]
                }

            # Communities
            if lg.get('communities'):
                communities = lg['communities']
                architecture['community_structure'] = {
                    'total_communities': communities.get('total_communities', 0),
                    'modularity': communities.get('modularity', 0),
                    'top_communities': communities.get('communities', [])[:3]
                }

        return architecture

    def _generate_semantic_section(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate semantic content analysis section"""
        semantic = {
            'main_topics': {},
            'topic_distribution': {},
            'content_redundancy': {},
            'key_entities': {},
            'sentiment_analysis': {}
        }

        if 'semantic' in analyses:
            sem = analyses['semantic']

            # Topics
            if sem.get('topics'):
                topics = sem['topics']
                semantic['main_topics'] = {
                    'total_topics': topics.get('num_topics', 0),
                    'topics': topics.get('topics', [])
                }
                if topics.get('section_distribution'):
                    semantic['topic_distribution'] = topics['section_distribution']

            # Content redundancy
            if sem.get('clusters'):
                semantic['content_redundancy'] = {
                    'total_clusters': sem['clusters'].get('total_clusters', 0),
                    'clusters': sem['clusters'].get('clusters', [])[:5]
                }

            # Entities
            if sem.get('entities'):
                ents = sem['entities']
                semantic['key_entities'] = {
                    'entity_types': ents.get('entity_types', []),
                    'top_entities_by_type': ents.get('top_entities_by_type', {})
                }

            # Sentiment
            if sem.get('sentiment'):
                semantic['sentiment_analysis'] = sem['sentiment']

        return semantic

    def _generate_insights_section(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights and recommendations"""
        insights = {
            'content_strategy': [],
            'technical_seo': [],
            'architecture_optimization': [],
            'redundancy_mitigation': []
        }

        # Content strategy insights
        if 'semantic' in analyses:
            sem = analyses['semantic']
            if sem.get('topics'):
                insights['content_strategy'].append(
                    "Ensure content strategy aligns with discovered topic distribution across site sections"
                )

        # Technical SEO insights
        if 'link_graph' in analyses:
            lg = analyses['link_graph']
            if lg.get('page_types', {}).get('orphan'):
                insights['technical_seo'].append(
                    f"Fix {lg['page_types'].get('orphan', 0)} orphan pages by adding internal links"
                )

            if lg.get('centrality', {}).get('top_betweenness'):
                insights['technical_seo'].append(
                    "Strengthen internal linking structure to critical bridge pages"
                )

        # Architecture optimization
        if 'link_graph' in analyses and 'data_quality' in analyses:
            lg = analyses['link_graph']
            if lg.get('graph_stats', {}).get('num_edges'):
                insights['architecture_optimization'].append(
                    "Optimize link distribution across site hierarchy"
                )

        # Redundancy mitigation
        if 'semantic' in analyses:
            sem = analyses['semantic']
            if sem.get('clusters', {}).get('clusters'):
                insights['redundancy_mitigation'].append(
                    "Consolidate semantically similar pages to reduce content cannibalization"
                )

        return insights

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive intelligence report

        Returns:
            Complete report dictionary
        """
        print("\nGenerating Comprehensive Website Intelligence Report")

        project_root = Path(__file__).parent.parent.parent
        analysis_dir = project_root / 'data' / 'results' / 'analysis'

        # Load all analyses
        print("\nLoading analysis results...")
        analyses = self._load_analysis_results(analysis_dir)
        print(f"  [+] Loaded {len(analyses)} analysis components")

        # Generate sections
        report = {
            'metadata': {
                'title': 'Comprehensive Website Intelligence Report',
                'generated_date': datetime.now().isoformat(),
                'components': list(analyses.keys())
            },
            'executive_summary': self._generate_executive_summary(analyses),
            'data_overview': self._generate_data_overview(analyses),
            'architecture': self._generate_architecture_section(analyses),
            'semantic_analysis': self._generate_semantic_section(analyses),
            'actionable_insights': self._generate_insights_section(analyses)
        }

        return report

    def save_report(self, report: Dict[str, Any]) -> Path:
        """
        Save comprehensive report to JSON and markdown

        Args:
            report: Report dictionary

        Returns:
            Path to saved report
        """
        # Save JSON report
        json_path = self.output_dir / 'comprehensive_intelligence_report.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n[+] Comprehensive report saved to: {json_path}")

        # Generate and save markdown report
        md_path = self.output_dir / 'comprehensive_intelligence_report.md'
        self._save_markdown_report(report, md_path)
        print(f"[+] Markdown report saved to: {md_path}")

        return json_path

    def _save_markdown_report(self, report: Dict[str, Any], filepath: Path):
        """Save report as formatted markdown"""
        with open(filepath, 'w') as f:
            f.write("# Comprehensive Website Intelligence Report\n\n")

            # Metadata
            f.write(f"**Generated:** {report['metadata']['generated_date']}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            es = report['executive_summary']
            f.write("### Top Insights\n\n")
            for i, insight in enumerate(es['top_insights'], 1):
                f.write(f"{i}. {insight}\n")
            f.write("\n### Top Recommendations\n\n")
            for i, rec in enumerate(es['top_recommendations'], 1):
                f.write(f"{i}. {rec}\n\n")

            # Data Overview
            f.write("## Data & Crawl Overview\n\n")
            do = report['data_overview']
            if do['basic_stats']:
                f.write("### Basic Statistics\n\n")
                for key, value in do['basic_stats'].items():
                    f.write(f"- **{key}**: {value}\n")
                f.write("\n")

            # Architecture
            f.write("## Website Architecture & Link Structure\n\n")
            arch = report['architecture']
            if arch['centrality_analysis']:
                f.write("### Key Central Pages\n\n")
                if arch['centrality_analysis'].get('top_in_degree'):
                    f.write("**Most Linked Pages (In-Degree):**\n")
                    for item in arch['centrality_analysis']['top_in_degree'][:3]:
                        f.write(f"- {item['url']} (links: {item['degree']})\n")
                    f.write("\n")

            if arch['community_structure']:
                f.write("### Content Communities\n\n")
                f.write(f"Found **{arch['community_structure'].get('total_communities', 0)}** content communities\n\n")

            # Semantic Analysis
            f.write("## Semantic Content Analysis\n\n")
            sem = report['semantic_analysis']
            if sem['main_topics']:
                f.write(f"### Main Topics\n\n")
                f.write(f"Discovered **{sem['main_topics'].get('total_topics', 0)}** main topics\n\n")

            if sem['content_redundancy']:
                f.write(f"### Content Redundancy\n\n")
                f.write(f"Found **{sem['content_redundancy'].get('total_clusters', 0)}** semantic clusters (similar pages)\n\n")

            # Insights
            f.write("## Actionable Insights\n\n")
            insights = report['actionable_insights']

            if insights['content_strategy']:
                f.write("### Content Strategy\n\n")
                for insight in insights['content_strategy']:
                    f.write(f"- {insight}\n")
                f.write("\n")

            if insights['technical_seo']:
                f.write("### Technical SEO\n\n")
                for insight in insights['technical_seo']:
                    f.write(f"- {insight}\n")
                f.write("\n")

            if insights['redundancy_mitigation']:
                f.write("### Redundancy Mitigation\n\n")
                for insight in insights['redundancy_mitigation']:
                    f.write(f"- {insight}\n")
                f.write("\n")

    def run(self) -> Dict[str, Any]:
        """Run complete report generation"""
        report = self.generate_comprehensive_report()
        self.save_report(report)
        return report


if __name__ == '__main__':
    generator = ComprehensiveReportGenerator()
    generator.run()
