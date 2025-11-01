#!/usr/bin/env python3
"""
Quick browser test to verify all browsers work with Playwright.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def test_browser(browser_type: str):
    """Test a single browser."""
    print(f"\n{'='*60}")
    print(f"Testing {browser_type.upper()}...")
    print(f"{'='*60}")

    async with async_playwright() as p:
        try:
            # Launch browser
            if browser_type == "chromium":
                browser = await p.chromium.launch(headless=True)
            elif browser_type == "webkit":
                browser = await p.webkit.launch(headless=True)
            elif browser_type == "firefox":
                browser = await p.firefox.launch(headless=True)
            else:
                raise ValueError(f"Unknown browser: {browser_type}")

            print(f" {browser_type} launched successfully")

            # Create page
            page = await browser.new_page()
            print(f" Created new page")

            # Navigate to a test URL
            await page.goto("https://example.com", wait_until="networkidle")
            print(f" Navigated to example.com")

            # Get title
            title = await page.title()
            print(f" Page title: {title}")

            # Close
            await browser.close()
            print(f" {browser_type} test PASSED")

            return True

        except Exception as e:
            print(f" {browser_type} test FAILED: {e}")
            return False


async def main():
    """Test all browsers."""
    print("\n" + "="*60)
    print("TestGPT Browser Verification Test")
    print("="*60)

    browsers = ["chromium", "webkit", "firefox"]
    results = {}

    for browser_type in browsers:
        results[browser_type] = await test_browser(browser_type)

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = True
    for browser_type, passed in results.items():
        status = " PASSED" if passed else " FAILED"
        print(f"{browser_type:12} {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n ALL BROWSERS WORKING CORRECTLY!")
        return 0
    else:
        print("\n SOME BROWSERS FAILED. Run ./scripts/ENSURE_BROWSERS_INSTALLED.sh")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
