"""
FastAPI Backend for Agent Memory Playground

This API server provides REST endpoints for the frontend to interact with
various memory strategy implementations.
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import all memory strategies
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
from llm_provider import LLMProvider

# Load environment variables
load_dotenv()

# --------------------------------------------------------------------------------------
# FastAPI App Configuration
# --------------------------------------------------------------------------------------

app = FastAPI(
    title="Agent Memory Playground API",
    description="Backend API for testing different AI agent memory strategies",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------------
# Global State Management
# --------------------------------------------------------------------------------------

# Store active agent instances by session ID with metadata
active_agents: Dict[str, Dict[str, Any]] = {}

# Strategy class mapping
STRATEGY_CLASSES = {
    "SequentialMemory": SequentialMemory,
    "SlidingWindowMemory": SlidingWindowMemory,
    "SummarizationMemory": SummarizationMemory,
    "RetrievalMemory": RetrievalMemory,
    "CompressionMemory": CompressionMemory,
    "HierarchicalMemory": HierarchicalMemory,
    "MemoryAugmentedMemory": MemoryAugmentedMemory,
    "GraphMemory": GraphMemory,
    "OSMemory": OSMemory,
}

# Load playground configuration
with open("playground_config.json", "r") as f:
    PLAYGROUND_CONFIG = json.load(f)

# --------------------------------------------------------------------------------------
# Pydantic Models
# --------------------------------------------------------------------------------------

class CreateAgentRequest(BaseModel):
    session_id: str
    strategy_type: str
    model: str = "gpt-4o-mini"
    strategy_params: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = """You are a helpful AI assistant.

IMPORTANT GUIDELINES:
1. When answering questions, recall facts EXACTLY as stated in the memory context.
2. Do NOT infer, calculate, or update facts based on new information unless explicitly asked.
3. If asked for "direct reports", only list people who report DIRECTLY to that person, not indirect reports through another manager.
4. Do NOT perform arithmetic on factual data - if the memory says "12 developers" and later mentions "hired 3 new", the answer to "how many developers" is still "12" unless explicitly told the new total.
"""

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    retrieval_time: float
    generation_time: float
    prompt_tokens: int
    context: str

class MemoryStatsResponse(BaseModel):
    stats: Dict[str, Any]

# --------------------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------------------

def create_memory_strategy(strategy_class_name: str, params: Optional[Dict[str, Any]] = None):
    """
    Create an instance of a memory strategy with given parameters.
    
    Args:
        strategy_class_name: Name of the strategy class
        params: Optional parameters for strategy initialization
        
    Returns:
        Instance of the memory strategy
    """
    if strategy_class_name not in STRATEGY_CLASSES:
        raise ValueError(f"Unknown strategy: {strategy_class_name}")
    
    strategy_class = STRATEGY_CLASSES[strategy_class_name]
    
    # Use default params if none provided
    if params is None:
        params = {}
    
    # Get client for strategies that need it
    client = get_openai_client()
    
    # Create strategy with appropriate parameters
    if strategy_class_name in ["SummarizationMemory", "RetrievalMemory", 
                                "CompressionMemory", "HierarchicalMemory", 
                                "MemoryAugmentedMemory", "GraphMemory"]:
        params["client"] = client
    
    return strategy_class(**params)

# --------------------------------------------------------------------------------------
# API Endpoints
# --------------------------------------------------------------------------------------

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "Agent Memory Playground API",
        "version": "1.0.0"
    }

@app.get("/api/strategies")
async def get_strategies():
    """
    Get list of all available memory strategies with their configurations.
    
    Returns:
        JSON object containing all strategy configurations
    """
    return PLAYGROUND_CONFIG

@app.post("/api/agent/create")
async def create_agent(request: CreateAgentRequest):
    """
    Create a new agent instance with specified memory strategy.
    
    Args:
        request: CreateAgentRequest containing session_id, strategy_type, model, and optional params
        
    Returns:
        Success message with agent configuration
    """
    try:
        # Get appropriate client based on model (reads from environment variables)
        client, provider_type = LLMProvider.get_client(request.model)
        
        # Get strategy configuration
        strategy_id = request.strategy_type
        if strategy_id not in PLAYGROUND_CONFIG["strategies"]:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {strategy_id}")
        
        strategy_config = PLAYGROUND_CONFIG["strategies"][strategy_id]
        class_name = strategy_config["class_name"]
        
        # Create memory strategy instance with appropriate client
        # Only pass client to strategies that need it
        params = request.strategy_params or {}
        
        # Strategies that need the client parameter
        strategies_needing_client = [
            "RetrievalMemory",
            "SummarizationMemory", 
            "GraphMemory",
            "HierarchicalMemory",
            "MemoryAugmentedMemory",
            "CompressionMemory"
        ]
        
        if class_name in strategies_needing_client:
            params["client"] = client
            
        memory_strategy = create_memory_strategy(class_name, params)
        
        # Create agent with the memory strategy and provider-specific client
        agent = AIAgent(
            memory_strategy=memory_strategy,
            system_prompt=request.system_prompt,
            client=client
        )
        
        # Store agent with metadata in global state
        active_agents[request.session_id] = {
            "agent": agent,
            "model": request.model,
            "provider": provider_type,
            "client": client,
            "strategy": strategy_id
        }
        
        return {
            "status": "success",
            "message": f"Agent created with {strategy_config['display_name']} using {request.model}",
            "session_id": request.session_id,
            "strategy": strategy_id,
            "strategy_name": strategy_config["display_name"],
            "model": request.model,
            "provider": provider_type
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to an agent and get a response.
    
    Args:
        request: ChatRequest containing session_id and message
        
    Returns:
        ChatResponse with AI response and performance metrics
    """
    try:
        # Check if agent exists
        if request.session_id not in active_agents:
            raise HTTPException(
                status_code=404, 
                detail="Agent not found. Please create an agent first."
            )
        
        agent_data = active_agents[request.session_id]
        agent = agent_data["agent"]
        
        # Get response from agent
        result = agent.chat(request.message, verbose=False)
        
        return ChatResponse(
            response=result["ai_response"],
            retrieval_time=result["retrieval_time"],
            generation_time=result["generation_time"],
            prompt_tokens=result["prompt_tokens"],
            context=result["context"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/api/agent/{session_id}/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(session_id: str):
    """
    Get memory statistics for an agent.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        MemoryStatsResponse containing current memory statistics
    """
    try:
        if session_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = active_agents[session_id]["agent"]
        stats = agent.get_memory_stats()
        
        return MemoryStatsResponse(stats=stats)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.post("/api/agent/{session_id}/clear")
async def clear_memory(session_id: str):
    """
    Clear an agent's memory.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Success message
    """
    try:
        if session_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = active_agents[session_id]["agent"]
        agent.clear_memory()
        
        return {
            "status": "success",
            "message": "Memory cleared successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@app.delete("/api/agent/{session_id}")
async def delete_agent(session_id: str):
    """
    Delete an agent instance.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Success message
    """
    try:
        if session_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        del active_agents[session_id]
        
        return {
            "status": "success",
            "message": "Agent deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting agent: {str(e)}")

@app.post("/api/agent/{session_id}/system-prompt")
async def update_system_prompt(session_id: str, system_prompt: str):
    """
    Update an agent's system prompt.
    
    Args:
        session_id: Unique session identifier
        system_prompt: New system prompt
        
    Returns:
        Success message
    """
    try:
        if session_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = active_agents[session_id]["agent"]
        agent.set_system_prompt(system_prompt)
        
        return {
            "status": "success",
            "message": "System prompt updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating system prompt: {str(e)}")

# --------------------------------------------------------------------------------------
# Run Server
# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
