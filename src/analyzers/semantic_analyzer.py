"""
Semantic Analyzer - Expert-level text analysis

Features:
1. Text Embeddings - Find similar pages via vector similarity
2. Named Entity Recognition (NER) - Extract people, organizations, locations
3. Topic Modeling - Discover hidden subjects
4. Advanced text analysis
"""
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import json
from pathlib import Path

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
    TOPIC_MODELING_AVAILABLE = True
except ImportError:
    TOPIC_MODELING_AVAILABLE = False
    print("Warning: scikit-learn not available. Install with: pip install scikit-learn")

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

    def embed_text(self, text: str) -> np.ndarray:
        """
        Convert text to vector embedding

        Args:
            text: Text to embed

        Returns:
            Numpy array of embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_pages(self, pages: List[PageContent]) -> Dict[str, np.ndarray]:
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


class SemanticAnalyzer:
    """
    High-level semantic analysis orchestrator
    """

    def __init__(self, output_dir: Path = None):
        """Initialize semantic analyzer"""
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'data' / 'analysis' / 'semantic'

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
                print(f"  ✓ Saved {len(embeddings)} embeddings")

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
            print(f"  ✓ Found {len(entity_stats)} entity types")

        # 3. Topic Modeling
        if TOPIC_MODELING_AVAILABLE:
            print("\n[3/3] Discovering topics...")
            texts = [
                f"{p.title or ''} {p.meta_description or ''} {(p.text_content or '')[:1000]}"
                for p in pages if p.text_content
            ]

            if len(texts) >= 5:  # Need minimum documents
                topic_modeler = TopicModeler(n_topics=min(5, len(texts) // 2))
                topic_modeler.fit(texts)

                topics = topic_modeler.get_topics(n_words=10)
                analysis['topics'] = {
                    'num_topics': len(topics),
                    'topics': [
                        {'id': i, 'words': words}
                        for i, words in enumerate(topics)
                    ]
                }

                print(f"  ✓ Discovered {len(topics)} topics")
                for i, words in enumerate(topics):
                    print(f"    Topic {i}: {', '.join(words[:5])}...")

        # Save analysis
        analysis_file = self.output_dir / 'semantic_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n✓ Semantic analysis saved to: {analysis_file}")

        return analysis


if __name__ == '__main__':
    print("Semantic Analyzer - Install dependencies:")
    print("  pip install sentence-transformers spacy scikit-learn")
    print("  python -m spacy download en_core_web_sm")
