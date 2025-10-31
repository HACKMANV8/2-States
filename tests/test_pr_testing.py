"""
Unit tests for PR testing functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime


# Test imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pr_testing.github_service import GitHubService
from pr_testing.deployment_detector import DeploymentDetector
from pr_testing.codebase_analyzer import CodebaseAnalyzer
from pr_testing.context_builder import PRContextBuilder


class TestGitHubService:
    """Tests for GitHubService class."""

    def test_parse_pr_url_full_url(self):
        """Test parsing full GitHub PR URL."""
        service = GitHubService()

        pr_url = "https://github.com/owner/repo/pull/123"
        result = service.parse_pr_url(pr_url)

        assert result is not None
        assert result["owner"] == "owner"
        assert result["repo"] == "repo"
        assert result["pr_number"] == "123"
        assert result["github_host"] == "github.com"

    def test_parse_pr_url_shorthand(self):
        """Test parsing shorthand PR URL."""
        service = GitHubService()

        pr_url = "owner/repo#123"
        result = service.parse_pr_url(pr_url)

        assert result is not None
        assert result["owner"] == "owner"
        assert result["repo"] == "repo"
        assert result["pr_number"] == "123"

    def test_parse_pr_url_invalid(self):
        """Test parsing invalid PR URL."""
        service = GitHubService()

        pr_url = "not-a-valid-url"
        result = service.parse_pr_url(pr_url)

        assert result is None

    def test_parse_diff_basic(self):
        """Test basic diff parsing."""
        service = GitHubService()

        diff_text = """diff --git a/file1.py b/file1.py
index 123..456 789
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,4 @@
+added line
 existing line
-removed line
"""

        result = service._parse_diff(diff_text)

        assert len(result) == 1
        assert result[0]["path"] == "file1.py"
        assert result[0]["additions"] == 1
        assert result[0]["deletions"] == 1


class TestDeploymentDetector:
    """Tests for DeploymentDetector class."""

    def test_extract_vercel_url(self):
        """Test extracting Vercel deployment URL."""
        detector = DeploymentDetector()

        text = "Preview deployed to https://my-app-pr123.vercel.app"
        urls = detector.extract_from_text(text)

        assert len(urls) == 1
        assert "vercel.app" in urls[0]

    def test_extract_netlify_url(self):
        """Test extracting Netlify deployment URL."""
        detector = DeploymentDetector()

        text = "Deploy preview: https://deploy-preview-123--my-app.netlify.app"
        urls = detector.extract_from_text(text)

        assert len(urls) == 1
        assert "netlify.app" in urls[0]

    def test_extract_multiple_urls(self):
        """Test extracting multiple deployment URLs."""
        detector = DeploymentDetector()

        text = """
        Vercel: https://my-app.vercel.app
        Netlify: https://my-app.netlify.app
        """
        urls = detector.extract_from_text(text)

        assert len(urls) == 2

    def test_detect_platform_vercel(self):
        """Test platform detection for Vercel."""
        detector = DeploymentDetector()

        platform = detector.detect_platform("https://my-app.vercel.app")
        assert platform == "Vercel"

    def test_detect_platform_netlify(self):
        """Test platform detection for Netlify."""
        detector = DeploymentDetector()

        platform = detector.detect_platform("https://my-app.netlify.app")
        assert platform == "Netlify"

    def test_detect_platform_unknown(self):
        """Test platform detection for unknown platform."""
        detector = DeploymentDetector()

        platform = detector.detect_platform("https://example.com")
        assert platform == "Unknown Platform"


class TestCodebaseAnalyzer:
    """Tests for CodebaseAnalyzer class."""

    def test_analyze_readme_basic(self):
        """Test basic README analysis."""
        analyzer = CodebaseAnalyzer()

        readme_content = """
# My Project

This is a test project using Next.js and React.

## Installation

```bash
npm install
npm run dev
```

## Testing

```bash
npm test
```
"""

        result = analyzer.analyze_readme(readme_content)

        assert "Next.js" in result["tech_stack"]
        assert "React" in result["tech_stack"]
        assert len(result["installation_steps"]) > 0
        assert len(result["test_commands"]) > 0

    def test_analyze_package_json(self):
        """Test package.json analysis."""
        analyzer = CodebaseAnalyzer()

        package_json = """{
    "name": "my-app",
    "version": "1.0.0",
    "scripts": {
        "dev": "next dev",
        "build": "next build",
        "test": "jest"
    },
    "dependencies": {
        "next": "^13.0.0",
        "react": "^18.0.0"
    }
}"""

        result = analyzer.analyze_package_json(package_json)

        assert result["name"] == "my-app"
        assert result["framework"] == "Next.js"
        assert "dev" in result["scripts"]
        assert "next" in result["dependencies"]

    def test_analyze_requirements_txt(self):
        """Test requirements.txt analysis."""
        analyzer = CodebaseAnalyzer()

        requirements = """fastapi==0.100.0
uvicorn==0.23.0
pytest==7.4.0
"""

        result = analyzer.analyze_requirements_txt(requirements)

        assert "fastapi" in result["dependencies"]
        assert result["framework"] == "FastAPI"
        assert "pytest" in result["dependencies"]


class TestPRContextBuilder:
    """Tests for PRContextBuilder class."""

    def test_extract_acceptance_criteria_checkboxes(self):
        """Test extracting acceptance criteria from checkboxes."""
        builder = PRContextBuilder()

        pr_description = """
## Changes
- Added new feature

## Acceptance Criteria
- [ ] Feature works on mobile
- [ ] Tests pass
- [ ] Documentation updated
"""

        criteria = builder.extract_acceptance_criteria(pr_description, [])

        assert len(criteria) >= 3
        assert any("mobile" in c.lower() for c in criteria)
        assert any("test" in c.lower() for c in criteria)

    def test_categorize_changed_files(self):
        """Test categorizing changed files."""
        builder = PRContextBuilder()

        files = [
            {"filename": "components/Button.tsx", "status": "modified"},
            {"filename": "pages/index.tsx", "status": "modified"},
            {"filename": "api/users.py", "status": "added"},
            {"filename": "styles/main.css", "status": "modified"},
        ]

        categories = builder.categorize_changed_files(files)

        assert "ui_components" in categories
        assert "pages" in categories
        assert "api_routes" in categories
        assert "styles" in categories

    def test_generate_test_scenarios(self):
        """Test generating test scenarios."""
        builder = PRContextBuilder()

        pr_context = {
            "metadata": {"description": "Added new dashboard"},
            "files": [
                {"filename": "components/Dashboard.tsx", "status": "added"}
            ],
            "linked_issues": []
        }

        codebase_analysis = {
            "project_type": "frontend",
            "tech_stack": ["Next.js", "React"]
        }

        deployment_url = "https://preview.vercel.app"

        scenarios = builder.generate_test_scenarios(
            pr_context,
            codebase_analysis,
            deployment_url
        )

        assert len(scenarios) > 0
        assert any("basic" in s["name"].lower() for s in scenarios)
        assert any(s["priority"] == "critical" for s in scenarios)


class TestGitHubRetry:
    """Tests for retry and rate limiting functionality."""

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        from pr_testing.github_retry import exponential_backoff

        delay0 = exponential_backoff(0, base_delay=1.0)
        delay1 = exponential_backoff(1, base_delay=1.0)
        delay2 = exponential_backoff(2, base_delay=1.0)

        # Should increase exponentially
        assert delay1 > delay0
        assert delay2 > delay1

    def test_rate_limiter_acquire(self):
        """Test rate limiter acquire logic."""
        from pr_testing.github_retry import GitHubRateLimiter

        limiter = GitHubRateLimiter(calls_per_hour=10)

        # Should allow first call immediately
        stats_before = limiter.get_stats()
        assert stats_before["calls_last_hour"] == 0

    def test_rate_limiter_stats(self):
        """Test rate limiter statistics."""
        from pr_testing.github_retry import GitHubRateLimiter

        limiter = GitHubRateLimiter(calls_per_hour=5000)
        stats = limiter.get_stats()

        assert "calls_last_hour" in stats
        assert "calls_remaining" in stats
        assert "rate_limit" in stats
        assert stats["rate_limit"] == 5000


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
