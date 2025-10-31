"""
Data models for TestGPT multi-environment QA testing system.

Defines all data structures for scenarios, test plans, run artifacts,
and environment profiles according to the TestGPT specification.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS AND TYPE DEFINITIONS
# ============================================================================

class TestStatus(str, Enum):
    """Test execution status."""
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class FailurePriority(str, Enum):
    """Failure priority levels."""
    P0 = "P0"  # Critical: fails on normal network + standard viewport
    P1 = "P1"  # Performance: fails on slow network but passes on normal
    P2 = "P2"  # Edge case: fails on edge viewports only


class ActionType(str, Enum):
    """Test step action types."""
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    WAIT_FOR_URL = "wait_for_url"
    ASSERT_VISIBLE = "assert_visible"
    ASSERT_IN_VIEWPORT = "assert_in_viewport"
    SCREENSHOT = "screenshot"
    WAIT = "wait"


# ============================================================================
# ENVIRONMENT PROFILES
# ============================================================================

@dataclass
class ViewportProfile:
    """Viewport/screen size configuration."""
    name: str
    width: int
    height: int
    device_class: str
    description: str
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    display_name: str = ""  # Human-readable display name (e.g., "iPhone 13 Pro")
    playwright_device: Optional[str] = None  # Playwright device descriptor (e.g., "iPhone 13 Pro")


@dataclass
class BrowserProfile:
    """Browser engine configuration."""
    name: str
    engine: Literal["chromium", "webkit", "firefox"]
    display_name: str
    platform: str
    user_agent_type: Optional[str] = None


@dataclass
class NetworkProfile:
    """Network condition configuration."""
    name: str
    display_name: str
    latency_ms: int
    download_kbps: int
    upload_kbps: int
    packet_loss_percent: float
    description: str


# ============================================================================
# TEST DEFINITION STRUCTURES
# ============================================================================

@dataclass
class TestStep:
    """Individual test step definition."""
    step_number: int
    action: ActionType
    target: str
    expected_outcome: str
    timeout_seconds: int = 10
    value: Optional[str] = None  # For fill actions


@dataclass
class TestFlow:
    """A logical flow/journey to test."""
    flow_name: str
    steps: List[TestStep]


@dataclass
class TestCheckpoint:
    """A verification checkpoint within a test."""
    step_number: int
    description: str
    expected: str
    timeout_seconds: int = 5


@dataclass
class EnvironmentMatrix:
    """Matrix of environments to test."""
    viewports: List[str]  # Viewport profile names
    browsers: List[str]   # Browser profile names
    networks: List[str]   # Network profile names


# ============================================================================
# SCENARIO DEFINITION (REUSABLE TEST)
# ============================================================================

@dataclass
class ScenarioDefinition:
    """
    A saved, reusable test scenario definition.
    This is what gets persisted and can be re-run later.
    """
    scenario_id: str
    scenario_name: str
    target_url: str
    created_at: datetime
    created_by: str
    last_run_at: Optional[datetime] = None
    flows: List[TestFlow] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    environment_matrix: Optional[EnvironmentMatrix] = None
    tags: List[str] = field(default_factory=list)
    preconditions: Dict[str, str] = field(default_factory=dict)


# ============================================================================
# TEST PLAN (PRE-EXECUTION)
# ============================================================================

@dataclass
class MatrixCell:
    """A single cell in the test matrix (one environment combination)."""
    cell_id: str
    viewport: ViewportProfile
    browser: BrowserProfile
    network: NetworkProfile
    steps: List[TestStep]


@dataclass
class TestPlan:
    """
    Complete test plan generated before execution.
    Deliverable A in the specification.
    """
    test_plan_id: str
    created_at: datetime
    created_by: str
    scenario_id: str
    scenario_name: str
    target_url: str
    flows: List[TestFlow]
    environment_matrix: EnvironmentMatrix
    matrix_cells: List[MatrixCell]
    total_cells_to_execute: int
    estimated_duration_minutes: int
    tags: List[str] = field(default_factory=list)
    user_request: str = ""  # Original user message for custom test instructions


# ============================================================================
# EXECUTION RESULTS
# ============================================================================

@dataclass
class StepResult:
    """Result of executing a single test step."""
    step_number: int
    action: str
    target: str
    expected_outcome: str
    actual_outcome: str
    passed: bool
    timestamp: datetime
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class Screenshot:
    """Screenshot captured during test."""
    label: str
    url: str
    storage_path: str
    captured_at: datetime


@dataclass
class ConsoleError:
    """Browser console error captured during test."""
    message: str
    severity: Literal["error", "warning"]
    timestamp: datetime
    source: Optional[str] = None


@dataclass
class NetworkRequest:
    """Network request logged during test."""
    url: str
    method: str
    status_code: int
    duration_ms: int
    failed: bool
    timestamp: datetime


@dataclass
class CellResult:
    """
    Result of executing one matrix cell.
    Contains all evidence and outcomes for one environment combination.
    """
    cell_id: str
    viewport: str
    browser: str
    network: str
    status: TestStatus
    started_at: datetime
    completed_at: datetime
    duration_ms: int
    step_results: List[StepResult]
    screenshots: List[Screenshot] = field(default_factory=list)
    console_errors: List[ConsoleError] = field(default_factory=list)
    network_requests: List[NetworkRequest] = field(default_factory=list)
    failure_summary: Optional[str] = None
    failure_priority: Optional[FailurePriority] = None


# ============================================================================
# RUN ARTIFACT (POST-EXECUTION)
# ============================================================================

@dataclass
class EnvironmentSummary:
    """Summary of what environments were tested."""
    viewports_tested: List[str]
    browsers_tested: List[str]
    networks_tested: List[str]


@dataclass
class ComparisonToPreviousRun:
    """Comparison to previous test run (for regression tracking)."""
    previous_run_id: str
    still_failing: List[str]  # cell_ids
    now_passing: List[str]    # cell_ids
    new_failures: List[str]   # cell_ids


@dataclass
class FailuresByPriority:
    """Failures grouped by priority level."""
    P0: List[str] = field(default_factory=list)  # cell_ids
    P1: List[str] = field(default_factory=list)
    P2: List[str] = field(default_factory=list)


@dataclass
class RunArtifact:
    """
    Complete record of a test run execution.
    Deliverable B in the specification.
    This gets stored and rendered in the dashboard.
    """
    run_id: str
    test_plan_id: str
    scenario_id: str
    scenario_name: str
    target_url: str
    triggered_by: str
    triggered_at: datetime
    started_at: datetime
    completed_at: datetime
    duration_total_seconds: int
    overall_status: TestStatus
    total_cells: int
    passed_cells: int
    failed_cells: int
    timed_out_cells: int
    environment_summary: EnvironmentSummary
    cell_results: List[CellResult]
    failures_by_priority: FailuresByPriority
    artifacts_storage_path: str
    comparison_to_previous_run: Optional[ComparisonToPreviousRun] = None


# ============================================================================
# SLACK OUTPUT
# ============================================================================

@dataclass
class SlackFailureDetail:
    """A single failure formatted for Slack display."""
    priority: FailurePriority
    environment: str  # e.g. "Safari (iOS) / iPhone 13 Pro / Normal Network"
    flow_name: str
    issue: str
    detail: str
    screenshot_url: Optional[str] = None
    console_error: Optional[str] = None


@dataclass
class SlackEnvironmentBreakdown:
    """Per-dimension pass/fail breakdown for Slack."""
    dimension: str  # "Viewports" or "Browsers" or "Network"
    items: Dict[str, str]  # e.g. {"iPhone 13 Pro": "2/4 runs passed ⚠️"}


@dataclass
class SlackSummary:
    """
    Human-readable Slack message content.
    Deliverable C in the specification.
    """
    scenario_name: str
    target_url: str
    run_id: str
    overall_status: TestStatus
    pass_count: int
    total_count: int
    critical_failures: List[SlackFailureDetail]
    passes_summary: List[str]
    environment_breakdown: List[SlackEnvironmentBreakdown]
    next_steps: List[str]
    rerun_command: str
    dashboard_link: str


# ============================================================================
# PARSING STRUCTURES
# ============================================================================

@dataclass
class ParsedSlackRequest:
    """
    Parsed representation of a Slack test request.
    Extracted from natural language input.
    """
    target_urls: List[str]
    flows: List[str]  # Inferred or explicit user journeys
    required_viewports: List[str]  # Viewport profile names
    required_browsers: List[str]   # Browser profile names
    required_networks: List[str]   # Network profile names
    explicit_expectations: List[str]  # Pass criteria mentioned by user
    is_rerun: bool = False
    rerun_scenario_reference: Optional[str] = None
    raw_message: str = ""
