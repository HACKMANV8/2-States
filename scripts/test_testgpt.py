"""
Test script for TestGPT engine.

Demonstrates the full flow without requiring Slack or Playwright MCP.
Shows how requests are parsed, plans are built, and results are formatted.
"""

import asyncio
from testgpt_engine import TestGPTEngine


async def test_pointblank_safari_responsive():
    """
    Test the canonical demo scenario:
    "Run responsive Safari/iPhone vs Chrome/Desktop tests on pointblank.club"
    """
    print("\n" + "=" * 80)
    print("TEST: Pointblank.club Safari vs Chrome Responsive Test")
    print("=" * 80 + "\n")

    # Initialize engine (without MCP tools for testing)
    engine = TestGPTEngine(mcp_tools=None, storage_dir="./testgpt_data_test")

    # Test request
    test_message = "Run responsive Safari/iPhone vs Chrome/Desktop tests on pointblank.club under bad network and tell me what breaks"

    # Process request
    result = await engine.process_test_request(test_message, user_id="test-user")

    print("\n" + "=" * 80)
    print("SLACK OUTPUT:")
    print("=" * 80)
    print(result)
    print("\n")


async def test_simple_landing_page():
    """Test a simple landing page check."""
    print("\n" + "=" * 80)
    print("TEST: Simple Landing Page Test")
    print("=" * 80 + "\n")

    engine = TestGPTEngine(mcp_tools=None, storage_dir="./testgpt_data_test")

    test_message = "test pointblank.club landing page on mobile and desktop"

    result = await engine.process_test_request(test_message, user_id="test-user")

    print("\n" + "=" * 80)
    print("SLACK OUTPUT:")
    print("=" * 80)
    print(result)
    print("\n")


async def test_cross_browser():
    """Test cross-browser scenario."""
    print("\n" + "=" * 80)
    print("TEST: Cross-Browser Test")
    print("=" * 80 + "\n")

    engine = TestGPTEngine(mcp_tools=None, storage_dir="./testgpt_data_test")

    test_message = "test pointblank.club on safari and chrome"

    result = await engine.process_test_request(test_message, user_id="test-user")

    print("\n" + "=" * 80)
    print("SLACK OUTPUT:")
    print("=" * 80)
    print(result)
    print("\n")


async def test_scenario_list():
    """Test listing saved scenarios."""
    print("\n" + "=" * 80)
    print("TEST: List Saved Scenarios")
    print("=" * 80 + "\n")

    engine = TestGPTEngine(mcp_tools=None, storage_dir="./testgpt_data_test")

    scenarios = engine.get_scenario_library()

    print("\n" + "=" * 80)
    print("SCENARIO LIBRARY:")
    print("=" * 80)
    print(scenarios)
    print("\n")


async def main():
    """Run all tests."""
    print("""

                                                                              
  TestGPT Engine Test Suite                                                  
                                                                              
  Demonstrates the full multi-environment QA testing pipeline                
                                                                              

    """)

    # Run tests
    await test_pointblank_safari_responsive()

    await test_simple_landing_page()

    await test_cross_browser()

    await test_scenario_list()

    print("\n" + "=" * 80)
    print(" ALL TESTS COMPLETED")
    print("=" * 80)
    print("\nCheck ./testgpt_data_test/ directory for:")
    print("  • scenarios/*.json - Saved scenario definitions")
    print("  • runs/*.json - Run artifacts with full results")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
