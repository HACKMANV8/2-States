"""
CRUD operations for PR Test Runs.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

from .database import PRTestRun, PRTestMetrics


def create_pr_test_run(db: Session, pr_test_data: Dict[str, Any]) -> PRTestRun:
    """
    Create a new PR test run record.

    Args:
        db: Database session
        pr_test_data: PR test data dictionary

    Returns:
        Created PRTestRun instance
    """
    pr_test = PRTestRun(
        id=pr_test_data.get("test_run_id", f"pr-test-{uuid.uuid4().hex[:8]}"),
        pr_url=pr_test_data["pr_url"],
        pr_number=pr_test_data["pr_number"],
        pr_title=pr_test_data["pr_title"],
        pr_author=pr_test_data.get("pr_author"),
        repo_owner=pr_test_data["repo_owner"],
        repo_name=pr_test_data["repo_name"],
        base_branch=pr_test_data.get("base_branch"),
        head_branch=pr_test_data.get("head_branch"),
        head_sha=pr_test_data.get("head_sha"),
        pr_description=pr_test_data.get("pr_description"),
        files_changed_count=pr_test_data.get("files_changed_count"),
        changed_files=pr_test_data.get("changed_files", []),
        acceptance_criteria=pr_test_data.get("acceptance_criteria", []),
        linked_issues=pr_test_data.get("linked_issues", []),
        deployment_url=pr_test_data.get("deployment_url"),
        deployment_platform=pr_test_data.get("deployment_platform"),
        deployment_accessible=pr_test_data.get("deployment_accessible"),
        deployment_response_time_ms=pr_test_data.get("deployment_response_time_ms"),
        project_type=pr_test_data.get("project_type"),
        tech_stack=pr_test_data.get("tech_stack", []),
        framework_detected=pr_test_data.get("framework_detected"),
        test_scenarios_generated=pr_test_data.get("test_scenarios", []),
        scenario_count=pr_test_data.get("scenario_count", 0),
        status=pr_test_data.get("status", "pending"),
        overall_pass=pr_test_data.get("overall_pass"),
        scenarios_passed=pr_test_data.get("scenarios_passed", 0),
        scenarios_failed=pr_test_data.get("scenarios_failed", 0),
        scenarios_total=pr_test_data.get("scenarios_total", 0),
        test_results=pr_test_data.get("test_results"),
        failures=pr_test_data.get("failures", []),
        console_errors=pr_test_data.get("console_errors", []),
        screenshots=pr_test_data.get("screenshots", []),
        agent_response=pr_test_data.get("agent_response"),
        started_at=pr_test_data.get("started_at", datetime.utcnow()),
        completed_at=pr_test_data.get("completed_at"),
        duration_ms=pr_test_data.get("duration_ms"),
        github_comment_posted=pr_test_data.get("github_comment_posted", False),
        github_comment_url=pr_test_data.get("github_comment_url"),
        github_comment_id=pr_test_data.get("github_comment_id"),
        slack_message_posted=pr_test_data.get("slack_message_posted", False),
        slack_channel_id=pr_test_data.get("slack_channel_id"),
        slack_message_ts=pr_test_data.get("slack_message_ts"),
        triggered_by=pr_test_data.get("triggered_by", "slack"),
        triggered_by_user=pr_test_data.get("triggered_by_user"),
        custom_instructions=pr_test_data.get("custom_instructions"),
        github_api_calls=pr_test_data.get("github_api_calls", 0),
        total_processing_time_ms=pr_test_data.get("total_processing_time_ms"),
        coverage_enabled=pr_test_data.get("coverage_enabled", False),
        coverage_percentage=pr_test_data.get("coverage_percentage"),
        coverage_html_path=pr_test_data.get("coverage_html_path"),
        coverage_report_data=pr_test_data.get("coverage_report"),
    )

    db.add(pr_test)
    db.commit()
    db.refresh(pr_test)

    # Update metrics
    _update_daily_metrics(db, pr_test)

    return pr_test


def update_pr_test_run(db: Session, test_run_id: str, updates: Dict[str, Any]) -> Optional[PRTestRun]:
    """
    Update an existing PR test run.

    Args:
        db: Database session
        test_run_id: ID of the test run to update
        updates: Dictionary of fields to update

    Returns:
        Updated PRTestRun instance or None if not found
    """
    pr_test = db.query(PRTestRun).filter(PRTestRun.id == test_run_id).first()

    if not pr_test:
        return None

    for key, value in updates.items():
        if hasattr(pr_test, key):
            setattr(pr_test, key, value)

    pr_test.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(pr_test)

    # Update metrics if status changed
    if "status" in updates:
        _update_daily_metrics(db, pr_test)

    return pr_test


def get_pr_test_run(db: Session, test_run_id: str) -> Optional[PRTestRun]:
    """Get a PR test run by ID."""
    return db.query(PRTestRun).filter(PRTestRun.id == test_run_id).first()


def get_pr_test_runs(
    db: Session,
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
    pr_number: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[PRTestRun]:
    """
    Get PR test runs with optional filters.

    Args:
        db: Database session
        repo_owner: Filter by repository owner
        repo_name: Filter by repository name
        pr_number: Filter by PR number
        status: Filter by status
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of PRTestRun instances
    """
    query = db.query(PRTestRun)

    if repo_owner:
        query = query.filter(PRTestRun.repo_owner == repo_owner)
    if repo_name:
        query = query.filter(PRTestRun.repo_name == repo_name)
    if pr_number:
        query = query.filter(PRTestRun.pr_number == pr_number)
    if status:
        query = query.filter(PRTestRun.status == status)

    query = query.order_by(desc(PRTestRun.created_at))
    query = query.limit(limit).offset(offset)

    return query.all()


def get_pr_test_stats(db: Session, days: int = 7) -> Dict[str, Any]:
    """
    Get aggregate statistics for PR tests.

    Args:
        db: Database session
        days: Number of days to look back

    Returns:
        Dictionary with statistics
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    tests = db.query(PRTestRun).filter(PRTestRun.created_at >= cutoff_date).all()

    total_tests = len(tests)
    passed_tests = sum(1 for t in tests if t.status == "passed")
    failed_tests = sum(1 for t in tests if t.status == "failed")
    error_tests = sum(1 for t in tests if t.status == "error")

    avg_duration = sum(t.duration_ms or 0 for t in tests) / total_tests if total_tests > 0 else 0

    # Platform breakdown
    platforms = {}
    for test in tests:
        platform = test.deployment_platform or "unknown"
        platforms[platform] = platforms.get(platform, 0) + 1

    # Framework breakdown
    frameworks = {}
    for test in tests:
        framework = test.framework_detected or "unknown"
        frameworks[framework] = frameworks.get(framework, 0) + 1

    return {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "errors": error_tests,
        "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        "avg_duration_ms": int(avg_duration),
        "platforms": platforms,
        "frameworks": frameworks,
        "period_days": days
    }


def delete_pr_test_run(db: Session, test_run_id: str) -> bool:
    """
    Delete a PR test run.

    Args:
        db: Database session
        test_run_id: ID of test run to delete

    Returns:
        True if deleted, False if not found
    """
    pr_test = db.query(PRTestRun).filter(PRTestRun.id == test_run_id).first()

    if not pr_test:
        return False

    db.delete(pr_test)
    db.commit()

    return True


def _update_daily_metrics(db: Session, pr_test: PRTestRun):
    """
    Update daily metrics based on a PR test run.

    Args:
        db: Database session
        pr_test: PR test run instance
    """
    # Get or create today's metrics
    today = datetime.utcnow().date()
    metrics_id = f"metrics-{today.isoformat()}"

    metrics = db.query(PRTestMetrics).filter(PRTestMetrics.id == metrics_id).first()

    if not metrics:
        metrics = PRTestMetrics(
            id=metrics_id,
            date=datetime.combine(today, datetime.min.time()),
            total_pr_tests=0,
            total_passed=0,
            total_failed=0,
            total_errors=0,
            deployments_found=0,
            deployments_accessible=0,
            deployment_platforms={},
            frameworks_detected={}
        )
        db.add(metrics)

    # Update counts
    metrics.total_pr_tests += 1

    if pr_test.status == "passed":
        metrics.total_passed += 1
    elif pr_test.status == "failed":
        metrics.total_failed += 1
    elif pr_test.status == "error":
        metrics.total_errors += 1

    # Update deployment metrics
    if pr_test.deployment_url:
        metrics.deployments_found += 1
        if pr_test.deployment_accessible:
            metrics.deployments_accessible += 1

        # Update platform counts
        platforms = metrics.deployment_platforms or {}
        platform = pr_test.deployment_platform or "unknown"
        platforms[platform] = platforms.get(platform, 0) + 1
        metrics.deployment_platforms = platforms

    # Update framework metrics
    if pr_test.framework_detected:
        frameworks = metrics.frameworks_detected or {}
        frameworks[pr_test.framework_detected] = frameworks.get(pr_test.framework_detected, 0) + 1
        metrics.frameworks_detected = frameworks

    # Update timing metrics
    all_tests_today = db.query(PRTestRun).filter(
        func.date(PRTestRun.created_at) == today
    ).all()

    if all_tests_today:
        total_duration = sum(t.duration_ms or 0 for t in all_tests_today)
        metrics.avg_execution_time_ms = int(total_duration / len(all_tests_today))

    # Update success rates by type
    frontend_tests = [t for t in all_tests_today if t.project_type == "frontend"]
    backend_tests = [t for t in all_tests_today if t.project_type == "backend"]
    fullstack_tests = [t for t in all_tests_today if t.project_type == "fullstack"]

    if frontend_tests:
        metrics.frontend_success_rate = sum(1 for t in frontend_tests if t.status == "passed") / len(frontend_tests) * 100

    if backend_tests:
        metrics.backend_success_rate = sum(1 for t in backend_tests if t.status == "passed") / len(backend_tests) * 100

    if fullstack_tests:
        metrics.fullstack_success_rate = sum(1 for t in fullstack_tests if t.status == "passed") / len(fullstack_tests) * 100

    metrics.updated_at = datetime.utcnow()

    db.commit()


def get_metrics(db: Session, days: int = 30) -> List[PRTestMetrics]:
    """
    Get metrics for the last N days.

    Args:
        db: Database session
        days: Number of days to retrieve

    Returns:
        List of PRTestMetrics instances
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    return db.query(PRTestMetrics).filter(
        PRTestMetrics.date >= cutoff_date
    ).order_by(desc(PRTestMetrics.date)).all()
