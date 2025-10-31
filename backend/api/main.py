"""
TestGPT Backend API Server

FastAPI server that provides REST endpoints for test management,
configuration, and execution.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

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
# TEST EXECUTION ENDPOINTS
# ============================================================================

@app.post("/api/tests/{test_id}/run", response_model=schemas.TestExecutionResponse)
async def run_test(
    test_id: str,
    execution: schemas.TestExecutionCreate,
    db: Session = Depends(get_db)
):
    """
    Execute a test suite with specified configuration

    This creates an execution record and triggers the test runner.
    For now, it creates a pending execution that needs to be picked up
    by the test runner service.
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

    # TODO: Trigger actual test execution via test runner
    # For now, just return the pending execution

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
# BATCH EXECUTION
# ============================================================================

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

    persistence = PersistenceLayer()
    scenarios = persistence.list_all_scenarios()

    migrated = 0
    errors = []

    for scenario_dict in scenarios:
        try:
            # Check if already exists
            existing = crud.get_test_suite(db, scenario_dict["scenario_id"])
            if existing:
                continue

            # Create test suite from scenario
            suite_create = schemas.TestSuiteCreate(
                name=scenario_dict.get("scenario_name", "Migrated Test"),
                description=f"Migrated from JSON: {scenario_dict.get('scenario_id')}",
                prompt=scenario_dict.get("target_url", ""),
                target_url=scenario_dict.get("target_url", ""),
                test_steps=[],  # Steps would need proper conversion
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
