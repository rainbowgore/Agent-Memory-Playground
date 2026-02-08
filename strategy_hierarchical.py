"""
Hierarchical Memory Strategy

This strategy combines multiple memory types into a layered system that mimics
human memory patterns with working memory (short-term) and long-term memory layers.
"""

import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from memory_strategy_base import BaseMemoryStrategy
from strategy_sliding_window import SlidingWindowMemory
from strategy_retrieval import RetrievalMemory
from memory_utils import get_openai_client


class HierarchicalMemory(BaseMemoryStrategy):
    """
    Hierarchical memory strategy combining working memory and long-term memory.

    Advantages:
    - Multi-level information processing
    - Intelligent information promotion
    - Combines strengths of multiple strategies
    - Resembles human cognitive patterns

    Disadvantages:
    - Complex implementation
    - Multiple memory systems to manage
    - Promotion logic may need tuning
    - Higher computational overhead
    """

    STRATEGY_ID = "hierarchical"
    STRATEGY_NAME = "Hierarchical Memory"
    STRATEGY_CATEGORY = "Hybrid"
    COMPLEXITY_LEVEL = "Complex"
    RECOMMENDED_USE_CASES = ["personal_assistant", "multi_tier_storage", "intelligent_routing"]
    UI_COLOR = "#8B5CF6"
    UI_ICON = "tiers"

    def __init__(
        self,
        window_size: int = 2,
        k: int = 2,
        embedding_dim: int = 1536,
        client: Optional[OpenAI] = None
    ):
        """
        Initialize hierarchical memory system.

        Args:
            window_size: Size of short-term working memory (in turns)
            k: Number of documents to retrieve from long-term memory
            embedding_dim: Embedding vector dimension for long-term memory
            client: Optional OpenAI client instance
        """
        self.client = client or get_openai_client()
        self.working_memory = SlidingWindowMemory(window_size=window_size)
        self.long_term_memory = RetrievalMemory(k=k, embedding_dim=embedding_dim, client=self.client)
        self.promotion_keywords = ["remember", "rule", "preference", "always", "never", "allergic", "important"]
        self.promotion_events: List[Dict[str, Any]] = []
        self.tier_access_counts = {"working": 0, "long_term": 0}
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [HIERARCHICAL] prefix."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "HIERARCHICAL"
        })

    def _track_promotion_event(self, user_input_preview: str) -> None:
        """Log when items are promoted to long-term memory."""
        self.promotion_events.append({
            "event_id": len(self.promotion_events) + 1,
            "preview": user_input_preview[:80],
            "timestamp": time.time()
        })

    def get_tier_utilization(self) -> Dict[str, Any]:
        """Usage stats per tier (working vs long-term)."""
        working_stats = self.working_memory.get_memory_stats()
        long_term_stats = self.long_term_memory.get_memory_stats()
        total_access = self.tier_access_counts["working"] + self.tier_access_counts["long_term"]
        ratio = (
            self.tier_access_counts["long_term"] / total_access
            if total_access > 0 else 0.0
        )
        return {
            "working_accesses": self.tier_access_counts["working"],
            "long_term_accesses": self.tier_access_counts["long_term"],
            "tier_access_ratio": round(ratio, 4),
            "working_stats": working_stats,
            "long_term_stats": long_term_stats
        }

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add messages to working memory and conditionally promote to long-term memory.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        self.working_memory.add_message(user_input, ai_response)
        if any(keyword in user_input.lower() for keyword in self.promotion_keywords):
            self._track_promotion_event(user_input)
            self.long_term_memory.add_message(user_input, ai_response)
            self._log_operation("PROMOTION", {"preview": user_input[:50]})
            print("[HIERARCHICAL] Promoting message to long-term storage.")
        self._log_operation("ADD_TURN", {"promoted": any(k in user_input.lower() for k in self.promotion_keywords)})

    def get_context(self, query: str) -> str:
        """
        Construct rich context by combining relevant information from both memory layers.

        Args:
            query: Current user query

        Returns:
            Combined context from long-term and short-term memory
        """
        self.tier_access_counts["working"] += 1
        working_context = self.working_memory.get_context(query)
        self.tier_access_counts["long_term"] += 1
        long_term_context = self.long_term_memory.get_context(query)

        if ("No information in memory yet" in long_term_context or
                "Could not find any relevant information" in long_term_context):
            return f"### Recent Context:\n{working_context}"
        return f"### Long-Term Context:\n{long_term_context}\n\n### Recent Context:\n{working_context}"

    def clear(self) -> None:
        """Reset both working memory and long-term memory."""
        self.working_memory.clear()
        self.long_term_memory.clear()
        self.promotion_events = []
        self.tier_access_counts = {"working": 0, "long_term": 0}
        self.operation_log = []
        print("[HIERARCHICAL] Hierarchical memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage from both layers.

        Returns:
            Dictionary containing memory statistics
        """
        utilization = self.get_tier_utilization()
        working_stats = self.working_memory.get_memory_stats()
        long_term_stats = self.long_term_memory.get_memory_stats()
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "HierarchicalMemory",
            "tier_metrics": {
                "working_memory": working_stats,
                "long_term_memory": long_term_stats,
                "promotions": len(self.promotion_events),
                "tier_access_ratio": utilization["tier_access_ratio"]
            },
            "promotion_keywords": self.promotion_keywords,
            "memory_size": f"Working: {working_stats.get('memory_size', 'N/A')}, Long-term: {long_term_stats.get('memory_size', 'N/A')}",
            "advantages": ["Multi-level processing", "Intelligent promotion", "Human-like patterns"],
            "disadvantages": ["Complex implementation", "Multiple systems", "Overhead"]
        }
