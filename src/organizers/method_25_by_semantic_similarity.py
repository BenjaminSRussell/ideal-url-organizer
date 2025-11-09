"""
Method 25: Organization by Semantic Similarity Clusters
Groups URLs by semantic similarity using text embeddings

This is THE KEY to finding truly similar pages based on meaning, not just keywords!
"""
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import json

try:
    from sklearn.cluster import KMeans
    import numpy as np
    from sentence_transformers import SentenceTransformer
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False

from src.core.web_crawler import PageContent


class BySemanticSimilarityOrganizer:
    """Organize URLs by semantic similarity clusters"""

    def __init__(self, output_dir: Path, n_clusters: int = 5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.n_clusters = n_clusters

        if not CLUSTERING_AVAILABLE:
            raise ImportError("sentence-transformers and scikit-learn required")

        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def organize(self, pages: List[PageContent]) -> Dict[str, List[PageContent]]:
        """Group pages by semantic similarity"""
        # Extract texts
        texts = []
        valid_pages = []

        for page in pages:
            text = f"{page.title or ''} {page.meta_description or ''} {(page.text_content or '')[:500]}"
            if text.strip():
                texts.append(text)
                valid_pages.append(page)

        if len(valid_pages) < 2:
            return {'cluster_0': valid_pages}

        # Compute embeddings
        embeddings = self.model.encode(texts)

        # Cluster
        n_clusters = min(self.n_clusters, len(valid_pages))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)

        # Organize by cluster
        organized = defaultdict(list)
        for page, cluster_id in zip(valid_pages, cluster_labels):
            organized[f'cluster_{cluster_id}'].append(page)

        return dict(organized)

    def save(self, organized_data: Dict[str, List[PageContent]]):
        """Save organized data"""
        summary = {
            'method': 'by_semantic_similarity',
            'num_clusters': len(organized_data),
            'cluster_sizes': {
                cluster_id: len(pages)
                for cluster_id, pages in organized_data.items()
            }
        }

        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save each cluster
        for cluster_id, pages in organized_data.items():
            filepath = self.output_dir / f'{cluster_id}.json'
            with open(filepath, 'w') as f:
                json.dump([p.to_dict() for p in pages], f, indent=2)

        return summary

    def run(self, pages: List[PageContent]):
        """Run the organization method"""
        print(f"[Method 25] Organizing by semantic similarity...")
        organized = self.organize(pages)
        summary = self.save(organized)

        print(f"  ✓ Created {summary['num_clusters']} semantic clusters")
        for cluster_id, size in summary['cluster_sizes'].items():
            print(f"    - {cluster_id}: {size} pages")

        return summary
