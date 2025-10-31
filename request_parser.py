"""
Slack request parser for TestGPT.

Parses natural language Slack messages into structured test requirements.
"""

import re
from typing import List, Optional
from models import ParsedSlackRequest
from config import select_viewports_for_keywords, select_browsers_for_keywords, select_networks_for_keywords


class SlackRequestParser:
    """
    Parses natural language Slack messages into structured test specifications.

    Implements behavioral rules from agent_instructions and specification TODO 1.
    """

    def __init__(self):
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        )

    def parse(self, message: str, user_id: str = "unknown") -> ParsedSlackRequest:
        """
        Parse a Slack message into structured test requirements.

        Args:
            message: Raw Slack message from user
            user_id: Slack user ID who triggered the request

        Returns:
            ParsedSlackRequest with extracted requirements
        """
        message_lower = message.lower()

        # Check if this is a re-run request
        is_rerun, rerun_ref = self._detect_rerun(message_lower)

        # Extract target URLs
        urls = self._extract_urls(message)

        # If no URL found, check for implicit pointblank.club reference
        if not urls:
            if any(keyword in message_lower for keyword in ["pointblank", "demo", "showcase"]):
                urls = ["https://pointblank.club"]
            elif any(keyword in message_lower for keyword in ["test", "check", "run"]):
                # Default to pointblank for demo purposes
                urls = ["https://pointblank.club"]

        # Extract flows/scenarios mentioned
        flows = self._extract_flows(message_lower)

        # Extract keywords for environment selection
        keywords = self._extract_keywords(message_lower)

        # Determine required environments
        target_url = urls[0] if urls else "https://pointblank.club"
        required_viewports = select_viewports_for_keywords(keywords)
        required_browsers = select_browsers_for_keywords(keywords, target_url)
        required_networks = select_networks_for_keywords(keywords)

        # Extract explicit expectations
        expectations = self._extract_expectations(message)

        return ParsedSlackRequest(
            target_urls=urls if urls else ["https://pointblank.club"],
            flows=flows,
            required_viewports=required_viewports,
            required_browsers=required_browsers,
            required_networks=required_networks,
            explicit_expectations=expectations,
            is_rerun=is_rerun,
            rerun_scenario_reference=rerun_ref,
            raw_message=message
        )

    def _detect_rerun(self, message: str) -> tuple[bool, Optional[str]]:
        """Detect if this is a re-run request."""
        rerun_patterns = [
            r're-?run\s+(.+)',
            r'run\s+(.+)\s+again',
            r'repeat\s+(.+)',
            r'execute\s+(scenario[- ][\w]+)',
        ]

        for pattern in rerun_patterns:
            match = re.search(pattern, message)
            if match:
                return True, match.group(1).strip()

        return False, None

    def _extract_urls(self, message: str) -> List[str]:
        """Extract URLs from message."""
        # Handle Slack-formatted URLs: <http://example.com|example.com>
        slack_url_pattern = re.compile(r'<(https?://[^|>]+)(?:\|[^>]+)?>')
        slack_urls = slack_url_pattern.findall(message)

        if slack_urls:
            return slack_urls

        # Standard URL extraction
        urls = self.url_pattern.findall(message)

        # Also check for domain mentions without protocol
        if not urls:
            domain_match = re.search(r'([\w-]+\.[\w]+(?:\.[\w]+)?)', message)
            if domain_match:
                domain = domain_match.group(1)
                if any(tld in domain for tld in ['.com', '.org', '.net', '.io', '.club', '.dev']):
                    urls = [f"https://{domain}"]

        return urls

    def _extract_flows(self, message: str) -> List[str]:
        """
        Extract test flows/scenarios from message.

        Examples:
        - "test login flow" → ["login"]
        - "checkout process" → ["checkout"]
        - "pricing modal" → ["pricing modal"]
        """
        flows = []

        # Common flow keywords
        flow_patterns = {
            "login": r"log\s*in|sign\s*in|authentication",
            "signup": r"sign\s*up|register|registration|recruit",
            "checkout": r"checkout|purchase|buy|payment",
            "cart": r"cart|basket|add to cart",
            "pricing": r"pricing|price|plans|tiers",
            "contact": r"contact|form|get in touch",
            "search": r"search",
            "landing": r"landing\s*page|home\s*page|hero",
            "navigation": r"navigation|nav|menu",
        }

        for flow_name, pattern in flow_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                flows.append(flow_name)

        # If "responsive" or "layout" mentioned with no specific flow, add landing
        if not flows and any(word in message.lower() for word in ["responsive", "layout", "screen"]):
            flows.append("landing")

        # If no flows detected, default to landing page test
        if not flows:
            flows.append("landing")

        return flows

    def _extract_keywords(self, message: str) -> List[str]:
        """
        Extract keywords relevant for environment selection.

        Returns list of keywords that will be used to determine
        viewports, browsers, and networks to test.
        """
        keywords = []

        # Viewport/device keywords
        viewport_keywords = [
            "mobile", "tablet", "desktop", "iphone", "ipad", "android",
            "responsive", "screen sizes", "aspect ratios", "viewports",
            "cheap", "budget", "small", "large", "ultrawide",
            "landscape", "portrait"
        ]

        # Browser keywords
        browser_keywords = [
            "safari", "chrome", "brave", "firefox", "webkit", "chromium",
            "ios", "macos", "cross-browser", "browser"
        ]

        # Network keywords
        network_keywords = [
            "slow network", "bad network", "poor connection", "flaky",
            "unstable", "slow", "3g", "edge case", "network conditions",
            "under load"
        ]

        all_keywords = viewport_keywords + browser_keywords + network_keywords

        for keyword in all_keywords:
            if keyword in message:
                keywords.append(keyword)

        return keywords

    def _extract_expectations(self, message: str) -> List[str]:
        """
        Extract explicit pass criteria mentioned by user.

        Examples:
        - "button should be visible" → ["button is visible"]
        - "modal must open" → ["modal opens"]
        - "no errors" → ["no console errors"]
        """
        expectations = []

        # Common expectation patterns
        expectation_patterns = {
            r"(button|cta|link) (?:should|must) be visible": "CTA/button is visible",
            r"modal (?:should|must) (?:open|appear)": "modal opens",
            r"page (?:should|must) load": "page loads successfully",
            r"no (?:console )?errors": "no console errors",
            r"(?:image|images) (?:should|must) load": "images load correctly",
            r"form (?:should|must) (?:work|submit)": "form is submittable",
        }

        for pattern, expectation in expectation_patterns.items():
            if re.search(pattern, message.lower()):
                expectations.append(expectation)

        return expectations

    def should_create_matrix(self, parsed: ParsedSlackRequest) -> bool:
        """
        Determine if this request requires a multi-environment matrix.

        Returns True if user mentioned multiple environments or
        keywords that imply matrix testing.
        """
        # More than one environment in any dimension = matrix required
        if len(parsed.required_viewports) > 1:
            return True
        if len(parsed.required_browsers) > 1:
            return True
        if len(parsed.required_networks) > 1:
            return True

        # Special keywords that always require matrix
        matrix_keywords = [
            "responsive", "cross-browser", "screen sizes", "aspect ratios",
            "comprehensive", "multiple", "various", "different"
        ]

        message_lower = parsed.raw_message.lower()
        if any(keyword in message_lower for keyword in matrix_keywords):
            return True

        # Pointblank.club with Safari = matrix (to show Safari vs Chrome)
        if "pointblank.club" in parsed.target_urls[0]:
            if len(parsed.required_browsers) >= 2:
                return True

        return False

    def get_scenario_name(self, parsed: ParsedSlackRequest) -> str:
        """
        Generate a stable, human-readable scenario name.

        Format: "{Target Site} - {Primary Flow} - {Key Check}"
        """
        # Extract domain from URL
        url = parsed.target_urls[0]
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        domain_clean = domain.replace("www.", "").title()

        # Get primary flow
        primary_flow = parsed.flows[0] if parsed.flows else "General"
        flow_title = primary_flow.replace("_", " ").title()

        # Add environment context if matrix
        if self.should_create_matrix(parsed):
            if len(parsed.required_browsers) > 1:
                env_context = "Cross-Browser Test"
            elif len(parsed.required_viewports) > 1:
                env_context = "Responsive Test"
            elif len(parsed.required_networks) > 1:
                env_context = "Network Conditions Test"
            else:
                env_context = "Multi-Environment Test"
        else:
            env_context = "Standard Test"

        return f"{domain_clean} - {flow_title} - {env_context}"

    def get_scenario_id(self, parsed: ParsedSlackRequest) -> str:
        """
        Generate a stable scenario ID for persistence.

        Format: scenario-{domain}-{flow}-{hash}
        """
        url = parsed.target_urls[0]
        domain = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        domain_slug = domain.replace(".", "-")

        primary_flow = parsed.flows[0] if parsed.flows else "general"
        flow_slug = primary_flow.replace(" ", "-").lower()

        # Create a simple hash based on environments
        env_hash = f"{len(parsed.required_viewports)}{len(parsed.required_browsers)}{len(parsed.required_networks)}"

        return f"scenario-{domain_slug}-{flow_slug}-{env_hash}"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_slack_message(message: str, user_id: str = "unknown") -> ParsedSlackRequest:
    """
    Convenience function to parse a Slack message.

    Args:
        message: Raw Slack message
        user_id: Slack user ID

    Returns:
        ParsedSlackRequest with structured requirements
    """
    parser = SlackRequestParser()
    return parser.parse(message, user_id)
