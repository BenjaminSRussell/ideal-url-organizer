"""
Semantic Analyzer - Expert-level text analysis

Features:
1. Text Embeddings - Find similar pages via vector similarity
2. Named Entity Recognition (NER) - Extract people, organizations, locations
3. Topic Modeling - Discover hidden subjects
4. Advanced text analysis
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple, TYPE_CHECKING
from collections import Counter, defaultdict
import json
from pathlib import Path

if TYPE_CHECKING:
    import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")

try:
    import spacy
    NER_AVAILABLE = True
except ImportError:
    NER_AVAILABLE = False
    print("Warning: spacy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.cluster import DBSCAN
    TOPIC_MODELING_AVAILABLE = True
except ImportError:
    TOPIC_MODELING_AVAILABLE = False
    print("Warning: scikit-learn not available. Install with: pip install scikit-learn")

try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("Warning: textblob not available. Install with: pip install textblob")

from src.core.web_crawler import PageContent


class TextEmbedder:
    """
    Create vector embeddings for semantic similarity

    This is THE KEY to finding similar pages based on meaning, not just keywords
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedder

        Args:
            model_name: Sentence-transformers model to use
                       'all-MiniLM-L6-v2' - Fast, 384 dimensions
                       'all-mpnet-base-v2' - Best quality, 768 dimensions
        """
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")

        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed_text(self, text: str) -> 'np.ndarray':
        """
        Convert text to vector embedding

        Args:
            text: Text to embed

        Returns:
            Numpy array of embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_pages(self, pages: List[PageContent]) -> Dict[str, 'np.ndarray']:
        """
        Embed multiple pages

        Args:
            pages: List of PageContent objects

        Returns:
            Dictionary mapping URL -> embedding vector
        """
        embeddings = {}

        for page in pages:
            # Use title + meta description + first 500 chars of text
            text_to_embed = f"{page.title or ''} {page.meta_description or ''} {(page.text_content or '')[:500]}"

            if text_to_embed.strip():
                embeddings[page.url] = self.embed_text(text_to_embed)

        return embeddings

    def find_similar(self,
                     query_url: str,
                     embeddings: Dict[str, np.ndarray],
                     top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find pages similar to query URL

        Args:
            query_url: URL to find similar pages for
            embeddings: Dictionary of URL -> embedding
            top_k: Number of similar pages to return

        Returns:
            List of (url, similarity_score) tuples
        """
        if query_url not in embeddings:
            return []

        query_embedding = embeddings[query_url].reshape(1, -1)

        similarities = []
        for url, embedding in embeddings.items():
            if url != query_url:
                sim = cosine_similarity(query_embedding, embedding.reshape(1, -1))[0][0]
                similarities.append((url, float(sim)))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]


class NamedEntityRecognizer:
    """
    Extract named entities (people, organizations, locations, etc.)

    This is THE KEY to understanding what pages are ABOUT
    """

    def __init__(self, model: str = 'en_core_web_sm'):
        """
        Initialize NER

        Args:
            model: Spacy model to use
        """
        if not NER_AVAILABLE:
            raise ImportError("spacy not installed")

        self.nlp = spacy.load(model)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text

        Args:
            text: Text to analyze

        Returns:
            Dictionary mapping entity type -> list of entities
        """
        if not text:
            return {}

        doc = self.nlp(text[:1000000])  # Limit text length for performance

        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)

        # Convert to regular dict with unique entities
        return {
            label: list(set(ents))
            for label, ents in entities.items()
        }

    def extract_from_pages(self, pages: List[PageContent]) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract entities from multiple pages

        Args:
            pages: List of PageContent objects

        Returns:
            Dictionary mapping URL -> entities
        """
        results = {}

        for page in pages:
            text = f"{page.title or ''} {page.meta_description or ''} {(page.text_content or '')[:5000]}"
            entities = self.extract_entities(text)
            if entities:
                results[page.url] = entities

        return results

    def find_pages_by_entity(self,
                            entity_name: str,
                            page_entities: Dict[str, Dict[str, List[str]]]) -> List[str]:
        """
        Find all pages that mention a specific entity

        Args:
            entity_name: Entity to search for
            page_entities: Result from extract_from_pages()

        Returns:
            List of URLs that mention the entity
        """
        matching_urls = []

        for url, entities in page_entities.items():
            for entity_type, entity_list in entities.items():
                if entity_name in entity_list:
                    matching_urls.append(url)
                    break

        return matching_urls


class TopicModeler:
    """
    Discover hidden topics in text corpus

    This is THE KEY to automatically categorizing pages
    """

    def __init__(self, n_topics: int = 10):
        """
        Initialize topic modeler

        Args:
            n_topics: Number of topics to discover
        """
        if not TOPIC_MODELING_AVAILABLE:
            raise ImportError("scikit-learn not installed")

        self.n_topics = n_topics
        self.vectorizer = CountVectorizer(
            max_features=1000,
            stop_words='english',
            min_df=2
        )
        self.lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42
        )
        self.feature_names = None
        self.fitted = False

    def fit(self, texts: List[str]):
        """
        Fit topic model to text corpus

        Args:
            texts: List of text documents
        """
        # Vectorize texts
        text_vectors = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

        # Fit LDA
        self.lda.fit(text_vectors)
        self.fitted = True

    def get_topics(self, n_words: int = 10) -> List[List[str]]:
        """
        Get top words for each topic

        Args:
            n_words: Number of words per topic

        Returns:
            List of topics, each topic is a list of words
        """
        if not self.fitted:
            raise ValueError("Model not fitted yet")

        topics = []
        for topic_idx, topic in enumerate(self.lda.components_):
            top_word_indices = topic.argsort()[-n_words:][::-1]
            top_words = [self.feature_names[i] for i in top_word_indices]
            topics.append(top_words)

        return topics

    def assign_topics(self, texts: List[str]) -> List[int]:
        """
        Assign topic to each document

        Args:
            texts: List of text documents

        Returns:
            List of topic assignments (0 to n_topics-1)
        """
        if not self.fitted:
            raise ValueError("Model not fitted yet")

        text_vectors = self.vectorizer.transform(texts)
        topic_distributions = self.lda.transform(text_vectors)

        # Assign dominant topic
        return topic_distributions.argmax(axis=1).tolist()


class SemanticClusterer:
    """
    Cluster similar pages based on semantic similarity

    This identifies content redundancy and cannibalization
    """

    def __init__(self, embedder: TextEmbedder):
        """
        Initialize semantic clusterer

        Args:
            embedder: TextEmbedder instance for creating vectors
        """
        self.embedder = embedder

    def cluster_pages(self, pages: List[PageContent], similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Cluster pages by semantic similarity

        Args:
            pages: List of PageContent objects
            similarity_threshold: Minimum similarity for clustering

        Returns:
            Clustering results
        """
        if not EMBEDDINGS_AVAILABLE:
            return {}

        # Get embeddings
        embeddings = self.embedder.embed_pages(pages)
        if not embeddings:
            return {}

        # Build embedding matrix
        import numpy as np
        urls = list(embeddings.keys())
        embedding_matrix = np.array([embeddings[url] for url in urls])

        # Compute similarity matrix
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(embedding_matrix)

        # Use DBSCAN for clustering (similarity_threshold -> distance)
        from sklearn.metrics.pairwise import cosine_distances
        distances = cosine_distances(embedding_matrix)

        try:
            from sklearn.cluster import DBSCAN
            clustering = DBSCAN(eps=1-similarity_threshold, min_samples=2, metric='precomputed')
            labels = clustering.fit_predict(distances)
        except Exception as e:
            print(f"  Warning: Clustering failed: {e}")
            return {}

        # Organize clusters
        clusters = defaultdict(list)
        for url, label in zip(urls, labels):
            clusters[int(label)].append(url)

        # Filter out noise (-1 label) and prepare results
        cluster_list = []
        for cluster_id, cluster_urls in clusters.items():
            if cluster_id != -1 and len(cluster_urls) > 1:
                cluster_list.append({
                    'id': cluster_id,
                    'size': len(cluster_urls),
                    'members': cluster_urls
                })

        # Sort by size
        cluster_list.sort(key=lambda x: x['size'], reverse=True)

        return {
            'clusters': cluster_list,
            'total_clusters': len(cluster_list),
            'singleton_count': sum(1 for label, urls in clusters.items() if label != -1 and len(urls) == 1)
        }


class SentimentAnalyzer:
    """
    Analyze sentiment of page content
    """

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text

        Args:
            text: Text to analyze

        Returns:
            Sentiment scores (polarity, subjectivity)
        """
        if not text or not SENTIMENT_AVAILABLE:
            return {'polarity': 0.0, 'subjectivity': 0.0}

        try:
            from textblob import TextBlob
            blob = TextBlob(text[:5000])
            return {
                'polarity': float(blob.sentiment.polarity),
                'subjectivity': float(blob.sentiment.subjectivity)
            }
        except Exception as e:
            print(f"  Warning: Sentiment analysis failed: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}

    def analyze_pages(self, pages: List[PageContent]) -> Dict[str, Any]:
        """
        Analyze sentiment across pages

        Args:
            pages: List of PageContent objects

        Returns:
            Sentiment analysis results
        """
        if not SENTIMENT_AVAILABLE:
            return {}

        sentiments = {}
        polarity_scores = []
        subjectivity_scores = []

        for page in pages:
            text = f"{page.title or ''} {page.meta_description or ''} {(page.text_content or '')[:5000]}"
            sentiment = self.analyze_sentiment(text)
            sentiments[page.url] = sentiment
            polarity_scores.append(sentiment['polarity'])
            subjectivity_scores.append(sentiment['subjectivity'])

        if not polarity_scores:
            return {}

        import numpy as np
        return {
            'total_analyzed': len(sentiments),
            'polarity': {
                'mean': float(np.mean(polarity_scores)),
                'std': float(np.std(polarity_scores)),
                'min': float(np.min(polarity_scores)),
                'max': float(np.max(polarity_scores))
            },
            'subjectivity': {
                'mean': float(np.mean(subjectivity_scores)),
                'std': float(np.std(subjectivity_scores)),
                'min': float(np.min(subjectivity_scores)),
                'max': float(np.max(subjectivity_scores))
            },
            'most_positive': sorted(sentiments.items(), key=lambda x: x[1]['polarity'], reverse=True)[:5],
            'most_negative': sorted(sentiments.items(), key=lambda x: x[1]['polarity'])[:5],
            'most_subjective': sorted(sentiments.items(), key=lambda x: x[1]['subjectivity'], reverse=True)[:5]
        }


class SemanticAnalyzer:
    """
    High-level semantic analysis orchestrator
    """

    def __init__(self, output_dir: Path = None):
        """Initialize semantic analyzer"""
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'results' / 'analysis' / 'semantic'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components (lazy loading)
        self._embedder = None
        self._ner = None
        self._topic_modeler = None

    @property
    def embedder(self) -> TextEmbedder:
        """Lazy load embedder"""
        if self._embedder is None and EMBEDDINGS_AVAILABLE:
            self._embedder = TextEmbedder()
        return self._embedder

    @property
    def ner(self) -> NamedEntityRecognizer:
        """Lazy load NER"""
        if self._ner is None and NER_AVAILABLE:
            self._ner = NamedEntityRecognizer()
        return self._ner

    def _get_section_from_url(self, url: str) -> str:
        """Extract main path section from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if path_parts and path_parts[0]:
            return path_parts[0]
        return 'root'

    def analyze(self, pages: List[PageContent]) -> Dict[str, Any]:
        """
        Perform comprehensive semantic analysis

        Args:
            pages: List of PageContent objects

        Returns:
            Analysis results
        """
        print("\nSemantic Analysis")

        analysis = {
            'total_pages': len(pages),
            'embeddings': {},
            'entities': {},
            'topics': {},
            'similarity': {}
        }

        # 1. Text Embeddings
        if EMBEDDINGS_AVAILABLE and self.embedder:
            print("\n[1/3] Computing text embeddings...")
            embeddings = self.embedder.embed_pages(pages)
            analysis['embeddings'] = {
                'model': self.embedder.model_name,
                'dimension': embeddings[list(embeddings.keys())[0]].shape[0] if embeddings else 0,
                'num_embedded': len(embeddings)
            }

            # Save embeddings
            embeddings_file = self.output_dir / 'embeddings.npy'
            if embeddings:
                import numpy as np
                np.save(embeddings_file, {url: emb.tolist() for url, emb in embeddings.items()})
                print(f"  [+] Saved {len(embeddings)} embeddings")

        # 2. Named Entity Recognition
        if NER_AVAILABLE and self.ner:
            print("\n[2/3] Extracting named entities...")
            entities = self.ner.extract_from_pages(pages)

            # Aggregate entity statistics
            entity_stats = defaultdict(Counter)
            for page_url, page_entities in entities.items():
                for entity_type, entity_list in page_entities.items():
                    entity_stats[entity_type].update(entity_list)

            analysis['entities'] = {
                'num_pages_with_entities': len(entities),
                'entity_types': list(entity_stats.keys()),
                'top_entities_by_type': {
                    etype: dict(counter.most_common(10))
                    for etype, counter in entity_stats.items()
                }
            }

            # Save entities
            entities_file = self.output_dir / 'entities.json'
            with open(entities_file, 'w') as f:
                json.dump(entities, f, indent=2)
            print(f"  [+] Found {len(entity_stats)} entity types")

        # 3. Semantic Clustering (Redundancy Analysis)
        if EMBEDDINGS_AVAILABLE and self.embedder:
            print("\n[3/5] Detecting semantic clusters (content redundancy)...")
            clusterer = SemanticClusterer(self.embedder)
            clusters = clusterer.cluster_pages(pages)

            if clusters:
                analysis['clusters'] = clusters
                print(f"  [+] Found {clusters.get('total_clusters', 0)} semantic clusters")
                if clusters.get('clusters'):
                    for cluster in clusters['clusters'][:3]:
                        print(f"    - Cluster {cluster['id']}: {cluster['size']} similar pages")

        # 4. Sentiment Analysis
        if SENTIMENT_AVAILABLE:
            print("\n[4/5] Analyzing sentiment...")
            sentiment_analyzer = SentimentAnalyzer()
            sentiment_results = sentiment_analyzer.analyze_pages(pages)

            if sentiment_results:
                analysis['sentiment'] = sentiment_results
                print(f"  [+] Analyzed sentiment for {sentiment_results.get('total_analyzed', 0)} pages")
                print(f"    - Polarity: {sentiment_results['polarity']['mean']:.2f} (avg)")
                print(f"    - Subjectivity: {sentiment_results['subjectivity']['mean']:.2f} (avg)")

        # 5. Topic Modeling with section distribution
        if TOPIC_MODELING_AVAILABLE:
            print("\n[5/5] Discovering topics and section distribution...")
            texts = [
                f"{p.title or ''} {p.meta_description or ''} {(p.text_content or '')[:1000]}"
                for p in pages if p.text_content
            ]
            pages_with_text = [p for p in pages if p.text_content]

            if len(texts) >= 5:  # Need minimum documents
                topic_modeler = TopicModeler(n_topics=min(5, len(texts) // 2))
                topic_modeler.fit(texts)

                topics = topic_modeler.get_topics(n_words=10)
                topic_assignments = topic_modeler.assign_topics(texts)

                # Calculate topic distribution by section
                section_topics = defaultdict(lambda: defaultdict(int))
                for page, topic_id in zip(pages_with_text, topic_assignments):
                    section = self._get_section_from_url(page.url)
                    section_topics[section][int(topic_id)] += 1

                analysis['topics'] = {
                    'num_topics': len(topics),
                    'topics': [
                        {'id': i, 'words': words}
                        for i, words in enumerate(topics)
                    ],
                    'section_distribution': {
                        section: dict(topic_counts)
                        for section, topic_counts in section_topics.items()
                    }
                }

                print(f"  [+] Discovered {len(topics)} topics")
                for i, words in enumerate(topics):
                    print(f"    Topic {i}: {', '.join(words[:5])}...")
                print(f"  [+] Topic distribution by {len(section_topics)} sections computed")

        # Save analysis
        analysis_file = self.output_dir / 'semantic_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n[+] Semantic analysis saved to: {analysis_file}")

        return analysis


if __name__ == '__main__':
    print("Semantic Analyzer - Install dependencies:")
    print("  pip install sentence-transformers spacy scikit-learn")
    print("  python -m spacy download en_core_web_sm")
