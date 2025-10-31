"""
Test Runner Service for TestGPT.

Executes tests with specified configurations (browser, viewport, network).
Integrates with existing test_executor.py and adds configuration support.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal
from backend import crud
from test_executor import TestExecutor
from models import TestPlan, MatrixCell, TestStep, ActionType
from config import VIEWPORTS, BROWSERS, NETWORKS


class TestRunnerService:
    """
    Service that runs tests with configuration support.

    Bridges the gap between:
    - Backend API (test suites, configs, execution records)
    - Test Executor (actual Playwright MCP execution)
    """

    def __init__(self):
        self.executor = TestExecutor()

    async def execute_test_with_config(
        self,
        execution_id: str,
        test_suite_dict: Dict[str, Any],
        config_dict: Optional[Dict[str, Any]] = None,
        browser: Optional[str] = None,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
        network_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a test suite with specified configuration.

        Args:
            execution_id: Database execution record ID
            test_suite_dict: Test suite data from database
            config_dict: Configuration template data (optional)
            browser: Override browser (optional)
            viewport_width: Override viewport width (optional)
            viewport_height: Override viewport height (optional)
            network_mode: Override network mode (optional)

        Returns:
            Execution result dictionary
        """
        db = SessionLocal()

        try:
            # Update status to running
            crud.update_test_execution_status(
                db,
                execution_id,
                status="running",
                started_at=datetime.utcnow()
            )

            # Determine configuration
            final_browser = browser or (config_dict["browsers"][0] if config_dict else "chrome")
            final_viewport_width = viewport_width or (
                config_dict["viewports"][0]["width"] if config_dict else 1920
            )
            final_viewport_height = viewport_height or (
                config_dict["viewports"][0]["height"] if config_dict else 1080
            )
            final_network_mode = network_mode or (
                config_dict["network_modes"][0] if config_dict else "online"
            )

            # Get viewport profile
            viewport_profile = self._get_viewport_profile(
                final_viewport_width,
                final_viewport_height
            )

            # Get browser profile
            browser_profile = self._get_browser_profile(final_browser)

            # Get network profile
            network_profile = self._get_network_profile(final_network_mode)

            # Convert test_steps to TestStep objects
            test_steps = self._convert_test_steps(test_suite_dict.get("test_steps", []))

            # Create a matrix cell (single environment)
            matrix_cell = MatrixCell(
                cell_id=f"cell-{execution_id}",
                viewport=viewport_profile,
                browser=browser_profile,
                network=network_profile,
                steps=test_steps,
            )

            # Create a minimal test plan
            test_plan = TestPlan(
                test_plan_id=f"plan-{execution_id}",
                created_at=datetime.utcnow(),
                created_by="api",
                scenario_id=test_suite_dict.get("id", "unknown"),
                scenario_name=test_suite_dict.get("name", "Test"),
                target_url=test_suite_dict.get("target_url", ""),
                flows=[],
                environment_matrix=None,
                matrix_cells=[matrix_cell],
                total_cells_to_execute=1,
                estimated_duration_minutes=5,
                user_request=test_suite_dict.get("prompt", ""),
            )

            # Execute the test
            print(f"🧪 Executing test: {test_suite_dict.get('name')}")
            print(f"   Browser: {final_browser}")
            print(f"   Viewport: {final_viewport_width}x{final_viewport_height}")
            print(f"   Network: {final_network_mode}")

            cell_results = await self.executor.execute_test_plan(test_plan)

            # Process results
            if cell_results and len(cell_results) > 0:
                cell_result = cell_results[0]

                # Determine final status
                final_status = "passed" if cell_result.status.value == "PASS" else "failed"

                # Extract screenshots
                screenshots = [
                    screenshot.storage_path for screenshot in cell_result.screenshots
                ]

                # Extract logs
                execution_logs = [
                    {
                        "step": step.step_number,
                        "action": step.action,
                        "passed": step.passed,
                        "error": step.error_message,
                    }
                    for step in cell_result.step_results
                ]

                # Update execution record
                crud.update_test_execution_status(
                    db,
                    execution_id,
                    status=final_status,
                    completed_at=datetime.utcnow(),
                    execution_logs=execution_logs,
                    screenshots=screenshots,
                    error_details=cell_result.failure_summary,
                )

                print(f"✅ Test completed: {final_status.upper()}")

                return {
                    "execution_id": execution_id,
                    "status": final_status,
                    "duration_ms": cell_result.duration_ms,
                    "screenshots": screenshots,
                }

            else:
                # No results - mark as error
                crud.update_test_execution_status(
                    db,
                    execution_id,
                    status="failed",
                    completed_at=datetime.utcnow(),
                    error_details="Test execution returned no results",
                )

                print(f"❌ Test failed: No results returned")

                return {
                    "execution_id": execution_id,
                    "status": "failed",
                    "error": "No results returned",
                }

        except Exception as e:
            # Update execution with error
            crud.update_test_execution_status(
                db,
                execution_id,
                status="failed",
                completed_at=datetime.utcnow(),
                error_details=str(e),
            )

            print(f"❌ Test execution error: {str(e)}")

            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
            }

        finally:
            db.close()

    def _get_viewport_profile(self, width: int, height: int):
        """Get viewport profile matching dimensions"""
        from models import ViewportProfile

        # Find matching viewport or create custom
        for viewport_name, viewport in VIEWPORTS.items():
            if viewport.width == width and viewport.height == height:
                return viewport

        # Create custom viewport
        return ViewportProfile(
            name="custom",
            width=width,
            height=height,
            device_class="Custom",
            description=f"Custom {width}x{height}",
            display_name=f"{width}x{height}",
        )

    def _get_browser_profile(self, browser: str):
        """Get browser profile"""
        from models import BrowserProfile

        browser_map = {
            "chrome": BROWSERS.get("chrome"),
            "firefox": BROWSERS.get("firefox"),
            "safari": BROWSERS.get("safari"),
            "edge": BROWSERS.get("chrome"),  # Use chrome engine for edge
        }

        return browser_map.get(browser.lower(), BROWSERS["chrome"])

    def _get_network_profile(self, network_mode: str):
        """Get network profile"""
        network_map = {
            "online": NETWORKS.get("normal"),
            "fast3g": NETWORKS.get("normal"),
            "slow3g": NETWORKS.get("slow3g"),
            "offline": NETWORKS.get("normal"),  # Would need special handling
        }

        return network_map.get(network_mode.lower(), NETWORKS["normal"])

    def _convert_test_steps(self, steps_data: List[Dict]) -> List[TestStep]:
        """Convert test steps data to TestStep objects"""
        test_steps = []

        for step_data in steps_data:
            try:
                step = TestStep(
                    step_number=step_data.get("step_number", 0),
                    action=ActionType(step_data.get("action", "navigate")),
                    target=step_data.get("target", ""),
                    expected_outcome=step_data.get("expected_outcome", ""),
                    timeout_seconds=step_data.get("timeout_seconds", 10),
                    value=step_data.get("value"),
                )
                test_steps.append(step)
            except Exception as e:
                print(f"⚠️  Warning: Could not convert step {step_data}: {e}")
                continue

        return test_steps


async def run_pending_executions():
    """
    Background worker that picks up pending executions and runs them.

    This can be run as a separate service or scheduled task.
    """
    db = SessionLocal()
    runner = TestRunnerService()

    try:
        # Get all pending executions
        pending = crud.get_test_executions(db, status="pending", limit=10)

        if not pending:
            print("No pending executions")
            return

        print(f"Found {len(pending)} pending executions")

        for execution in pending:
            print(f"\n🔄 Processing execution: {execution.id}")

            # Get test suite
            test_suite = crud.get_test_suite(db, execution.test_suite_id)
            if not test_suite:
                print(f"  ⚠️  Test suite not found: {execution.test_suite_id}")
                continue

            # Get config if specified
            config = None
            if execution.config_id:
                config = crud.get_config_template(db, execution.config_id)

            # Convert to dict
            test_suite_dict = {
                "id": test_suite.id,
                "name": test_suite.name,
                "prompt": test_suite.prompt,
                "target_url": test_suite.target_url,
                "test_steps": test_suite.test_steps,
            }

            config_dict = None
            if config:
                config_dict = {
                    "browsers": config.browsers,
                    "viewports": config.viewports,
                    "network_modes": config.network_modes,
                }

            # Execute
            await runner.execute_test_with_config(
                execution_id=execution.id,
                test_suite_dict=test_suite_dict,
                config_dict=config_dict,
                browser=execution.browser,
                viewport_width=execution.viewport_width,
                viewport_height=execution.viewport_height,
                network_mode=execution.network_mode,
            )

    finally:
        db.close()


if __name__ == "__main__":
    # Run pending executions
    asyncio.run(run_pending_executions())
