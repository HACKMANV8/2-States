#!/usr/bin/env python3
"""
Test PR testing with a real GitHub PR.
"""

import sys
import os
import asyncio

# Load GitHub token from .env file
from dotenv import load_dotenv
load_dotenv()

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from testgpt_engine import TestGPTEngine

async def test_real_pr():
    """Test with a real PR."""

    # Example PR - a small PR from a public repo with deployment
    # You can change this to any PR you want to test
    test_pr_url = "https://github.com/vercel/next.js/pull/71519"

    print("="*70)
    print("🧪 TESTING PR TESTING WITH REAL GITHUB PR")
    print("="*70)
    print(f"\n📋 PR URL: {test_pr_url}")
    print("\nThis will:")
    print("  1. Fetch PR metadata from GitHub")
    print("  2. Detect deployment URL (if available)")
    print("  3. Analyze codebase structure")
    print("  4. Generate intelligent test scenarios")
    print("  5. Run Playwright tests")
    print("  6. Save results to database")
    print("  7. Post comment to GitHub PR (if not already posted)")
    print("\nStarting in 3 seconds...")
    print("")

    await asyncio.sleep(3)

    # Initialize engine
    engine = TestGPTEngine()

    # Simulate Slack message
    user_message = f"Test this PR: {test_pr_url}"
    user_id = "test_user"

    try:
        # Process the PR test request
        result = await engine.process_request(user_message, user_id)

        print("\n" + "="*70)
        print("✅ TEST COMPLETED!")
        print("="*70)
        print(f"\n{result}\n")

        print("Next steps:")
        print("  1. Check the GitHub PR for posted comment")
        print("  2. View results in API: curl http://localhost:8000/api/pr-tests/")
        print("  3. View in frontend: http://localhost:3000/pr-tests")
        print("")

    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"\nError: {e}\n")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    result = asyncio.run(test_real_pr())
    sys.exit(0 if result else 1)
