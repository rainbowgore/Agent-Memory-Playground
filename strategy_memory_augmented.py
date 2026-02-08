"""
Memory-Augmented Memory Strategy

This strategy simulates memory-enhanced transformer behavior by maintaining
a short-term sliding window of recent conversations and a separate list of
"memory tokens" - important facts extracted from conversations.
"""

import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from memory_strategy_base import BaseMemoryStrategy
from strategy_sliding_window import SlidingWindowMemory
from memory_utils import generate_text, get_openai_client


class MemoryAugmentedMemory(BaseMemoryStrategy):
    """
    Memory-augmented strategy combining sliding window with persistent memory tokens.

    Advantages:
    - Excellent long-term retention of key information
    - Suitable for evolving long-term conversations
    - Intelligent fact extraction mechanism
    - Strong foundation for personal assistants

    Disadvantages:
    - More complex implementation
    - Additional LLM calls increase cost
    - Depends on fact extraction quality
    - May increase response time
    """

    STRATEGY_ID = "memory_augmented"
    STRATEGY_NAME = "Memory-Augmented"
    STRATEGY_CATEGORY = "Hybrid"
    COMPLEXITY_LEVEL = "Moderate"
    RECOMMENDED_USE_CASES = ["fact_retention", "personal_preferences", "persistent_knowledge"]
    UI_COLOR = "#EC4899"
    UI_ICON = "brain"

    def __init__(self, window_size: int = 2, client: Optional[OpenAI] = None):
        """
        Initialize memory-augmented system.

        Args:
            window_size: Number of recent turns to retain in short-term memory
            client: Optional OpenAI client instance
        """
        self.client = client or get_openai_client()
        self.recent_memory = SlidingWindowMemory(window_size=window_size)
        self.memory_tokens: List[str] = []
        self.fact_extraction_log: List[Dict[str, Any]] = []
        self.token_quality_scores: List[float] = []
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [MEM_AUG] prefix."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "MEM_AUG"
        })

    def _track_fact_extraction(self, fact: str, quality_score: float) -> None:
        """Log extracted facts and their quality score."""
        self.fact_extraction_log.append({
            "fact_preview": fact[:80],
            "quality_score": quality_score,
            "timestamp": time.time()
        })
        self.token_quality_scores.append(quality_score)

    def get_token_quality_distribution(self) -> Dict[str, Any]:
        """Return distribution of token quality scores."""
        if not self.token_quality_scores:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        return {
            "avg": round(sum(self.token_quality_scores) / len(self.token_quality_scores), 4),
            "min": round(min(self.token_quality_scores), 4),
            "max": round(max(self.token_quality_scores), 4),
            "count": len(self.token_quality_scores)
        }

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add latest turn to recent memory, then use LLM call to decide
        if new persistent memory tokens should be created from this interaction.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        self.recent_memory.add_message(user_input, ai_response)
        fact_extraction_prompt = (
            f"Analyze the following conversation turn. Does it contain a core fact, preference, or decision that should be remembered long-term? "
            f"Examples include user preferences ('I hate flying'), key decisions ('The budget is $1000'), or important facts ('My user ID is 12345').\n\n"
            f"Conversation Turn:\nUser: {user_input}\nAI: {ai_response}\n\n"
            f"If it contains such a fact, state the fact concisely in one sentence. Otherwise, respond with 'No important fact.'"
        )
        extracted_fact = generate_text(
            "You are a fact-extraction expert.",
            fact_extraction_prompt,
            self.client
        )
        if "no important fact" not in extracted_fact.lower():
            quality = min(1.0, len(extracted_fact.strip()) / 100.0) if extracted_fact.strip() else 0.5
            self._track_fact_extraction(extracted_fact.strip(), quality)
            self.memory_tokens.append(extracted_fact.strip())
            self._log_operation("FACT_EXTRACTED", {"preview": extracted_fact[:50], "quality": quality})
            print("[MEM_AUG] New memory token created.")
        self._log_operation("ADD_TURN", {"tokens_count": len(self.memory_tokens)})

    def get_context(self, query: str) -> str:
        """
        Construct context by combining short-term recent conversation
        with list of all long-term, persistent memory tokens.

        Args:
            query: Current user query

        Returns:
            Combined context from memory tokens and recent conversation
        """
        recent_context = self.recent_memory.get_context(query)
        if self.memory_tokens:
            memory_token_context = "\n".join([f"- {token}" for token in self.memory_tokens])
            return f"### Key Memory Tokens (Long-Term Facts):\n{memory_token_context}\n\n### Recent Conversation:\n{recent_context}"
        return f"### Recent Conversation:\n{recent_context}"

    def clear(self) -> None:
        """Reset both recent memory and memory tokens."""
        self.recent_memory.clear()
        self.memory_tokens = []
        self.fact_extraction_log = []
        self.token_quality_scores = []
        self.operation_log = []
        print("[MEM_AUG] Memory-augmented memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        recent_stats = self.recent_memory.get_memory_stats()
        num_tokens = len(self.memory_tokens)
        quality_dist = self.get_token_quality_distribution()
        recent_window_size = recent_stats.get("window_metrics", {}).get("utilization", 0)
        if not isinstance(recent_window_size, int):
            recent_window_size = len(getattr(self.recent_memory, "circular_buffer", []))
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "MemoryAugmentedMemory",
            "augmentation_metrics": {
                "memory_tokens_count": num_tokens,
                "facts_extracted": len(self.fact_extraction_log),
                "recent_window_size": recent_window_size,
                "token_quality_avg": quality_dist["avg"]
            },
            "recent_memory_stats": recent_stats,
            "memory_size": f"{num_tokens} memory tokens + recent window",
            "advantages": ["Long-term retention", "Intelligent extraction", "Personal assistant ready"],
            "disadvantages": ["Complex implementation", "Additional LLM calls", "Fact extraction dependent"]
        }
