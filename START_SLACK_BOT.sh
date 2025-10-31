#!/bin/bash
# Start TestGPT Slack Bot

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║              STARTING TESTGPT SLACK BOT                            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# GitHub token is loaded from .env (leave empty for public repos)

echo "✅ Environment configured"
echo "   - Slack Bot Token: ${SLACK_BOT_TOKEN:0:20}..."
echo "   - Slack App Token: ${SLACK_APP_TOKEN:0:20}..."
echo "   - GitHub Token: ${GITHUB_TOKEN:0:20}..."
echo ""

# Initialize database if needed
if [ ! -f "frontend/lib/db/testgpt.db" ]; then
    echo "📁 Initializing database..."
    python scripts/init_pr_test_db.py
fi

echo "🤖 Starting Slack bot..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BOT IS READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💬 In Slack, just type:"
echo ""
echo "   Test this PR: https://github.com/owner/repo/pull/123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the bot
python main.py
