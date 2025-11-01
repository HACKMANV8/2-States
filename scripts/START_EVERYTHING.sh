#!/bin/bash
# Start TestGPT with Backend + Frontend for Full Testing

echo ""
echo "              STARTING TESTGPT - FULL SYSTEM                        "
echo ""
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Load GitHub token from .env if available
if [ -f "../.env" ]; then
    export $(cat ../.env | grep GITHUB_TOKEN | xargs)
fi

# Ensure all Playwright browsers are installed
echo " Ensuring Playwright browsers are installed..."
npx playwright install chromium webkit firefox > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo " All browsers installed (Chrome, Safari, Firefox)"
else
    echo "  Browser installation had issues, but continuing..."
fi
echo ""

# Check if backend is already running
curl -s http://localhost:8000/api/pr-tests/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo " Backend API already running at http://localhost:8000"
else
    echo " Starting Backend API..."
    # Activate venv and start backend
    source venv/bin/activate
    python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload > /tmp/testgpt_backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   PID: $BACKEND_PID"
    echo "   Logs: /tmp/testgpt_backend.log"
    sleep 3

    # Verify backend started
    curl -s http://localhost:8000/api/pr-tests/ > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo " Backend API running at http://localhost:8000"
    else
        echo " Backend failed to start. Check /tmp/testgpt_backend.log"
        exit 1
    fi
fi

echo ""
echo ""
echo "                  SYSTEM IS READY                                   "
echo ""
echo ""
echo " Backend API:  http://localhost:8000"
echo " API Docs:     http://localhost:8000/docs"
echo ""
echo ""
echo "WHAT TO DO NEXT:"
echo ""
echo ""
echo "1⃣  Start Frontend (in NEW terminal):"
echo "   npm run dev"
echo "   Then open: http://localhost:3000/pr-tests"
echo ""
echo "2⃣  Test with a REAL PR:"
echo "   python testgpt_engine.py"
echo "   Then type: Test this PR: https://github.com/owner/repo/pull/123"
echo ""
echo "3⃣  View existing results in API:"
echo "   curl http://localhost:8000/api/pr-tests/ | python -m json.tool"
echo ""
echo "4⃣  Use via Slack (if configured):"
echo "   Just type in Slack: Test this PR: https://github.com/owner/repo/pull/123"
echo ""
echo ""
echo ""
