"""
Base Memory Strategy Abstract Class

This module defines the abstract base class that all memory strategies must implement.
It ensures consistency and interchangeability between different memory optimization techniques.
"""

import abc
from typing import Any, Dict, List, Optional


class BaseMemoryStrategy(abc.ABC):
    """Abstract base class for all memory strategies."""

    # Class-level unique identifiers (each strategy defines these)
    STRATEGY_ID: str = "base"
    STRATEGY_NAME: str = "Base Strategy"
    STRATEGY_CATEGORY: str = "Abstract"
    COMPLEXITY_LEVEL: str = "N/A"
    RECOMMENDED_USE_CASES: List[str] = []
    UI_COLOR: str = "#CCCCCC"
    UI_ICON: str = ""

    @abc.abstractmethod
    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add a new user-AI interaction to the memory storage.
        
        Args:
            user_input: The user's message
            ai_response: The AI's response
        """
        pass
    
    @abc.abstractmethod
    def get_context(self, query: str) -> str:
        """
        Retrieve and format relevant context from memory for the LLM.
        
        Args:
            query: The current user query to find relevant context for
            
        Returns:
            Formatted context string to send to the LLM
        """
        pass
    
    @abc.abstractmethod
    def clear(self) -> None:
        """
        Reset the memory storage, useful for starting new conversations.
        """
        pass

    @abc.abstractmethod
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """
        Return strategy-specific operation log.

        Returns:
            List of operation log entries (each a dict with type, timestamp, details).
        """
        pass

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        return {
            "strategy_type": self.__class__.__name__,
            "strategy_id": getattr(self.__class__, "STRATEGY_ID", "base"),
            "memory_size": "Unknown"
        }
