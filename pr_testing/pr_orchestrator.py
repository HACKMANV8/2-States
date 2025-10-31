"""
PR Test Orchestrator.

Main coordination layer for PR-based testing that:
1. Fetches PR context from GitHub
2. Detects and validates deployment URL
3. Analyzes codebase structure
4. Builds test context
5. Executes tests via Playwright
6. Posts results to GitHub and Slack
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .github_service import GitHubService
from .deployment_detector import DeploymentDetector
from .codebase_analyzer import CodebaseAnalyzer
from .context_builder import PRContextBuilder


class PRTestOrchestrator:
    """
    Orchestrates end-to-end PR testing workflow.

    This is the main entry point for PR-based testing.
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize PR test orchestrator.

        Args:
            github_token: GitHub Personal Access Token (falls back to env var)
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.github_service = GitHubService(github_token=self.github_token)
        self.deployment_detector = DeploymentDetector()
        self.codebase_analyzer = CodebaseAnalyzer()
        self.context_builder = PRContextBuilder()

    async def test_pr(self, pr_url: str, custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Test a GitHub Pull Request.

        This is the main entry point that coordinates the entire PR testing workflow.

        Args:
            pr_url: GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
            custom_instructions: Optional custom testing instructions from user

        Returns:
            Dict with complete test results
        """
        print("\n" + "=" * 80)
        print("🚀 STARTING PR-BASED TESTING")
        print("=" * 80)
        print(f"PR URL: {pr_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

        test_run_id = f"pr-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

        result = {
            "test_run_id": test_run_id,
            "pr_url": pr_url,
            "started_at": datetime.now(),
            "status": "in_progress",
            "pr_context": None,
            "deployment_info": None,
            "codebase_analysis": None,
            "test_context": None,
            "test_results": None,
            "error": None
        }

        try:
            # STEP 1: Fetch PR Context from GitHub
            print("📥 STEP 1: Fetching PR Context from GitHub")
            print("-" * 80)

            pr_context = await self.github_service.get_full_pr_context(pr_url)
            result["pr_context"] = pr_context

            pr_info = pr_context["pr_info"]
            pr_metadata = pr_context["metadata"]

            print(f"\n✅ PR Context Retrieved")
            print(f"   Title: {pr_metadata['title']}")
            print(f"   Author: @{pr_metadata['author']}")
            print(f"   Status: {pr_metadata['state']}")
            print(f"   Files Changed: {len(pr_context['files'])}")
            print("")

            # STEP 2: Detect and Validate Deployment URL
            print("🔍 STEP 2: Detecting Deployment URL")
            print("-" * 80)

            deployment_info = await self.deployment_detector.find_and_validate_deployment(pr_context)
            result["deployment_info"] = deployment_info

            if not deployment_info["found"] or not deployment_info["accessible"]:
                error_msg = "Could not find an accessible deployment URL for this PR"
                print(f"\n❌ {error_msg}")
                print("   Please ensure the PR has a deployment preview URL in:")
                print("   - PR description")
                print("   - PR comments")
                print("   - CI/CD status checks")
                print("")

                result["status"] = "failed"
                result["error"] = error_msg
                result["completed_at"] = datetime.now()
                return result

            deployment_url = deployment_info["deployment_url"]
            platform = self.deployment_detector.detect_platform(deployment_url)

            print(f"\n✅ Deployment Found and Validated")
            print(f"   URL: {deployment_url}")
            print(f"   Platform: {platform}")
            print(f"   HTTP Status: {deployment_info['validation']['status_code']}")
            print(f"   Response Time: {deployment_info['validation']['response_time_ms']}ms")
            print("")

            # STEP 3: Analyze Codebase
            print("📚 STEP 3: Analyzing Codebase Structure")
            print("-" * 80)

            codebase_analysis = await self.codebase_analyzer.analyze_repository(
                owner=pr_info["owner"],
                repo=pr_info["repo"],
                branch=pr_metadata["head_branch"],
                github_token=self.github_token
            )
            result["codebase_analysis"] = codebase_analysis

            print(f"\n✅ Codebase Analysis Complete")
            print(f"   Project Type: {codebase_analysis['project_type']}")
            print(f"   Tech Stack: {', '.join(codebase_analysis['tech_stack']) if codebase_analysis['tech_stack'] else 'Unknown'}")
            print("")

            # STEP 4: Build Test Context
            print("📝 STEP 4: Building Test Context")
            print("-" * 80)

            context_document = self.context_builder.build_context_document(
                pr_context=pr_context,
                codebase_analysis=codebase_analysis,
                deployment_info=deployment_info
            )

            test_scenarios = self.context_builder.generate_test_scenarios(
                pr_context=pr_context,
                codebase_analysis=codebase_analysis,
                deployment_url=deployment_url
            )

            agent_instructions = self.context_builder.build_agent_instructions(
                context_document=context_document,
                test_scenarios=test_scenarios,
                deployment_url=deployment_url
            )

            result["test_context"] = {
                "context_document": context_document,
                "test_scenarios": test_scenarios,
                "agent_instructions": agent_instructions,
                "deployment_url": deployment_url
            }

            print(f"\n✅ Test Context Prepared")
            print(f"   Scenarios: {len(test_scenarios)}")
            print(f"   Deployment URL: {deployment_url}")
            print("")

            # STEP 5: Execute Tests (this will be handled by TestGPT engine)
            print("🧪 STEP 5: Test Execution Ready")
            print("-" * 80)
            print("   Test context prepared for Playwright agent")
            print("   Will be executed by TestGPT engine")
            print("")

            result["status"] = "ready_for_execution"
            result["completed_at"] = datetime.now()

            print("=" * 80)
            print("✅ PR TESTING PREPARATION COMPLETE")
            print("=" * 80)
            print(f"Test Run ID: {test_run_id}")
            print(f"Ready to execute {len(test_scenarios)} test scenarios")
            print("")

            return result

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()

            print(f"\n❌ ERROR: {str(e)}")
            print(f"\nTraceback:\n{error_trace}")

            result["status"] = "failed"
            result["error"] = str(e)
            result["error_trace"] = error_trace
            result["completed_at"] = datetime.now()

            return result

    async def post_results_to_github(
        self,
        pr_url: str,
        test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Post test results as a comment on the GitHub PR.

        Args:
            pr_url: GitHub PR URL
            test_results: Test execution results

        Returns:
            Dict with posting result
        """
        print("\n📤 Posting test results to GitHub...")

        # Parse PR URL
        pr_info = self.github_service.parse_pr_url(pr_url)
        if not pr_info:
            return {"success": False, "error": "Invalid PR URL"}

        # Format comment body
        comment_body = self._format_github_comment(test_results)

        try:
            # Post comment
            comment_result = await self.github_service.post_pr_comment(
                owner=pr_info["owner"],
                repo=pr_info["repo"],
                pr_number=pr_info["pr_number"],
                comment_body=comment_body
            )

            print(f"   ✅ Comment posted successfully")
            print(f"   Comment URL: {comment_result['html_url']}")

            return {
                "success": True,
                "comment_url": comment_result["html_url"],
                "comment_id": comment_result["comment_id"]
            }

        except Exception as e:
            print(f"   ❌ Failed to post comment: {e}")
            return {"success": False, "error": str(e)}

    def _format_github_comment(self, test_results: Dict[str, Any]) -> str:
        """
        Format test results as a GitHub comment with markdown.

        Args:
            test_results: Test execution results

        Returns:
            Formatted markdown comment
        """
        lines = []

        # Header
        lines.append("## 🤖 TestGPT PR Testing Results")
        lines.append("")

        # Status badge
        overall_status = test_results.get("overall_status", "unknown")
        if overall_status == "PASS":
            lines.append("### ✅ All Tests Passed")
        elif overall_status == "FAIL":
            lines.append("### ❌ Some Tests Failed")
        else:
            lines.append("### ⚠️ Tests Completed with Issues")

        lines.append("")

        # Summary
        passed = test_results.get("passed_count", 0)
        total = test_results.get("total_count", 0)
        lines.append(f"**Test Summary:** {passed}/{total} scenarios passed")
        lines.append(f"**Test Run ID:** `{test_results.get('test_run_id', 'N/A')}`")
        lines.append(f"**Deployment URL:** {test_results.get('deployment_url', 'N/A')}")
        lines.append("")

        # Scenario results
        if test_results.get("scenario_results"):
            lines.append("### 📋 Scenario Results")
            lines.append("")

            for scenario in test_results["scenario_results"]:
                status_emoji = "✅" if scenario["passed"] else "❌"
                lines.append(f"{status_emoji} **{scenario['name']}** - {scenario['priority']} priority")

                if not scenario["passed"]:
                    lines.append(f"   - ❌ {scenario.get('failure_reason', 'Test failed')}")

                lines.append("")

        # Failures detail
        if test_results.get("failures"):
            lines.append("### ❌ Failed Tests Details")
            lines.append("")

            for failure in test_results["failures"]:
                lines.append(f"**{failure['scenario']}**")
                lines.append(f"```")
                lines.append(failure['error'])
                lines.append(f"```")
                lines.append("")

        # Console errors
        if test_results.get("console_errors"):
            lines.append("### ⚠️ Console Errors")
            lines.append("")
            lines.append("```")
            for error in test_results["console_errors"][:5]:  # Limit to 5
                lines.append(error)
            lines.append("```")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"🤖 *Automated testing by [TestGPT](https://github.com/yourusername/TestGPT)*")
        lines.append(f"⏱️ *Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*")

        return "\n".join(lines)

    def format_slack_summary(self, pr_test_result: Dict[str, Any], test_execution_result: Optional[Dict[str, Any]] = None) -> str:
        """
        Format PR test results for Slack.

        Args:
            pr_test_result: Result from test_pr()
            test_execution_result: Optional test execution results from Playwright

        Returns:
            Formatted Slack message
        """
        lines = []

        # Header
        if pr_test_result["status"] == "failed":
            lines.append("❌ **PR Testing Failed**")
        elif pr_test_result["status"] == "ready_for_execution":
            lines.append("✅ **PR Testing Preparation Complete**")
        else:
            lines.append("ℹ️  **PR Testing Status Update**")

        lines.append("")

        # PR Info
        if pr_test_result.get("pr_context"):
            pr_metadata = pr_test_result["pr_context"]["metadata"]
            lines.append(f"**PR:** {pr_metadata['title']}")
            lines.append(f"**Author:** @{pr_metadata['author']}")
            lines.append(f"**Branch:** `{pr_metadata['head_branch']}` → `{pr_metadata['base_branch']}`")
            lines.append("")

        # Deployment Info
        if pr_test_result.get("deployment_info", {}).get("deployment_url"):
            deployment_url = pr_test_result["deployment_info"]["deployment_url"]
            platform = self.deployment_detector.detect_platform(deployment_url)
            lines.append(f"**Deployment:** {deployment_url}")
            lines.append(f"**Platform:** {platform}")
            lines.append("")

        # Codebase Info
        if pr_test_result.get("codebase_analysis"):
            analysis = pr_test_result["codebase_analysis"]
            lines.append(f"**Project Type:** {analysis['project_type']}")
            lines.append(f"**Tech Stack:** {', '.join(analysis['tech_stack']) if analysis['tech_stack'] else 'Unknown'}")
            lines.append("")

        # Test Scenarios
        if pr_test_result.get("test_context", {}).get("test_scenarios"):
            scenarios = pr_test_result["test_context"]["test_scenarios"]
            lines.append(f"**Test Scenarios Generated:** {len(scenarios)}")

            for scenario in scenarios[:3]:  # Show first 3
                lines.append(f"  • {scenario['name']} ({scenario['priority']} priority)")

            if len(scenarios) > 3:
                lines.append(f"  ... and {len(scenarios) - 3} more")

            lines.append("")

        # Test Execution Results (if available)
        if test_execution_result:
            passed = test_execution_result.get("passed_count", 0)
            total = test_execution_result.get("total_count", 0)
            lines.append(f"**Test Results:** {passed}/{total} scenarios passed")

            if test_execution_result.get("failures"):
                lines.append("")
                lines.append("**Failures:**")
                for failure in test_execution_result["failures"][:3]:
                    lines.append(f"  ❌ {failure['scenario']}: {failure['error'][:100]}")

            lines.append("")

        # Error (if any)
        if pr_test_result.get("error"):
            lines.append("**Error:**")
            lines.append(f"```{pr_test_result['error']}```")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"🤖 *TestGPT PR Testing*")
        lines.append(f"🆔 *Test Run:* `{pr_test_result['test_run_id']}`")

        return "\n".join(lines)
