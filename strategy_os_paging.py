"""
Operating System-like Memory Management Strategy

This strategy simulates how computer operating systems manage memory with
RAM (active memory) and disk (passive memory), implementing paging mechanisms
for intelligent memory management.
"""

import time
from collections import deque
from typing import Dict, Any, Optional, Tuple, List
from memory_strategy_base import BaseMemoryStrategy


class OSMemory(BaseMemoryStrategy):
    """
    OS-like memory management strategy simulating RAM and disk storage.

    Advantages:
    - Scalable memory management
    - Intelligent paging system
    - Efficient active context
    - Nearly unlimited memory capacity

    Disadvantages:
    - Complex paging logic
    - May miss relevant passive information
    - Requires tuning of RAM size
    - Page fault overhead
    """

    STRATEGY_ID = "os_paging"
    STRATEGY_NAME = "OS-Style Paging Memory"
    STRATEGY_CATEGORY = "Intermediate"
    COMPLEXITY_LEVEL = "Moderate"
    RECOMMENDED_USE_CASES = ["very_long_conversations", "selective_recall", "lru_management"]
    UI_COLOR = "#14B8A6"
    UI_ICON = "disk"

    def __init__(self, ram_size: int = 2):
        """
        Initialize OS-like memory system.

        Args:
            ram_size: Maximum number of conversation turns to retain in active memory (RAM)
        """
        self.ram_size = ram_size
        self.ram_storage: deque = deque()
        self.disk_storage: Dict[int, str] = {}
        self.turn_count = 0
        self.page_fault_log: List[Dict[str, Any]] = []
        self.lru_stats = {"hits": 0, "misses": 0}
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [OS_PAGE] prefix."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "OS_PAGE"
        })

    def _track_page_fault(self, turn_id: int, data_preview: str) -> None:
        """Log page faults (when loading from disk)."""
        self.page_fault_log.append({
            "turn_id": turn_id,
            "data_preview": data_preview[:80],
            "timestamp": time.time()
        })

    def get_memory_distribution(self) -> Dict[str, Any]:
        """RAM vs disk breakdown and paging stats."""
        ram_util = len(self.ram_storage)
        disk_pages = len(self.disk_storage)
        total = self.lru_stats["hits"] + self.lru_stats["misses"]
        lru_efficiency = self.lru_stats["hits"] / total if total > 0 else 0.0
        return {
            "ram_capacity": self.ram_size,
            "ram_utilization": ram_util,
            "disk_pages": disk_pages,
            "page_faults_count": len(self.page_fault_log),
            "lru_efficiency": round(lru_efficiency, 4)
        }

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add turn to active memory, page out oldest turn to passive memory if RAM is full.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        turn_id = self.turn_count
        turn_data = f"User: {user_input}\nAI: {ai_response}"

        if len(self.ram_storage) >= self.ram_size:
            lru_turn_id, lru_turn_data = self.ram_storage.popleft()
            self.disk_storage[lru_turn_id] = lru_turn_data
            self._log_operation("PAGE_OUT", {"turn_id": lru_turn_id})
            print("[OS_PAGE] Paging out turn to passive storage.")

        self.ram_storage.append((turn_id, turn_data))
        self.turn_count += 1
        self._log_operation("ADD_TURN", {"turn_id": turn_id})

    def get_context(self, query: str) -> str:
        """
        Provide RAM context and simulate page faults by pulling from passive memory if needed.

        Args:
            query: Current user query

        Returns:
            Context from active memory and any paged-in passive memory
        """
        active_context = "\n".join([data for _, data in self.ram_storage])
        paged_in_context = ""
        query_words = [word.lower() for word in query.split() if len(word) > 3]

        for turn_id, data in self.disk_storage.items():
            if any(word in data.lower() for word in query_words):
                self._track_page_fault(turn_id, data)
                paged_in_context += f"\n(Paged in from Turn {turn_id}): {data}"
                print("[OS_PAGE] Page fault: paging in from passive storage.")

        if paged_in_context:
            self.lru_stats["misses"] += 1
            self._log_operation("PAGE_FAULT", {"paged_in": True})
            return f"### Active Memory (RAM):\n{active_context}\n\n### Paged-In from Passive Memory (Disk):\n{paged_in_context}"
        self.lru_stats["hits"] += 1
        return f"### Active Memory (RAM):\n{active_context}" if active_context else "No information in memory yet."

    def clear(self) -> None:
        """Clear both active and passive memory storage."""
        self.ram_storage.clear()
        self.disk_storage = {}
        self.turn_count = 0
        self.page_fault_log = []
        self.lru_stats = {"hits": 0, "misses": 0}
        self.operation_log = []
        print("[OS_PAGE] OS-like memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.

        Returns:
            Dictionary containing memory statistics
        """
        dist = self.get_memory_distribution()
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "OSMemory",
            "paging_metrics": {
                "ram_capacity": dist["ram_capacity"],
                "ram_utilization": dist["ram_utilization"],
                "disk_pages": dist["disk_pages"],
                "page_faults": dist["page_faults_count"],
                "lru_efficiency": dist["lru_efficiency"]
            },
            "total_turns": self.turn_count,
            "memory_size": f"{dist['ram_utilization']} in RAM, {dist['disk_pages']} on disk",
            "advantages": ["Scalable management", "Intelligent paging", "Unlimited capacity"],
            "disadvantages": ["Complex paging", "May miss passive info", "Page fault overhead"]
        }
