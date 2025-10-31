#!/bin/bash
# Start TestGPT Backend API Server

echo "🚀 Starting TestGPT Backend API..."

# Change to project directory
cd "$(dirname "$0")/.."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# Check database exists
if [ ! -f "frontend/lib/db/testgpt.db" ]; then
    echo "📁 Database not found. Creating..."
    python scripts/init_pr_test_db.py
fi

# Start server
echo ""
echo "🌐 Starting API server at http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
