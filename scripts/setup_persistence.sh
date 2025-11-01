#!/bin/bash

# TestGPT Test Persistence and Re-run Setup Script
# This script sets up the backend API and frontend for test management

set -e  # Exit on error

echo "=========================================="
echo "TestGPT Test Persistence Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED} Virtual environment not found${NC}"
    echo "Please create it first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW} Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW} Installing Python dependencies...${NC}"
pip install -q --upgrade pip
pip install -q sqlalchemy alembic requests

echo -e "${GREEN} Python dependencies installed${NC}"
echo ""

# Initialize database and seed default configs
echo -e "${YELLOW}  Initializing database and seeding default configurations...${NC}"
python backend/seed_data.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN} Database initialized successfully${NC}"
else
    echo -e "${RED} Database initialization failed${NC}"
    exit 1
fi

echo ""

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo -e "${YELLOW} Setting up frontend...${NC}"
    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    else
        echo "Frontend dependencies already installed"
    fi

    echo -e "${GREEN} Frontend ready${NC}"
    cd ..
else
    echo -e "${YELLOW}  Frontend directory not found, skipping frontend setup${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN} Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend API server:"
echo -e "   ${YELLOW}bash start_backend.sh${NC}"
echo "   OR"
echo -e "   ${YELLOW}cd backend/api && python main.py${NC}"
echo ""
echo "2. Start the frontend (in another terminal):"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo "3. Test the API:"
echo -e "   ${YELLOW}python test_backend_api.py${NC}"
echo ""
echo "Access points:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo "  - Test Library: http://localhost:3000/test-library"
echo ""
echo "Documentation:"
echo "  - See PERSISTENCE_AND_RERUN_IMPLEMENTATION.md for details"
echo ""
