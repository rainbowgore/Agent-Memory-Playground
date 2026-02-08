#!/bin/bash

# --------------------------------------------------------------------------------------
# Agent Memory Playground - Start Backend + Frontend
# --------------------------------------------------------------------------------------

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1

echo "Agent Memory Playground - Starting backend and frontend"
echo ""

# --------------------------------------------------------------------------------------
# Kill any existing processes
# --------------------------------------------------------------------------------------
echo "Checking for existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "Killed existing backend on port 8000" || true
pkill -f "next dev" 2>/dev/null && echo "Killed existing Next.js dev server" || true
sleep 1

# --------------------------------------------------------------------------------------
# Backend checks
# --------------------------------------------------------------------------------------
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Create a .env file with OPENAI_API_KEY=sk-..."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install Python 3.8+"
    exit 1
fi

python3 -c "import fastapi" 2>/dev/null || {
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
}

# --------------------------------------------------------------------------------------
# Start backend in background
# --------------------------------------------------------------------------------------
echo "Starting backend on http://localhost:8000"
python3 api.py &
BACKEND_PID=$!

# Give backend a moment to bind
sleep 2
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend failed to start."
    exit 1
fi

# --------------------------------------------------------------------------------------
# Frontend checks and start
# --------------------------------------------------------------------------------------
cd "$ROOT/frontend" || exit 1
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting frontend on http://localhost:3000"
echo "Backend: http://localhost:8000  |  API docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop both."
echo ""

trap 'kill $BACKEND_PID 2>/dev/null' EXIT

npm run dev
