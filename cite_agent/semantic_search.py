#!/usr/bin/env python3
"""
Semantic Search Module for Cite Agent
Provides embedding-based similarity search for papers and queries.

Uses lightweight sentence embeddings for local similarity matching,
enabling "find papers similar to this one" functionality.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import math


@dataclass
class EmbeddingEntry:
    """A cached embedding entry"""
    text: str
    vector: List[float]
    paper_id: Optional[str] = None
    title: Optional[str] = None
    created_at: float = 0.0


class SemanticSearch:
    """
    Semantic search engine using text embeddings.

    Uses a simple TF-IDF-like approach for lightweight local embeddings.
    No external API calls required.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cite_agent" / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._embeddings: Dict[str, EmbeddingEntry] = {}
        self._vocabulary: Dict[str, int] = {}
        self._idf_scores: Dict[str, float] = {}
        self._doc_count = 0

        # Load cached embeddings
        self._load_cache()

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase, split on non-alphanumeric"""
        import re
        text = text.lower()
        tokens = re.findall(r'\b[a-z0-9]+\b', text)
        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
                     'used', 'this', 'that', 'these', 'those', 'it', 'its', 'over', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below', 'between'}
        return [t for t in tokens if t not in stopwords and len(t) > 2]

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency"""
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        # Normalize
        max_freq = max(tf.values()) if tf else 1
        return {k: v / max_freq for k, v in tf.items()}

    def _update_vocabulary(self, tokens: List[str]):
        """Update global vocabulary and IDF scores"""
        unique_tokens = set(tokens)
        for token in unique_tokens:
            if token not in self._vocabulary:
                self._vocabulary[token] = len(self._vocabulary)
            self._idf_scores[token] = self._idf_scores.get(token, 0) + 1
        self._doc_count += 1

    def _compute_embedding(self, text: str) -> List[float]:
        """
        Compute TF-IDF embedding vector for text.
        Returns a sparse vector representation.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * min(len(self._vocabulary), 1000)

        # Update vocabulary
        self._update_vocabulary(tokens)

        # Compute TF-IDF
        tf = self._compute_tf(tokens)

        # Create vector (use top 1000 vocabulary terms)
        vocab_size = min(len(self._vocabulary), 1000)
        vector = [0.0] * vocab_size

        for token, freq in tf.items():
            if token in self._vocabulary:
                idx = self._vocabulary[token]
                if idx < vocab_size:
                    # IDF = log(N / df)
                    idf = math.log((self._doc_count + 1) / (self._idf_scores.get(token, 1) + 1))
                    vector[idx] = freq * idf

        # Normalize vector (L2 norm)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def add_paper(self, paper_id: str, title: str, abstract: str = "", authors: str = ""):
        """Add a paper to the semantic index"""
        import time

        # Combine text fields
        text = f"{title} {abstract} {authors}"
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Check if already indexed
        if text_hash in self._embeddings:
            return

        # Compute embedding
        vector = self._compute_embedding(text)

        # Store
        entry = EmbeddingEntry(
            text=text[:500],  # Truncate for storage
            vector=vector,
            paper_id=paper_id,
            title=title,
            created_at=time.time()
        )
        self._embeddings[text_hash] = entry

        # Persist
        self._save_cache()

    def add_query(self, query: str) -> str:
        """Add a query to enable finding similar queries later"""
        import time

        text_hash = hashlib.md5(query.encode()).hexdigest()

        if text_hash in self._embeddings:
            return text_hash

        vector = self._compute_embedding(query)

        entry = EmbeddingEntry(
            text=query[:500],
            vector=vector,
            created_at=time.time()
        )
        self._embeddings[text_hash] = entry
        self._save_cache()

        return text_hash

    def find_similar_papers(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find papers similar to the query.

        Returns list of (paper_id, title, similarity_score)
        """
        query_vector = self._compute_embedding(query)

        # Compute similarities
        similarities = []
        for text_hash, entry in self._embeddings.items():
            if entry.paper_id:  # Only papers
                sim = self._cosine_similarity(query_vector, entry.vector)
                similarities.append({
                    "paper_id": entry.paper_id,
                    "title": entry.title,
                    "similarity": sim
                })

        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        return similarities[:top_k]

    def find_similar_to_paper(self, paper_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find papers similar to a given paper"""
        # Find the paper's embedding
        target_entry = None
        for entry in self._embeddings.values():
            if entry.paper_id == paper_id:
                target_entry = entry
                break

        if not target_entry:
            return []

        # Find similar papers
        similarities = []
        for text_hash, entry in self._embeddings.items():
            if entry.paper_id and entry.paper_id != paper_id:
                sim = self._cosine_similarity(target_entry.vector, entry.vector)
                similarities.append({
                    "paper_id": entry.paper_id,
                    "title": entry.title,
                    "similarity": sim
                })

        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            # Pad shorter vector
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _save_cache(self):
        """Save embeddings to disk"""
        cache_file = self.cache_dir / "embeddings.json"

        # Convert to serializable format
        data = {
            "vocabulary": self._vocabulary,
            "idf_scores": self._idf_scores,
            "doc_count": self._doc_count,
            "embeddings": {
                k: asdict(v) for k, v in self._embeddings.items()
            }
        }

        with open(cache_file, 'w') as f:
            json.dump(data, f)

    def _load_cache(self):
        """Load embeddings from disk"""
        cache_file = self.cache_dir / "embeddings.json"

        if not cache_file.exists():
            return

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            self._vocabulary = data.get("vocabulary", {})
            self._idf_scores = data.get("idf_scores", {})
            self._doc_count = data.get("doc_count", 0)

            embeddings_data = data.get("embeddings", {})
            for k, v in embeddings_data.items():
                self._embeddings[k] = EmbeddingEntry(**v)
        except Exception:
            # Corrupted cache, start fresh
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Get semantic search statistics"""
        paper_count = sum(1 for e in self._embeddings.values() if e.paper_id)
        query_count = sum(1 for e in self._embeddings.values() if not e.paper_id)

        return {
            "total_embeddings": len(self._embeddings),
            "papers_indexed": paper_count,
            "queries_indexed": query_count,
            "vocabulary_size": len(self._vocabulary),
            "doc_count": self._doc_count
        }

    def clear(self):
        """Clear all embeddings"""
        self._embeddings = {}
        self._vocabulary = {}
        self._idf_scores = {}
        self._doc_count = 0

        cache_file = self.cache_dir / "embeddings.json"
        if cache_file.exists():
            cache_file.unlink()


# Global instance
_semantic_search: Optional[SemanticSearch] = None


def get_semantic_search() -> SemanticSearch:
    """Get or create global semantic search instance"""
    global _semantic_search
    if _semantic_search is None:
        _semantic_search = SemanticSearch()
    return _semantic_search


def add_paper_to_index(paper_id: str, title: str, abstract: str = "", authors: str = ""):
    """Add paper to semantic index"""
    search = get_semantic_search()
    search.add_paper(paper_id, title, abstract, authors)


def find_similar_papers(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Find papers similar to query"""
    search = get_semantic_search()
    return search.find_similar_papers(query, top_k)


def semantic_search_stats() -> Dict[str, Any]:
    """Get semantic search statistics"""
    search = get_semantic_search()
    return search.get_stats()
