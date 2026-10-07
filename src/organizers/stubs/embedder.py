"""Deterministic hash embedder for CPU CI (no torch/sentence-transformers)."""
from __future__ import annotations
import hashlib
from typing import List, Sequence
import numpy as np


class StubSentenceEmbedder:
    """Drop-in stand-in for SentenceTransformer.encode for tests/CI."""

    def __init__(self, dim: int = 32):
        self.dim = dim

    def encode(self, texts: Sequence[str]):
        vectors = []
        for text in texts:
            digest = hashlib.sha256((text or "").encode("utf-8")).digest()
            # Expand digest into dim floats in [0,1)
            vals = []
            seed = digest
            while len(vals) < self.dim:
                seed = hashlib.sha256(seed).digest()
                vals.extend(b / 255.0 for b in seed)
            vectors.append(vals[: self.dim])
        return np.asarray(vectors, dtype=np.float64)
