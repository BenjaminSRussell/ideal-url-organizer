"""
Advanced Analytics - Temporal and Predictive Analysis

Features:
1. Time Series Analysis - Track URL discovery patterns over time
2. Predictive Page Classification - ML-based page type classification
"""
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timedelta
import json

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available. Install with: pip install numpy")

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import LabelEncoder
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn not available. Install with: pip install scikit-learn")

from src.core.web_crawler import PageContent
from src.core.data_loader import URLRecord


class TimeSeriesAnalyzer:
    """
    Analyze temporal patterns in URL discovery
    """

    def analyze_discovery_timeline(self, records: List[URLRecord]) -> Dict[str, Any]:
        """
        Analyze URL discovery over time

        Args:
            records: List of URLRecord objects

        Returns:
            Time series analysis results
        """
        if not records:
            return {}

        # Filter records with discovery timestamps
        discovered_records = [r for r in records if r.discovered_at]
        if not discovered_records:
            return {}

        # Group by date
        from datetime import datetime
        discovery_by_date = defaultdict(int)
        for record in discovered_records:
            if record.discovered_at:
                try:
                    # Handle both unix timestamp (int) and datetime
                    if isinstance(record.discovered_at, int):
                        dt = datetime.fromtimestamp(record.discovered_at)
                    else:
                        dt = record.discovered_at
                    date = dt.date()
                    discovery_by_date[date] += 1
                except Exception:
                    pass

        # Sort by date
        sorted_dates = sorted(discovery_by_date.items())

        # Calculate statistics
        daily_counts = [count for _, count in sorted_dates]
        if not daily_counts:
            return {}

        # Detect trend
        if len(daily_counts) > 1:
            # Simple linear trend
            x = np.arange(len(daily_counts)) if NUMPY_AVAILABLE else list(range(len(daily_counts)))
            y = daily_counts
            if NUMPY_AVAILABLE and len(x) > 1:
                z = np.polyfit(x, y, 1)
                trend = "increasing" if z[0] > 0 else "decreasing" if z[0] < 0 else "stable"
            else:
                trend = "unknown"
        else:
            trend = "insufficient data"

        # Detect anomalies (spikes)
        if NUMPY_AVAILABLE and len(daily_counts) > 2:
            mean = np.mean(daily_counts)
            std = np.std(daily_counts)
            anomalies = []
            for date, count in sorted_dates:
                if count > mean + 2 * std:
                    anomalies.append({'date': str(date), 'count': count})
        else:
            anomalies = []

        return {
            'total_discovery_days': len(sorted_dates),
            'total_discovered': len(discovered_records),
            'daily_stats': {
                'min': min(daily_counts) if daily_counts else 0,
                'max': max(daily_counts) if daily_counts else 0,
                'mean': float(np.mean(daily_counts)) if NUMPY_AVAILABLE else sum(daily_counts) / len(daily_counts),
                'std': float(np.std(daily_counts)) if NUMPY_AVAILABLE else 0.0
            },
            'trend': trend,
            'anomalies': anomalies,
            'daily_timeline': [
                {'date': str(date), 'count': count}
                for date, count in sorted_dates
            ]
        }

    def analyze_crawl_timeline(self, records: List[URLRecord]) -> Dict[str, Any]:
        """
        Analyze crawl progress over time

        Args:
            records: List of URLRecord objects

        Returns:
            Crawl timeline analysis
        """
        if not records:
            return {}

        from datetime import datetime
        crawled_records = [r for r in records if r.crawled_at]
        if not crawled_records:
            return {}

        # Group by date
        crawl_by_date = defaultdict(int)
        cumulative_crawled = 0
        cumulative_timeline = []

        # Sort by crawled_at (handle both int and datetime)
        def sort_key(r):
            try:
                if isinstance(r.crawled_at, int):
                    return r.crawled_at
                return r.crawled_at.timestamp() if hasattr(r.crawled_at, 'timestamp') else 0
            except:
                return 0

        for record in sorted(crawled_records, key=sort_key):
            if record.crawled_at:
                try:
                    if isinstance(record.crawled_at, int):
                        dt = datetime.fromtimestamp(record.crawled_at)
                    else:
                        dt = record.crawled_at
                    date = dt.date()
                    crawl_by_date[date] += 1
                except Exception:
                    pass
                cumulative_crawled += 1

        sorted_dates = sorted(crawl_by_date.items())
        cumulative = 0
        for date, count in sorted_dates:
            cumulative += count
            cumulative_timeline.append({
                'date': str(date),
                'daily_count': count,
                'cumulative_crawled': cumulative
            })

        return {
            'total_crawled': len(crawled_records),
            'crawl_coverage': float(len(crawled_records) / len(records) * 100) if records else 0,
            'crawl_progress': cumulative_timeline,
            'crawl_rate_per_day': {
                'min': min([c for _, c in sorted_dates]) if sorted_dates else 0,
                'max': max([c for _, c in sorted_dates]) if sorted_dates else 0,
                'mean': float(np.mean([c for _, c in sorted_dates])) if NUMPY_AVAILABLE and sorted_dates else 0
            }
        }


class PredictivePageClassifier:
    """
    Classify pages into types using machine learning
    """

    def __init__(self):
        """Initialize classifier"""
        self.classifier = None
        self.vectorizer = None
        self.label_encoder = None

    def _extract_features(self, page: PageContent) -> Dict[str, Any]:
        """
        Extract features from a page for classification

        Args:
            page: PageContent object

        Returns:
            Dictionary of features
        """
        features = {
            'url_depth': page.url.count('/') - 3,  # Subtract https://domain/
            'url_length': len(page.url),
            'has_query_params': 1 if '?' in page.url else 0,
            'text_length': len(page.text_content) if page.text_content else 0,
            'title_length': len(page.title) if page.title else 0,
            'link_count': len(page.internal_links) + len(page.external_links),
            'internal_links_count': len(page.internal_links),
            'image_count': len(page.images) if page.images else 0,
            'has_meta_description': 1 if page.meta_description else 0,
        }
        return features

    def _classify_page_type(self, page: PageContent) -> str:
        """
        Heuristic-based page type classification (fallback)

        Args:
            page: PageContent object

        Returns:
            Page type classification
        """
        url_lower = page.url.lower()

        # Check for specific patterns
        if any(pattern in url_lower for pattern in ['category', 'archive', 'tag', 'listing']):
            return 'category_page'
        elif any(pattern in url_lower for pattern in ['product', 'item', 'sku']):
            return 'product_page'
        elif any(pattern in url_lower for pattern in ['profile', 'user', 'account']):
            return 'user_profile'
        elif any(pattern in url_lower for pattern in ['article', 'post', 'blog']):
            return 'article'
        elif any(pattern in url_lower for pattern in ['api', 'service', 'endpoint']):
            return 'api_endpoint'
        elif any(pattern in url_lower for pattern in ['.pdf', '.doc', '.xls', '.zip']):
            return 'document'

        # Based on structure
        depth = url_lower.count('/') - 3
        if depth <= 1:
            return 'homepage_or_root'
        elif len(page.text_content or '') > 5000:
            return 'article'
        elif len(page.internal_links) > 20:
            return 'hub_page'
        else:
            return 'content_page'

    def predict_page_types(self, pages: List[PageContent]) -> Dict[str, Any]:
        """
        Predict page types for a collection of pages

        Args:
            pages: List of PageContent objects

        Returns:
            Predictions and statistics
        """
        predictions = {}
        type_distribution = Counter()

        for page in pages:
            page_type = self._classify_page_type(page)
            predictions[page.url] = page_type
            type_distribution[page_type] += 1

        # Extract features for analysis
        feature_stats = defaultdict(lambda: defaultdict(list))
        for page, page_type in zip(pages, predictions.values()):
            features = self._extract_features(page)
            for feature_name, feature_value in features.items():
                feature_stats[page_type][feature_name].append(feature_value)

        # Calculate averages
        feature_averages = {}
        if NUMPY_AVAILABLE:
            for page_type, features in feature_stats.items():
                feature_averages[page_type] = {
                    fname: float(np.mean(fvalues)) if fvalues else 0
                    for fname, fvalues in features.items()
                }

        return {
            'total_classified': len(predictions),
            'type_distribution': dict(type_distribution),
            'predictions': predictions,
            'feature_averages': feature_averages
        }


class AdvancedAnalytics:
    """
    Orchestrator for advanced analytics
    """

    def __init__(self, output_dir: Path = None):
        """Initialize advanced analytics"""
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'results' / 'analysis' / 'advanced'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, pages: List[PageContent], records: List[URLRecord]) -> Dict[str, Any]:
        """
        Perform comprehensive advanced analysis

        Args:
            pages: List of PageContent objects
            records: List of URLRecord objects

        Returns:
            Analysis results
        """
        print("\nAdvanced Analytics")

        analysis = {}

        # 1. Time Series Analysis
        print("\n[1/2] Analyzing temporal patterns...")
        ts_analyzer = TimeSeriesAnalyzer()

        discovery_timeline = ts_analyzer.analyze_discovery_timeline(records)
        if discovery_timeline:
            analysis['discovery_timeline'] = discovery_timeline
            print(f"  [+] Discovery timeline: {discovery_timeline.get('total_discovery_days', 0)} days")
            print(f"    - Trend: {discovery_timeline.get('trend', 'unknown')}")

        crawl_timeline = ts_analyzer.analyze_crawl_timeline(records)
        if crawl_timeline:
            analysis['crawl_timeline'] = crawl_timeline
            print(f"  [+] Crawl coverage: {crawl_timeline.get('crawl_coverage', 0):.1f}%")

        # 2. Predictive Page Classification
        print("\n[2/2] Classifying pages with machine learning...")
        classifier = PredictivePageClassifier()
        predictions = classifier.predict_page_types(pages)

        if predictions:
            analysis['page_classification'] = predictions
            print(f"  [+] Classified {predictions.get('total_classified', 0)} pages")
            for ptype, count in predictions.get('type_distribution', {}).items():
                print(f"    - {ptype}: {count} pages")

        # Save analysis
        analysis_file = self.output_dir / 'advanced_analytics.json'
        with open(analysis_file, 'w') as f:
            # Convert numpy types to native Python types
            def convert_types(obj):
                if isinstance(obj, (np.integer, np.floating)):
                    return float(obj) if isinstance(obj, np.floating) else int(obj)
                elif isinstance(obj, dict):
                    return {k: convert_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(item) for item in obj]
                return obj

            json.dump(convert_types(analysis), f, indent=2)

        print(f"\n[+] Advanced analytics saved to: {analysis_file}")

        return analysis


if __name__ == '__main__':
    print("Advanced Analytics - Install dependencies:")
    print("  pip install numpy scikit-learn")
