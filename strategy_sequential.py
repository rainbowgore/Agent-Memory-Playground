"""
Sequential Memory Strategy

This is the most basic memory strategy that stores the entire conversation
history in chronological order. While it provides perfect recall, it's not
scalable as the context grows linearly with each conversation turn.
"""

import time
from typing import List, Dict, Any
from memory_strategy_base import BaseMemoryStrategy
from memory_utils import count_tokens


class SequentialMemory(BaseMemoryStrategy):
    """
    Sequential memory strategy that stores all conversation history.

    Advantages:
    - Simple implementation
    - Perfect recall of all conversations
    - Complete context preservation

    Disadvantages:
    - Linear token growth with conversation length
    - Expensive for long conversations
    - May hit token limits quickly
    """

    STRATEGY_ID = "sequential"
    STRATEGY_NAME = "Sequential Memory"
    STRATEGY_CATEGORY = "Basic"
    COMPLEXITY_LEVEL = "Simple"
    RECOMMENDED_USE_CASES = ["short_conversations", "complete_history", "debugging"]
    UI_COLOR = "#8B5CF6"
    UI_ICON = "scroll"

    def __init__(self):
        """Initialize memory with empty list to store conversation history."""
        self.full_history_buffer: List[Dict[str, str]] = []
        self.total_content_tokens = 0
        self.total_prompt_tokens = 0
        self.linear_growth_tracker: List[Dict[str, Any]] = []
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [SEQUENTIAL] prefix for unique identification."""
        entry = {
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "SEQUENTIAL"
        }
        self.operation_log.append(entry)

    def _track_linear_growth(self, turn_tokens: int) -> None:
        """Track token growth rate for linear metrics."""
        total_turns = len(self.full_history_buffer) // 2
        self.linear_growth_tracker.append({
            "turn": total_turns,
            "tokens_this_turn": turn_tokens,
            "cumulative_tokens": self.total_content_tokens
        })

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add new user-AI interaction to history.

        Each interaction is stored as two dictionary entries in the list.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        turn_tokens = count_tokens(user_input + ai_response)
        self.full_history_buffer.append({"role": "user", "content": user_input})
        self.full_history_buffer.append({"role": "assistant", "content": ai_response})
        self.total_content_tokens += turn_tokens
        self._track_linear_growth(turn_tokens)
        self._log_operation("ADD_TURN", {
            "messages_added": 2,
            "turn_tokens": turn_tokens,
            "total_turns": len(self.full_history_buffer) // 2
        })

    def get_context(self, query: str) -> str:
        """
        Retrieve entire conversation history formatted as a single string.

        The 'query' parameter is ignored since this strategy always
        returns the complete history.

        Args:
            query: Current user query (ignored in this strategy)

        Returns:
            Complete conversation history as formatted string
        """
        if not self.full_history_buffer:
            return "No conversation history yet."

        return "\n".join([
            f"{turn['role'].capitalize()}: {turn['content']}"
            for turn in self.full_history_buffer
        ])

    def clear(self) -> None:
        """Reset conversation history by clearing the list."""
        self.full_history_buffer = []
        self.total_content_tokens = 0
        self.total_prompt_tokens = 0
        self.linear_growth_tracker = []
        self.operation_log = []
        print("[SEQUENTIAL] Sequential memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        total_messages = len(self.full_history_buffer)
        total_turns = total_messages // 2
        growth_rate = 0.0
        projected_next_size = total_messages
        if len(self.linear_growth_tracker) >= 2:
            recent = self.linear_growth_tracker[-5:]
            tokens_added = sum(t["tokens_this_turn"] for t in recent)
            growth_rate = tokens_added / len(recent) if recent else 0
            projected_next_size = total_messages + 2 if growth_rate > 0 else total_messages

        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "SequentialMemory",
            "linear_metrics": {
                "total_turns": total_turns,
                "total_messages": total_messages,
                "growth_rate": round(growth_rate, 2),
                "projected_next_size": projected_next_size
            },
            "total_content_tokens": self.total_content_tokens,
            "total_prompt_tokens": self.total_prompt_tokens,
            "memory_size": f"{total_messages} messages",
            "operation_log": self.get_operation_log(),
            "advantages": ["Perfect recall", "Simple implementation"],
            "disadvantages": ["Linear token growth", "Not scalable"]
        }
