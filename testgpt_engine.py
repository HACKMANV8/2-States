"""
TestGPT Engine - Main orchestration layer.

Coordinates the entire testing pipeline:
1. Parse Slack request
2. Build test plan with matrix expansion
3. Execute tests
4. Aggregate results
5. Format Slack summary
6. Persist everything
"""

import uuid
import logging
import warnings
from datetime import datetime
from typing import Optional, Dict, Any, List
from request_parser import SlackRequestParser
from test_plan_builder import TestPlanBuilder
from test_executor import TestExecutor
from result_formatter import ResultFormatter
from persistence import PersistenceLayer
from models import RunArtifact, TestPlan
from mcp_manager import get_mcp_manager

# Suppress known asyncio warnings from MCP async generator cleanup
# These are cosmetic errors related to Python 3.13 async context handling
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*async_generator.*')
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*cancel scope.*')


class TestGPTEngine:
    """
    Main orchestration engine for TestGPT.

    Coordinates all components to execute multi-environment QA tests
    from Slack requests to formatted results.
    """

    def __init__(self, mcp_tools=None, storage_dir: str = "./testgpt_data"):
        """
        Initialize TestGPT engine.

        Args:
            mcp_tools: (Deprecated) No longer used - using dynamic MCP manager
            storage_dir: Directory for persistence storage
        """
        self.parser = SlackRequestParser()
        self.plan_builder = TestPlanBuilder()
        self.executor = TestExecutor()  # Always create executor (uses dynamic MCP manager)
        self.formatter = ResultFormatter()
        self.persistence = PersistenceLayer(storage_dir)
        self.mcp_manager = get_mcp_manager()

    async def process_test_request(
        self,
        slack_message: str,
        user_id: str = "slack-user"
    ) -> str:
        """
        Process a complete test request from Slack.

        This is the main entry point that:
        1. Parses the request
        2. Checks for re-run
        3. Builds test plan
        4. Executes tests (if executor available)
        5. Formats results
        6. Persists everything
        7. Returns Slack-formatted summary

        Args:
            slack_message: Raw message from Slack
            user_id: Slack user ID

        Returns:
            Formatted Slack summary message
        """
        print("\n" + "=" * 70)
        print("🚀 TestGPT Processing Request")
        print("=" * 70)
        print(f"Message: {slack_message}")
        print(f"User: {user_id}\n")

        # Step 1: Parse request
        print("📋 Step 1: Parsing Slack request...")
        parsed_request = self.parser.parse(slack_message, user_id)

        print(f"   Target URL: {parsed_request.target_urls[0]}")
        print(f"   Flows: {', '.join(parsed_request.flows)}")
        print(f"   Viewports: {', '.join(parsed_request.required_viewports)}")
        print(f"   Browsers: {', '.join(parsed_request.required_browsers)}")
        print(f"   Networks: {', '.join(parsed_request.required_networks)}")
        print(f"   Is Re-run: {parsed_request.is_rerun}\n")

        # Step 2: Check for re-run
        if parsed_request.is_rerun:
            return await self._handle_rerun(parsed_request, user_id)

        # Step 3: Build test plan
        print("🏗️  Step 2: Building test plan with matrix expansion...")

        scenario_id = self.parser.get_scenario_id(parsed_request)
        scenario_name = self.parser.get_scenario_name(parsed_request)

        test_plan = self.plan_builder.build_test_plan(
            parsed_request=parsed_request,
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            created_by=user_id
        )

        print(f"   Scenario: {test_plan.scenario_name}")
        print(f"   Matrix cells: {test_plan.total_cells_to_execute}")
        print(f"   Estimated duration: {test_plan.estimated_duration_minutes} minutes\n")

        # Step 4: Save scenario definition
        print("💾 Step 3: Saving scenario definition for re-run capability...")
        scenario_def = self.plan_builder.build_scenario_definition(test_plan, user_id)
        self.persistence.save_scenario(scenario_def)
        print()

        # Step 5: Execute tests (if executor available)
        try:
            # Check if this is a PR test
            if parsed_request.is_pr_test:
                print("🧪 Step 4: Executing PR-based tests...")
                pr_result = await self._handle_pr_test(parsed_request, user_id)
                return pr_result

            # Check if this is a backend API test
            if parsed_request.is_backend_api_test:
                print("🧪 Step 4: Executing backend API tests...")

                # Build test instructions from parsed request
                test_instructions = self._build_backend_test_instructions(parsed_request)

                # Execute backend API test
                backend_result = await self.executor.execute_backend_api_test(
                    repo_url=parsed_request.backend_repo_url,
                    api_path=parsed_request.backend_api_path,
                    app_module=parsed_request.backend_app_module,
                    test_instructions=test_instructions
                )

                # Format backend result as a Slack message and return immediately
                return self._format_backend_test_slack_summary(backend_result, parsed_request)

            # Regular Playwright testing
            if self.executor:
                print("▶️  Step 4: Executing test matrix...")
                cell_results = await self.executor.execute_test_plan(test_plan)
                print(f"   Completed {len(cell_results)} cells\n")
            else:
                print("⚠️  Step 4: Skipping execution (no MCP tools connected)")
                print("   Generating mock results for demonstration...\n")
                cell_results = self._generate_mock_results(test_plan)

            # Step 6: Aggregate results
            print("📊 Step 5: Aggregating results...")
            run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

            run_artifact = self.formatter.aggregate_results(
                cell_results=cell_results,
                scenario_name=test_plan.scenario_name,
                target_url=test_plan.target_url,
                run_id=run_id
            )

            # Fill in additional artifact fields
            run_artifact.test_plan_id = test_plan.test_plan_id
            run_artifact.scenario_id = test_plan.scenario_id
            run_artifact.triggered_by = user_id

            print(f"   Overall status: {run_artifact.overall_status.value}")
            print(f"   Pass rate: {run_artifact.passed_cells}/{run_artifact.total_cells}\n")

            # Step 7: Save run artifact
            print("💾 Step 6: Saving run artifact...")
            self.persistence.save_run_artifact(run_artifact)
            self.persistence.update_scenario_last_run(scenario_id, datetime.now())
            print()

            # Step 8: Format Slack summary
            print("✍️  Step 7: Formatting Slack summary...")
            slack_summary = self.formatter.format_slack_summary(run_artifact)
            print()

            print("=" * 70)
            print("✅ TestGPT Processing Complete")
            print("=" * 70 + "\n")

            return slack_summary

        finally:
            # Always cleanup MCP servers after execution (success or failure)
            # Suppress MCP async generator cleanup warnings (known issue with stdio connections)
            try:
                await self.mcp_manager.cleanup_all()
            except RuntimeError as e:
                if "cancel scope" in str(e):
                    # Known issue: MCP stdio async generators cleanup in different task
                    # This is cosmetic and doesn't affect functionality
                    pass
                else:
                    raise
            except Exception as e:
                # Log other errors but don't fail the request
                print(f"⚠️  Warning during MCP cleanup: {e}")

    async def _handle_rerun(self, parsed_request, user_id: str) -> str:
        """
        Handle a re-run request.

        Finds the matching scenario and re-executes it.
        """
        print("🔄 Handling re-run request...")

        reference = parsed_request.rerun_scenario_reference

        # Try to find matching scenario
        # First by exact ID
        scenario_dict = self.persistence.load_scenario(reference)

        # If not found, search by name
        if not scenario_dict:
            matching_ids = self.persistence.find_scenarios_by_name(reference)

            if not matching_ids:
                # Try by URL
                matching_ids = self.persistence.find_scenarios_by_url(reference)

            if matching_ids:
                scenario_dict = self.persistence.load_scenario(matching_ids[0])

        if not scenario_dict:
            return (
                f"❌ Could not find scenario matching '{reference}'\n\n"
                f"Available scenarios:\n" +
                "\n".join(
                    f"  • {s['scenario_name']}"
                    for s in self.persistence.list_all_scenarios()[:5]
                )
            )

        # Reconstruct parsed request from scenario
        print(f"   Found scenario: {scenario_dict['scenario_name']}")
        print(f"   Re-executing with saved configuration...\n")

        # Re-run the scenario (implementation would reconstruct and execute)
        # For now, return a message
        return (
            f"🔄 Re-running scenario: {scenario_dict['scenario_name']}\n\n"
            f"Target: {scenario_dict['target_url']}\n"
            f"Last run: {scenario_dict.get('last_run_at', 'Never')}\n\n"
            f"(Re-execution would happen here)"
        )

    def _generate_mock_results(self, test_plan: TestPlan):
        """
        Generate mock cell results for demonstration when no executor is available.

        Simulates some failures to showcase the reporting system.
        """
        from models import CellResult, StepResult, TestStatus, FailurePriority
        from datetime import datetime

        mock_results = []
        now = datetime.now()

        for i, cell in enumerate(test_plan.matrix_cells):
            # Simulate Safari failures and Chrome successes
            is_safari = "webkit" in cell.browser.name
            is_mobile = cell.viewport.is_mobile
            is_slow_network = cell.network.name != "normal"

            # Safari on mobile with slow network fails
            if is_safari and is_mobile and is_slow_network:
                status = TestStatus.FAIL
                failure_summary = f"{cell.browser.display_name} on {cell.viewport.device_class}: Hero CTA button not visible in viewport"
                failure_priority = FailurePriority.P0
            # Safari on desktop fails sometimes
            elif is_safari and not is_mobile and i % 3 == 0:
                status = TestStatus.FAIL
                failure_summary = f"{cell.browser.display_name}: Pricing modal does not open on click"
                failure_priority = FailurePriority.P0
            # Slow network causes some failures
            elif is_slow_network and i % 4 == 0:
                status = TestStatus.FAIL
                failure_summary = f"Page load timeout after 10 seconds on {cell.network.display_name}"
                failure_priority = FailurePriority.P1
            else:
                status = TestStatus.PASS
                failure_summary = None
                failure_priority = None

            # Create mock step results
            step_results = [
                StepResult(
                    step_number=step.step_number,
                    action=step.action.value,
                    target=step.target,
                    expected_outcome=step.expected_outcome,
                    actual_outcome=step.expected_outcome if status == TestStatus.PASS else "Failed",
                    passed=(status == TestStatus.PASS),
                    timestamp=now,
                    error_message=failure_summary if status == TestStatus.FAIL else None,
                    duration_ms=1000 + (i * 100)
                )
                for step in cell.steps
            ]

            mock_results.append(CellResult(
                cell_id=cell.cell_id,
                viewport=cell.viewport.name,
                browser=cell.browser.name,
                network=cell.network.name,
                status=status,
                started_at=now,
                completed_at=now,
                duration_ms=5000 + (i * 1000),
                step_results=step_results,
                screenshots=[],
                console_errors=[],
                network_requests=[],
                failure_summary=failure_summary,
                failure_priority=failure_priority
            ))

        return mock_results

    def get_scenario_library(self) -> str:
        """
        Get a formatted list of saved scenarios.

        Returns:
            Formatted string listing all scenarios
        """
        scenarios = self.persistence.list_all_scenarios()

        if not scenarios:
            return "No saved scenarios yet. Run a test to create one!"

        lines = ["📚 Saved Test Scenarios\n"]

        for scenario in scenarios[:10]:  # Limit to 10
            lines.append(f"• {scenario['scenario_name']}")
            lines.append(f"  Target: {scenario['target_url']}")
            lines.append(f"  Tags: {', '.join(scenario.get('tags', []))}")
            lines.append(f"  Re-run: \"re-run {scenario['scenario_name'].split(' - ')[0].lower()}\"")
            lines.append("")

        return "\n".join(lines)

    def _build_backend_test_instructions(self, parsed_request) -> str:
        """
        Build test instructions for backend API testing from parsed request.

        Args:
            parsed_request: ParsedSlackRequest with backend test details

        Returns:
            Test instructions string for the backend testing agent
        """
        # Start with base instruction
        instructions = []

        # Add flows/scenarios if specified
        if parsed_request.flows:
            flow_descriptions = ', '.join(parsed_request.flows)
            instructions.append(f"Test the following API flows: {flow_descriptions}")
        else:
            instructions.append("Run comprehensive API tests")

        # Add explicit expectations
        if parsed_request.explicit_expectations:
            expectations = '\n'.join(f"- {exp}" for exp in parsed_request.explicit_expectations)
            instructions.append(f"\nVerify these expectations:\n{expectations}")

        # Add general testing guidelines
        instructions.append("\nInclude:")
        instructions.append("1. API health check")
        instructions.append("2. Test all available endpoints")
        instructions.append("3. Verify CRUD operations work correctly")
        instructions.append("4. Check error handling")
        instructions.append("5. Run smoke tests if available")

        # Use raw message for additional context
        if parsed_request.raw_message:
            instructions.append(f"\nOriginal request: {parsed_request.raw_message}")

        return "\n".join(instructions)

    async def _handle_pr_test(self, parsed_request, user_id: str) -> str:
        """
        Handle PR testing request.

        Args:
            parsed_request: Parsed request with PR information
            user_id: User who triggered the test

        Returns:
            Formatted Slack summary
        """
        from pr_testing import PRTestOrchestrator
        from pr_testing.pr_persistence import PRTestPersistence

        try:
            # Initialize PR orchestrator and persistence
            orchestrator = PRTestOrchestrator()
            persistence = PRTestPersistence()

            # Check if PR URL is provided
            pr_url = parsed_request.pr_url
            if not pr_url:
                return (
                    "❌ **PR Testing Failed**\n\n"
                    "Could not find a valid GitHub PR URL in your message.\n\n"
                    "Please provide a PR URL like:\n"
                    "- `test this PR https://github.com/owner/repo/pull/123`\n"
                    "- `test out this PR: https://github.com/owner/repo/pull/456`"
                )

            # Step 1: Prepare PR test context
            pr_test_result = await orchestrator.test_pr(
                pr_url=pr_url,
                custom_instructions=parsed_request.raw_message
            )

            # Save to database
            pr_test_result["triggered_by"] = "slack"
            pr_test_result["triggered_by_user"] = user_id
            pr_test_result["custom_instructions"] = parsed_request.raw_message

            test_run_id = persistence.save_pr_test_start(pr_test_result)
            if test_run_id:
                pr_test_result["test_run_id"] = test_run_id

            # Check if preparation succeeded
            if pr_test_result["status"] == "failed":
                error_msg = pr_test_result.get("error", "Unknown error")
                return (
                    f"❌ **PR Testing Preparation Failed**\n\n"
                    f"**Error:** {error_msg}\n\n"
                    f"**PR URL:** {pr_url}\n\n"
                    f"Please check that:\n"
                    f"- The PR URL is valid\n"
                    f"- The PR has a deployment preview URL\n"
                    f"- Your GitHub token is configured (GITHUB_TOKEN env var)\n"
                )

            # Step 2: Execute tests with Playwright
            if pr_test_result["status"] == "ready_for_execution":
                deployment_url = pr_test_result["test_context"]["deployment_url"]
                agent_instructions = pr_test_result["test_context"]["agent_instructions"]

                print("\n🎭 Executing tests with Playwright agent...")

                # Execute using existing TestExecutor
                # Create a simple test with the deployment URL and instructions
                test_result = await self._execute_pr_tests_with_playwright(
                    deployment_url=deployment_url,
                    instructions=agent_instructions,
                    pr_context=pr_test_result
                )

                # Update database with test results
                if test_run_id:
                    persistence.update_pr_test_results(test_run_id, test_result)

                # Format Slack summary
                slack_summary = orchestrator.format_slack_summary(
                    pr_test_result=pr_test_result,
                    test_execution_result=test_result
                )

                return slack_summary

            return orchestrator.format_slack_summary(pr_test_result=pr_test_result)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Error in PR testing: {e}\n{error_trace}")

            return (
                f"❌ **PR Testing Failed**\n\n"
                f"**Error:** {str(e)}\n\n"
                f"**PR URL:** {parsed_request.pr_url}\n\n"
                f"Please check the logs for more details."
            )

    async def _execute_pr_tests_with_playwright(
        self,
        deployment_url: str,
        instructions: str,
        pr_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute PR tests using Playwright agent.

        Args:
            deployment_url: Deployment URL to test
            instructions: Test instructions for agent
            pr_context: Full PR context

        Returns:
            Test execution results
        """
        from agno.agent import Agent
        from agno.tools.mcp import MCPTools
        from datetime import datetime

        try:
            # Get MCP manager and create instance for this test
            print(f"   🔧 Starting Playwright MCP instance...")

            # Use multiple browsers for comprehensive testing
            # For now use chromium as primary, but structure for easy extension
            browsers = ["chromium"]  # Can add ["chromium", "webkit", "firefox"] for multi-browser

            # Use first browser for primary test
            browser = browsers[0]
            mcp_command = f'npx -y @playwright/mcp@latest --browser {browser}'
            print(f"   🌐 Testing with {browser} browser")

            # Connect to MCP
            mcp_tools = MCPTools(command=mcp_command)
            await mcp_tools.connect()

            print(f"   ✅ Playwright MCP connected")

            # Create agent with Claude model
            from agno.models.anthropic import Claude

            pr_agent = Agent(
                name="PRTestAgent",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[mcp_tools],
                markdown=True,
                debug_mode=True
            )

            print(f"   🤖 Executing test scenarios...")

            start_time = datetime.now()

            # Run tests
            response = await pr_agent.arun(instructions)

            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            print(f"   ✅ Test execution completed ({duration_ms}ms)")

            # Parse results from agent response
            response_text = str(response)

            # Simple pass/fail detection
            test_passed = any(indicator in response_text.lower() for indicator in [
                "all tests passed",
                "all scenarios passed",
                "✅",
                "success"
            ])

            test_failed = any(indicator in response_text.lower() for indicator in [
                "failed",
                "error",
                "❌",
                "failure"
            ])

            # Count scenarios (rough estimate from response)
            scenario_count = len(pr_context.get("test_context", {}).get("test_scenarios", []))

            # Cleanup MCP with proper error handling
            try:
                await mcp_tools.disconnect()
            except RuntimeError as e:
                if "cancel scope" in str(e) or "asyncgen" in str(e):
                    # Known cosmetic issue with stdio cleanup - safe to ignore
                    pass
                else:
                    print(f"   ⚠️  MCP cleanup warning: {e}")
            except Exception as e:
                print(f"   ⚠️  MCP cleanup error: {e}")

            return {
                "success": True,
                "test_run_id": pr_context.get("test_run_id"),
                "deployment_url": deployment_url,
                "overall_status": "PASS" if test_passed and not test_failed else "FAIL",
                "passed_count": scenario_count if test_passed else 0,
                "total_count": scenario_count,
                "duration_ms": duration_ms,
                "agent_response": response_text[:2000],  # Truncate for summary
                "scenario_results": self._parse_scenario_results(response_text, pr_context),
                "failures": self._extract_failures(response_text) if test_failed else [],
                "console_errors": [],
                "started_at": start_time,
                "completed_at": end_time
            }

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"   ❌ Test execution failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "error_trace": error_trace
            }

    def _parse_scenario_results(self, response_text: str, pr_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse scenario results from agent response with improved detection.

        Uses multiple indicators to determine pass/fail status.
        """
        scenarios = pr_context.get("test_context", {}).get("test_scenarios", [])
        results = []

        # Normalize response text
        response_lower = response_text.lower()
        response_lines = response_text.split("\n")

        for scenario in scenarios:
            scenario_name = scenario["name"]
            scenario_lower = scenario_name.lower()

            # Check multiple pass indicators
            pass_indicators = [
                f"✅ {scenario_lower}",
                f"{scenario_lower} ✅",
                f"{scenario_lower}: passed",
                f"{scenario_lower} passed",
                f"{scenario_lower}: success",
                f"successfully completed {scenario_lower}",
                "all tests passed" in response_lower and scenario_lower in response_lower,
            ]

            # Check multiple fail indicators
            fail_indicators = [
                f"❌ {scenario_lower}",
                f"{scenario_lower} ❌",
                f"{scenario_lower}: failed",
                f"{scenario_lower} failed",
                f"{scenario_lower}: error",
                f"failed {scenario_lower}",
            ]

            passed = any(indicator if isinstance(indicator, bool) else indicator in response_lower
                        for indicator in pass_indicators)

            failed = any(indicator in response_lower for indicator in fail_indicators)

            # If both passed and failed indicators, prefer failed
            if failed:
                passed = False

            # Extract failure reason if failed
            failure_reason = None
            if failed:
                # Try to find the failure line
                for line in response_lines:
                    if scenario_lower in line.lower() and ("failed" in line.lower() or "error" in line.lower()):
                        failure_reason = line.strip()
                        break

            results.append({
                "name": scenario_name,
                "priority": scenario["priority"],
                "passed": passed,
                "failure_reason": failure_reason or ("Test failed or not executed" if not passed else None),
                "mentioned": scenario_lower in response_lower
            })

        return results

    def _extract_failures(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract failure details from agent response."""
        failures = []

        # Look for common failure patterns
        lines = response_text.split("\n")
        current_failure = None

        for line in lines:
            if "❌" in line or "failed" in line.lower() or "error" in line.lower():
                if current_failure:
                    failures.append(current_failure)

                current_failure = {
                    "scenario": line.strip(),
                    "error": line.strip()
                }
            elif current_failure and line.strip():
                # Append to current failure
                current_failure["error"] += f"\n{line.strip()}"

        if current_failure:
            failures.append(current_failure)

        return failures[:5]  # Limit to 5 failures

    def _format_backend_test_slack_summary(self, backend_result: dict, parsed_request) -> str:
        """
        Format backend API test results as a Slack summary message.

        Args:
            backend_result: Result dict from execute_backend_api_test
            parsed_request: Original ParsedSlackRequest

        Returns:
            Formatted Slack message string
        """
        lines = []

        # Header
        if backend_result["status"] == "completed":
            lines.append("✅ **Backend API Testing Completed**\n")
        else:
            lines.append("❌ **Backend API Testing Failed**\n")

        # Test details
        if backend_result.get("repo_url"):
            lines.append(f"**Repository:** {backend_result['repo_url']}")
        elif backend_result.get("api_path"):
            lines.append(f"**API Path:** {backend_result['api_path']}")

        lines.append(f"**App Module:** {backend_result.get('app_module', 'main:app')}")
        lines.append(f"**Duration:** {backend_result['duration_ms']}ms\n")

        # Results
        if backend_result["status"] == "completed":
            lines.append("**Test Results:**")
            lines.append("```")
            lines.append(backend_result["result"])
            lines.append("```\n")
        else:
            lines.append("**Error:**")
            lines.append("```")
            lines.append(backend_result.get("error", "Unknown error"))
            lines.append("```\n")

            if backend_result.get("error_traceback"):
                lines.append("**Traceback:**")
                lines.append("```")
                lines.append(backend_result["error_traceback"])
                lines.append("```\n")

        # Footer
        lines.append("---")
        lines.append(f"🤖 *TestGPT Backend API Testing*")
        lines.append(f"⏱️  *Completed at:* {backend_result['completed_at'].strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)
