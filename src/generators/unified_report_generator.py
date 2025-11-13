"""
Unified Report Generator

Generates a single, comprehensive HTML report combining all analysis results.
Replaces scattered JSON/MD files with one beautiful, interactive report.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import base64
from jinja2 import Template


class UnifiedReportGenerator:
    """
    Generate unified HTML report from all analysis components
    """

    def __init__(self, output_dir: Path = None):
        """Initialize unified report generator"""
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'results' / 'unified_reports'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Paths to analysis results
        self.project_root = Path(__file__).parent.parent.parent
        self.analysis_dir = self.project_root / 'data' / 'results' / 'analysis'
        self.viz_dir = self.project_root / 'data' / 'results' / 'visualizations'
        self.template_dir = self.project_root / 'src' / 'templates'

    def _load_json_file(self, filepath: Path) -> Optional[Dict]:
        """Load JSON file if it exists"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"  Warning: Could not load {filepath.name}: {e}")
        return None

    def _load_all_analysis_data(self) -> Dict[str, Any]:
        """Load all analysis results from JSON files"""
        print("\n[1/5] Loading analysis data...")

        data = {}

        # Data quality
        dq_path = self.analysis_dir / 'data_quality_report.json'
        if dq_file := self._load_json_file(dq_path):
            data['data_quality'] = dq_file
            print("  [+] Loaded data quality analysis")

        # Advanced analytics
        adv_path = self.analysis_dir / 'advanced' / 'advanced_analytics.json'
        if adv_file := self._load_json_file(adv_path):
            data['advanced'] = adv_file
            print("  [+] Loaded advanced analytics")

        # Link graph
        lg_path = self.analysis_dir / 'link_graph' / 'link_graph_analysis.json'
        if lg_file := self._load_json_file(lg_path):
            data['link_graph'] = lg_file
            print("  [+] Loaded link graph analysis")

        # Semantic analysis
        sem_path = self.analysis_dir / 'semantic' / 'semantic_analysis.json'
        if sem_file := self._load_json_file(sem_path):
            data['semantic'] = sem_file
            print("  [+] Loaded semantic analysis")

        print(f"  [+] Total components loaded: {len(data)}")
        return data

    def _encode_image_to_base64(self, image_path: Path) -> Optional[str]:
        """Encode image file to base64 string"""
        if not image_path.exists():
            return None

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return base64_data
        except Exception as e:
            print(f"  Warning: Could not encode {image_path.name}: {e}")
            return None

    def _load_visualizations(self) -> List[Dict[str, str]]:
        """Load and encode all visualization images"""
        print("\n[2/5] Loading visualizations...")

        visualizations = []

        viz_files = [
            ('depth_distribution.png', 'URL Distribution by Crawl Depth'),
            ('domain_distribution.png', 'URL Distribution by Domain'),
            ('protocol_distribution.png', 'Protocol Distribution (HTTP vs HTTPS)'),
            ('url_length_distribution.png', 'URL Length Distribution'),
            ('crawl_status.png', 'Crawl Status'),
        ]

        for filename, title in viz_files:
            filepath = self.viz_dir / filename
            if base64_data := self._encode_image_to_base64(filepath):
                visualizations.append({
                    'title': title,
                    'filename': filename,
                    'image_base64': base64_data
                })
                print(f"  [+] Encoded {filename}")

        print(f"  [+] Total visualizations: {len(visualizations)}")
        return visualizations

    def _calculate_quality_score(self, data: Dict) -> float:
        """Calculate overall data quality score (0-100)"""
        if 'data_quality' not in data:
            return 0.0

        dq = data['data_quality']
        completeness = dq.get('completeness', {})

        # Average completeness across key fields
        key_fields = ['crawled_at', 'status_code', 'content_type', 'title', 'discovered_at', 'queued_at']
        percentages = [
            completeness.get(field, {}).get('percentage', 0)
            for field in key_fields
            if field in completeness
        ]

        if not percentages:
            return 0.0

        avg_completeness = sum(percentages) / len(percentages)

        # Deduct points for weaknesses
        weaknesses_count = len(dq.get('weaknesses', []))
        deduction = min(weaknesses_count * 5, 20)  # Max 20 points deduction

        score = max(0, avg_completeness - deduction)
        return round(score, 1)

    def _process_executive_summary(self, data: Dict) -> Dict[str, Any]:
        """Process data for executive summary section"""
        summary = {
            'total_urls': 0,
            'total_domains': 0,
            'crawl_coverage': 0.0,
            'avg_depth': 0.0,
            'quality_score': 0.0,
            'top_insights': [],
            'top_recommendations': [],
            'crawled_count': 0,
            'min_depth': 0,
            'max_depth': 0
        }

        # Basic stats from data quality
        if 'data_quality' in data:
            dq = data['data_quality']
            overview = dq.get('overview', {})

            summary['total_urls'] = overview.get('total_records', 0)
            summary['total_domains'] = overview.get('unique_domains', 0)

            depth_range = overview.get('depth_range', {})
            summary['avg_depth'] = round(depth_range.get('avg', 0.0), 1)
            summary['min_depth'] = depth_range.get('min', 0)
            summary['max_depth'] = depth_range.get('max', 0)

            # Crawl coverage
            temporal = dq.get('temporal_analysis', {})
            summary['crawl_coverage'] = round(temporal.get('crawl_rate', 0), 1)
            summary['crawled_count'] = temporal.get('crawled_count', 0)

            # Quality score
            summary['quality_score'] = self._calculate_quality_score(data)

            # Top insights from strengths
            summary['top_insights'] = dq.get('strengths', [])[:5]

            # Top recommendations
            summary['top_recommendations'] = dq.get('recommendations', [])[:5]

        return summary

    def _process_data_overview(self, data: Dict) -> Dict[str, Any]:
        """Process data for data overview section"""
        overview = {
            'total_records': 0,
            'unique_urls': 0,
            'unique_domains': 0,
            'https_count': 0,
            'http_count': 0,
            'avg_url_length': 0,
            'orphan_count': 0,
            'completeness_data': {}
        }

        if 'data_quality' not in data:
            return overview

        dq = data['data_quality']

        # Basic statistics
        dq_overview = dq.get('overview', {})
        overview['total_records'] = dq_overview.get('total_records', 0)
        overview['unique_urls'] = dq_overview.get('unique_urls', 0)
        overview['unique_domains'] = dq_overview.get('unique_domains', 0)

        # URL quality
        url_quality = dq.get('url_quality', {})
        protocols = url_quality.get('protocols', {})
        overview['https_count'] = protocols.get('https', 0)
        overview['http_count'] = protocols.get('http', 0)
        overview['avg_url_length'] = round(url_quality.get('url_length', {}).get('avg', 0), 1)

        # Relationships
        relationships = dq.get('relationships', {})
        overview['orphan_count'] = relationships.get('orphan_count', 0)

        # Completeness data with progress bar classes
        completeness = dq.get('completeness', {})
        for field, metrics in completeness.items():
            percentage = metrics.get('percentage', 0)
            progress_class = 'low' if percentage < 40 else 'medium' if percentage < 70 else 'high'

            overview['completeness_data'][field] = {
                'count': metrics.get('count', 0),
                'percentage': round(percentage, 1),
                'class': progress_class
            }

        return overview

    def _process_data_quality(self, data: Dict) -> Dict[str, Any]:
        """Process data for data quality assessment section"""
        quality = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

        if 'data_quality' in data:
            dq = data['data_quality']
            quality['strengths'] = dq.get('strengths', [])
            quality['weaknesses'] = dq.get('weaknesses', [])
            quality['recommendations'] = dq.get('recommendations', [])

        return quality

    def _process_advanced_analytics(self, data: Dict) -> Dict[str, Any]:
        """Process data for advanced analytics section"""
        analytics = {
            'discovery_days': 0,
            'discovery_trend': 'N/A',
            'daily_avg': 0,
            'anomalies_count': 0,
            'page_classification': {}
        }

        if 'advanced' not in data:
            return analytics

        adv = data['advanced']

        # Discovery timeline
        if 'discovery_timeline' in adv:
            dt = adv['discovery_timeline']
            analytics['discovery_days'] = dt.get('total_discovery_days', 0)
            analytics['discovery_trend'] = dt.get('trend', 'unknown').capitalize()
            analytics['daily_avg'] = round(dt.get('daily_stats', {}).get('mean', 0), 1)
            analytics['anomalies_count'] = len(dt.get('anomalies', []))

        # Page classification
        if 'page_classification' in adv:
            pc = adv['page_classification']
            type_dist = pc.get('type_distribution', {})
            total = sum(type_dist.values())

            analytics['page_classification'] = [
                {
                    'page_type': ptype,
                    'count': count,
                    'percentage': round(count / total * 100, 1) if total > 0 else 0
                }
                for ptype, count in sorted(type_dist.items(), key=lambda x: x[1], reverse=True)
            ]

        return analytics

    def _process_architecture(self, data: Dict) -> Dict[str, Any]:
        """Process data for website architecture section"""
        architecture = {
            'num_nodes': 0,
            'num_edges': 0,
            'density': 0.0,
            'communities': 0,
            'top_pages': []
        }

        if 'link_graph' not in data:
            return architecture

        lg = data['link_graph']

        # Graph statistics
        if 'graph_stats' in lg:
            stats = lg['graph_stats']
            architecture['num_nodes'] = stats.get('num_nodes', 0)
            architecture['num_edges'] = stats.get('num_edges', 0)
            architecture['density'] = round(stats.get('density', 0), 4)

        # Communities
        if 'communities' in lg:
            architecture['communities'] = lg['communities'].get('total_communities', 0)

        # Top pages by centrality
        centrality = lg.get('centrality', {})
        pagerank_data = lg.get('pagerank', {})

        # Combine top pages from in-degree and pagerank
        top_in_degree = centrality.get('top_in_degree', [])[:5]
        top_pagerank = pagerank_data.get('top_10', [])[:5]

        # Create a merged list
        for item in top_in_degree:
            url = item.get('url', '')
            in_degree = item.get('degree', 0)

            # Find pagerank for this URL
            pr_score = 0
            for pr in top_pagerank:
                if pr.get('url') == url:
                    pr_score = round(pr.get('score', 0), 4)
                    break

            architecture['top_pages'].append({
                'url': url[:80] + '...' if len(url) > 80 else url,
                'in_degree': in_degree,
                'pagerank': pr_score,
                'type': 'Hub' if in_degree > 10 else 'Regular'
            })

        return architecture

    def _process_semantic_analysis(self, data: Dict) -> Dict[str, Any]:
        """Process data for semantic analysis section"""
        semantic = {
            'topics': [],
            'clusters': [],
            'entity_data': {}
        }

        if 'semantic' not in data:
            return semantic

        sem = data['semantic']

        # Topics
        if 'topics' in sem:
            topics_data = sem['topics']
            semantic['topics'] = topics_data.get('topics', [])[:5]

        # Clusters
        if 'clusters' in sem:
            clusters_data = sem['clusters']
            cluster_list = clusters_data.get('clusters', [])[:10]

            semantic['clusters'] = [
                {
                    'id': c.get('id', 0),
                    'size': c.get('size', 0),
                    'representative': c.get('representative_url', 'N/A')[:80]
                }
                for c in cluster_list
            ]

        # Entities
        if 'entities' in sem:
            entities = sem['entities']
            top_entities = entities.get('top_entities_by_type', {})

            for entity_type, entity_dict in list(top_entities.items())[:5]:
                semantic['entity_data'][entity_type] = list(entity_dict.items())[:10]

        return semantic

    def _process_actionable_insights(self, data: Dict) -> Dict[str, Any]:
        """Process data for actionable insights section"""
        insights = {
            'content_strategy': [],
            'technical_seo': [],
            'architecture_optimization': [],
            'redundancy_mitigation': []
        }

        # From data quality recommendations
        if 'data_quality' in data:
            dq = data['data_quality']
            recommendations = dq.get('recommendations', [])

            for rec in recommendations:
                if 'crawl' in rec.lower() or 'content' in rec.lower():
                    insights['content_strategy'].append(rec)
                elif 'http' in rec.lower() or 'seo' in rec.lower():
                    insights['technical_seo'].append(rec)

        # From semantic analysis
        if 'semantic' in data:
            sem = data['semantic']
            if 'clusters' in sem:
                clusters = sem['clusters']
                total_clusters = clusters.get('total_clusters', 0)
                if total_clusters > 0:
                    insights['redundancy_mitigation'].append(
                        f"Found {total_clusters} semantic clusters indicating content redundancy - consolidate similar pages"
                    )

        # From link graph
        if 'link_graph' in data:
            lg = data['link_graph']
            if 'page_types' in lg:
                orphans = lg['page_types'].get('orphan', 0)
                if orphans > 0:
                    insights['technical_seo'].append(
                        f"Fix {orphans} orphan pages by adding internal links"
                    )

            if 'communities' in lg:
                total_communities = lg['communities'].get('total_communities', 0)
                if total_communities > 0:
                    insights['architecture_optimization'].append(
                        f"Optimize link distribution across {total_communities} content communities"
                    )

        # Add defaults if empty
        if not insights['content_strategy']:
            insights['content_strategy'].append("Continue monitoring content quality and completeness")

        if not insights['technical_seo']:
            insights['technical_seo'].append("Maintain current SEO practices")

        if not insights['architecture_optimization']:
            insights['architecture_optimization'].append("Review internal linking structure regularly")

        if not insights['redundancy_mitigation']:
            insights['redundancy_mitigation'].append("No significant content redundancy detected")

        return insights

    def _build_template_context(self, data: Dict, visualizations: List[Dict]) -> Dict[str, Any]:
        """Build complete template context from all data"""
        print("\n[3/5] Processing data for report...")

        context = {}

        # Metadata
        context['report_title'] = 'Comprehensive Website Intelligence Report'
        context['generated_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        context['components_count'] = len(data)

        # Process each section
        context['executive_summary'] = self._process_executive_summary(data)
        print("  [+] Processed executive summary")

        context['data_overview'] = self._process_data_overview(data)
        print("  [+] Processed data overview")

        context['data_quality'] = self._process_data_quality(data)
        print("  [+] Processed data quality")

        context['advanced_analytics'] = self._process_advanced_analytics(data)
        print("  [+] Processed advanced analytics")

        context['architecture'] = self._process_architecture(data)
        print("  [+] Processed architecture")

        context['semantic_analysis'] = self._process_semantic_analysis(data)
        print("  [+] Processed semantic analysis")

        context['actionable_insights'] = self._process_actionable_insights(data)
        print("  [+] Processed actionable insights")

        # Add visualizations
        context['visualizations'] = visualizations
        print("  [+] Added visualizations")

        # Convenience variables for header
        exec_summary = context['executive_summary']
        context['total_urls'] = exec_summary['total_urls']
        context['total_domains'] = exec_summary['total_domains']

        return context

    def _render_html_sections(self, context: Dict[str, Any]) -> str:
        """Render all HTML sections"""
        sections_html = []

        # Executive Summary
        sections_html.append(self._render_executive_summary(context))

        # Data Overview
        sections_html.append(self._render_data_overview(context))

        # Data Quality
        sections_html.append(self._render_data_quality(context))

        # Advanced Analytics
        sections_html.append(self._render_advanced_analytics(context))

        # Architecture (if available)
        if context['architecture']['num_nodes'] > 0:
            sections_html.append(self._render_architecture(context))

        # Semantic Analysis (if available)
        if context['semantic_analysis']['topics'] or context['semantic_analysis']['clusters']:
            sections_html.append(self._render_semantic_analysis(context))

        # Visualizations
        sections_html.append(self._render_visualizations(context))

        # Actionable Insights
        sections_html.append(self._render_actionable_insights(context))

        return '\n\n'.join(sections_html)

    def _render_executive_summary(self, context: Dict) -> str:
        """Render executive summary section"""
        es = context['executive_summary']

        insights_html = '\n'.join([
            f'            <li class="insight-item">{insight}</li>'
            for insight in es['top_insights']
        ]) if es['top_insights'] else '            <li class="insight-item">No specific insights available</li>'

        recommendations_html = '\n'.join([
            f'            <li class="insight-item recommendation">{rec}</li>'
            for rec in es['top_recommendations']
        ]) if es['top_recommendations'] else '            <li class="insight-item recommendation">No recommendations at this time</li>'

        return f'''
<section id="executive-summary" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Executive Summary
            <span class="section-badge">Overview</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('exec-summary-content')">Collapse</button>
    </div>
    <div id="exec-summary-content" class="section-content">
        <div class="card-grid">
            <div class="metric-card success">
                <div class="metric-label">Total URLs Analyzed</div>
                <div class="metric-value">{es['total_urls']:,}</div>
                <div class="metric-description">Across {es['total_domains']} unique domains</div>
            </div>
            <div class="metric-card info">
                <div class="metric-label">Crawl Coverage</div>
                <div class="metric-value">{es['crawl_coverage']}%</div>
                <div class="metric-description">{es['crawled_count']:,} of {es['total_urls']:,} URLs crawled</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">Average Depth</div>
                <div class="metric-value">{es['avg_depth']}</div>
                <div class="metric-description">Range: {es['min_depth']} - {es['max_depth']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Data Quality Score</div>
                <div class="metric-value">{es['quality_score']}/100</div>
                <div class="metric-description">Based on completeness metrics</div>
            </div>
        </div>

        <h3 class="mb-md">Top Insights</h3>
        <ul class="insight-list">
{insights_html}
        </ul>

        <h3 class="mb-md mt-lg">Top Recommendations</h3>
        <ul class="insight-list">
{recommendations_html}
        </ul>
    </div>
</section>'''

    def _render_data_overview(self, context: Dict) -> str:
        """Render data overview section"""
        do = context['data_overview']

        completeness_html = '\n'.join([
            f'''        <div class="progress-item">
            <div class="progress-header">
                <span class="progress-label">{field.replace('_', ' ').title()}</span>
                <span class="progress-value">{metrics['percentage']}%</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar {metrics['class']}" style="width: {metrics['percentage']}%;">
                    {metrics['count']:,} records
                </div>
            </div>
        </div>'''
            for field, metrics in list(do['completeness_data'].items())[:8]
        ])

        return f'''
<section id="data-overview" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Data Overview
            <span class="section-badge">Statistics</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('data-overview-content')">Collapse</button>
    </div>
    <div id="data-overview-content" class="section-content">
        <h3 class="mb-md">Basic Statistics</h3>
        <div class="stats-grid mb-lg">
            <div class="stat-box">
                <div class="stat-value">{do['total_records']:,}</div>
                <div class="stat-label">Total Records</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{do['unique_urls']:,}</div>
                <div class="stat-label">Unique URLs</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{do['unique_domains']}</div>
                <div class="stat-label">Unique Domains</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{do['orphan_count']:,}</div>
                <div class="stat-label">Orphan URLs</div>
            </div>
        </div>

        <h3 class="mb-md">URL Quality</h3>
        <div class="stats-grid mb-lg">
            <div class="stat-box">
                <div class="stat-value">{do['https_count']:,}</div>
                <div class="stat-label">HTTPS URLs</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{do['http_count']:,}</div>
                <div class="stat-label">HTTP URLs</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{do['avg_url_length']}</div>
                <div class="stat-label">Avg URL Length</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{round((do['https_count'] / (do['https_count'] + do['http_count']) * 100) if (do['https_count'] + do['http_count']) > 0 else 0, 1)}%</div>
                <div class="stat-label">HTTPS Coverage</div>
            </div>
        </div>

        <h3 class="mb-md">Data Completeness</h3>
{completeness_html}
    </div>
</section>'''

    def _render_data_quality(self, context: Dict) -> str:
        """Render data quality section"""
        dq = context['data_quality']

        strengths_html = '\n'.join([
            f'            <li class="insight-item strength">{strength}</li>'
            for strength in dq['strengths']
        ]) if dq['strengths'] else '            <li class="insight-item strength">No specific strengths identified</li>'

        weaknesses_html = '\n'.join([
            f'            <li class="insight-item weakness">{weakness}</li>'
            for weakness in dq['weaknesses']
        ]) if dq['weaknesses'] else '            <li class="insight-item">No weaknesses identified</li>'

        recommendations_html = '\n'.join([
            f'            <li class="insight-item recommendation">{rec}</li>'
            for rec in dq['recommendations']
        ]) if dq['recommendations'] else '            <li class="insight-item">No recommendations at this time</li>'

        return f'''
<section id="data-quality" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Data Quality Assessment
            <span class="section-badge">Quality</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('data-quality-content')">Collapse</button>
    </div>
    <div id="data-quality-content" class="section-content">
        <h3 class="mb-md">Strengths</h3>
        <ul class="insight-list mb-lg">
{strengths_html}
        </ul>

        <h3 class="mb-md">Weaknesses</h3>
        <ul class="insight-list mb-lg">
{weaknesses_html}
        </ul>

        <h3 class="mb-md">Recommendations</h3>
        <ul class="insight-list">
{recommendations_html}
        </ul>
    </div>
</section>'''

    def _render_advanced_analytics(self, context: Dict) -> str:
        """Render advanced analytics section"""
        aa = context['advanced_analytics']

        page_class_rows = '\n'.join([
            f'''                <tr>
                    <td>{pc['page_type'].replace('_', ' ').title()}</td>
                    <td>{pc['count']:,}</td>
                    <td>{pc['percentage']}%</td>
                </tr>'''
            for pc in aa['page_classification'][:10]
        ]) if aa['page_classification'] else '''                <tr>
                    <td colspan="3">No page classification data available</td>
                </tr>'''

        return f'''
<section id="advanced-analytics" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Advanced Analytics
            <span class="section-badge">Trends</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('advanced-analytics-content')">Collapse</button>
    </div>
    <div id="advanced-analytics-content" class="section-content">
        <h3 class="mb-md">Discovery Timeline</h3>
        <div class="stats-grid mb-lg">
            <div class="stat-box">
                <div class="stat-value">{aa['discovery_days']}</div>
                <div class="stat-label">Discovery Days</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{aa['discovery_trend']}</div>
                <div class="stat-label">Trend</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{aa['daily_avg']}</div>
                <div class="stat-label">Daily Average</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{aa['anomalies_count']}</div>
                <div class="stat-label">Anomalies Detected</div>
            </div>
        </div>

        <h3 class="mb-md">Page Classification</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Page Type</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
{page_class_rows}
            </tbody>
        </table>
    </div>
</section>'''

    def _render_architecture(self, context: Dict) -> str:
        """Render architecture section"""
        arch = context['architecture']

        top_pages_rows = '\n'.join([
            f'''                <tr>
                    <td class="font-mono">{page['url']}</td>
                    <td>{page['in_degree']}</td>
                    <td>{page['pagerank']}</td>
                    <td><span class="badge info">{page['type']}</span></td>
                </tr>'''
            for page in arch['top_pages']
        ]) if arch['top_pages'] else '''                <tr>
                    <td colspan="4">No page data available</td>
                </tr>'''

        return f'''
<section id="architecture" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Website Architecture
            <span class="section-badge">Structure</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('architecture-content')">Collapse</button>
    </div>
    <div id="architecture-content" class="section-content">
        <h3 class="mb-md">Link Graph Statistics</h3>
        <div class="stats-grid mb-lg">
            <div class="stat-box">
                <div class="stat-value">{arch['num_nodes']:,}</div>
                <div class="stat-label">Total Nodes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{arch['num_edges']:,}</div>
                <div class="stat-label">Total Links</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{arch['density']}</div>
                <div class="stat-label">Graph Density</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{arch['communities']}</div>
                <div class="stat-label">Communities</div>
            </div>
        </div>

        <h3 class="mb-md">Top Pages by Centrality</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>URL</th>
                    <th>In-Degree</th>
                    <th>PageRank</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
{top_pages_rows}
            </tbody>
        </table>
    </div>
</section>'''

    def _render_semantic_analysis(self, context: Dict) -> str:
        """Render semantic analysis section"""
        sem = context['semantic_analysis']

        topics_html = '\n'.join([
            f'''            <div class="mb-md">
                <strong>Topic {topic['id']}:</strong>
                {' '.join([f'<span class="badge info">{word}</span>' for word in topic['words'][:10]])}
            </div>'''
            for topic in sem['topics']
        ]) if sem['topics'] else '            <div class="mb-md">No topics discovered</div>'

        clusters_rows = '\n'.join([
            f'''                <tr>
                    <td>{cluster['id']}</td>
                    <td>{cluster['size']}</td>
                    <td class="font-mono">{cluster['representative']}</td>
                </tr>'''
            for cluster in sem['clusters']
        ]) if sem['clusters'] else '''                <tr>
                    <td colspan="3">No content redundancy clusters detected</td>
                </tr>'''

        entities_html = '\n'.join([
            f'''            <div class="mb-md">
                <strong>{entity_type}:</strong>
                {' '.join([f'<span class="badge success">{entity} ({count})</span>' for entity, count in entities[:8]])}
            </div>'''
            for entity_type, entities in list(sem['entity_data'].items())[:5]
        ]) if sem['entity_data'] else '            <div class="mb-md">No named entities extracted</div>'

        return f'''
<section id="semantic-analysis" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Semantic Analysis
            <span class="section-badge">Content</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('semantic-content')">Collapse</button>
    </div>
    <div id="semantic-content" class="section-content">
        <h3 class="mb-md">Main Topics Discovered</h3>
        <div class="mb-lg">
{topics_html}
        </div>

        <h3 class="mb-md">Content Redundancy Analysis</h3>
        <table class="data-table mb-lg">
            <thead>
                <tr>
                    <th>Cluster ID</th>
                    <th>Pages</th>
                    <th>Representative URL</th>
                </tr>
            </thead>
            <tbody>
{clusters_rows}
            </tbody>
        </table>

        <h3 class="mb-md">Key Named Entities</h3>
        <div class="mb-lg">
{entities_html}
        </div>
    </div>
</section>'''

    def _render_visualizations(self, context: Dict) -> str:
        """Render visualizations section"""
        viz_cards = '\n'.join([
            f'''            <div class="visualization-card">
                <h3 class="visualization-title">{viz['title']}</h3>
                <img src="data:image/png;base64,{viz['image_base64']}" alt="{viz['title']}">
            </div>'''
            for viz in context['visualizations']
        ]) if context['visualizations'] else '            <div class="visualization-card"><p>No visualizations available</p></div>'

        return f'''
<section id="visualizations" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Visualizations
            <span class="section-badge">Charts</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('visualizations-content')">Collapse</button>
    </div>
    <div id="visualizations-content" class="section-content">
        <div class="visualization-grid">
{viz_cards}
        </div>
    </div>
</section>'''

    def _render_actionable_insights(self, context: Dict) -> str:
        """Render actionable insights section"""
        ai = context['actionable_insights']

        content_strategy_html = '\n'.join([
            f'            <li class="insight-item">{insight}</li>'
            for insight in ai['content_strategy']
        ])

        technical_seo_html = '\n'.join([
            f'            <li class="insight-item">{insight}</li>'
            for insight in ai['technical_seo']
        ])

        arch_opt_html = '\n'.join([
            f'            <li class="insight-item">{insight}</li>'
            for insight in ai['architecture_optimization']
        ])

        redundancy_html = '\n'.join([
            f'            <li class="insight-item recommendation">{insight}</li>'
            for insight in ai['redundancy_mitigation']
        ])

        return f'''
<section id="insights" class="section">
    <div class="section-header">
        <h2 class="section-title">
            Actionable Insights
            <span class="section-badge">Recommendations</span>
        </h2>
        <button class="toggle-btn" onclick="toggleSection('insights-content')">Collapse</button>
    </div>
    <div id="insights-content" class="section-content">
        <h3 class="mb-md">Content Strategy</h3>
        <ul class="insight-list mb-lg">
{content_strategy_html}
        </ul>

        <h3 class="mb-md">Technical SEO</h3>
        <ul class="insight-list mb-lg">
{technical_seo_html}
        </ul>

        <h3 class="mb-md">Architecture Optimization</h3>
        <ul class="insight-list mb-lg">
{arch_opt_html}
        </ul>

        <h3 class="mb-md">Redundancy Mitigation</h3>
        <ul class="insight-list">
{redundancy_html}
        </ul>
    </div>
</section>'''

    def generate_report(self, cleanup_old_files: bool = False) -> Path:
        """
        Generate unified HTML report

        Args:
            cleanup_old_files: If True, archive old scattered report files after generation

        Returns:
            Path to generated report
        """
        print("\n" + "="*60)
        print("UNIFIED REPORT GENERATOR")
        print("="*60)

        # Load all data
        data = self._load_all_analysis_data()

        if not data:
            print("\n[-] No analysis data found. Run analyzers first.")
            return None

        # Load visualizations
        visualizations = self._load_visualizations()

        # Build template context
        context = self._build_template_context(data, visualizations)

        # Load template
        print("\n[4/5] Rendering HTML report...")
        template_path = self.template_dir / 'unified_report_template.html'

        if not template_path.exists():
            print(f"  [-] Template not found: {template_path}")
            return None

        with open(template_path, 'r') as f:
            template_content = f.read()

        # Render sections
        sections_html = self._render_html_sections(context)

        # Replace template variables
        html_output = template_content
        html_output = html_output.replace('{{ report_title }}', context['report_title'])
        html_output = html_output.replace('{{ generated_timestamp }}', context['generated_timestamp'])
        html_output = html_output.replace('{{ total_urls }}', f"{context['total_urls']:,}")
        html_output = html_output.replace('{{ total_domains }}', str(context['total_domains']))
        html_output = html_output.replace('{{ components_count }}', str(context['components_count']))
        html_output = html_output.replace('{{ content }}', sections_html)

        print("  [+] Template rendered successfully")

        # Save report
        print("\n[5/5] Saving report...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'unified_report_{timestamp}.html'
        report_path = self.output_dir / report_filename

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        # Create symlink to latest
        latest_link = self.output_dir / 'unified_report_latest.html'
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()

        try:
            latest_link.symlink_to(report_filename)
            print(f"  [+] Created symlink: unified_report_latest.html")
        except Exception:
            # Windows doesn't always support symlinks
            import shutil
            shutil.copy(report_path, latest_link)
            print(f"  [+] Created copy: unified_report_latest.html")

        # Calculate file size
        file_size_kb = report_path.stat().st_size / 1024

        print("\n" + "="*60)
        print("[+] UNIFIED REPORT GENERATED SUCCESSFULLY")
        print("="*60)
        print(f"\nReport saved to: {report_path}")
        print(f"File size: {file_size_kb:.1f} KB")
        print(f"\nOpen in browser:")
        print(f"  file://{report_path.absolute()}")
        print("\n" + "="*60)

        # Optional: Clean up old scattered files
        if cleanup_old_files:
            print("\nCleaning up old scattered report files...")
            try:
                from src.utils.cleanup_old_reports import archive_old_reports
                archive_path = archive_old_reports(self.project_root)
                if archive_path:
                    print(f"[+] Old files archived to: {archive_path.relative_to(self.project_root)}")
            except Exception as e:
                print(f"[!] Warning: Could not clean up old files: {e}")

        return report_path


if __name__ == '__main__':
    generator = UnifiedReportGenerator()
    generator.generate_report()
