"""
Claude API-based viewport parser for TestGPT.

Uses Claude to intelligently extract viewport/browser/network requirements
from natural language Slack messages.
"""

import os
import json
from typing import Dict, List
from anthropic import Anthropic


class ClaudeViewportParser:
    """
    Uses Claude API to parse natural language requests into structured
    viewport/browser/network requirements.

    This replaces keyword-based matching with intelligent LLM parsing.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.available_config = self._load_available_config()

    def _load_available_config(self) -> dict:
        """Load available viewports/browsers/networks from config.json."""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def parse_environments(self, slack_message: str, target_url: str = "") -> Dict[str, List[str]]:
        """
        Parse Slack message to extract viewport/browser/network requirements.

        Args:
            slack_message: Raw Slack message from user
            target_url: Target URL being tested (for context)

        Returns:
            Dictionary with keys: viewports, browsers, networks
            Each value is a list of profile names to use

        Example:
            Input: "test pointblank.club on iPhone and desktop"
            Output: {
                "viewports": ["iphone-13-pro", "desktop-standard"],
                "browsers": ["webkit-ios", "chromium-desktop"],
                "networks": ["normal"]
            }
        """
        # Build prompt with available options
        prompt = self._build_parsing_prompt(slack_message, target_url)

        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Parse JSON response
        try:
            result = json.loads(response_text)

            # Validate and set defaults
            return {
                "viewports": result.get("viewports", ["desktop-standard"]),
                "browsers": result.get("browsers", ["chromium-desktop"]),
                "networks": result.get("networks", ["normal"])
            }
        except json.JSONDecodeError as e:
            print(f"  Failed to parse Claude response as JSON: {e}")
            print(f"Response was: {response_text}")
            # Fallback to defaults
            return {
                "viewports": ["desktop-standard"],
                "browsers": ["chromium-desktop"],
                "networks": ["normal"]
            }

    def _build_parsing_prompt(self, slack_message: str, target_url: str) -> str:
        """Build the prompt for Claude to parse environment requirements."""

        # Get available options from config
        viewports = self.available_config.get("viewports", {})
        browsers = self.available_config.get("browsers", {})
        networks = self.available_config.get("networks", {})

        # Build viewport descriptions
        viewport_descriptions = []
        for vp_name, vp_config in viewports.items():
            desc = f"- **{vp_name}**: {vp_config.get('display_name', vp_name)} ({vp_config.get('width')}×{vp_config.get('height')}) - {vp_config.get('device_class', '')}"
            viewport_descriptions.append(desc)

        # Build browser descriptions
        browser_descriptions = []
        for br_name, br_config in browsers.items():
            desc = f"- **{br_name}**: {br_config.get('display_name', br_name)} ({br_config.get('engine')})"
            browser_descriptions.append(desc)

        # Build network descriptions
        network_descriptions = []
        for net_name, net_config in networks.items():
            desc = f"- **{net_name}**: {net_config.get('display_name', net_name)} - {net_config.get('description', '')}"
            network_descriptions.append(desc)

        return f"""You are parsing a user's test request to determine which viewports, browsers, and network conditions to test.

USER'S REQUEST:
"{slack_message}"

TARGET URL: {target_url if target_url else "(not specified)"}

AVAILABLE VIEWPORTS:
{chr(10).join(viewport_descriptions)}

AVAILABLE BROWSERS:
{chr(10).join(browser_descriptions)}

AVAILABLE NETWORK CONDITIONS:
{chr(10).join(network_descriptions)}

PARSING RULES:
1. **Viewports**:
   - If user mentions "iPhone", "iOS", or "mobile" → include iphone-13-pro
   - If user mentions "iPad" or "tablet" → include ipad-air
   - If user mentions "Android" → include android-medium
   - If user mentions "desktop" or no device → include desktop-standard
   - If user mentions "responsive" or "multiple screen sizes" → include iphone-13-pro, ipad-air, desktop-standard
   - If user mentions "comprehensive" → include ALL viewports

2. **Browsers**:
   - If user mentions "Safari" or "iOS" → include webkit-ios or webkit-desktop
   - If user mentions "Chrome" or "Chromium" → include chromium-desktop
   - If user mentions "Firefox" → include firefox-desktop
   - If user mentions "cross-browser" → include chromium-desktop and webkit-desktop
   - Default if nothing specified → chromium-desktop

3. **Networks**:
   - ALWAYS include "normal" (baseline)
   - If user mentions "slow", "3G", "poor connection" → add slow-3g
   - If user mentions "flaky", "unstable", "packet loss" → add flaky-edge
   - Default → ["normal"] only

4. **Combinations**:
   - Match browsers to viewports appropriately (e.g., webkit-ios for mobile viewports, chromium-desktop for desktop)
   - If multiple viewports selected, use appropriate browsers for each platform

OUTPUT FORMAT:
Return ONLY a JSON object with this exact structure (no other text):
{{
  "viewports": ["viewport-name-1", "viewport-name-2"],
  "browsers": ["browser-name-1", "browser-name-2"],
  "networks": ["network-name-1"]
}}

Use the exact profile names from the available options above (e.g., "iphone-13-pro", not "iPhone 13 Pro").

Example outputs:
- "test on iPhone" → {{"viewports": ["iphone-13-pro"], "browsers": ["webkit-ios"], "networks": ["normal"]}}
- "test on iPhone and desktop" → {{"viewports": ["iphone-13-pro", "desktop-standard"], "browsers": ["webkit-ios", "chromium-desktop"], "networks": ["normal"]}}
- "responsive test with slow network" → {{"viewports": ["iphone-13-pro", "ipad-air", "desktop-standard"], "browsers": ["webkit-ios", "chromium-desktop"], "networks": ["normal", "slow-3g"]}}
- "cross-browser test" → {{"viewports": ["desktop-standard"], "browsers": ["chromium-desktop", "webkit-desktop"], "networks": ["normal"]}}

Now parse the user's request and return the JSON:"""

    def get_smart_defaults(self, target_url: str = "") -> Dict[str, List[str]]:
        """
        Get smart default environments based on target URL.

        Args:
            target_url: Target URL being tested

        Returns:
            Default viewport/browser/network configuration
        """
        # Generic default
        return {
            "viewports": ["desktop-standard"],
            "browsers": ["chromium-desktop"],
            "networks": ["normal"]
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_environments_with_claude(slack_message: str, target_url: str = "") -> Dict[str, List[str]]:
    """
    Convenience function to parse environments using Claude API.

    Args:
        slack_message: Raw Slack message
        target_url: Target URL being tested

    Returns:
        Dictionary with viewports, browsers, networks lists
    """
    parser = ClaudeViewportParser()
    return parser.parse_environments(slack_message, target_url)
