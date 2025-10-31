"""
API endpoints for PR Test Management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db, PRTestRun, PRTestMetrics
from ..pr_test_crud import (
    create_pr_test_run,
    update_pr_test_run,
    get_pr_test_run,
    get_pr_test_runs,
    get_pr_test_stats,
    delete_pr_test_run,
    get_metrics
)

router = APIRouter(prefix="/api/pr-tests", tags=["PR Tests"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PRTestRunResponse(BaseModel):
    """PR test run response model"""
    id: str
    pr_url: str
    pr_number: int
    pr_title: str
    pr_author: Optional[str]
    repo_owner: str
    repo_name: str
    base_branch: Optional[str]
    head_branch: Optional[str]
    deployment_url: Optional[str]
    deployment_platform: Optional[str]
    project_type: Optional[str]
    framework_detected: Optional[str]
    status: str
    overall_pass: Optional[bool]
    scenarios_passed: int
    scenarios_failed: int
    scenarios_total: int
    duration_ms: Optional[int]
    github_comment_posted: bool
    github_comment_url: Optional[str]
    slack_message_posted: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PRTestStatsResponse(BaseModel):
    """PR test statistics response"""
    total_tests: int
    passed: int
    failed: int
    errors: int
    success_rate: float
    avg_duration_ms: int
    platforms: dict
    frameworks: dict
    period_days: int


class PRTestDetailResponse(BaseModel):
    """Detailed PR test run response"""
    id: str
    pr_url: str
    pr_number: int
    pr_title: str
    pr_author: Optional[str]
    pr_description: Optional[str]
    repo_owner: str
    repo_name: str
    base_branch: Optional[str]
    head_branch: Optional[str]
    head_sha: Optional[str]
    files_changed_count: Optional[int]
    changed_files: Optional[list]
    acceptance_criteria: Optional[list]
    linked_issues: Optional[list]
    deployment_url: Optional[str]
    deployment_platform: Optional[str]
    deployment_accessible: Optional[bool]
    deployment_response_time_ms: Optional[int]
    project_type: Optional[str]
    tech_stack: Optional[list]
    framework_detected: Optional[str]
    test_scenarios_generated: Optional[list]
    scenario_count: int
    status: str
    overall_pass: Optional[bool]
    scenarios_passed: int
    scenarios_failed: int
    scenarios_total: int
    test_results: Optional[dict]
    failures: Optional[list]
    console_errors: Optional[list]
    screenshots: Optional[list]
    agent_response: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    github_comment_posted: bool
    github_comment_url: Optional[str]
    slack_message_posted: bool
    triggered_by: str
    triggered_by_user: Optional[str]
    custom_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PRTestMetricsResponse(BaseModel):
    """PR test metrics response"""
    id: str
    date: datetime
    total_pr_tests: int
    total_passed: int
    total_failed: int
    total_errors: int
    avg_execution_time_ms: Optional[int]
    deployments_found: int
    deployments_accessible: int
    deployment_platforms: Optional[dict]
    frameworks_detected: Optional[dict]
    frontend_success_rate: Optional[float]
    backend_success_rate: Optional[float]
    fullstack_success_rate: Optional[float]

    class Config:
        from_attributes = True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[PRTestRunResponse])
def list_pr_tests(
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
    pr_number: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List PR test runs with optional filters.

    Args:
        repo_owner: Filter by repository owner
        repo_name: Filter by repository name
        pr_number: Filter by PR number
        status: Filter by status (pending, running, passed, failed, error)
        limit: Maximum number of results (max 100)
        offset: Offset for pagination
        db: Database session

    Returns:
        List of PR test runs
    """
    tests = get_pr_test_runs(
        db=db,
        repo_owner=repo_owner,
        repo_name=repo_name,
        pr_number=pr_number,
        status=status,
        limit=limit,
        offset=offset
    )

    return tests


@router.get("/{test_run_id}", response_model=PRTestDetailResponse)
def get_pr_test_detail(test_run_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific PR test run.

    Args:
        test_run_id: ID of the test run
        db: Database session

    Returns:
        Detailed PR test run information

    Raises:
        HTTPException: If test run not found
    """
    test = get_pr_test_run(db, test_run_id)

    if not test:
        raise HTTPException(status_code=404, detail="PR test run not found")

    return test


@router.get("/repo/{owner}/{name}", response_model=List[PRTestRunResponse])
def get_repo_pr_tests(
    owner: str,
    name: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all PR tests for a specific repository.

    Args:
        owner: Repository owner
        name: Repository name
        limit: Maximum number of results
        offset: Offset for pagination
        db: Database session

    Returns:
        List of PR test runs for the repository
    """
    tests = get_pr_test_runs(
        db=db,
        repo_owner=owner,
        repo_name=name,
        limit=limit,
        offset=offset
    )

    return tests


@router.get("/pr/{owner}/{name}/{pr_number}", response_model=List[PRTestRunResponse])
def get_specific_pr_tests(
    owner: str,
    name: str,
    pr_number: int,
    db: Session = Depends(get_db)
):
    """
    Get all test runs for a specific PR.

    Args:
        owner: Repository owner
        name: Repository name
        pr_number: PR number
        db: Database session

    Returns:
        List of test runs for the specific PR
    """
    tests = get_pr_test_runs(
        db=db,
        repo_owner=owner,
        repo_name=name,
        pr_number=pr_number
    )

    return tests


@router.delete("/{test_run_id}")
def delete_pr_test(test_run_id: str, db: Session = Depends(get_db)):
    """
    Delete a PR test run.

    Args:
        test_run_id: ID of the test run to delete
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If test run not found
    """
    success = delete_pr_test_run(db, test_run_id)

    if not success:
        raise HTTPException(status_code=404, detail="PR test run not found")

    return {"message": "PR test run deleted successfully", "id": test_run_id}


@router.get("/stats/summary", response_model=PRTestStatsResponse)
def get_pr_test_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get aggregate statistics for PR tests.

    Args:
        days: Number of days to look back (1-90)
        db: Database session

    Returns:
        Aggregate statistics
    """
    stats = get_pr_test_stats(db, days=days)
    return stats


@router.get("/metrics/daily", response_model=List[PRTestMetricsResponse])
def get_daily_metrics(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get daily metrics for PR tests.

    Args:
        days: Number of days to retrieve (1-90)
        db: Database session

    Returns:
        List of daily metrics
    """
    metrics = get_metrics(db, days=days)
    return metrics


@router.get("/health", include_in_schema=True)
def health_check():
    """Health check endpoint for PR test API."""
    return {
        "status": "healthy",
        "service": "pr-tests-api",
        "timestamp": datetime.utcnow().isoformat()
    }
