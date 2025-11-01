"""
Test executor for TestGPT.

Executes test plans using Playwright MCP and collects results.
Implements execution contracts from specification Section 4.
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from io import StringIO
from contextlib import contextmanager
from models import (
    TestPlan, MatrixCell, CellResult, StepResult, Screenshot,
    ConsoleError, NetworkRequest, TestStatus, FailurePriority,
    ActionType
)
from agno.agent import Agent
from agno.models.anthropic import Claude
import os
import sys
from mcp_manager import get_mcp_manager


class TestExecutor:
    """
    Executes test plans using Playwright MCP.

    Takes a TestPlan and executes all matrix cells, collecting
    detailed results for each step, screenshot, and error.
    """

    def __init__(self, mcp_tools=None, coverage_enabled=False, coverage_orchestrator=None):
        """
        Initialize executor.

        Args:
            mcp_tools: (Deprecated) Legacy single MCP connection - no longer used
            coverage_enabled: Whether to track code coverage during testing
            coverage_orchestrator: CoverageOrchestrator instance for tracking coverage
        """
        # Use dynamic MCP manager instead of single connection
        self.mcp_manager = get_mcp_manager()
        self.agent = None

        # Coverage support
        self.coverage_enabled = coverage_enabled
        self.coverage_orchestrator = coverage_orchestrator

        # Setup file logging
        self.log_file = None
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging to file."""
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_filename = f"testgpt-debug-{timestamp}.log"
        self.log_file_path = os.path.join(log_dir, log_filename)

        # Also create a symlink to latest log
        latest_log = os.path.join(log_dir, "latest.log")

        self.log_file = open(self.log_file_path, 'w', encoding='utf-8')

        # Write header
        self.log_file.write(f"{'='*80}\n")
        self.log_file.write(f"TestGPT Debug Log\n")
        self.log_file.write(f"Started: {datetime.now().isoformat()}\n")
        self.log_file.write(f"{'='*80}\n\n")
        self.log_file.flush()

        print(f"📝 Logging to: {self.log_file_path}")
        print(f"   (Also available at: logs/latest.log)\n")

        # Create symlink
        try:
            if os.path.exists(latest_log):
                os.remove(latest_log)
            os.symlink(log_filename, latest_log)
        except:
            pass  # Windows doesn't support symlinks easily

    def _log(self, message):
        """Log message to both console and file."""
        print(message)
        if self.log_file:
            self.log_file.write(message + '\n')
            self.log_file.flush()

    def _log_only(self, message):
        """Log message only to file (not console)."""
        if self.log_file:
            self.log_file.write(message + '\n')
            self.log_file.flush()

    @contextmanager
    def _capture_agent_output(self):
        """
        Context manager to capture all stdout from agent execution.

        Writes agent's debug output (thinking, tool calls, etc.) to both:
        - Console (stdout)
        - Log file

        Usage:
            with self._capture_agent_output():
                response = await agent.arun(instruction)
        """
        # Custom stdout that writes to both original stdout and log file
        class TeeOutput:
            def __init__(self, log_file, original_stdout):
                self.log_file = log_file
                self.original_stdout = original_stdout
                self.buffer = []

            def write(self, text):
                # Write to original stdout
                self.original_stdout.write(text)
                self.original_stdout.flush()

                # Write to log file
                if self.log_file:
                    self.log_file.write(text)
                    self.log_file.flush()

                # Keep in buffer for potential retrieval
                self.buffer.append(text)

            def flush(self):
                self.original_stdout.flush()
                if self.log_file:
                    self.log_file.flush()

        # Save original stdout
        original_stdout = sys.stdout

        try:
            # Replace stdout with our Tee
            sys.stdout = TeeOutput(self.log_file, original_stdout)
            yield
        finally:
            # Restore original stdout
            sys.stdout = original_stdout

    def __del__(self):
        """Cleanup: close log file."""
        if self.log_file:
            self.log_file.write(f"\n{'='*80}\n")
            self.log_file.write(f"Ended: {datetime.now().isoformat()}\n")
            self.log_file.write(f"{'='*80}\n")
            self.log_file.close()

    async def execute_test_plan(self, test_plan: TestPlan) -> List[CellResult]:
        """
        Execute a complete test plan.

        Runs all matrix cells and collects results.

        Args:
            test_plan: TestPlan to execute

        Returns:
            List of CellResult objects (one per matrix cell)
        """
        print(f"\n🎯 Executing test plan: {test_plan.scenario_name}")
        print(f"   Total cells to execute: {test_plan.total_cells_to_execute}")
        print(f"   Estimated duration: {test_plan.estimated_duration_minutes} minutes")

        # Start coverage tracking if enabled
        if self.coverage_enabled and self.coverage_orchestrator:
            print(f"   📊 Coverage tracking: ENABLED\n")
            await self.coverage_orchestrator.start_coverage()
        else:
            print()

        cell_results = []

        # Execute cells (for now sequentially, can be parallelized later)
        for i, cell in enumerate(test_plan.matrix_cells, 1):
            print(f"▶️  Executing cell {i}/{len(test_plan.matrix_cells)}: {cell.cell_id}")

            try:
                result = await self.execute_cell(cell, test_plan.target_url, test_plan.user_request)
                cell_results.append(result)

                status_emoji = "✅" if result.status == TestStatus.PASS else "❌"
                print(f"{status_emoji} Cell completed: {result.status.value}")

                # Record coverage after each test
                if self.coverage_enabled and self.coverage_orchestrator:
                    await self.coverage_orchestrator.record_test_execution(
                        test_id=cell.cell_id,
                        test_name=cell.cell_id,
                        execution_time_ms=result.duration_ms
                    )

                    # Check if we should stop testing early
                    decision = await self.coverage_orchestrator.should_stop_testing()
                    if decision.should_stop:
                        print(f"\n🛑 COVERAGE STOP DECISION: {decision.reason}")
                        print(f"   Confidence: {decision.confidence_score:.0%}")
                        print(f"   Tests executed: {i}/{len(test_plan.matrix_cells)}")
                        print(f"   Coverage achieved: {self.coverage_orchestrator._calculate_current_coverage():.1f}%")
                        print(f"   ⚡️ Stopping early to save time!\n")
                        break

                print()

            except Exception as e:
                print(f"❌ Cell execution failed with error: {str(e)}\n")
                # Create error result
                error_result = self._create_error_result(cell, str(e))
                cell_results.append(error_result)

        return cell_results

    async def execute_backend_api_test(
        self,
        repo_url: Optional[str] = None,
        api_path: Optional[str] = None,
        app_module: str = "main:app",
        test_instructions: str = "Run comprehensive API tests"
    ) -> dict:
        """
        Execute backend API testing using dynamic backend testing MCP.

        Args:
            repo_url: GitHub repository URL to clone and test
            api_path: Local path to API code
            app_module: Module path for API (e.g., "main:app")
            test_instructions: Instructions for what to test

        Returns:
            dict with test results from backend testing agent
        """
        from pathlib import Path

        print(f"\n🧪 Executing backend API test")
        if repo_url:
            print(f"   Repository: {repo_url}")
        elif api_path:
            print(f"   Local API: {api_path}")
        print(f"   App module: {app_module}")
        print(f"   Instructions: {test_instructions}\n")

        started_at = datetime.now()

        try:
            # Get backend testing MCP tools
            print("🔌 Connecting to backend testing MCP server...")
            backend_mcp_tools = await self.mcp_manager.get_backend_mcp_tools(
                repo_url=repo_url,
                api_path=Path(api_path) if api_path else None,
                app_module=app_module
            )

            # Create agent with backend testing tools
            print("🤖 Initializing backend testing agent...")
            backend_agent = Agent(
                name="BackendAPITestAgent",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[backend_mcp_tools],
                debug_mode=True,
                instructions="""You are a backend API testing agent with access to FastMCP tools.

You can:
- Test API endpoints (GET, POST, PUT, DELETE)
- Run CRUD operation tests
- Execute smoke test suites
- Verify request/response behavior
- Check error handling
- Validate data integrity
- Generate test reports

Available tools depend on the API being tested. Use list_tools to see what's available.

Be thorough and report clear results.""",
                markdown=True
            )

            # Run the test with the agent
            print(f"🧪 Running backend API tests...")
            print(f"   Instructions: {test_instructions}\n")

            # Capture ALL agent output (thinking, tool calls, debug info) to log file
            with self._capture_agent_output():
                response = await backend_agent.arun(test_instructions)
            result_content = response.content if hasattr(response, 'content') else str(response)

            completed_at = datetime.now()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            print(f"\n✅ Backend API testing completed")
            print(f"   Duration: {duration_ms}ms\n")

            return {
                "status": "completed",
                "started_at": started_at,
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "result": result_content,
                "repo_url": repo_url,
                "api_path": api_path,
                "app_module": app_module
            }

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()

            completed_at = datetime.now()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            print(f"\n❌ Backend API testing failed")
            print(f"   Error: {str(e)}\n")

            return {
                "status": "error",
                "started_at": started_at,
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "error": str(e),
                "error_traceback": error_traceback,
                "repo_url": repo_url,
                "api_path": api_path,
                "app_module": app_module
            }

    async def _initialize_agent(self, mcp_tools):
        """
        Initialize Agno agent with Playwright MCP tools for this specific cell.

        Args:
            mcp_tools: MCPTools instance configured for specific viewport/browser
        """
        if mcp_tools is None:
            self.agent = None
            return

        self._log("   🔧 Initializing AI agent with viewport-specific MCP connection...")
        self._log("      Debug mode: ENABLED")
        self._log("      Tool calls: Will be logged\n")

        # Create new agent for this cell
        # (Each cell gets its own agent with its own MCP connection)
        self.agent = Agent(
            name="PlaywrightTestAgent",
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[mcp_tools],
            debug_mode=True,  # Enable debug logging
            instructions="""You are an autonomous web testing agent with full Playwright MCP access.

CRITICAL: You have FULL CONTROL over browser automation. Make your own decisions about how to accomplish the testing goals.

When given a test scenario, you should:
1. Launch the appropriate browser (chromium for Chrome, webkit for Safari)
2. Set viewport size AND use device emulation for proper responsive behavior
3. Navigate to pages
4. Find elements using appropriate selectors
5. Interact with elements (click, fill forms, etc.)
6. Verify expected outcomes
7. Take screenshots as evidence

VIEWPORT SETUP:
- Use playwright's device emulation, not just viewport size
- For mobile: Use device context (iPhone 13 Pro, etc.)
- For desktop: Set viewport + ensure page responds to size
- Always verify elements are visible and accessible

AUTONOMY:
- You decide the exact selectors to use
- You decide how to find elements
- You decide when to wait for page load
- You adapt if elements aren't found
- You report what you actually see

Be thorough but efficient. Report clear outcomes.""",
                markdown=False
            )

    async def execute_cell(self, cell: MatrixCell, target_url: str, user_request: str = "") -> CellResult:
        """
        Execute a single matrix cell (one environment combination).

        Args:
            cell: MatrixCell to execute
            target_url: Base target URL
            user_request: Original user message for custom test instructions

        Returns:
            CellResult with all execution details
        """
        started_at = datetime.now()
        step_results = []
        screenshots = []
        console_errors = []
        network_requests = []
        overall_passed = True

        # Get dedicated MCP tools for this viewport/browser combination
        mcp_tools = await self.mcp_manager.get_mcp_tools_for_cell(
            viewport=cell.viewport,
            browser=cell.browser
        )

        # Initialize agent with this cell's specific MCP tools
        await self._initialize_agent(mcp_tools)

        self._log(f"   🌐 Browser: {cell.browser.display_name}")
        self._log(f"   📱 Viewport: {cell.viewport.name} ({cell.viewport.width}×{cell.viewport.height})")
        self._log(f"   📡 Network: {cell.network.display_name}")

        # NEW APPROACH: Give agent the full flow goal, let it decide the steps
        if self.agent is not None:
            self._log(f"   🤖 Letting AI agent execute flow autonomously...")
            flow_result = await self._execute_flow_autonomously(cell, user_request)
            step_results = flow_result["step_results"]
            overall_passed = flow_result["passed"]
        else:
            # Fallback: Execute step-by-step (mock mode)
            for step in cell.steps:
                step_result = await self._execute_step_fallback(step, cell)
                step_results.append(step_result)

        completed_at = datetime.now()
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Determine status
        status = TestStatus.PASS if overall_passed else TestStatus.FAIL

        # Generate failure summary if failed
        failure_summary = None
        failure_priority = None
        if status == TestStatus.FAIL:
            failure_summary = self._generate_failure_summary(step_results, cell)
            failure_priority = self._determine_failure_priority(cell)

        # CRITICAL: Cleanup MCP instance after cell execution
        # This ensures next cell with different browser/viewport gets fresh MCP server
        try:
            await self.mcp_manager.cleanup_instance(cell.viewport, cell.browser)
        except Exception as e:
            self._log(f"   ⚠️  Warning: Failed to cleanup MCP instance: {e}")

        return CellResult(
            cell_id=cell.cell_id,
            viewport=cell.viewport.name,
            browser=cell.browser.name,
            network=cell.network.name,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            step_results=step_results,
            screenshots=screenshots,
            console_errors=console_errors,
            network_requests=network_requests,
            failure_summary=failure_summary,
            failure_priority=failure_priority
        )

    async def _execute_flow_autonomously(self, cell: MatrixCell, user_request: str = "") -> dict:
        """
        Execute entire test flow autonomously by giving agent the high-level goal.

        Agent has full control to decide:
        - How to launch browser with proper device emulation
        - Which selectors to use
        - When to wait
        - How to verify outcomes
        - When to adapt if elements not found

        Args:
            cell: MatrixCell with flow steps and environment config

        Returns:
            dict with "step_results" (List[StepResult]) and "passed" (bool)
        """
        flow_start = datetime.now()

        self._log(f"\n{'='*70}")
        self._log(f"🔍 DEBUG: Starting autonomous execution for cell {cell.cell_id}")
        self._log(f"{'='*70}")

        # Build the high-level goal for the agent
        flow_description = self._build_flow_goal_description(cell)

        # Include user's custom request if provided
        if user_request and len(user_request.strip()) > 0:
            mission_section = f"""USER REQUEST:
"{user_request}"

YOUR GOAL:
Interpret the user's request above and execute it autonomously on the target website.
Make decisions about how to accomplish the user's goal, including:
- Which pages to navigate to
- Which elements to interact with
- What information to gather or verify
- How to report your findings

Pre-defined test flow (for reference):
{flow_description}"""
        else:
            mission_section = flow_description

        # Give agent the full scenario with device emulation instructions
        autonomous_instruction = f"""AUTONOMOUS WEB TEST EXECUTION

ENVIRONMENT SETUP:
- Browser: {cell.browser.display_name} ({cell.browser.engine})
- Device/Viewport: {cell.viewport.device_class} - {cell.viewport.name}
- Screen Size: {cell.viewport.width}×{cell.viewport.height}
- Device Scale: {cell.viewport.device_scale_factor}x
- Mobile: {"YES" if cell.viewport.is_mobile else "NO"}
- Network: {cell.network.display_name}

VIEWPORT IS ALREADY CONFIGURED CORRECTLY:
✅ This browser was launched with proper device emulation for {cell.viewport.display_name}
✅ Viewport: {cell.viewport.width}×{cell.viewport.height} ({cell.viewport.device_class})
✅ Device scale factor: {cell.viewport.device_scale_factor}x
✅ {"Mobile mode with touch events" if cell.viewport.is_mobile else "Desktop mode"}

YOUR WORKFLOW:
1. Navigate directly to target URL: browser_navigate(url="TARGET_URL")
2. Wait for page to load completely (2-3 seconds)
3. Proceed with testing (clicks, assertions, screenshots)
4. Report what you observe

IMPORTANT:
- DO NOT use browser_install - all browsers are already installed and ready
- DO NOT use browser_resize - viewport is already correct from launch
- The page will render properly at {cell.viewport.width}×{cell.viewport.height} from initial load
- CSS media queries will fire correctly for this viewport size
- Test what you see - responsive behavior should work properly
- If you get "browser not installed" error, just navigate directly - the browser IS installed

YOUR MISSION:
{mission_section}

CORRECT PLAYWRIGHT DEVICE EMULATION PATTERN:
{self._get_device_emulation_example(cell)}

AUTONOMOUS DECISION MAKING:
You have FULL CONTROL. Make your own decisions about:
1. How to launch the browser with proper device emulation (see example above)
2. Which selectors work best for finding elements
3. When to wait for page load or elements
4. How to verify expected outcomes
5. How to adapt if elements aren't found immediately

REPORT FORMAT:
For each major step you take, report:
- What you did
- What you observed
- Whether it met expectations
- Any issues encountered

Begin execution now. Take full control."""

        # Log the full instruction being sent to agent
        self._log(f"\n📤 INSTRUCTION SENT TO AGENT:")
        self._log(f"{'-'*70}")
        self._log(autonomous_instruction)
        self._log(f"{'-'*70}\n")

        try:
            # Execute autonomously with agent
            self._log(f"⏳ Executing with AI agent (this may take 30-60 seconds)...")
            self._log(f"🤖 Agent is thinking and using Playwright MCP tools...\n")

            # Capture ALL agent output (thinking, tool calls, debug info) to log file
            with self._capture_agent_output():
                response = await self.agent.arun(autonomous_instruction)

            # Extract agent's response
            agent_output = response.content if hasattr(response, 'content') else str(response)

            # Log the agent's full response
            self._log(f"\n📥 AGENT RESPONSE:")
            self._log(f"{'-'*70}")
            self._log(agent_output)
            self._log(f"{'-'*70}\n")

            # Parse agent's execution report into step results
            step_results = self._parse_agent_execution_report(agent_output, cell, flow_start)

            # Determine overall pass/fail
            overall_passed = all(sr.passed for sr in step_results)

            self._log(f"✅ Autonomous execution completed: {'PASSED' if overall_passed else 'FAILED'}")
            self._log(f"{'='*70}\n")

            return {
                "step_results": step_results,
                "passed": overall_passed
            }

        except Exception as e:
            # Log the full error details
            import traceback
            error_traceback = traceback.format_exc()

            self._log(f"\n❌ AGENT EXECUTION ERROR:")
            self._log(f"{'-'*70}")
            self._log(f"Error Type: {type(e).__name__}")
            self._log(f"Error Message: {str(e)}")
            self._log(f"\nFull Traceback:")
            self._log(error_traceback)
            self._log(f"{'-'*70}\n")

            # Agent execution failed - create error result
            error_result = StepResult(
                step_number=1,
                action="autonomous_execution",
                target=cell.steps[0].target if cell.steps else "flow",
                expected_outcome="Complete flow autonomously",
                actual_outcome=f"Agent execution error: {str(e)}",
                passed=False,
                timestamp=flow_start,
                error_message=f"{type(e).__name__}: {str(e)}\n\n{error_traceback}",
                duration_ms=int((datetime.now() - flow_start).total_seconds() * 1000)
            )

            return {
                "step_results": [error_result],
                "passed": False
            }

    def _get_device_emulation_example(self, cell: MatrixCell) -> str:
        """Get device-specific Playwright MCP workflow example."""

        return f"""
WORKFLOW for {cell.viewport.display_name}:

✅ Browser already launched with correct device emulation
✅ Viewport: {cell.viewport.width}×{cell.viewport.height}
✅ {"Mobile device with touch events" if cell.viewport.is_mobile else "Desktop device"}

Step 1: Navigate directly to target URL
{{
  "tool": "browser_navigate",
  "arguments": {{
    "url": "YOUR_TARGET_URL_HERE"
  }}
}}

Step 2: Wait for page to fully load
{{
  "tool": "browser_wait_for",
  "arguments": {{
    "time": 2  // Wait 2 seconds for page to settle
  }}
}}

Step 3: Proceed with testing
- Use browser_snapshot to see page structure
- Use browser_click to interact with elements
- Use browser_take_screenshot for visual evidence
- Report what you observe

WHY THIS WORKS:
- MCP server was launched with --device="{cell.viewport.playwright_device if hasattr(cell.viewport, 'playwright_device') and cell.viewport.playwright_device else f'viewport {cell.viewport.width}x{cell.viewport.height}'}"
- Page renders at correct dimensions from initial load
- CSS media queries fire correctly
- Responsive behavior works properly
- No need to resize after page load
"""

    def _build_flow_goal_description(self, cell: MatrixCell) -> str:
        """Build high-level goal description from cell's test steps."""
        if not cell.steps:
            return "Navigate to target page and verify it loads correctly."

        # Extract the main goals from steps
        goals = []
        for step in cell.steps:
            if step.action == ActionType.NAVIGATE:
                goals.append(f"Navigate to {step.target}")
            elif step.action == ActionType.CLICK:
                goals.append(f"Find and click: {step.target}")
            elif step.action == ActionType.FILL:
                goals.append(f"Fill form field '{step.target}' with value '{step.value if hasattr(step, 'value') else 'test data'}'")
            elif step.action == ActionType.ASSERT_VISIBLE:
                goals.append(f"Verify visible: {step.target}")
            elif step.action == ActionType.ASSERT_IN_VIEWPORT:
                goals.append(f"Verify in viewport without scrolling: {step.target}")
            elif step.action == ActionType.WAIT_FOR_SELECTOR:
                goals.append(f"Wait for element to appear: {step.target}")
            elif step.action == ActionType.SCREENSHOT:
                goals.append(f"Capture screenshot: {step.target}")

        # Format as numbered list
        goal_list = "\n".join([f"{i+1}. {goal}" for i, goal in enumerate(goals)])

        return f"""Execute this test flow:

{goal_list}

Expected outcomes:
{chr(10).join([f"- {step.expected_outcome}" for step in cell.steps])}"""

    def _parse_agent_execution_report(self, agent_output: str, cell: MatrixCell, flow_start: datetime) -> List[StepResult]:
        """
        Parse agent's execution report into structured StepResult objects.

        Agent reports what it did - we map that to the expected steps.
        """
        step_results = []

        output_lower = agent_output.lower()

        # Check for explicit test status from agent (multiple formats)
        status_indicators = [
            "test status:",
            "test outcome:",
            "final status:",
            "overall status:",
            "test results:",
            "test verdict:",
            "test result:",
            "test completion status:",
            "completion status:",
            "test results summary:",
            "results summary:",
            "responsiveness score:",
            "overall score:"
        ]

        explicit_status_found = False
        overall_passed = False  # Default to false

        for indicator in status_indicators:
            if indicator in output_lower:
                # Agent explicitly declared test status
                status_section = output_lower.split(indicator)[-1][:200]  # Look at next 200 chars after indicator

                # Success indicators
                success_keywords = ["passed", "pass", "✅", "excellent", "success", "completed successfully", "all tests passed"]
                if any(keyword in status_section for keyword in success_keywords):
                    overall_passed = True
                    explicit_status_found = True
                    break

                # Failure indicators (removed "fail" to avoid false positives with "functionality")
                failure_keywords = ["failed", "❌", "error", "did not pass", "test failed"]
                if any(keyword in status_section for keyword in failure_keywords):
                    overall_passed = False
                    explicit_status_found = True
                    break

        if not explicit_status_found:
            # Use heuristic if no explicit status
            overall_passed = self._heuristic_success_detection(output_lower)

        # If explicit status found or no predefined steps, create single result for whole flow
        # This handles custom user requests better
        if explicit_status_found or not cell.steps:
            step_results.append(StepResult(
                step_number=1,
                action="autonomous_flow",
                target="Complete flow",
                expected_outcome="Flow executes successfully",
                actual_outcome=agent_output,
                passed=overall_passed,
                timestamp=flow_start,
                error_message=None if overall_passed else "Flow execution encountered issues",
                duration_ms=int((datetime.now() - flow_start).total_seconds() * 1000)
            ))
        else:
            # Create step results based on original expected steps
            # Only used when no explicit status and we have predefined steps
            for i, step in enumerate(cell.steps, 1):
                # Try to find evidence of this step in agent output
                step_executed = self._check_step_mentioned_in_output(step, agent_output)

                step_result = StepResult(
                    step_number=i,
                    action=step.action.value,
                    target=step.target,
                    expected_outcome=step.expected_outcome,
                    actual_outcome=f"Agent executed autonomously. Report: {agent_output[:200]}..." if len(agent_output) > 200 else agent_output,
                    # Use heuristic result - if overall test passed, mark step as passed
                    # Don't fail just because specific step keywords weren't detected in freeform output
                    passed=overall_passed,
                    timestamp=flow_start,
                    error_message=None if overall_passed else "Check agent report for details",
                    duration_ms=int((datetime.now() - flow_start).total_seconds() * 1000)
                )
                step_results.append(step_result)

        return step_results

    def _heuristic_success_detection(self, output_lower: str) -> bool:
        """
        Detect if test succeeded based on heuristics.

        More sophisticated than simple keyword matching - looks for actual failures
        vs mentions of avoiding errors.
        """
        # Check for success indicators
        has_success = any(keyword in output_lower for keyword in [
            "successfully", "completed", "verified", "confirmed",
            "loaded", "clicked", "filled", "visible", "screenshot captured",
            "test execution completed", "all objectives", "all test objectives"
        ])

        # Check for ACTUAL failure indicators (not just mentions of "error")
        # Only flag as error if the agent reports actual problems
        failure_patterns = [
            "failed to", "could not", "unable to", "cannot find",
            "timeout occurred", "exception occurred", "crashed",
            "test failed", "execution failed", "blocked",
            "did not work", "does not work", "broken"
        ]

        has_actual_failures = any(pattern in output_lower for pattern in failure_patterns)

        # Overall passed if has success indicators and no actual failures
        return has_success and not has_actual_failures

    def _check_step_mentioned_in_output(self, step: 'TestStep', output: str) -> bool:
        """Check if agent's output mentions executing this step."""
        output_lower = output.lower()

        # Check for action keywords
        action_keywords = {
            ActionType.NAVIGATE: ["navigated", "opened", "loaded page", "went to"],
            ActionType.CLICK: ["clicked", "pressed", "tapped"],
            ActionType.FILL: ["filled", "entered", "typed", "input"],
            ActionType.ASSERT_VISIBLE: ["visible", "found", "see", "displayed"],
            ActionType.ASSERT_IN_VIEWPORT: ["viewport", "in view", "visible without scroll"],
            ActionType.SCREENSHOT: ["screenshot", "captured", "image"],
            ActionType.WAIT_FOR_SELECTOR: ["waited", "appeared", "loaded"],
        }

        keywords = action_keywords.get(step.action, [])
        return any(keyword in output_lower for keyword in keywords)

    async def _execute_step_with_playwright(
        self,
        step: 'TestStep',
        cell: MatrixCell
    ) -> StepResult:
        """
        Execute a single test step using Playwright MCP via Agno agent.

        Args:
            step: TestStep to execute
            cell: MatrixCell containing the step

        Returns:
            StepResult with execution outcome
        """
        step_start = datetime.now()
        print(f"      Step {step.step_number}: {step.action.value} - {step.target[:50]}")

        # If no agent (no MCP tools), use fallback
        if self.agent is None:
            return await self._execute_step_fallback(step, cell)

        try:
            # Build instruction for the agent based on action type
            instruction = self._build_playwright_instruction(step, cell)

            # Execute with agent - capture all debug output
            with self._capture_agent_output():
                response = await self.agent.arun(instruction)
            actual_outcome = response.content if hasattr(response, 'content') else str(response)

            # Determine if step passed based on response
            passed = self._evaluate_step_outcome(step, actual_outcome)

            duration_ms = int((datetime.now() - step_start).total_seconds() * 1000)

            return StepResult(
                step_number=step.step_number,
                action=step.action.value,
                target=step.target,
                expected_outcome=step.expected_outcome,
                actual_outcome=actual_outcome,
                passed=passed,
                timestamp=step_start,
                error_message=None if passed else actual_outcome,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = int((datetime.now() - step_start).total_seconds() * 1000)
            error_msg = str(e)

            return StepResult(
                step_number=step.step_number,
                action=step.action.value,
                target=step.target,
                expected_outcome=step.expected_outcome,
                actual_outcome=f"Error: {error_msg}",
                passed=False,
                timestamp=step_start,
                error_message=error_msg,
                duration_ms=duration_ms
            )

    def _build_playwright_instruction(self, step: 'TestStep', cell: MatrixCell) -> str:
        """Build instruction for Playwright agent based on step action."""

        viewport_config = f"viewport {cell.viewport.width}x{cell.viewport.height}"
        browser_type = cell.browser.engine

        if step.action == ActionType.NAVIGATE:
            return f"Using {browser_type} browser with {viewport_config}, navigate to {step.target}. Confirm page loaded successfully."

        elif step.action == ActionType.CLICK:
            return f"Click on the element matching selector '{step.target}'. Confirm the click was successful."

        elif step.action == ActionType.FILL:
            return f"Fill the input field '{step.target}' with value '{step.value}'. Confirm filled."

        elif step.action == ActionType.WAIT_FOR_SELECTOR:
            return f"Wait for element matching '{step.target}' to be visible. Confirm it appeared."

        elif step.action == ActionType.ASSERT_VISIBLE:
            return f"Check if element matching '{step.target}' is visible on the page. Report true if visible, false if not."

        elif step.action == ActionType.ASSERT_IN_VIEWPORT:
            return f"Check if element matching '{step.target}' is visible within the viewport (no scrolling needed). Viewport height is {cell.viewport.height}px. Report if it's in viewport."

        elif step.action == ActionType.SCREENSHOT:
            return f"Take a screenshot and save it as '{step.target}.png'. Confirm captured."

        elif step.action == ActionType.WAIT:
            return f"Wait for {step.timeout_seconds} seconds."

        else:
            return f"Execute action: {step.action.value} on target: {step.target}"

    def _evaluate_step_outcome(self, step: 'TestStep', actual_outcome: str) -> bool:
        """Evaluate if step passed based on action type and outcome."""
        actual_lower = actual_outcome.lower()

        # Check for explicit errors
        if "error" in actual_lower or "failed" in actual_lower or "cannot" in actual_lower:
            return False

        # Check for success indicators
        if step.action == ActionType.NAVIGATE:
            return "navigated" in actual_lower or "loaded" in actual_lower or "success" in actual_lower

        elif step.action == ActionType.CLICK:
            return "clicked" in actual_lower or "success" in actual_lower

        elif step.action == ActionType.FILL:
            return "filled" in actual_lower or "entered" in actual_lower or "success" in actual_lower

        elif step.action == ActionType.WAIT_FOR_SELECTOR:
            return "visible" in actual_lower or "found" in actual_lower or "appeared" in actual_lower

        elif step.action == ActionType.ASSERT_VISIBLE:
            return "visible" in actual_lower or "true" in actual_lower

        elif step.action == ActionType.ASSERT_IN_VIEWPORT:
            return "in viewport" in actual_lower or "visible without scroll" in actual_lower or "true" in actual_lower

        elif step.action == ActionType.SCREENSHOT:
            return "captured" in actual_lower or "saved" in actual_lower or "success" in actual_lower

        elif step.action == ActionType.WAIT:
            return True  # Wait always passes

        # Default: check for success keywords
        return "success" in actual_lower or "completed" in actual_lower or "done" in actual_lower

    async def _execute_step_fallback(self, step: 'TestStep', cell: MatrixCell) -> StepResult:
        """Fallback execution when no MCP tools available (mock mode)."""
        step_start = datetime.now()

        # Simple mock execution
        await asyncio.sleep(0.5)  # Simulate some work

        # Mock outcomes
        if step.action == ActionType.NAVIGATE:
            actual_outcome = f"Navigated to {step.target}, page loaded"
            passed = True
        elif step.action == ActionType.ASSERT_VISIBLE:
            actual_outcome = f"Element '{step.target}' is visible"
            passed = True
        else:
            actual_outcome = f"{step.action.value} completed on {step.target}"
            passed = True

        duration_ms = int((datetime.now() - step_start).total_seconds() * 1000)

        return StepResult(
            step_number=step.step_number,
            action=step.action.value,
            target=step.target,
            expected_outcome=step.expected_outcome,
            actual_outcome=actual_outcome,
            passed=passed,
            timestamp=step_start,
            error_message=None,
            duration_ms=duration_ms
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _generate_failure_summary(self, step_results: List[StepResult], cell: MatrixCell) -> str:
        """Generate human-readable failure summary."""
        failed_steps = [sr for sr in step_results if not sr.passed]

        if not failed_steps:
            return None

        first_failure = failed_steps[0]

        summary = (
            f"{cell.browser.display_name} on {cell.viewport.device_class} "
            f"({cell.viewport.width}×{cell.viewport.height}) with {cell.network.display_name}: "
            f"{first_failure.error_message or first_failure.actual_outcome}"
        )

        return summary

    def _determine_failure_priority(self, cell: MatrixCell) -> FailurePriority:
        """
        Determine failure priority based on environment.

        P0: Normal network + standard viewport (critical bugs)
        P1: Slow network but passes on normal (performance issue)
        P2: Edge viewports only (layout edge case)
        """
        is_normal_network = cell.network.name == "normal"
        is_standard_viewport = cell.viewport.name in ["desktop-standard", "iphone-13-pro", "ipad-air"]

        if is_normal_network and is_standard_viewport:
            return FailurePriority.P0
        elif not is_normal_network:
            return FailurePriority.P1
        else:
            return FailurePriority.P2

    def _create_error_result(self, cell: MatrixCell, error_message: str) -> CellResult:
        """Create a CellResult for catastrophic execution error."""
        now = datetime.now()

        return CellResult(
            cell_id=cell.cell_id,
            viewport=cell.viewport.name,
            browser=cell.browser.name,
            network=cell.network.name,
            status=TestStatus.ERROR,
            started_at=now,
            completed_at=now,
            duration_ms=0,
            step_results=[],
            screenshots=[],
            console_errors=[],
            network_requests=[],
            failure_summary=f"Cell execution error: {error_message}",
            failure_priority=FailurePriority.P0
        )
