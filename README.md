# Agent Memory Playground

![Agent Memory Playground](agent-memory-playground.png)

Nine memory strategies. Two mischievous agents. One playground. No extra tokens to lose.

## Quick Start

- **Run:** `cp .env.example .env` (add keys), then `./start.sh`
- **Ports:** Backend 8000, frontend 3000
- **Manual:** Backend `python3 api.py`; frontend `cd frontend && npm install && npm run dev`

## Features

### Core Functionality

- **9 Memory Strategies**: Compare different approaches to managing conversation history
- **Dual Agent Comparison**: Run two agents side-by-side with different strategies
- **Real-time Performance Metrics**: Track retrieval time, generation time, and token usage
- **Interactive Dark UI**: Modern minimalist design with glassmorphism effects

### Memory Strategies

#### Basic

- **Sequential Memory**: Stores complete conversation history
- **Sliding Window**: Maintains only the N most recent turns

#### Intermediate

- **Summarization Memory**: Periodically summarizes old conversations
- **OS-Style Paging**: Simulates RAM/disk with intelligent paging

#### Advanced

- **RAG Memory**: Vector-based semantic search
- **Compression Memory**: Intelligent information compression
- **Graph Knowledge Memory**: Relationship-based knowledge graph

#### Hybrid

- **Hierarchical Memory**: Combines working memory + long-term storage
- **Memory-Augmented**: Sliding window + persistent memory tokens

## Keyboard Shortcuts

| Shortcut                   | Action                          |
| -------------------------- | ------------------------------- |
| `Cmd/Ctrl + Enter`         | Send message (to focused agent) |
| `Cmd/Ctrl + Shift + Enter` | Send message to both agents     |
| `Cmd/Ctrl + K`             | Clear agent memory              |
| `Cmd/Ctrl + /`             | Focus message input             |

## Technology Stack

### Backend

- **FastAPI** - Modern Python web framework
- **OpenAI API** - LLM and embeddings
- **FAISS** - Vector similarity search
- **NetworkX** - Graph-based memory
- **Tiktoken** - Token counting

### Key Endpoints

```
GET  /api/strategies              # List available strategies
POST /api/agent/create            # Create agent with strategy
POST /api/chat                    # Send message to agent
GET  /api/agent/{id}/stats        # Get memory statistics
POST /api/agent/{id}/clear        # Clear agent memory
DELETE /api/agent/{id}            # Delete agent
```

## Usage

1. **Start both servers** (backend on 8000, frontend on 3000)
2. **Configure Agent A**: Select "Sequential Memory" strategy
3. **Configure Agent B**: Select "Sliding Window" strategy
4. **Send the same message** to both agents
5. **Compare responses** and observe memory behavior
6. **Monitor metrics**: Check retrieval time, generation time, token usage
7. **Try different strategies** to see how they handle long conversations

### Using the Playground

- **Config panel**: Use the config panel to choose memory strategy and model for Agent A and Agent B. Each agent can use a different strategy and model.
- **Shared input**: One message input at the bottom sends to the focused agent. **Cmd/Ctrl + Enter** sends to that agent; **Cmd/Ctrl + Shift + Enter** sends the same message to both agents at once.
- **Metrics**: Retrieval time, generation time, and token usage appear below each agent's chat so you can compare cost and latency.
- **Backend offline**: If the UI shows "Backend offline", the frontend cannot reach the API. Start the backend first (e.g. `./start.sh` or `python api.py`) and ensure it is running on port 8000 (or set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to match).

## Agent Performance

The metrics area under each agent window will show:

- **Retrieval time** – Time to fetch context from memory (e.g. vector search for RAG, graph lookup) before the LLM runs.
- **Generation time** – Time the LLM took to produce the reply.
- **Token usage** – Prompt and completion tokens so you can compare strategies by latency and token use.

###

---

###

**Built for devs allergic to misbehaving agents**
