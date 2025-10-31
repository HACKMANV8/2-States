#!/bin/bash

# TestGPT Backend Startup Script

echo "🚀 Starting TestGPT Backend API Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q sqlalchemy alembic

# Initialize database and seed default configs
echo "🗄️  Initializing database..."
python backend/seed_data.py

# Start FastAPI server
echo "🌐 Starting API server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""

cd backend/api && python main.py
