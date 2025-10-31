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
from datetime import datetime
from typing import Optional
from request_parser import SlackRequestParser
from test_plan_builder import TestPlanBuilder
from test_executor import TestExecutor
from result_formatter import ResultFormatter
from persistence import PersistenceLayer
from models import RunArtifact, TestPlan
from mcp_manager import get_mcp_manager


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
            await self.mcp_manager.cleanup_all()

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
