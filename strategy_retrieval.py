"""
Retrieval-based Memory Strategy

This strategy implements the core concept of Retrieval-Augmented Generation (RAG).
It converts conversations into vector embeddings and uses similarity search to find
the most relevant historical interactions for any given query.
"""

import time
import hashlib
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from openai import OpenAI
from memory_strategy_base import BaseMemoryStrategy
from memory_utils import generate_embedding, get_openai_client


class RetrievalMemory(BaseMemoryStrategy):
    """
    Retrieval-based memory strategy using vector embeddings and similarity search.

    Advantages:
    - Semantic understanding of queries
    - Efficient retrieval of relevant information
    - Scalable to large conversation histories
    - Industry standard for RAG applications

    Disadvantages:
    - Complex implementation
    - Requires embedding model
    - Dependent on embedding quality
    - Additional computational overhead
    """

    STRATEGY_ID = "retrieval_rag"
    STRATEGY_NAME = "Retrieval (RAG) Memory"
    STRATEGY_CATEGORY = "Advanced"
    COMPLEXITY_LEVEL = "Complex"
    RECOMMENDED_USE_CASES = ["knowledge_base", "semantic_search", "large_history"]
    UI_COLOR = "#F59E0B"
    UI_ICON = "search"

    def __init__(self, k: int = 2, embedding_dim: int = 1536, client: Optional[OpenAI] = None):
        """
        Initialize retrieval memory system.

        Args:
            k: Number of most relevant documents to retrieve for a given query
            embedding_dim: Dimension of embedding vectors (1536 for text-embedding-3-small)
            client: Optional OpenAI client instance
        """
        self.k = k
        self.embedding_dim = embedding_dim
        self.client = client or get_openai_client()
        self.document_registry: List[str] = []
        self.vector_store = faiss.IndexFlatL2(self.embedding_dim)
        self.embedding_cache: Dict[str, List[float]] = {}
        self.retrieval_history: List[Dict[str, Any]] = []
        self.cache_hits = 0
        self.operation_log: List[Dict[str, Any]] = []

    def _cache_key(self, text: str) -> str:
        """Generate cache key for embedding lookup."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [RETRIEVAL] prefix."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "RETRIEVAL"
        })

    def _track_retrieval(self, query: str, results: List[str], elapsed: float) -> None:
        """Log retrieval events."""
        self.retrieval_history.append({
            "query_preview": query[:80],
            "result_count": len(results),
            "elapsed_seconds": round(elapsed, 4),
            "timestamp": time.time()
        })

    def get_cache_efficiency(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        total_lookups = len(self.retrieval_history) + len(self.document_registry) * 2
        if total_lookups <= 0:
            return 0.0
        return self.cache_hits / max(1, total_lookups)

    def visualize_vector_space(self) -> Dict[str, Any]:
        """Return data for vector space visualization (document count, dimensions)."""
        return {
            "num_vectors": self.vector_store.ntotal,
            "embedding_dim": self.embedding_dim,
            "document_count": len(self.document_registry),
            "cache_size": len(self.embedding_cache)
        }

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add new conversation turn to memory.

        Each part of the turn (user input and AI response) is embedded
        and indexed separately for fine-grained retrieval.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        docs_to_add = [
            f"User said: {user_input}",
            f"AI responded: {ai_response}"
        ]
        for doc in docs_to_add:
            cache_key = self._cache_key(doc)
            if cache_key in self.embedding_cache:
                self.cache_hits += 1
                embedding = self.embedding_cache[cache_key]
            else:
                embedding = generate_embedding(doc, self.client)
                if embedding:
                    self.embedding_cache[cache_key] = embedding
            if embedding:
                self.document_registry.append(doc)
                vector = np.array([embedding], dtype='float32')
                self.vector_store.add(vector)
        self._log_operation("ADD_DOCUMENTS", {"docs_added": len(docs_to_add), "total_docs": len(self.document_registry)})

    def get_context(self, query: str) -> str:
        """
        Find k most relevant documents from memory based on semantic similarity to query.

        Args:
            query: Current user query to find relevant context for

        Returns:
            Formatted string containing most relevant retrieved information
        """
        if self.vector_store.ntotal == 0:
            return "No information in memory yet."

        start = time.time()
        cache_key = self._cache_key(query)
        if cache_key in self.embedding_cache:
            self.cache_hits += 1
            query_embedding = self.embedding_cache[cache_key]
        else:
            query_embedding = generate_embedding(query, self.client)
            if query_embedding:
                self.embedding_cache[cache_key] = query_embedding
        if not query_embedding:
            return "Could not process query for retrieval."

        query_vector = np.array([query_embedding], dtype='float32')
        distances, indices = self.vector_store.search(query_vector, self.k)
        retrieved_docs = [
            self.document_registry[i] for i in indices[0]
            if i != -1 and i < len(self.document_registry)
        ]
        elapsed = time.time() - start
        self._track_retrieval(query, retrieved_docs, elapsed)
        self._log_operation("RETRIEVE", {"k": self.k, "results": len(retrieved_docs), "elapsed": round(elapsed, 4)})

        if not retrieved_docs:
            return "Could not find any relevant information in memory."
        return "### Relevant Information Retrieved from Memory:\n" + "\n---\n".join(retrieved_docs)

    def clear(self) -> None:
        """Reset both document storage and FAISS index."""
        self.document_registry = []
        self.vector_store = faiss.IndexFlatL2(self.embedding_dim)
        self.embedding_cache = {}
        self.retrieval_history = []
        self.cache_hits = 0
        self.operation_log = []
        print("[RETRIEVAL] Retrieval memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        num_docs = len(self.document_registry)
        num_vectors = self.vector_store.ntotal
        avg_retrieval_time = 0.0
        if self.retrieval_history:
            avg_retrieval_time = sum(h["elapsed_seconds"] for h in self.retrieval_history) / len(self.retrieval_history)
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "RetrievalMemory",
            "vector_metrics": {
                "total_vectors": num_vectors,
                "documents_count": num_docs,
                "cache_hits": self.cache_hits,
                "cache_efficiency": round(self.get_cache_efficiency(), 4),
                "avg_retrieval_time": round(avg_retrieval_time, 4)
            },
            "k": self.k,
            "embedding_dim": self.embedding_dim,
            "memory_size": f"{num_docs} documents, {num_vectors} vectors",
            "advantages": ["Semantic search", "Scalable", "Relevant retrieval"],
            "disadvantages": ["Complex implementation", "Embedding dependent"]
        }
