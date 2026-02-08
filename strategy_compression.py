"""
Memory Compression and Integration Strategy

This strategy compresses and integrates historical conversations through intelligent
algorithms, significantly reducing storage space and processing overhead while
retaining key information through multi-level compression mechanisms.
"""

import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from memory_strategy_base import BaseMemoryStrategy
from memory_utils import generate_text, get_openai_client, count_tokens


class CompressionMemory(BaseMemoryStrategy):
    """
    Memory compression strategy with intelligent information integration.

    Advantages:
    - Significant storage space reduction
    - Intelligent information merging
    - Dynamic importance scoring
    - Automatic redundancy filtering

    Disadvantages:
    - Complex compression algorithms
    - Potential information loss
    - Computational overhead for compression
    - Tuning required for optimal performance
    """

    STRATEGY_ID = "compression"
    STRATEGY_NAME = "Compression Memory"
    STRATEGY_CATEGORY = "Advanced"
    COMPLEXITY_LEVEL = "Complex"
    RECOMMENDED_USE_CASES = ["storage_optimization", "long_term_memory", "importance_filtering"]
    UI_COLOR = "#EF4444"
    UI_ICON = "compress"

    def __init__(
        self,
        compression_ratio: float = 0.5,
        importance_threshold: float = 0.7,
        client: Optional[OpenAI] = None
    ):
        """
        Initialize compression memory system.

        Args:
            compression_ratio: Target compression ratio (0.5 = 50% compression)
            importance_threshold: Threshold for importance scoring (0-1)
            client: Optional OpenAI client instance
        """
        self.compression_ratio = compression_ratio
        self.importance_threshold = importance_threshold
        self.client = client or get_openai_client()
        self.segment_pool: List[Dict[str, Any]] = []
        self.compressed_archive: List[Dict[str, Any]] = []
        self.importance_distribution: List[float] = []
        self.compression_events: List[Dict[str, Any]] = []
        self.compression_stats = {
            "original_tokens": 0,
            "compressed_tokens": 0,
            "compression_count": 0
        }
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [COMPRESS] prefix."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "COMPRESS"
        })

    def _track_compression_event(self, segments_compressed: int, original_tokens: int, compressed_tokens: int) -> None:
        """Log compression cycles."""
        self.compression_events.append({
            "event_id": len(self.compression_events) + 1,
            "segments_compressed": segments_compressed,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "timestamp": time.time()
        })

    def get_importance_distribution(self) -> Dict[str, Any]:
        """Return distribution of importance scores (buckets and average)."""
        if not self.importance_distribution:
            return {"avg_score": 0.0, "buckets": {}, "count": 0}
        avg = sum(self.importance_distribution) / len(self.importance_distribution)
        buckets = {"high": 0, "medium": 0, "low": 0}
        for s in self.importance_distribution:
            if s >= self.importance_threshold:
                buckets["high"] += 1
            elif s >= 0.4:
                buckets["medium"] += 1
            else:
                buckets["low"] += 1
        return {"avg_score": round(avg, 4), "buckets": buckets, "count": len(self.importance_distribution)}

    def estimate_space_savings(self) -> float:
        """Calculate space savings as percentage (0-100)."""
        orig = self.compression_stats["original_tokens"]
        comp = self.compression_stats["compressed_tokens"]
        if orig <= 0:
            return 0.0
        return round((1.0 - comp / orig) * 100.0, 2)

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add new conversation turn with importance scoring and compression triggers.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        importance_score = self._calculate_importance_score(user_input, ai_response)
        self.importance_distribution.append(importance_score)
        segment = {
            "user_input": user_input,
            "ai_response": ai_response,
            "importance_score": importance_score,
            "timestamp": len(self.segment_pool),
            "token_count": count_tokens(user_input + ai_response),
            "compressed": False
        }
        self.segment_pool.append(segment)
        self.compression_stats["original_tokens"] += segment["token_count"]
        self._log_operation("ADD_SEGMENT", {"importance": importance_score, "pool_size": len(self.segment_pool)})

        if len(self.segment_pool) >= 6:
            self._compress_memory_segments()

    def _calculate_importance_score(self, user_input: str, ai_response: str) -> float:
        """Calculate importance score for a conversation turn using LLM."""
        scoring_prompt = (
            f"Rate the importance of this conversation turn on a scale of 0.0 to 1.0. "
            f"Consider factors like: factual information, user preferences, decisions, "
            f"emotional significance, and future relevance. "
            f"Respond with only a number between 0.0 and 1.0.\n\n"
            f"User: {user_input}\n"
            f"AI: {ai_response}"
        )
        try:
            score_text = generate_text("You are an importance scoring expert.", scoring_prompt, self.client)
            score = float(score_text.strip())
            return max(0.0, min(1.0, score))
        except Exception:
            return 0.5

    def _compress_memory_segments(self) -> None:
        """Compress memory segments using intelligent algorithms."""
        high_importance = [s for s in self.segment_pool if s["importance_score"] >= self.importance_threshold]
        low_importance = [s for s in self.segment_pool if s["importance_score"] < self.importance_threshold]
        original_tokens = sum(s["token_count"] for s in self.segment_pool)
        compressed_tokens_this_cycle = 0

        if low_importance:
            compressed_segment = self._semantic_compression(low_importance)
            self.compressed_archive.append(compressed_segment)
            compressed_tokens_this_cycle += count_tokens(compressed_segment.get("content", ""))

        for segment in high_importance:
            segment["compressed"] = True
            content = f"User: {segment['user_input']}\nAI: {segment['ai_response']}"
            compressed_tokens_this_cycle += count_tokens(content)
            self.compressed_archive.append({
                "type": "high_importance",
                "content": content,
                "importance_score": segment["importance_score"],
                "timestamp": segment["timestamp"]
            })

        self.compression_stats["compressed_tokens"] += compressed_tokens_this_cycle
        self.compression_stats["compression_count"] += 1
        self._track_compression_event(len(self.segment_pool), original_tokens, compressed_tokens_this_cycle)
        self.segment_pool = []
        self._log_operation("COMPRESSION_CYCLE", {"segments_processed": len(high_importance) + len(low_importance)})
        print("[COMPRESS] Memory compression cycle completed.")

    def _semantic_compression(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform semantic-level compression on low importance segments."""
        combined_text = "\n".join([
            f"User: {s['user_input']}\nAI: {s['ai_response']}"
            for s in segments
        ])
        compression_prompt = (
            f"Compress the following conversations into a concise summary that retains "
            f"the key information while reducing length by approximately {int(self.compression_ratio * 100)}%. "
            f"Focus on facts, decisions, and context that might be relevant later.\n\n"
            f"Conversations:\n{combined_text}\n\n"
            f"Compressed Summary:"
        )
        compressed_content = generate_text("You are a memory compression expert.", compression_prompt, self.client)
        compressed_tokens = count_tokens(compressed_content)
        original_tokens = sum(s["token_count"] for s in segments)
        return {
            "type": "compressed",
            "content": compressed_content,
            "original_segments": len(segments),
            "compression_ratio": compressed_tokens / original_tokens if original_tokens > 0 else 0,
            "timestamp_range": (segments[0]["timestamp"], segments[-1]["timestamp"])
        }

    def get_context(self, query: str) -> str:
        """Retrieve relevant context from both active segments and compressed memory."""
        context_parts = []
        for compressed_segment in self.compressed_archive:
            if self._is_relevant_to_query(compressed_segment["content"], query):
                context_parts.append(f"[Compressed Memory]: {compressed_segment['content']}")
        for segment in self.segment_pool[-3:]:
            context_parts.append(f"User: {segment['user_input']}\nAI: {segment['ai_response']}")
        if not context_parts:
            return "No relevant information in memory yet."
        return "### Memory Context:\n" + "\n---\n".join(context_parts)

    def _is_relevant_to_query(self, content: str, query: str) -> bool:
        """Simple relevance check based on keyword overlap."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        overlap = len(query_words.intersection(content_words))
        return overlap >= 2

    def clear(self) -> None:
        """Reset all memory storage and statistics."""
        self.segment_pool = []
        self.compressed_archive = []
        self.importance_distribution = []
        self.compression_events = []
        self.compression_stats = {"original_tokens": 0, "compressed_tokens": 0, "compression_count": 0}
        self.operation_log = []
        print("[COMPRESS] Compression memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about memory compression."""
        active_segments = len(self.segment_pool)
        compressed_segments = len(self.compressed_archive)
        achieved_ratio = (
            self.compression_stats["compressed_tokens"] / self.compression_stats["original_tokens"]
            if self.compression_stats["original_tokens"] > 0 else 0
        )
        dist = self.get_importance_distribution()
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "CompressionMemory",
            "compression_metrics": {
                "target_ratio": self.compression_ratio,
                "achieved_ratio": round(achieved_ratio, 4),
                "compression_cycles": len(self.compression_events),
                "segments_active": active_segments,
                "segments_archived": compressed_segments,
                "space_savings_percent": self.estimate_space_savings()
            },
            "importance_analysis": {
                "avg_score": dist["avg_score"],
                "distribution": dist["buckets"]
            },
            "memory_size": f"{active_segments} active + {compressed_segments} compressed",
            "advantages": ["Space reduction", "Intelligent merging", "Redundancy filtering"],
            "disadvantages": ["Complex algorithms", "Information loss", "Computational overhead"]
        }
