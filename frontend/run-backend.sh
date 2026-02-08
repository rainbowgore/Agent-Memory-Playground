#!/usr/bin/env bash
# Run the FastAPI backend from the project root (one level up from frontend/).
# Use this when you are in the frontend/ directory.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
exec python api.py
