"""
Slack request parser for TestGPT.

Parses natural language Slack messages into structured test requirements.
"""

import re
import os
from typing import List, Optional
from models import ParsedSlackRequest
from config import select_viewports_for_keywords, select_browsers_for_keywords, select_networks_for_keywords

# Claude API-based parser (smart parsing)
try:
    from viewport_parser_claude import ClaudeViewportParser
    CLAUDE_PARSER_AVAILABLE = True
except ImportError:
    CLAUDE_PARSER_AVAILABLE = False


class SlackRequestParser:
    """
    Parses natural language Slack messages into structured test specifications.

    Implements behavioral rules from agent_instructions and specification TODO 1.
    """

    def __init__(self, use_claude_parser: bool = True):
        """
        Initialize request parser.

        Args:
            use_claude_parser: If True and Claude API is available, use Claude-based
                             environment parsing. Otherwise fall back to keyword matching.
        """
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        )

        # GitHub URL pattern
        self.github_url_pattern = re.compile(
            r'https?://github\.com/([\w-]+)/([\w-]+)'
        )

        # GitHub PR URL pattern
        self.github_pr_pattern = re.compile(
            r'https?://(?:www\.)?github\.com/([\w-]+)/([\w-]+)/pull/(\d+)'
        )

        # Initialize Claude parser if available and requested
        self.use_claude_parser = use_claude_parser and CLAUDE_PARSER_AVAILABLE
        if self.use_claude_parser:
            try:
                self.claude_parser = ClaudeViewportParser()
                print(" Claude API parser initialized for smart viewport detection")
            except Exception as e:
                print(f"  Claude parser initialization failed: {e}")
                print("   Falling back to keyword-based parsing")
                self.use_claude_parser = False
                self.claude_parser = None
        else:
            self.claude_parser = None
            if use_claude_parser and not CLAUDE_PARSER_AVAILABLE:
                print("  Claude parser not available (import failed)")
                print("   Using keyword-based parsing")

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

        # If no URL found, only default to pointblank if explicitly mentioned WITHOUT subdomain
        if not urls:
            # Only use pointblank.club if user explicitly said "pointblank" without a subdomain
            if "pointblank.club" in message_lower and "." not in message_lower.split("pointblank")[0][-10:]:
                urls = ["https://pointblank.club"]
                print(f"   ℹ  Using default demo site: pointblank.club")

        # Extract flows/scenarios mentioned
        flows = self._extract_flows(message_lower)

        # Determine target URL
        target_url = urls[0] if urls else "https://pointblank.club"

        # Determine required environments using Claude parser or keyword matching
        if self.use_claude_parser and self.claude_parser:
            # Use Claude API for intelligent parsing
            try:
                print(f" Using Claude API to parse environment requirements...")
                env_requirements = self.claude_parser.parse_environments(message, target_url)
                required_viewports = env_requirements.get("viewports", ["desktop-standard"])
                required_browsers = env_requirements.get("browsers", ["chromium-desktop"])
                required_networks = env_requirements.get("networks", ["normal"])
                print(f"    Viewports: {', '.join(required_viewports)}")
                print(f"    Browsers: {', '.join(required_browsers)}")
                print(f"    Networks: {', '.join(required_networks)}")
            except Exception as e:
                print(f"  Claude parsing failed: {e}")
                print("   Falling back to keyword-based parsing")
                # Fallback to keyword-based parsing
                keywords = self._extract_keywords(message_lower)
                required_viewports = select_viewports_for_keywords(keywords)
                required_browsers = select_browsers_for_keywords(keywords, target_url)
                required_networks = select_networks_for_keywords(keywords)
        else:
            # Use keyword-based parsing
            keywords = self._extract_keywords(message_lower)
            required_viewports = select_viewports_for_keywords(keywords)
            required_browsers = select_browsers_for_keywords(keywords, target_url)
            required_networks = select_networks_for_keywords(keywords)

        # Extract explicit expectations
        expectations = self._extract_expectations(message)

        # Detect PR testing request
        is_pr_test, pr_url = self._detect_pr_test(message)

        # Detect backend API testing
        is_backend_test = self._detect_backend_api_test(message) if not is_pr_test else False
        backend_repo_url = None
        backend_app_module = "main:app"

        if is_pr_test:
            print(f"    Detected PR testing request")
            print(f"      PR URL: {pr_url}")
        elif is_backend_test:
            # Extract GitHub URL if present
            backend_repo_url = self._extract_github_url(message)
            # Extract app module if specified
            backend_app_module = self._extract_app_module(message)

            print(f"    Detected backend API testing request")
            if backend_repo_url:
                print(f"      Repository: {backend_repo_url}")
            print(f"      App module: {backend_app_module}")

        return ParsedSlackRequest(
            target_urls=urls if urls else ["https://pointblank.club"],
            flows=flows,
            required_viewports=required_viewports,
            required_browsers=required_browsers,
            required_networks=required_networks,
            explicit_expectations=expectations,
            is_rerun=is_rerun,
            rerun_scenario_reference=rerun_ref,
            raw_message=message,
            is_backend_api_test=is_backend_test,
            backend_repo_url=backend_repo_url,
            backend_app_module=backend_app_module,
            is_pr_test=is_pr_test,
            pr_url=pr_url
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
            print(f"    Extracted Slack-formatted URL: {slack_urls}")
            return slack_urls

        # Standard URL extraction
        urls = self.url_pattern.findall(message)
        if urls:
            print(f"    Extracted URL with protocol: {urls}")
            return urls

        # Check for domain mentions without protocol (supports subdomains)
        # Pattern matches: subdomain.domain.tld OR domain.tld
        # Examples: careers.pointblank.club, pointblank.club, api.github.com, github.com
        domain_pattern = r'\b((?:[\w-]+\.)+[\w-]+\.(?:com|org|net|io|club|dev|ai|tech|app|co))\b'
        domain_match = re.search(domain_pattern, message, re.IGNORECASE)

        if domain_match:
            domain = domain_match.group(1)
            print(f"    Extracted domain without protocol: {domain}")
            urls = [f"https://{domain}"]
            return urls

        print(f"     No URL found in message: {message[:100]}")
        return []

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

    def _detect_pr_test(self, message: str) -> tuple[bool, Optional[str]]:
        """
        Detect if this is a PR testing request.

        Looks for:
        - GitHub PR URLs
        - Keywords like "test this PR", "test out this PR"

        Args:
            message: User message

        Returns:
            Tuple of (is_pr_test, pr_url)
        """
        message_lower = message.lower()

        # Check for explicit PR testing keywords
        pr_test_keywords = [
            "test this pr",
            "test out this pr",
            "test the pr",
            "test pr",
            "check this pr",
            "review this pr"
        ]

        has_pr_keyword = any(keyword in message_lower for keyword in pr_test_keywords)

        # Check for GitHub PR URL
        pr_match = self.github_pr_pattern.search(message)

        if pr_match:
            pr_url = pr_match.group(0)
            return True, pr_url

        # If PR keyword is present, look for any GitHub URL and append "/pull/" if needed
        if has_pr_keyword:
            # Look for GitHub repo URL that might need /pull/ appended
            github_match = self.github_url_pattern.search(message)
            if github_match:
                # User might have said "test this PR" and provided a repo URL
                # We'll return True but with None URL, let the orchestrator handle it
                return True, None

        return False, None

    def _detect_backend_api_test(self, message: str) -> bool:
        """
        Detect if this is a backend API testing request.

        Indicators:
        - GitHub URL mentioned (for repo testing)
        - Explicit API test patterns ("test the api", "test backend", etc.)
        - API keywords NOT in URLs combined with test actions

        IMPORTANT: Frontend/UI tests take priority. If message contains
        UI/navigation keywords, this returns False even if API keywords present.
        """
        message_lower = message.lower()

        # FIRST: Check for UI/frontend test indicators (HIGHEST PRIORITY)
        # These keywords indicate Playwright browser automation, not API testing
        frontend_ui_keywords = [
            "open", "opening", "navigate", "navigating", "go to", "going to",
            "visit", "visiting", "click", "clicking", "scroll", "scrolling",
            "page", "website", "site", "button", "modal", "form", "input",
            "events page", "landing page", "home page", "about page",
            "responsive", "viewport", "browser", "safari", "chrome", "firefox",
            "screenshot", "visual", "render", "display", "show", "visible",
            "hover", "drag", "drop", "select", "type", "fill", "submit"
        ]

        # If ANY frontend keyword is present, this is NOT a backend test
        for keyword in frontend_ui_keywords:
            if keyword in message_lower:
                return False

        # SECOND: Remove URLs from detection to avoid false positives with "http" in URLs
        # Strip out <url|text> Slack format and regular URLs
        message_without_urls = re.sub(r'<https?://[^>]+>', '', message_lower)
        message_without_urls = re.sub(r'https?://\S+', '', message_without_urls)

        # Check for GitHub URL (repo testing)
        if self.github_url_pattern.search(message):
            # Only if it's explicitly an API test request
            if any(keyword in message_without_urls for keyword in ["api", "backend", "endpoint"]):
                return True

        # Test + API combinations (explicit patterns)
        test_api_patterns = [
            r"test\s+(the\s+)?api",
            r"test\s+(the\s+)?backend",
            r"test\s+(the\s+)?endpoints?",
            r"api\s+test",
            r"backend\s+test",
            r"test.*endpoints?",
            r"api\s+health",
            r"smoke\s+test.*api"
        ]

        # Check for explicit patterns (in message without URLs)
        for pattern in test_api_patterns:
            if re.search(pattern, message_without_urls):
                return True

        # API-specific keywords (excluding generic ones like "http", "server")
        api_specific_keywords = [
            "api", "endpoint", "rest api", "fastapi", "flask",
            "django", "express", "graphql", "crud", "auth api"
        ]

        # Check for API-specific keywords (NOT in URLs)
        for keyword in api_specific_keywords:
            if keyword in message_without_urls:
                # If API keyword + test/check/verify, it's likely a backend test
                if any(action in message_without_urls for action in ["test", "check", "verify", "run"]):
                    return True

        return False

    def _extract_github_url(self, message: str) -> Optional[str]:
        """Extract GitHub repository URL from message."""
        # Handle Slack-formatted URLs: <http://github.com/user/repo|github.com/user/repo>
        slack_github_pattern = re.compile(r'<(https?://github\.com/[\w-]+/[\w-]+)(?:\|[^>]+)?>')
        slack_match = slack_github_pattern.search(message)

        if slack_match:
            return slack_match.group(1)

        # Standard GitHub URL
        match = self.github_url_pattern.search(message)
        if match:
            return match.group(0)

        return None

    def _extract_app_module(self, message: str) -> str:
        """
        Extract app module path from message.

        Examples:
        - "app module is server:app" → "server:app"
        - "use main.py" → "main:app"
        """
        # Look for explicit module specification
        module_patterns = [
            r"(?:app\s+)?module\s+(?:is\s+)?([a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*)",
            r"app\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*)",
        ]

        for pattern in module_patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1)

        # Default
        return "main:app"

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
