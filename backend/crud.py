"""
CRUD operations for TestGPT database.

Handles all database queries and mutations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime
import uuid

from backend.database import TestSuite, ConfigurationTemplate, TestExecution, ExecutionStep
from backend.schemas import (
    TestSuiteCreate,
    TestSuiteUpdate,
    ConfigurationTemplateCreate,
    ConfigurationTemplateUpdate,
    TestExecutionCreate,
)


# ============================================================================
# TEST SUITE CRUD
# ============================================================================

def create_test_suite(db: Session, suite: TestSuiteCreate) -> TestSuite:
    """Create a new test suite"""
    db_suite = TestSuite(
        id=f"suite-{uuid.uuid4().hex[:8]}",
        name=suite.name,
        description=suite.description,
        prompt=suite.prompt,
        target_url=suite.target_url,
        test_steps=[step.model_dump() for step in suite.test_steps],
        created_by=suite.created_by,
        source_type=suite.source_type,
        tags=suite.tags,
        created_at=datetime.utcnow(),
    )
    db.add(db_suite)
    db.commit()
    db.refresh(db_suite)
    return db_suite


def get_test_suite(db: Session, suite_id: str) -> Optional[TestSuite]:
    """Get a test suite by ID"""
    return db.query(TestSuite).filter(TestSuite.id == suite_id).first()


def get_test_suite_by_name(db: Session, name: str) -> Optional[TestSuite]:
    """Get a test suite by name"""
    return db.query(TestSuite).filter(TestSuite.name == name).first()


def get_test_suites(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tags: Optional[List[str]] = None,
    search: Optional[str] = None,
) -> List[TestSuite]:
    """Get all test suites with optional filtering"""
    query = db.query(TestSuite)

    # Filter by tags
    if tags:
        # This is a simple JSON containment check - might need adjustment based on SQLite JSON support
        for tag in tags:
            query = query.filter(TestSuite.tags.contains(tag))

    # Search by name or URL
    if search:
        query = query.filter(
            (TestSuite.name.ilike(f"%{search}%"))
            | (TestSuite.target_url.ilike(f"%{search}%"))
        )

    return query.order_by(desc(TestSuite.created_at)).offset(skip).limit(limit).all()


def update_test_suite(
    db: Session, suite_id: str, suite_update: TestSuiteUpdate
) -> Optional[TestSuite]:
    """Update a test suite"""
    db_suite = get_test_suite(db, suite_id)
    if not db_suite:
        return None

    update_data = suite_update.model_dump(exclude_unset=True)

    # Convert test_steps if present
    if "test_steps" in update_data and update_data["test_steps"]:
        update_data["test_steps"] = [step.model_dump() for step in update_data["test_steps"]]

    for field, value in update_data.items():
        setattr(db_suite, field, value)

    db.commit()
    db.refresh(db_suite)
    return db_suite


def delete_test_suite(db: Session, suite_id: str) -> bool:
    """Delete a test suite"""
    db_suite = get_test_suite(db, suite_id)
    if not db_suite:
        return False

    db.delete(db_suite)
    db.commit()
    return True


def update_test_suite_last_run(db: Session, suite_id: str) -> None:
    """Update the last_run timestamp for a test suite"""
    db_suite = get_test_suite(db, suite_id)
    if db_suite:
        db_suite.last_run = datetime.utcnow()
        db.commit()


# ============================================================================
# CONFIGURATION TEMPLATE CRUD
# ============================================================================

def create_config_template(
    db: Session, config: ConfigurationTemplateCreate
) -> ConfigurationTemplate:
    """Create a new configuration template"""
    db_config = ConfigurationTemplate(
        id=f"config-{uuid.uuid4().hex[:8]}",
        name=config.name,
        description=config.description,
        browsers=config.browsers,
        viewports=[vp.model_dump() for vp in config.viewports],
        network_modes=config.network_modes,
        user_agent_strings=config.user_agent_strings,
        screenshot_on_failure=config.screenshot_on_failure,
        video_recording=config.video_recording,
        parallel_execution=config.parallel_execution,
        max_workers=config.max_workers,
        default_timeout=config.default_timeout,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_config_template(db: Session, config_id: str) -> Optional[ConfigurationTemplate]:
    """Get a configuration template by ID"""
    return (
        db.query(ConfigurationTemplate)
        .filter(ConfigurationTemplate.id == config_id)
        .first()
    )


def get_config_templates(
    db: Session, skip: int = 0, limit: int = 100
) -> List[ConfigurationTemplate]:
    """Get all configuration templates"""
    return (
        db.query(ConfigurationTemplate)
        .order_by(desc(ConfigurationTemplate.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_config_template(
    db: Session, config_id: str, config_update: ConfigurationTemplateUpdate
) -> Optional[ConfigurationTemplate]:
    """Update a configuration template"""
    db_config = get_config_template(db, config_id)
    if not db_config:
        return None

    update_data = config_update.model_dump(exclude_unset=True)

    # Convert viewports if present
    if "viewports" in update_data and update_data["viewports"]:
        update_data["viewports"] = [vp.model_dump() for vp in update_data["viewports"]]

    for field, value in update_data.items():
        setattr(db_config, field, value)

    db_config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_config)
    return db_config


def delete_config_template(db: Session, config_id: str) -> bool:
    """Delete a configuration template"""
    db_config = get_config_template(db, config_id)
    if not db_config:
        return False

    db.delete(db_config)
    db.commit()
    return True


# ============================================================================
# TEST EXECUTION CRUD
# ============================================================================

def create_test_execution(
    db: Session, execution: TestExecutionCreate
) -> TestExecution:
    """Create a new test execution"""
    db_execution = TestExecution(
        id=f"exec-{uuid.uuid4().hex[:8]}",
        test_suite_id=execution.test_suite_id,
        config_id=execution.config_id,
        status="pending",
        browser=execution.browser,
        viewport_width=execution.viewport_width,
        viewport_height=execution.viewport_height,
        network_mode=execution.network_mode,
        triggered_by=execution.triggered_by,
        triggered_by_user=execution.triggered_by_user,
        created_at=datetime.utcnow(),
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


def get_test_execution(db: Session, execution_id: str) -> Optional[TestExecution]:
    """Get a test execution by ID"""
    return db.query(TestExecution).filter(TestExecution.id == execution_id).first()


def get_test_executions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    test_suite_id: Optional[str] = None,
) -> List[TestExecution]:
    """Get all test executions with optional filtering"""
    query = db.query(TestExecution)

    if status:
        query = query.filter(TestExecution.status == status)

    if test_suite_id:
        query = query.filter(TestExecution.test_suite_id == test_suite_id)

    return query.order_by(desc(TestExecution.created_at)).offset(skip).limit(limit).all()


def update_test_execution_status(
    db: Session,
    execution_id: str,
    status: str,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    error_details: Optional[str] = None,
    execution_logs: Optional[List] = None,
    screenshots: Optional[List[str]] = None,
) -> Optional[TestExecution]:
    """Update test execution status and results"""
    db_execution = get_test_execution(db, execution_id)
    if not db_execution:
        return None

    db_execution.status = status

    if started_at:
        db_execution.started_at = started_at

    if completed_at:
        db_execution.completed_at = completed_at

        # Calculate execution time
        if db_execution.started_at:
            delta = completed_at - db_execution.started_at
            db_execution.execution_time_ms = int(delta.total_seconds() * 1000)

    if error_details:
        db_execution.error_details = error_details

    if execution_logs:
        db_execution.execution_logs = execution_logs

    if screenshots:
        db_execution.screenshots = screenshots

    db.commit()
    db.refresh(db_execution)
    return db_execution


def get_execution_history(
    db: Session, test_suite_id: str, limit: int = 50
) -> List[TestExecution]:
    """Get execution history for a specific test suite"""
    return (
        db.query(TestExecution)
        .filter(TestExecution.test_suite_id == test_suite_id)
        .order_by(desc(TestExecution.created_at))
        .limit(limit)
        .all()
    )


# ============================================================================
# STATISTICS
# ============================================================================

def get_statistics(db: Session) -> dict:
    """Get overall statistics"""
    total_suites = db.query(func.count(TestSuite.id)).scalar()
    total_executions = db.query(func.count(TestExecution.id)).scalar()

    passed_executions = (
        db.query(func.count(TestExecution.id))
        .filter(TestExecution.status == "passed")
        .scalar()
    )

    failed_executions = (
        db.query(func.count(TestExecution.id))
        .filter(TestExecution.status == "failed")
        .scalar()
    )

    running_executions = (
        db.query(func.count(TestExecution.id))
        .filter(TestExecution.status == "running")
        .scalar()
    )

    avg_execution_time = db.query(func.avg(TestExecution.execution_time_ms)).scalar()

    # Get most run test
    most_run_test = None
    try:
        # Query to find test suite with most executions
        result = (
            db.query(
                TestExecution.test_suite_id,
                func.count(TestExecution.id).label("run_count")
            )
            .filter(TestExecution.test_suite_id.isnot(None))
            .group_by(TestExecution.test_suite_id)
            .order_by(desc("run_count"))
            .first()
        )

        if result:
            suite = db.query(TestSuite).filter(TestSuite.id == result[0]).first()
            if suite:
                most_run_test = {
                    "id": suite.id,
                    "name": suite.name,
                    "run_count": result[1]
                }
    except Exception:
        pass  # If no executions exist, return None

    # Get recent failures
    recent_failures = (
        db.query(TestExecution)
        .filter(TestExecution.status == "failed")
        .order_by(desc(TestExecution.created_at))
        .limit(5)
        .all()
    )

    return {
        "total_test_suites": total_suites or 0,
        "total_executions": total_executions or 0,
        "passed_executions": passed_executions or 0,
        "failed_executions": failed_executions or 0,
        "running_executions": running_executions or 0,
        "average_execution_time_ms": avg_execution_time,
        "most_run_test": most_run_test,
        "recent_failures": recent_failures,
    }
