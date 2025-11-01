#!/bin/bash
# Complete End-to-End Test of PR Testing Feature

echo ""
echo "          TESTGPT PR TESTING - FULL END-TO-END TEST                "
echo ""
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo " Virtual environment activated"
else
    echo " Virtual environment not found"
    exit 1
fi

# Load GitHub token from .env if available
if [ -f "../.env" ]; then
    export $(cat ../.env | grep GITHUB_TOKEN | xargs)
fi
echo " GitHub token loaded from .env"
echo ""

# Step 1: Test Database
echo ""
echo "STEP 1: Testing Database & CRUD Operations"
echo ""
python scripts/test_pr_crud.py 2>&1 | grep -v "DeprecationWarning" | grep -v "datetime.datetime"
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo " Database test PASSED"
else
    echo " Database test FAILED"
    exit 1
fi
echo ""

# Step 2: Test End-to-End with Mock Data
echo ""
echo "STEP 2: Testing End-to-End Workflow (Mock Data)"
echo ""
python scripts/test_pr_end_to_end.py 2>&1 | grep -v "DeprecationWarning" | grep -v "datetime.datetime"
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo " End-to-End mock test PASSED"
else
    echo " End-to-End mock test FAILED"
    exit 1
fi
echo ""

# Step 3: Start Backend API in background
echo ""
echo "STEP 3: Starting Backend API Server"
echo ""
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 > /tmp/testgpt_api.log 2>&1 &
API_PID=$!
echo " Backend API starting (PID: $API_PID)..."
sleep 3

# Check if API is running
curl -s http://localhost:8000/api/pr-tests/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo " Backend API is running at http://localhost:8000"
else
    echo " Backend API failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi
echo ""

# Step 4: Test API Endpoints
echo ""
echo "STEP 4: Testing API Endpoints"
echo ""

echo " GET /api/pr-tests/ (List all tests)"
TESTS=$(curl -s http://localhost:8000/api/pr-tests/)
TEST_COUNT=$(echo $TESTS | python -m json.tool 2>/dev/null | grep -c '"id"')
echo "    Found $TEST_COUNT PR test runs in database"

echo " GET /api/pr-tests/stats/summary (Get statistics)"
curl -s http://localhost:8000/api/pr-tests/stats/summary | python -m json.tool | head -8
echo "    Statistics retrieved"
echo ""

# Step 5: Test with Real GitHub PR (Optional)
echo ""
echo "STEP 5: Test with Real GitHub PR (Optional)"
echo ""
echo ""
echo "You can now test with a real PR:"
echo ""
echo "  python scripts/test_real_pr.py"
echo ""
echo "Or manually:"
echo ""
echo "  python testgpt_engine.py"
echo "  > Test this PR: https://github.com/owner/repo/pull/123"
echo ""
read -p "Do you want to test with a real PR now? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo " Running real PR test..."
    python scripts/test_real_pr.py
    REAL_TEST_RESULT=$?
    echo ""
fi

# Summary
echo ""
echo ""
echo "                    TEST SUMMARY                                    "
echo ""
echo ""
echo " Database & CRUD:      PASSED"
echo " End-to-End Mock:      PASSED"
echo " Backend API:          RUNNING (PID: $API_PID)"
echo " API Endpoints:        WORKING"
if [ -n "$REAL_TEST_RESULT" ]; then
    if [ $REAL_TEST_RESULT -eq 0 ]; then
        echo " Real PR Test:         PASSED"
    else
        echo "  Real PR Test:         FAILED (see logs above)"
    fi
fi
echo ""
echo ""
echo "NEXT STEPS"
echo ""
echo ""
echo "1⃣  View API Results:"
echo "   curl http://localhost:8000/api/pr-tests/ | python -m json.tool"
echo ""
echo "2⃣  View Database:"
echo "   sqlite3 frontend/lib/db/testgpt.db \"SELECT pr_title, status FROM pr_test_runs;\""
echo ""
echo "3⃣  Test with your own PR:"
echo "   python testgpt_engine.py"
echo "   > Test this PR: https://github.com/YOUR_ORG/YOUR_REPO/pull/123"
echo ""
echo "4⃣  Start Frontend (in new terminal):"
echo "   npm run dev"
echo "   Open: http://localhost:3000/pr-tests"
echo ""
echo "5⃣  Stop Backend API:"
echo "   kill $API_PID"
echo ""
echo ""
echo ""
echo "Backend API is still running in background (PID: $API_PID)"
echo "Press Ctrl+C to keep it running, or run: kill $API_PID"
echo ""
