"""
Pydantic schemas for TestGPT API.

Defines request/response models for FastAPI endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


# ============================================================================
# TEST SUITE SCHEMAS
# ============================================================================

class TestStepSchema(BaseModel):
    """Individual test step definition"""
    step_number: int
    action: str
    target: str
    expected_outcome: str
    timeout_seconds: int = 10
    value: Optional[str] = None


class TestSuiteCreate(BaseModel):
    """Request to create a new test suite"""
    name: str
    description: Optional[str] = None
    prompt: str
    target_url: str
    test_steps: List[TestStepSchema]
    created_by: Optional[str] = None
    source_type: Literal["slack_trigger", "github_pr", "manual"] = "manual"
    tags: List[str] = []


class TestSuiteUpdate(BaseModel):
    """Request to update a test suite"""
    name: Optional[str] = None
    description: Optional[str] = None
    test_steps: Optional[List[TestStepSchema]] = None
    tags: Optional[List[str]] = None


class TestSuiteResponse(BaseModel):
    """Test suite response"""
    id: str
    name: str
    description: Optional[str]
    prompt: str
    target_url: str
    test_steps: List[Dict[str, Any]]
    created_at: datetime
    last_run: Optional[datetime]
    created_by: Optional[str]
    source_type: str
    tags: List[str]

    class Config:
        from_attributes = True


class TestSuiteListItem(BaseModel):
    """Simplified test suite for list views"""
    id: str
    name: str
    description: Optional[str]
    target_url: str
    created_at: datetime
    last_run: Optional[datetime]
    tags: List[str]

    class Config:
        from_attributes = True


# ============================================================================
# CONFIGURATION TEMPLATE SCHEMAS
# ============================================================================

class ViewportConfig(BaseModel):
    """Viewport configuration"""
    width: int
    height: int
    device_name: str = "custom"


class ConfigurationTemplateCreate(BaseModel):
    """Request to create configuration template"""
    name: str
    description: Optional[str] = None
    browsers: List[str] = ["chrome"]
    viewports: List[ViewportConfig] = [{"width": 1920, "height": 1080, "device_name": "desktop"}]
    network_modes: List[str] = ["online"]
    user_agent_strings: Optional[List[str]] = None
    screenshot_on_failure: bool = True
    video_recording: bool = False
    parallel_execution: bool = True
    max_workers: int = 4
    default_timeout: int = 30000


class ConfigurationTemplateUpdate(BaseModel):
    """Request to update configuration template"""
    name: Optional[str] = None
    description: Optional[str] = None
    browsers: Optional[List[str]] = None
    viewports: Optional[List[ViewportConfig]] = None
    network_modes: Optional[List[str]] = None
    screenshot_on_failure: Optional[bool] = None
    video_recording: Optional[bool] = None
    parallel_execution: Optional[bool] = None
    max_workers: Optional[int] = None
    default_timeout: Optional[int] = None


class ConfigurationTemplateResponse(BaseModel):
    """Configuration template response"""
    id: str
    name: str
    description: Optional[str]
    browsers: List[str]
    viewports: List[Dict[str, Any]]
    network_modes: List[str]
    user_agent_strings: Optional[List[str]]
    screenshot_on_failure: bool
    video_recording: bool
    parallel_execution: bool
    max_workers: int
    default_timeout: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TEST EXECUTION SCHEMAS
# ============================================================================

class TestExecutionCreate(BaseModel):
    """Request to execute a test"""
    test_suite_id: str
    config_id: Optional[str] = None

    # Override config if needed
    browser: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    network_mode: Optional[str] = None

    # Trigger information
    triggered_by: Literal["slack", "manual", "github"] = "manual"
    triggered_by_user: Optional[str] = None


class TestExecutionResponse(BaseModel):
    """Test execution response"""
    id: str
    test_suite_id: Optional[str]
    config_id: Optional[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    execution_logs: Optional[List[Dict[str, Any]]]
    screenshots: Optional[List[str]]
    video_url: Optional[str]
    error_details: Optional[str]
    browser: Optional[str]
    viewport_width: Optional[int]
    viewport_height: Optional[int]
    network_mode: Optional[str]
    triggered_by: str
    triggered_by_user: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TestExecutionListItem(BaseModel):
    """Simplified execution for list views"""
    id: str
    test_suite_id: Optional[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    browser: Optional[str]
    triggered_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionHistoryResponse(BaseModel):
    """Execution history for a test suite"""
    test_suite_id: str
    test_suite_name: str
    executions: List[TestExecutionListItem]
    total_runs: int
    passed_runs: int
    failed_runs: int


# ============================================================================
# BATCH EXECUTION SCHEMAS
# ============================================================================

class BatchExecutionCreate(BaseModel):
    """Request to run multiple tests"""
    test_suite_ids: List[str]
    config_id: Optional[str] = None
    triggered_by: Literal["slack", "manual", "github"] = "manual"
    triggered_by_user: Optional[str] = None


class BatchExecutionResponse(BaseModel):
    """Batch execution response"""
    batch_id: str
    execution_ids: List[str]
    total_tests: int
    status: str


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class TestStatistics(BaseModel):
    """Overall test statistics"""
    total_test_suites: int
    total_executions: int
    passed_executions: int
    failed_executions: int
    running_executions: int
    average_execution_time_ms: Optional[float]
    most_run_test: Optional[Dict[str, Any]]
    recent_failures: List[TestExecutionListItem]
