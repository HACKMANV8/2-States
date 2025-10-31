#!/bin/bash
# Test all PR testing components

echo "🧪 Testing PR Testing Implementation"
echo "===================================="
echo ""

# Change to project directory
cd "$(dirname "$0")/.."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Test 1: Database CRUD
echo "1️⃣  Testing Database CRUD Operations..."
python scripts/test_pr_crud.py
if [ $? -eq 0 ]; then
    echo "✅ Database CRUD: PASSED"
else
    echo "❌ Database CRUD: FAILED"
    exit 1
fi
echo ""

# Test 2: End-to-End
echo "2️⃣  Testing End-to-End Workflow..."
python scripts/test_pr_end_to_end.py
if [ $? -eq 0 ]; then
    echo "✅ End-to-End: PASSED"
else
    echo "❌ End-to-End: FAILED"
    exit 1
fi
echo ""

# Test 3: Unit Tests
echo "3️⃣  Running Unit Tests..."
python -m pytest tests/test_pr_testing.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "✅ Unit Tests: PASSED"
else
    echo "❌ Unit Tests: FAILED"
    exit 1
fi
echo ""

# Test 4: API Endpoints (if server is running)
echo "4️⃣  Testing API Endpoints..."
curl -s http://localhost:8000/api/pr-tests/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ API Server: Running"
    echo "   GET /api/pr-tests/ - OK"

    # Test stats endpoint
    curl -s http://localhost:8000/api/pr-tests/stats/summary > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   GET /api/pr-tests/stats/summary - OK"
    fi
else
    echo "⚠️  API Server: Not running (start with: ./scripts/start_backend.sh)"
fi
echo ""

echo "===================================="
echo "✅ All tests completed!"
echo ""
echo "Next steps:"
echo "1. Start backend: ./scripts/start_backend.sh"
echo "2. Test with real PR: python testgpt_engine.py"
echo "3. View results: http://localhost:3000/pr-tests"
echo ""
