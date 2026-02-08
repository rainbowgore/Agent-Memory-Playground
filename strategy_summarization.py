"""
Summarization Memory Strategy

This strategy manages long conversations by periodically summarizing conversation history.
It maintains a buffer of recent messages and triggers summarization when the buffer
reaches a threshold, using LLM to compress historical information intelligently.
"""

import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from memory_strategy_base import BaseMemoryStrategy
from memory_utils import generate_text, get_openai_client


class SummarizationMemory(BaseMemoryStrategy):
    """
    Summarization memory strategy that compresses conversation history using LLM.

    Advantages:
    - Manages long conversations efficiently
    - Retains key information through intelligent compression
    - Scalable token usage
    - Maintains conversation flow

    Disadvantages:
    - May lose details during summarization
    - Depends on LLM summarization quality
    - Additional LLM calls increase cost
    - Information decay over time
    """

    STRATEGY_ID = "summarization"
    STRATEGY_NAME = "Summarization Memory"
    STRATEGY_CATEGORY = "Intermediate"
    COMPLEXITY_LEVEL = "Moderate"
    RECOMMENDED_USE_CASES = ["long_conversations", "context_preservation", "cost_optimization"]
    UI_COLOR = "#10B981"
    UI_ICON = "doc"

    def __init__(self, summary_threshold: int = 4, client: Optional[OpenAI] = None):
        """
        Initialize summarization memory.

        Args:
            summary_threshold: Number of messages to accumulate before triggering summary
            client: Optional OpenAI client instance
        """
        self.summary_threshold = summary_threshold
        self.client = client or get_openai_client()
        self.cumulative_summary = ""
        self.pending_turns_buffer: List[Dict[str, str]] = []
        self.summary_versions: List[Dict[str, Any]] = []
        self.consolidation_events: List[Dict[str, Any]] = []
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [SUMMARIZE] prefix for unique identification."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "SUMMARIZE"
        })

    def _track_consolidation_event(self, buffer_size: int, new_summary_length: int) -> None:
        """Log when summaries happen."""
        self.consolidation_events.append({
            "event_id": len(self.consolidation_events) + 1,
            "buffer_messages_consumed": buffer_size,
            "new_summary_length": new_summary_length,
            "timestamp": time.time()
        })
        self.summary_versions.append({
            "version": len(self.summary_versions) + 1,
            "length": new_summary_length
        })

    def get_summary_quality_score(self) -> float:
        """Estimate summary quality (heuristic: length and number of consolidations)."""
        if not self.cumulative_summary:
            return 0.0
        length = len(self.cumulative_summary)
        consolidations = len(self.consolidation_events)
        if consolidations == 0:
            return min(1.0, length / 500.0)
        return min(1.0, (length / 300.0 + consolidations * 0.1) / 2.0)

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add new user-AI interaction to buffer.

        If buffer size reaches threshold, triggers memory consolidation process.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        self.pending_turns_buffer.append({"role": "user", "content": user_input})
        self.pending_turns_buffer.append({"role": "assistant", "content": ai_response})
        self._log_operation("ADD_TURN", {"buffer_size": len(self.pending_turns_buffer)})

        if len(self.pending_turns_buffer) >= self.summary_threshold:
            self._consolidate_memory()

    def _consolidate_memory(self) -> None:
        """
        Use LLM to summarize buffer contents and merge with existing summary.
        """
        buffer_size = len(self.pending_turns_buffer)
        buffer_text = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in self.pending_turns_buffer
        ])
        summarization_prompt = (
            f"You are a summarization expert. Your task is to create a concise summary of a conversation. "
            f"Combine the 'Previous Summary' with the 'New Conversation' into a single, updated summary. "
            f"Capture all key facts, names, decisions, and important details.\n\n"
            f"### Previous Summary:\n{self.cumulative_summary}\n\n"
            f"### New Conversation:\n{buffer_text}\n\n"
            f"### Updated Summary:"
        )
        new_summary = generate_text(
            "You are an expert summarization engine.",
            summarization_prompt,
            self.client
        )
        self.cumulative_summary = new_summary
        self._track_consolidation_event(buffer_size, len(new_summary))
        self.pending_turns_buffer = []
        self._log_operation("CONSOLIDATE", {"buffer_consumed": buffer_size, "summary_length": len(new_summary)})
        print("[SUMMARIZE] Memory consolidation triggered; new summary generated.")

    def get_context(self, query: str) -> str:
        """
        Construct context to send to LLM by combining long-term summary
        with short-term buffer of recent messages.

        Args:
            query: Current user query (ignored in this strategy)

        Returns:
            Combined context from summary and recent messages
        """
        buffer_text = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in self.pending_turns_buffer
        ])
        if self.cumulative_summary:
            return f"### Summary of Past Conversation:\n{self.cumulative_summary}\n\n### Recent Messages:\n{buffer_text}"
        return f"### Recent Messages:\n{buffer_text}" if buffer_text else "No conversation history yet."

    def clear(self) -> None:
        """Reset both summary and buffer."""
        self.cumulative_summary = ""
        self.pending_turns_buffer = []
        self.summary_versions = []
        self.consolidation_events = []
        self.operation_log = []
        print("[SUMMARIZE] Summarization memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        pending_size = len(self.pending_turns_buffer)
        summary_length = len(self.cumulative_summary)
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "SummarizationMemory",
            "summary_metrics": {
                "summary_length": summary_length,
                "pending_buffer_size": pending_size,
                "consolidations_count": len(self.consolidation_events),
                "summary_versions": len(self.summary_versions)
            },
            "summary_threshold": self.summary_threshold,
            "memory_size": f"Summary + {pending_size} buffered messages",
            "advantages": ["Efficient compression", "Retains key info", "Scalable"],
            "disadvantages": ["May lose details", "LLM dependent", "Additional cost"]
        }
