"""
Deployment Link Detector.

Detects and validates deployment URLs from PR descriptions, comments, and CI/CD status.
Supports common deployment platforms like Vercel, Netlify, Heroku, AWS, etc.
"""

import re
from typing import List, Optional, Dict, Any
import httpx


class DeploymentDetector:
    """
    Detects deployment/preview URLs from various sources.

    Supports:
    - Vercel preview deployments
    - Netlify deploy previews
    - Heroku review apps
    - AWS Amplify previews
    - Custom deployment URLs in PR descriptions
    """

    # Common deployment platform patterns
    DEPLOYMENT_PATTERNS = [
        # Vercel
        r'https?://[a-zA-Z0-9-]+\.vercel\.app',
        r'https?://[a-zA-Z0-9-]+\.vercel\.com',

        # Netlify
        r'https?://[a-zA-Z0-9-]+\.netlify\.app',
        r'https?://deploy-preview-\d+--[a-zA-Z0-9-]+\.netlify\.app',

        # Heroku
        r'https?://[a-zA-Z0-9-]+\.herokuapp\.com',
        r'https?://[a-zA-Z0-9-]+-pr-\d+\.herokuapp\.com',

        # AWS Amplify
        r'https?://[a-zA-Z0-9-]+\.amplifyapp\.com',

        # Render
        r'https?://[a-zA-Z0-9-]+\.onrender\.com',

        # Railway
        r'https?://[a-zA-Z0-9-]+\.railway\.app',

        # Cloudflare Pages
        r'https?://[a-zA-Z0-9-]+\.pages\.dev',

        # GitHub Pages
        r'https?://[a-zA-Z0-9-]+\.github\.io',

        # Generic preview patterns (staging, preview, dev subdomains)
        r'https?://(?:staging|preview|dev|pr-\d+)\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
    ]

    def __init__(self):
        """Initialize deployment detector."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DEPLOYMENT_PATTERNS]

    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract deployment URLs from text.

        Args:
            text: Text to search (PR description, comments, etc.)

        Returns:
            List of found deployment URLs (deduplicated)
        """
        if not text:
            return []

        found_urls = set()

        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            found_urls.update(matches)

        return sorted(list(found_urls))

    def extract_from_pr_context(self, pr_context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract deployment URLs from complete PR context.

        Searches in:
        - PR description
        - PR comments
        - CI/CD status (target URLs)

        Args:
            pr_context: Full PR context from GitHubService

        Returns:
            Dict with deployment URLs categorized by source
        """
        deployment_urls = {
            "from_description": [],
            "from_comments": [],
            "from_ci_status": [],
            "all_unique": []
        }

        # Search PR description
        description = pr_context.get("metadata", {}).get("description", "")
        deployment_urls["from_description"] = self.extract_from_text(description)

        # Search comments
        comments_data = pr_context.get("comments", {})
        for comment in comments_data.get("issue_comments", []):
            urls = self.extract_from_text(comment.get("body", ""))
            deployment_urls["from_comments"].extend(urls)

        for comment in comments_data.get("review_comments", []):
            urls = self.extract_from_text(comment.get("body", ""))
            deployment_urls["from_comments"].extend(urls)

        # Deduplicate comments URLs
        deployment_urls["from_comments"] = list(set(deployment_urls["from_comments"]))

        # Search CI/CD status
        ci_status = pr_context.get("ci_status", {})
        for status in ci_status.get("statuses", []):
            target_url = status.get("target_url", "")
            if target_url:
                # Check if target URL itself is a deployment
                urls = self.extract_from_text(target_url)
                deployment_urls["from_ci_status"].extend(urls)

                # Also check status description for URLs
                description = status.get("description", "")
                urls = self.extract_from_text(description)
                deployment_urls["from_ci_status"].extend(urls)

        # Deduplicate CI URLs
        deployment_urls["from_ci_status"] = list(set(deployment_urls["from_ci_status"]))

        # Get all unique URLs
        all_urls = (
            deployment_urls["from_description"] +
            deployment_urls["from_comments"] +
            deployment_urls["from_ci_status"]
        )
        deployment_urls["all_unique"] = sorted(list(set(all_urls)))

        return deployment_urls

    async def validate_url(self, url: str, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Validate that a deployment URL is accessible.

        Args:
            url: Deployment URL to validate
            timeout: Request timeout in seconds

        Returns:
            Dict with validation result
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=timeout)

                return {
                    "url": url,
                    "accessible": True,
                    "status_code": response.status_code,
                    "final_url": str(response.url),
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "error": None
                }

        except httpx.TimeoutException:
            return {
                "url": url,
                "accessible": False,
                "status_code": None,
                "error": "Timeout - deployment may be slow or unavailable"
            }

        except httpx.HTTPStatusError as e:
            return {
                "url": url,
                "accessible": False,
                "status_code": e.response.status_code,
                "error": f"HTTP {e.response.status_code}"
            }

        except Exception as e:
            return {
                "url": url,
                "accessible": False,
                "status_code": None,
                "error": str(e)
            }

    async def validate_all_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Validate multiple deployment URLs.

        Args:
            urls: List of URLs to validate

        Returns:
            List of validation results
        """
        results = []

        for url in urls:
            result = await self.validate_url(url)
            results.append(result)

        return results

    def get_best_deployment_url(self, pr_context: Dict[str, Any]) -> Optional[str]:
        """
        Get the best deployment URL for testing.

        Priority:
        1. URLs from PR description (author explicitly provided)
        2. URLs from CI/CD status (official deployment)
        3. URLs from comments (might be mentioned by reviewers)

        Args:
            pr_context: Full PR context

        Returns:
            Best deployment URL or None if none found
        """
        deployment_urls = self.extract_from_pr_context(pr_context)

        # Priority 1: Description
        if deployment_urls["from_description"]:
            return deployment_urls["from_description"][0]

        # Priority 2: CI/CD
        if deployment_urls["from_ci_status"]:
            return deployment_urls["from_ci_status"][0]

        # Priority 3: Comments
        if deployment_urls["from_comments"]:
            return deployment_urls["from_comments"][0]

        return None

    async def find_and_validate_deployment(self, pr_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find and validate deployment URL for a PR.

        This is the main entry point for deployment detection.

        Args:
            pr_context: Full PR context from GitHubService

        Returns:
            Dict with deployment information and validation results
        """
        print("\n🔍 Searching for deployment URLs...")

        # Extract all deployment URLs
        deployment_urls = self.extract_from_pr_context(pr_context)

        if not deployment_urls["all_unique"]:
            print("   ⚠️  No deployment URLs found in PR")
            return {
                "found": False,
                "deployment_url": None,
                "all_urls": [],
                "validation": None
            }

        print(f"   ✅ Found {len(deployment_urls['all_unique'])} deployment URL(s)")

        # Get best URL
        best_url = self.get_best_deployment_url(pr_context)

        print(f"   🎯 Selected deployment URL: {best_url}")
        print(f"   🔍 Validating deployment accessibility...")

        # Validate the best URL
        validation = await self.validate_url(best_url)

        if validation["accessible"]:
            print(f"   ✅ Deployment is accessible (HTTP {validation['status_code']})")
            print(f"      Response time: {validation['response_time_ms']}ms")
        else:
            print(f"   ❌ Deployment validation failed: {validation['error']}")

            # Try other URLs if best one failed
            for url in deployment_urls["all_unique"]:
                if url != best_url:
                    print(f"   🔄 Trying alternative URL: {url}")
                    alt_validation = await self.validate_url(url)
                    if alt_validation["accessible"]:
                        print(f"   ✅ Alternative deployment is accessible")
                        best_url = url
                        validation = alt_validation
                        break

        return {
            "found": True,
            "deployment_url": best_url,
            "all_urls": deployment_urls,
            "validation": validation,
            "accessible": validation.get("accessible", False)
        }

    def detect_platform(self, url: str) -> str:
        """
        Detect the deployment platform from URL.

        Args:
            url: Deployment URL

        Returns:
            Platform name or "Unknown"
        """
        url_lower = url.lower()

        if "vercel.app" in url_lower or "vercel.com" in url_lower:
            return "Vercel"
        elif "netlify.app" in url_lower:
            return "Netlify"
        elif "herokuapp.com" in url_lower:
            return "Heroku"
        elif "amplifyapp.com" in url_lower:
            return "AWS Amplify"
        elif "onrender.com" in url_lower:
            return "Render"
        elif "railway.app" in url_lower:
            return "Railway"
        elif "pages.dev" in url_lower:
            return "Cloudflare Pages"
        elif "github.io" in url_lower:
            return "GitHub Pages"
        else:
            return "Unknown Platform"
