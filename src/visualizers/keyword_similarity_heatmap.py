"""
Keyword Similarity Heatmap
Generate a similarity heatmap for the URLs that contain a keyword.
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.data_loader import DataLoader, URLRecord

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns

    PLOTTING_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    PLOTTING_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    SKLEARN_AVAILABLE = False


class KeywordSimilarityHeatmap:
    """Create a similarity heatmap for the subset of URLs mentioning a keyword."""

    MAX_RECORDS_LIMIT = 40
    MIN_RECORDS = 2

    def __init__(self,
                 keyword: str,
                 max_records: int = 20,
                 output_dir: Path = None,
                 data_loader: DataLoader = None):
        if not PLOTTING_AVAILABLE:
            raise RuntimeError("matplotlib/seaborn are required to draw heatmaps")
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn is required to compute similarity")

        self.keyword = keyword.strip().lower()
        if not self.keyword:
            raise ValueError("Keyword cannot be empty")

        self.max_records = max(self.MIN_RECORDS, min(max_records, self.MAX_RECORDS_LIMIT))
        self.data_loader = data_loader or DataLoader()
        project_root = Path(__file__).parent.parent.parent
        self.output_dir = Path(output_dir) if output_dir else project_root / 'data' / 'visualizations' / 'charts'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.keyword_safe = re.sub(r'[^a-z0-9_-]', '_', self.keyword).strip('_') or 'keyword'

    @staticmethod
    def _record_text(record: URLRecord) -> str:
        parts = [
            record.title,
            record.url,
            record.url_normalized,
            record.parent_url
        ]

        return ' '.join(part for part in parts if part).strip()

    @staticmethod
    def _wrap_label(label: str, width: int = 45) -> str:
        return textwrap.fill(label, width=width)

    def _pick_records(self, records: List[URLRecord]) -> List[Tuple[URLRecord, str]]:
        matches = []
        for record in records:
            text = self._record_text(record)
            if self.keyword in text.lower():
                matches.append((record, text))

        matches.sort(key=lambda item: (item[1].lower().count(self.keyword), -len(item[1])), reverse=True)
        selected = matches[:self.max_records]

        return selected

    def _build_similarity_matrix(self, texts: List[str]):
        vectorizer = TfidfVectorizer(max_features=512, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix

    def _render_heatmap(self, similarity_matrix, labels: List[str]):
        label_list = [self._wrap_label(label) for label in labels]
        size = max(6, len(label_list) * 0.4)
        fig, ax = plt.subplots(figsize=(size, size))

        sns.heatmap(
            similarity_matrix,
            xticklabels=label_list,
            yticklabels=label_list,
            cmap='rocket_r',
            square=True,
            cbar=True,
            vmin=0.0,
            vmax=1.0,
            linewidths=0.5,
            linecolor='white'
        )

        ax.set_title(f"Similarity heatmap ({self.keyword})", fontsize=16, pad=12)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)

        plt.tight_layout()
        filepath = self.output_dir / f'keyword_similarity_heatmap_{self.keyword_safe}.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        return filepath

    def _print_similarity_pairs(self, similarity_matrix, labels: List[str], top_n: int = 3):
        """Print the most similar label pairs for transparency."""
        pairs = []
        length = len(labels)
        for i in range(length):
            for j in range(i + 1, length):
                pairs.append((similarity_matrix[i, j], i, j))

        if not pairs:
            return

        pairs.sort(key=lambda item: item[0], reverse=True)
        print("  Top similarity pairs:")
        for score, i, j in pairs[:top_n]:
            print(f"    {labels[i]} <-> {labels[j]}: {score:.3f}")

    def run(self) -> Path:
        """Generate the heatmap."""
        records = self.data_loader.load()
        selected_records = self._pick_records(records)

        if len(selected_records) < self.MIN_RECORDS:
            raise RuntimeError(f"Found only {len(selected_records)} records mentioning '{self.keyword}'. "
                               f"At least {self.MIN_RECORDS} are required for a heatmap.")

        texts = [text for _, text in selected_records]
        labels = [(record.url_normalized or record.url) for record, _ in selected_records]
        similarity_matrix = self._build_similarity_matrix(texts)

        heatmap_path = self._render_heatmap(similarity_matrix, labels)
        print(f"  ✓ Saved similarity heatmap for '{self.keyword}' [{len(selected_records)} records] -> {heatmap_path}")
        self._print_similarity_pairs(similarity_matrix, labels)
        return heatmap_path


def main():
    parser = argparse.ArgumentParser(description='Generate a keyword similarity heatmap for the URL dataset.')
    parser.add_argument('--keyword', '-k', type=str, default='heat',
                        help='Keyword (case-insensitive) to filter URLs by.')
    parser.add_argument('--max-records', '-n', type=int, default=20,
                        help='Maximum number of matching URLs to include (2-40).')
    parser.add_argument('--data-path', '-d', type=str, help='Override the input JSONL file path.')
    parser.add_argument('--output-dir', '-o', type=str, help='Directory to save the heatmap.')
    args = parser.parse_args()

    loader = DataLoader(args.data_path) if args.data_path else DataLoader()
    generator = KeywordSimilarityHeatmap(
        keyword=args.keyword,
        max_records=args.max_records,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        data_loader=loader
    )

    print(f"\nGenerating similarity heatmap for '{args.keyword}' (max {generator.max_records} records)...")
    generator.run()


if __name__ == '__main__':
    main()
