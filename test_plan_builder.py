"""
Test plan builder for TestGPT.

Builds complete test plans with matrix expansion from parsed requests.
Implements matrix expansion logic from specification TODO 5.
"""

import uuid
import re
from datetime import datetime
from typing import List
from models import (
    TestPlan, TestFlow, TestStep, MatrixCell, EnvironmentMatrix,
    ActionType, ParsedSlackRequest, ScenarioDefinition
)
from config import get_viewport, get_browser, get_network
from agent_instructions import get_pointblank_landing_flow, get_pointblank_pricing_flow, get_pointblank_signup_flow


class TestPlanBuilder:
    """
    Builds complete test plans with matrix expansion.

    Takes parsed Slack requests and generates:
    - Flow definitions with deterministic steps
    - Environment matrix
    - Expanded matrix cells (Flow × Viewport × Browser × Network)
    """

    def build_test_plan(
        self,
        parsed_request: ParsedSlackRequest,
        scenario_id: str,
        scenario_name: str,
        created_by: str
    ) -> TestPlan:
        """
        Build a complete test plan from a parsed request.

        Args:
            parsed_request: Parsed Slack request
            scenario_id: Stable scenario ID
            scenario_name: Human-readable scenario name
            created_by: User ID who created the request

        Returns:
            Complete TestPlan ready for execution
        """
        test_plan_id = f"plan-{uuid.uuid4().hex[:12]}"
        created_at = datetime.now()
        target_url = parsed_request.target_urls[0]

        # Build flows
        flows = self._build_flows(parsed_request)

        # Build environment matrix
        env_matrix = EnvironmentMatrix(
            viewports=parsed_request.required_viewports,
            browsers=parsed_request.required_browsers,
            networks=parsed_request.required_networks
        )

        # Expand matrix into cells
        matrix_cells = self._expand_matrix(flows, env_matrix, target_url)

        # Calculate estimates
        total_cells = len(matrix_cells)
        estimated_duration_minutes = self._estimate_duration(matrix_cells)

        return TestPlan(
            test_plan_id=test_plan_id,
            created_at=created_at,
            created_by=created_by,
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            target_url=target_url,
            flows=flows,
            environment_matrix=env_matrix,
            matrix_cells=matrix_cells,
            total_cells_to_execute=total_cells,
            estimated_duration_minutes=estimated_duration_minutes,
            tags=self._generate_tags(parsed_request)
        )

    def _build_flows(self, parsed_request: ParsedSlackRequest) -> List[TestFlow]:
        """
        Build test flows based on parsed request.

        Uses templates for known scenarios (pointblank.club)
        or generates flows based on user requirements.
        """
        flows = []
        target_url = parsed_request.target_urls[0]

        # Special handling for pointblank.club
        if "pointblank.club" in target_url:
            flows_to_include = []

            if "landing" in parsed_request.flows:
                landing_flow_dict = get_pointblank_landing_flow()
                flows_to_include.append(self._dict_to_flow(landing_flow_dict))

            if "pricing" in parsed_request.flows:
                pricing_flow_dict = get_pointblank_pricing_flow()
                flows_to_include.append(self._dict_to_flow(pricing_flow_dict))

            if "signup" in parsed_request.flows:
                signup_flow_dict = get_pointblank_signup_flow()
                flows_to_include.append(self._dict_to_flow(signup_flow_dict))

            # If no specific flows, include landing by default
            if not flows_to_include:
                landing_flow_dict = get_pointblank_landing_flow()
                flows_to_include.append(self._dict_to_flow(landing_flow_dict))

            return flows_to_include

        # Generic flow generation for other URLs
        for flow_name in parsed_request.flows:
            flow = self._generate_generic_flow(flow_name, target_url, parsed_request)
            flows.append(flow)

        # If no flows, create basic page load flow
        if not flows:
            flows.append(self._generate_basic_page_load_flow(target_url))

        return flows

    def _dict_to_flow(self, flow_dict: dict) -> TestFlow:
        """Convert flow dictionary to TestFlow object."""
        steps = []
        for step_dict in flow_dict["steps"]:
            step = TestStep(
                step_number=step_dict["step_number"],
                action=ActionType(step_dict["action"]),
                target=step_dict["target"],
                expected_outcome=step_dict["expected"],
                timeout_seconds=step_dict["timeout_seconds"]
            )
            steps.append(step)

        return TestFlow(
            flow_name=flow_dict["flow_name"],
            steps=steps
        )

    def _generate_generic_flow(
        self,
        flow_name: str,
        target_url: str,
        parsed_request: ParsedSlackRequest
    ) -> TestFlow:
        """Generate a generic test flow based on flow name."""
        steps = []
        step_num = 1

        # Always start with navigation
        steps.append(TestStep(
            step_number=step_num,
            action=ActionType.NAVIGATE,
            target=target_url,
            expected_outcome=f"Page loads with status 200 within 10 seconds",
            timeout_seconds=10
        ))
        step_num += 1

        # Wait for body
        steps.append(TestStep(
            step_number=step_num,
            action=ActionType.WAIT_FOR_SELECTOR,
            target="body",
            expected_outcome="Page body renders within 5 seconds",
            timeout_seconds=5
        ))
        step_num += 1

        # Add flow-specific steps
        if flow_name == "login":
            steps.append(TestStep(
                step_number=step_num,
                action=ActionType.ASSERT_VISIBLE,
                target="input[type='email'], input[name='username']",
                expected_outcome="Login form is visible",
                timeout_seconds=3
            ))
            step_num += 1

        elif flow_name == "checkout":
            steps.append(TestStep(
                step_number=step_num,
                action=ActionType.ASSERT_VISIBLE,
                target="button:has-text('Checkout'), button:has-text('Buy'), button:has-text('Purchase')",
                expected_outcome="Checkout button is visible",
                timeout_seconds=3
            ))
            step_num += 1

        elif flow_name == "search":
            steps.append(TestStep(
                step_number=step_num,
                action=ActionType.ASSERT_VISIBLE,
                target="input[type='search'], input[placeholder*='Search']",
                expected_outcome="Search input is visible",
                timeout_seconds=3
            ))
            step_num += 1

        else:
            # Generic: check for key interactive elements
            steps.append(TestStep(
                step_number=step_num,
                action=ActionType.ASSERT_VISIBLE,
                target="button, a.btn, a.button, [class*='cta']",
                expected_outcome="Primary interactive element is visible",
                timeout_seconds=3
            ))
            step_num += 1

        # Screenshot for evidence
        steps.append(TestStep(
            step_number=step_num,
            action=ActionType.SCREENSHOT,
            target=f"{flow_name}-completed",
            expected_outcome="Screenshot captured for evidence",
            timeout_seconds=2
        ))

        return TestFlow(
            flow_name=f"{flow_name.title()} Flow",
            steps=steps
        )

    def _generate_basic_page_load_flow(self, target_url: str) -> TestFlow:
        """Generate a basic page load test flow."""
        return TestFlow(
            flow_name="Basic Page Load",
            steps=[
                TestStep(
                    step_number=1,
                    action=ActionType.NAVIGATE,
                    target=target_url,
                    expected_outcome="Page loads with status 200",
                    timeout_seconds=10
                ),
                TestStep(
                    step_number=2,
                    action=ActionType.WAIT_FOR_SELECTOR,
                    target="body",
                    expected_outcome="Page body renders",
                    timeout_seconds=5
                ),
                TestStep(
                    step_number=3,
                    action=ActionType.SCREENSHOT,
                    target="page-loaded",
                    expected_outcome="Screenshot captured",
                    timeout_seconds=2
                )
            ]
        )

    def _expand_matrix(
        self,
        flows: List[TestFlow],
        env_matrix: EnvironmentMatrix,
        target_url: str
    ) -> List[MatrixCell]:
        """
        Expand test matrix into individual cells.

        Creates Cartesian product: Flows × Viewports × Browsers × Networks

        Each cell represents one test run in a specific environment.
        Cell ID format: {flow_slug}_{viewport}_{browser}_{network}_{timestamp}
        """
        matrix_cells = []
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        for flow in flows:
            flow_slug = flow.flow_name.lower().replace(" ", "-")[:20]

            for viewport_name in env_matrix.viewports:
                viewport = get_viewport(viewport_name)

                for browser_name in env_matrix.browsers:
                    browser = get_browser(browser_name)

                    for network_name in env_matrix.networks:
                        network = get_network(network_name)

                        cell_id = f"{flow_slug}_{viewport_name}_{browser_name}_{network_name}_{timestamp}"

                        cell = MatrixCell(
                            cell_id=cell_id,
                            viewport=viewport,
                            browser=browser,
                            network=network,
                            steps=flow.steps
                        )

                        matrix_cells.append(cell)

        return matrix_cells

    def _estimate_duration(self, matrix_cells: List[MatrixCell]) -> int:
        """
        Estimate total test duration in minutes.

        Assumes parallel execution with max 4 concurrent cells.
        """
        if not matrix_cells:
            return 1

        # Calculate total time for one cell (sum of all step timeouts + buffer)
        sample_cell = matrix_cells[0]
        total_step_timeout = sum(step.timeout_seconds for step in sample_cell.steps)
        per_cell_time_seconds = total_step_timeout + 10  # 10s buffer

        # Assume max 4 parallel executions
        max_parallel = 4
        total_cells = len(matrix_cells)

        # Calculate serial batches
        batches = (total_cells + max_parallel - 1) // max_parallel
        total_time_seconds = batches * per_cell_time_seconds

        # Convert to minutes, minimum 1
        total_time_minutes = max(1, total_time_seconds // 60)

        return total_time_minutes

    def _generate_tags(self, parsed_request: ParsedSlackRequest) -> List[str]:
        """Generate tags for categorizing the test plan."""
        tags = []

        # Add domain tag
        target_url = parsed_request.target_urls[0]
        domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]
        tags.append(domain)

        # Add flow tags
        tags.extend(parsed_request.flows)

        # Add environment tags
        if len(parsed_request.required_viewports) > 1:
            tags.append("responsive")
        if len(parsed_request.required_browsers) > 1:
            tags.append("cross-browser")
        if len(parsed_request.required_networks) > 1:
            tags.append("network-conditions")

        # Add special tags
        if "pointblank.club" in target_url:
            tags.append("pointblank")
            tags.append("demo")

        if any(b in parsed_request.required_browsers for b in ["webkit-ios", "webkit-desktop"]):
            tags.append("safari")

        return tags

    def build_scenario_definition(
        self,
        test_plan: TestPlan,
        created_by: str
    ) -> ScenarioDefinition:
        """
        Build a scenario definition from a test plan for persistence.

        This allows the scenario to be re-run later.
        """
        return ScenarioDefinition(
            scenario_id=test_plan.scenario_id,
            scenario_name=test_plan.scenario_name,
            target_url=test_plan.target_url,
            created_at=test_plan.created_at,
            created_by=created_by,
            last_run_at=None,
            flows=test_plan.flows,
            steps=[],  # Flows contain steps
            environment_matrix=test_plan.environment_matrix,
            tags=test_plan.tags,
            preconditions={}
        )
