"""
Example: Test a Pull Request

This example shows how to test a GitHub Pull Request
before merging, ensuring API changes don't break existing functionality.

This is perfect for CI/CD integration.

Usage:
    python examples/test_pr.py

    # Or from CI/CD:
    python examples/test_pr.py --repo $REPO_URL --pr $PR_NUMBER
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dynamic_backend_testing import DynamicBackendOrchestrator


async def test_pull_request(
    repo_url: str,
    pr_number: int,
    app_module: str = "main:app"
):
    """
    Test a GitHub Pull Request.

    Args:
        repo_url: GitHub repository URL
        pr_number: Pull request number
        app_module: Module path to the app

    Returns:
        Test results dictionary
    """
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          Testing Pull Request #{pr_number:04d}                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Repository: {repo_url}
PR Number: {pr_number}
App Module: {app_module}
    """)

    # Initialize orchestrator
    orchestrator = DynamicBackendOrchestrator()

    print("🔄 Testing PR changes...")
    print("=" * 70)

    # Test the PR
    result = await orchestrator.test_repo(
        repo_url=repo_url,
        pr_number=pr_number,
        app_module=app_module,
        test_suite="comprehensive",  # More thorough for PRs
        auto_detect=True,
        cleanup=True
    )

    # Display results
    print("\n" + "=" * 70)
    print("PR TEST RESULTS")
    print("=" * 70)

    print(f"\nStatus: {result['status']}")

    if result.get('repo_info'):
        print(f"\nPR Information:")
        print(f"  Commit: {result['repo_info'].get('current_commit', 'Unknown')[:8]}")
        print(f"  Message: {result['repo_info'].get('commit_message', 'Unknown')[:60]}...")

    if result.get('api_info'):
        print(f"\nAPI Information:")
        print(f"  Framework: {result['api_info'].get('framework', 'Unknown')}")
        print(f"  Title: {result['api_info'].get('title', 'Unknown')}")
        print(f"  Endpoints: {len(result.get('endpoints', []))}")

    if result.get('test_results'):
        passed = result.get('passed_count', 0)
        total = len(result['test_results'])
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"\nTest Results:")
        print(f"  Total Tests: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {result.get('failed_count', 0)}")
        print(f"  Success Rate: {success_rate:.1f}%")

        if result['overall_success']:
            print("\n✅ PR TESTS PASSED - Safe to merge!")
        else:
            print("\n❌ PR TESTS FAILED - DO NOT MERGE")
            print("\nFailed Tests:")
            for test in result['test_results']:
                if not test.get('success'):
                    print(f"  ❌ {test.get('endpoint')}")
                    if test.get('error'):
                        print(f"     Error: {test['error']}")

    if result.get('error'):
        print(f"\n❌ Error: {result['error']}")

    print("\n" + "=" * 70)

    return result


async def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Test a GitHub Pull Request with dynamic API testing"
    )
    parser.add_argument(
        "--repo",
        default="https://github.com/YOUR_USERNAME/YOUR_API_REPO",
        help="GitHub repository URL"
    )
    parser.add_argument(
        "--pr",
        type=int,
        default=1,
        help="Pull request number"
    )
    parser.add_argument(
        "--app-module",
        default="main:app",
        help="Module path to the app (e.g., main:app)"
    )

    args = parser.parse_args()

    # Check if using defaults
    if "YOUR_USERNAME" in args.repo:
        print("\n⚠️  Using default placeholder URL.")
        print("Please provide --repo and --pr arguments:")
        print(f"  python {sys.argv[0]} --repo https://github.com/user/repo --pr 123")
        print("\nFor this demo, we'll show the expected output format:\n")

        # Show example output
        print("=" * 70)
        print("EXAMPLE OUTPUT")
        print("=" * 70)
        print("""
Status: completed

PR Information:
  Commit: abc12345
  Message: Add new user endpoints for profile management

API Information:
  Framework: fastapi
  Title: My API
  Endpoints: 15

Test Results:
  Total Tests: 15
  Passed: 14
  Failed: 1
  Success Rate: 93.3%

❌ PR TESTS FAILED - DO NOT MERGE

Failed Tests:
  ❌ POST /users
     Error: Validation error in request body schema
        """)
        return {"overall_success": False}

    # Run actual test
    result = await test_pull_request(
        repo_url=args.repo,
        pr_number=args.pr,
        app_module=args.app_module
    )

    return result


if __name__ == "__main__":
    result = asyncio.run(main())

    # Exit with appropriate code for CI/CD
    # 0 = success (all tests passed)
    # 1 = failure (some tests failed or error occurred)
    sys.exit(0 if result.get('overall_success') else 1)
