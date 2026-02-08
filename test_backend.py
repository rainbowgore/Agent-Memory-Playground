"""
Test Script for Agent Memory Playground Backend

This script verifies that all imports work correctly and agents can be created.
"""

import sys
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test that all strategy imports work."""
    print("Testing imports...")
    try:
        from strategy_sequential import SequentialMemory
        from strategy_sliding_window import SlidingWindowMemory
        from strategy_summarization import SummarizationMemory
        from strategy_retrieval import RetrievalMemory
        from strategy_compression import CompressionMemory
        from strategy_hierarchical import HierarchicalMemory
        from strategy_memory_augmented import MemoryAugmentedMemory
        from strategy_graph import GraphMemory
        from strategy_os_paging import OSMemory
        from conversation_agent import AIAgent
        from memory_utils import get_openai_client
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_agent():
    """Test creating a basic agent."""
    print("\nTesting basic agent creation...")
    try:
        from strategy_sequential import SequentialMemory
        from conversation_agent import AIAgent
        
        memory = SequentialMemory()
        agent = AIAgent(memory_strategy=memory)
        print("✓ Basic agent created successfully")
        return True
    except Exception as e:
        print(f"✗ Agent creation error: {e}")
        return False

def test_agent_with_params():
    """Test creating agents with different parameters."""
    print("\nTesting agents with parameters...")
    try:
        from strategy_sliding_window import SlidingWindowMemory
        from conversation_agent import AIAgent
        
        memory = SlidingWindowMemory(window_size=5)
        agent = AIAgent(
            memory_strategy=memory,
            system_prompt="You are a test assistant."
        )
        print("✓ Parameterized agent created successfully")
        return True
    except Exception as e:
        print(f"✗ Parameterized agent error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Agent Memory Playground Backend Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_agent,
        test_agent_with_params
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("=" * 60)
        return 0
    else:
        print(f"✗ Some tests failed ({passed}/{total} passed)")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
