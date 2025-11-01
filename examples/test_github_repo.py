"""
Example: Test a GitHub Repository

This example shows how to use the Dynamic Backend Orchestrator
to test an API from a GitHub repository.

Usage:
    python examples/test_github_repo.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dynamic_backend_testing import DynamicBackendOrchestrator


async def test_github_repo_example():
    """
    Example: Test our own sample backend API from the repo.

    This demonstrates testing a known working API to verify
    the dynamic system works correctly.
    """
    print("""

                                                                      
          Example: Test GitHub Repository                            
                                                                      

    """)

    # Initialize orchestrator
    orchestrator = DynamicBackendOrchestrator()

    # For this example, we'll test the local sample API
    # In a real scenario, you would provide a GitHub URL
    print("\n Test Configuration:")
    print("=" * 70)
    print("NOTE: For this demo, you need a real API to test.")
    print("Please modify this example to point to your own API,")
    print("or use option 2 to test a GitHub repository.")
    print("=" * 70)

    print("\n  No sample API available in this demo.")
    print("Please use option 2 to test a real GitHub repository.")
    return {"overall_success": False, "status": "skipped"}


    # Display results
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    print(f"\nStatus: {result['status']}")
    print(f"API Framework: {result['api_info'].get('framework', 'Unknown')}")
    print(f"API Title: {result['api_info'].get('title', 'Unknown')}")
    print(f"Endpoints Discovered: {len(result['endpoints'])}")

    if result.get('test_results'):
        print(f"\nTests Run: {len(result['test_results'])}")
        print(f"Passed: {result.get('passed_count', 0)}")
        print(f"Failed: {result.get('failed_count', 0)}")
        print(f"Overall Success: {' YES' if result['overall_success'] else ' NO'}")

        print("\n Test Details:")
        for i, test in enumerate(result['test_results'], 1):
            status = " PASS" if test.get('success') else " FAIL"
            endpoint = test.get('endpoint', 'Unknown')
            print(f"  {i}. {status} - {endpoint}")
            if test.get('error'):
                print(f"      Error: {test['error']}")

    if result.get('error'):
        print(f"\n Error: {result['error']}")

    print("\n" + "=" * 70)

    return result


async def test_real_github_repo_example():
    """
    Example: Test an actual GitHub repository.

    Uncomment and modify this to test a real repo.
    """
    print("""

                                                                      
          Example: Test Real GitHub Repository                       
                                                                      

    """)

    orchestrator = DynamicBackendOrchestrator()

    # Example: Test a public FastAPI repo
    # Replace with your own repo URL
    result = await orchestrator.test_repo(
        repo_url="https://github.com/YOUR_USERNAME/YOUR_API_REPO",
        branch="main",  # or "feature-branch"
        app_module="main:app",  # adjust based on your app structure
        test_suite="smoke",
        auto_detect=True,  # Let it find the app automatically
        cleanup=True  # Clean up cloned repo after testing
    )

    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Status: {result['status']}")
    print(f"Overall Success: {' YES' if result.get('overall_success') else ' NO'}")

    if result.get('repo_info'):
        print(f"\nRepository: {result['repo_info'].get('remote_url')}")
        print(f"Branch: {result['repo_info'].get('current_branch')}")
        print(f"Commit: {result['repo_info'].get('current_commit')[:8]}")

    if result.get('test_results'):
        print(f"\nTests: {result.get('passed_count', 0)}/{len(result['test_results'])} passed")

    return result


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DYNAMIC BACKEND API TESTING - GITHUB REPOSITORY EXAMPLE")
    print("=" * 70)
    print("\nThis example tests a GitHub repository's backend API.")
    print("\nTo use this example:")
    print("1. Edit this file")
    print("2. Update the repo URL in test_real_github_repo_example()")
    print("3. Set your ANTHROPIC_API_KEY environment variable")
    print("4. Run again")
    print("\nFor now, showing expected output format:\n")

    result = asyncio.run(test_github_repo_example())

    # Uncomment below and edit test_real_github_repo_example() to test a real repo:
    # result = asyncio.run(test_real_github_repo_example())

    # Exit with appropriate code
    sys.exit(0 if result.get('overall_success') else 1)
