"""
TestGPT Backend API Server

FastAPI server that provides REST endpoints for test management,
configuration, and execution.
"""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.database import init_db, get_db
from backend import crud
from backend import schemas
from backend.api import pr_tests

# Initialize FastAPI app
app = FastAPI(
    title="TestGPT API",
    description="Backend API for TestGPT - AI-powered testing automation system",
    version="1.0.0",
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include PR Tests router
app.include_router(pr_tests.router)


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("🚀 TestGPT API Server started")
    print("📚 API Docs: http://localhost:8000/docs")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "TestGPT API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }


# ============================================================================
# TEST SUITE ENDPOINTS
# ============================================================================

@app.post("/api/tests", response_model=schemas.TestSuiteResponse)
def create_test(
    suite: schemas.TestSuiteCreate,
    db: Session = Depends(get_db)
):
    """Create a new test suite"""
    return crud.create_test_suite(db, suite)


@app.get("/api/tests", response_model=List[schemas.TestSuiteListItem])
def list_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = Query(None, description="Search in name and URL"),
    db: Session = Depends(get_db)
):
    """List all test suites with optional filtering"""
    tags_list = tags.split(",") if tags else None
    suites = crud.get_test_suites(db, skip=skip, limit=limit, tags=tags_list, search=search)
    return suites


@app.get("/api/tests/{test_id}", response_model=schemas.TestSuiteResponse)
def get_test(test_id: str, db: Session = Depends(get_db)):
    """Get a specific test suite by ID"""
    suite = crud.get_test_suite(db, test_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return suite


@app.put("/api/tests/{test_id}", response_model=schemas.TestSuiteResponse)
def update_test(
    test_id: str,
    suite_update: schemas.TestSuiteUpdate,
    db: Session = Depends(get_db)
):
    """Update a test suite"""
    suite = crud.update_test_suite(db, test_id, suite_update)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return suite


@app.delete("/api/tests/{test_id}")
def delete_test(test_id: str, db: Session = Depends(get_db)):
    """Delete a test suite"""
    success = crud.delete_test_suite(db, test_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return {"status": "deleted", "id": test_id}


# ============================================================================
# CONFIGURATION TEMPLATE ENDPOINTS
# ============================================================================

@app.post("/api/configs", response_model=schemas.ConfigurationTemplateResponse)
def create_config(
    config: schemas.ConfigurationTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new configuration template"""
    return crud.create_config_template(db, config)


@app.get("/api/configs", response_model=List[schemas.ConfigurationTemplateResponse])
def list_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all configuration templates"""
    return crud.get_config_templates(db, skip=skip, limit=limit)


@app.get("/api/configs/{config_id}", response_model=schemas.ConfigurationTemplateResponse)
def get_config(config_id: str, db: Session = Depends(get_db)):
    """Get a specific configuration template"""
    config = crud.get_config_template(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration template not found")
    return config


@app.put("/api/configs/{config_id}", response_model=schemas.ConfigurationTemplateResponse)
def update_config(
    config_id: str,
    config_update: schemas.ConfigurationTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update a configuration template"""
    config = crud.update_config_template(db, config_id, config_update)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration template not found")
    return config


@app.delete("/api/configs/{config_id}")
def delete_config(config_id: str, db: Session = Depends(get_db)):
    """Delete a configuration template"""
    success = crud.delete_config_template(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration template not found")
    return {"status": "deleted", "id": config_id}


# ============================================================================
# BACKGROUND TEST EXECUTION
# ============================================================================

def execute_test_in_background(
    execution_id: str,
    test_suite_id: str,
    browser: str,
    viewport_width: int,
    viewport_height: int,
    network_mode: str
):
    """
    Execute a test in the background and update the execution record.

    This function runs as a background task and updates the database
    with execution results.
    """
    import asyncio
    from testgpt_engine import TestGPTEngine
    from datetime import datetime

    # Get a new database session for this background task
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Update status to running
        crud.update_test_execution_status(
            db,
            execution_id,
            status="running",
            started_at=datetime.utcnow()
        )

        # Get the test suite
        suite = crud.get_test_suite(db, test_suite_id)
        if not suite:
            crud.update_test_execution_status(
                db,
                execution_id,
                status="failed",
                completed_at=datetime.utcnow(),
                error_details="Test suite not found"
            )
            return

        # Map browser names to test engine format
        browser_map = {
            "chrome": "chromium",
            "firefox": "firefox",
            "safari": "webkit",
            "edge": "chromium"
        }
        engine_browser = browser_map.get(browser.lower(), "chromium")

        # Map viewport to device class
        if viewport_width <= 500:
            viewports = ["mobile_portrait"]
        elif viewport_width <= 900:
            viewports = ["tablet_portrait"]
        else:
            viewports = ["desktop_1920"]

        # Map network mode
        network_map = {
            "online": "normal",
            "fast3g": "fast_3g",
            "slow3g": "slow_3g"
        }
        network = network_map.get(network_mode.lower(), "normal")

        # Build proper test message from test steps
        test_steps_text = ""
        if suite.test_steps:
            steps = []
            for step in suite.test_steps:
                # Handle both dict and object types
                if isinstance(step, dict):
                    step_num = step.get('step_number', 0)
                    action = step.get('action', '')
                    target = step.get('target', '')
                    value = step.get('value', '')
                    expected = step.get('expected_outcome', '')
                else:
                    step_num = step.step_number
                    action = step.action
                    target = step.target
                    value = step.value if hasattr(step, 'value') else ''
                    expected = step.expected_outcome

                step_text = f"{step_num}. {action} {target}"
                if value:
                    step_text += f" with value '{value}'"
                step_text += f" - Expected: {expected}"
                steps.append(step_text)

            test_steps_text = "\n".join(steps)

        # Build Slack-style test message
        slack_message = f"test {suite.target_url}"
        if test_steps_text:
            slack_message += f"\n\nTest Steps:\n{test_steps_text}"
        if suite.description:
            slack_message += f"\n\nDescription: {suite.description}"

        # Add browser and viewport info
        slack_message += f" browser:{browser} viewport:{viewport_width}x{viewport_height}"

        print(f"🚀 Starting API test execution for suite: {suite.name}")
        print(f"📝 Test message: {slack_message[:200]}...")

        # Initialize TestGPT engine and run the test
        engine = TestGPTEngine()

        try:
            # Execute the test
            print("🤖 Calling TestGPT engine.process_test_request()...")
            slack_summary = asyncio.run(engine.process_test_request(
                slack_message=slack_message,
                user_id="api-user"
            ))
            print(f"✅ Test execution completed: {slack_summary[:100]}...")

            # Update execution with success
            crud.update_test_execution_status(
                db,
                execution_id,
                status="passed",
                completed_at=datetime.utcnow(),
                execution_logs=[{
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": slack_summary
                }]
            )

        except Exception as test_error:
            # Update execution with failure
            crud.update_test_execution_status(
                db,
                execution_id,
                status="failed",
                completed_at=datetime.utcnow(),
                error_details=str(test_error)
            )

    except Exception as e:
        # Critical error during execution setup
        try:
            crud.update_test_execution_status(
                db,
                execution_id,
                status="failed",
                completed_at=datetime.utcnow(),
                error_details=f"Execution setup error: {str(e)}"
            )
        except:
            pass
    finally:
        db.close()


# ============================================================================
# TEST EXECUTION ENDPOINTS
# ============================================================================

# NOTE: Batch execution must come BEFORE parameterized routes to avoid path conflicts
@app.post("/api/tests/batch/run", response_model=schemas.BatchExecutionResponse)
async def run_batch_tests(
    batch: schemas.BatchExecutionCreate,
    db: Session = Depends(get_db)
):
    """
    Run multiple test suites with the same configuration

    Creates execution records for all specified test suites.
    """
    execution_ids = []

    for test_suite_id in batch.test_suite_ids:
        # Verify test suite exists
        suite = crud.get_test_suite(db, test_suite_id)
        if not suite:
            continue

        # Create execution
        execution = schemas.TestExecutionCreate(
            test_suite_id=test_suite_id,
            config_id=batch.config_id,
            triggered_by=batch.triggered_by,
            triggered_by_user=batch.triggered_by_user,
        )

        db_execution = crud.create_test_execution(db, execution)
        execution_ids.append(db_execution.id)

        # Update last_run
        crud.update_test_suite_last_run(db, test_suite_id)

    batch_id = f"batch-{execution_ids[0]}" if execution_ids else "batch-empty"

    return {
        "batch_id": batch_id,
        "execution_ids": execution_ids,
        "total_tests": len(execution_ids),
        "status": "pending",
    }


@app.post("/api/tests/{test_id}/run", response_model=schemas.TestExecutionResponse)
async def run_test(
    test_id: str,
    execution: schemas.TestExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute a test suite with specified configuration

    This creates an execution record and triggers the test runner
    in the background. The test runs asynchronously and updates
    the execution record with results.
    """
    # Verify test suite exists
    suite = crud.get_test_suite(db, test_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")

    # Override test_suite_id
    execution.test_suite_id = test_id

    # Create execution record
    db_execution = crud.create_test_execution(db, execution)

    # Update test suite last_run timestamp
    crud.update_test_suite_last_run(db, test_id)

    # Trigger actual test execution in background
    # Use default values if not provided
    browser = execution.browser or "chrome"
    viewport_width = execution.viewport_width or 1920
    viewport_height = execution.viewport_height or 1080
    network_mode = execution.network_mode or "online"

    # Schedule background task
    background_tasks.add_task(
        execute_test_in_background,
        db_execution.id,
        test_id,
        browser,
        viewport_width,
        viewport_height,
        network_mode
    )

    return db_execution


@app.get("/api/executions", response_model=List[schemas.TestExecutionListItem])
def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    test_suite_id: Optional[str] = Query(None, description="Filter by test suite"),
    db: Session = Depends(get_db)
):
    """List all test executions with optional filtering"""
    return crud.get_test_executions(
        db,
        skip=skip,
        limit=limit,
        status=status,
        test_suite_id=test_suite_id
    )


@app.get("/api/executions/{execution_id}", response_model=schemas.TestExecutionResponse)
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    """Get a specific test execution"""
    execution = crud.get_test_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Test execution not found")
    return execution


@app.get("/api/tests/{test_id}/history", response_model=schemas.ExecutionHistoryResponse)
def get_test_history(
    test_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get execution history for a specific test suite"""
    suite = crud.get_test_suite(db, test_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")

    executions = crud.get_execution_history(db, test_id, limit=limit)

    # Calculate statistics
    total_runs = len(executions)
    passed_runs = sum(1 for e in executions if e.status == "passed")
    failed_runs = sum(1 for e in executions if e.status == "failed")

    return {
        "test_suite_id": test_id,
        "test_suite_name": suite.name,
        "executions": executions,
        "total_runs": total_runs,
        "passed_runs": passed_runs,
        "failed_runs": failed_runs,
    }


# ============================================================================
# STATISTICS
# ============================================================================

@app.get("/api/statistics", response_model=schemas.TestStatistics)
def get_statistics(db: Session = Depends(get_db)):
    """Get overall testing statistics"""
    stats = crud.get_statistics(db)
    return stats


# ============================================================================
# MIGRATION ENDPOINT
# ============================================================================

@app.post("/api/migrate/json-to-db")
async def migrate_json_to_db(db: Session = Depends(get_db)):
    """
    Migrate existing JSON-based test scenarios to the database

    This reads from the testgpt_data directory and imports
    scenarios into the new database.
    """
    from persistence import PersistenceLayer
    import json
    from pathlib import Path

    persistence = PersistenceLayer()
    scenarios_dir = Path("./testgpt_data/scenarios")

    migrated = 0
    errors = []

    # Read full scenario files directly
    for file_path in scenarios_dir.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                scenario_dict = json.load(f)
        except Exception as e:
            errors.append({"file": str(file_path), "error": f"Failed to read file: {str(e)}"})
            continue
        try:
            # Check if already exists
            existing = crud.get_test_suite(db, scenario_dict["scenario_id"])
            if existing:
                # Update existing with steps if they don't have any
                if not existing.test_steps or len(existing.test_steps) == 0:
                    # Extract test steps from flows
                    test_steps = []
                    flows = scenario_dict.get("flows", [])
                    for flow in flows:
                        steps = flow.get("steps", [])
                        test_steps.extend(steps)

                    if test_steps:
                        existing.test_steps = test_steps
                        db.commit()
                        db.refresh(existing)
                        migrated += 1
                continue

            # Extract test steps from flows
            test_steps = []
            flows = scenario_dict.get("flows", [])
            for flow in flows:
                steps = flow.get("steps", [])
                test_steps.extend(steps)

            # Create test suite from scenario
            suite_create = schemas.TestSuiteCreate(
                name=scenario_dict.get("scenario_name", "Migrated Test"),
                description=f"Migrated from JSON: {scenario_dict.get('scenario_id')}",
                prompt=scenario_dict.get("target_url", ""),
                target_url=scenario_dict.get("target_url", ""),
                test_steps=[schemas.TestStepSchema(**step) for step in test_steps] if test_steps else [],
                created_by=scenario_dict.get("created_by", "migration"),
                source_type="manual",
                tags=scenario_dict.get("tags", []),
            )

            crud.create_test_suite(db, suite_create)
            migrated += 1

        except Exception as e:
            errors.append({"scenario_id": scenario_dict.get("scenario_id"), "error": str(e)})

    return {
        "status": "completed",
        "migrated": migrated,
        "errors": errors,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
