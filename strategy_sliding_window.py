"""
Sliding Window Memory Strategy

This strategy maintains only the most recent N conversation turns using a fixed-size
window. It prevents unbounded context growth but may lose important historical information.
"""

import time
from collections import deque
from typing import List, Dict, Any, Optional
from memory_strategy_base import BaseMemoryStrategy
from memory_utils import count_tokens


class SlidingWindowMemory(BaseMemoryStrategy):
    """
    Sliding window memory strategy that keeps only recent N conversation turns.

    Advantages:
    - Controlled memory usage
    - Predictable token consumption
    - Scalable for long conversations

    Disadvantages:
    - Loses old information
    - May forget important early context
    - Fixed window size may not suit all scenarios
    """

    STRATEGY_ID = "sliding_window"
    STRATEGY_NAME = "Sliding Window Memory"
    STRATEGY_CATEGORY = "Basic"
    COMPLEXITY_LEVEL = "Simple"
    RECOMMENDED_USE_CASES = ["real_time_chat", "bounded_memory", "streaming"]
    UI_COLOR = "#3B82F6"
    UI_ICON = "window"

    def __init__(self, window_size: int = 4):
        """
        Initialize memory with fixed-size deque.

        Args:
            window_size: Number of conversation turns to retain in memory.
                        A single turn includes one user message and one AI response.
        """
        self.window_size = window_size
        self.circular_buffer: deque = deque(maxlen=window_size)
        self.total_content_tokens = 0
        self.total_prompt_tokens = 0
        self.eviction_count = 0
        self.eviction_log: List[Dict[str, Any]] = []
        self.window_efficiency_tracker: List[Dict[str, Any]] = []
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [WINDOW] prefix for unique identification."""
        entry = {
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "WINDOW"
        }
        self.operation_log.append(entry)

    def _track_eviction(self, evicted_turn: List[Dict[str, str]]) -> None:
        """Log what was evicted when window is full."""
        self.eviction_count += 1
        summary = ""
        for msg in evicted_turn:
            summary += msg.get("content", "")[:50] + "... "
        self.eviction_log.append({
            "eviction_id": self.eviction_count,
            "turn_preview": summary.strip(),
            "timestamp": time.time()
        })
        self._log_operation("EVICTION", {"eviction_id": self.eviction_count, "preview": summary[:80]})

    def _calculate_window_efficiency(self) -> float:
        """Utilization percentage: how full the window is (0.0 to 1.0)."""
        if self.window_size <= 0:
            return 0.0
        return len(self.circular_buffer) / self.window_size

    def peek_oldest_entry(self) -> Optional[List[Dict[str, str]]]:
        """View next item to be evicted (oldest in window), or None if empty."""
        if not self.circular_buffer:
            return None
        return list(self.circular_buffer[0]) if self.circular_buffer else None

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add new conversation turn to history.

        If deque is full, the oldest turn is automatically removed.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        if len(self.circular_buffer) >= self.window_size and self.window_size > 0:
            oldest = self.peek_oldest_entry()
            if oldest:
                self._track_eviction(oldest)

        turn_data = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ]
        self.circular_buffer.append(turn_data)
        self.total_content_tokens += count_tokens(user_input + ai_response)
        eff = self._calculate_window_efficiency()
        self.window_efficiency_tracker.append({"utilization": eff, "turns": len(self.circular_buffer)})
        self._log_operation("ADD_TURN", {"utilization": eff, "turns": len(self.circular_buffer)})

    def get_context(self, query: str) -> str:
        """
        Retrieve conversation history within current window.

        The 'query' parameter is ignored in this strategy.

        Args:
            query: Current user query (ignored in this strategy)

        Returns:
            Recent conversation history as formatted string
        """
        if not self.circular_buffer:
            return "No conversation history yet."

        context_list = []
        for turn in self.circular_buffer:
            for message in turn:
                context_list.append(f"{message['role'].capitalize()}: {message['content']}")
        return "\n".join(context_list)

    def clear(self) -> None:
        """Reset conversation history by clearing the deque."""
        self.circular_buffer.clear()
        self.total_content_tokens = 0
        self.total_prompt_tokens = 0
        self.eviction_count = 0
        self.eviction_log = []
        self.window_efficiency_tracker = []
        self.operation_log = []
        print("[WINDOW] Sliding window memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        current_turns = len(self.circular_buffer)
        total_messages = sum(len(turn) for turn in self.circular_buffer)
        efficiency = self._calculate_window_efficiency()
        is_full = current_turns == self.window_size and self.window_size > 0

        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "SlidingWindowMemory",
            "window_metrics": {
                "capacity": self.window_size,
                "utilization": current_turns,
                "evictions": self.eviction_count,
                "efficiency": round(efficiency, 4),
                "is_full": is_full
            },
            "total_messages": total_messages,
            "total_content_tokens": self.total_content_tokens,
            "total_prompt_tokens": self.total_prompt_tokens,
            "memory_size": f"{current_turns}/{self.window_size} turns",
            "advantages": ["Controlled memory", "Predictable tokens", "Scalable"],
            "disadvantages": ["Loses old info", "Fixed window size"]
        }
