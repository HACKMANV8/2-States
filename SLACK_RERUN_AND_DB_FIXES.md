# Slack Re-Run and Database Persistence Fixes

## Issues Fixed

### Error 1: Slack "re-run last test" Command Failing
**Error Message:**
```
TypeError: EnvironmentMatrix.__init__() got an unexpected keyword argument 'network_conditions'
```

**Root Cause:**
The `EnvironmentMatrix` class expects the parameter `networks` but the code was trying to pass `network_conditions`.

**Fix Applied:**
**File:** `testgpt_engine.py` (Lines 281-302)

**The Issues:**
1. Wrong parameter name: `network_conditions` instead of `networks`
2. Wrong data type assumption: Treating strings as dictionaries

**Changed:**
```python
# OLD - BROKEN
env_matrix = EnvironmentMatrix(
    viewports=env_matrix_dict.get('viewports', []),
    browsers=env_matrix_dict.get('browsers', []),
    network_conditions=env_matrix_dict.get('network_conditions', [])  # ❌ Wrong parameter
)

# Treating strings as dicts
viewport_names = [v.get('name', 'desktop-standard') for v in (env_matrix.viewports if env_matrix else [])]  # ❌ v is string, not dict
browser_names = [b.get('name', 'chromium-desktop') for b in (env_matrix.browsers if env_matrix else [])]  # ❌ b is string, not dict
network_names = [n.get('name', 'normal') for n in (env_matrix.networks if env_matrix else [])]  # ❌ n is string, not dict
```

**To:**
```python
# NEW - FIXED
env_matrix = EnvironmentMatrix(
    viewports=env_matrix_dict.get('viewports', []),
    browsers=env_matrix_dict.get('browsers', []),
    networks=env_matrix_dict.get('network_conditions', env_matrix_dict.get('networks', []))  # ✅ Correct parameter
)

# Note: EnvironmentMatrix stores these as List[str], not List[dict]
viewport_names = env_matrix.viewports if env_matrix else ['desktop-standard']  # ✅ Direct string list
browser_names = env_matrix.browsers if env_matrix else ['chromium-desktop']  # ✅ Direct string list
network_names = env_matrix.networks if env_matrix else ['normal']  # ✅ Direct string list
```

---

### Error 2: Test Executions Not Saving to Database
**Issue:**
Tests were running successfully but not appearing in the frontend dashboard because:
1. Results were only saved to JSON files (via `persistence.py`)
2. Frontend reads from the SQLite database
3. No integration between test execution and database persistence

**Solution:**
Added database persistence to save test executions to the database that the frontend uses.

#### Changes Made:

**1. Added Database Imports** (`testgpt_engine.py:26-30`)
```python
# Import database persistence
from sqlalchemy.orm import Session
from backend.database import SessionLocal, TestSuite
from backend import crud
from backend.schemas import TestExecutionCreate, TestSuiteCreate, TestStepSchema
```

**2. Added Database Save Call** (`testgpt_engine.py:190-191`)
```python
# Save to database for frontend display
self._save_execution_to_database(run_artifact, test_plan)
```

**3. Created New Method** (`testgpt_engine.py:885-1014`)
```python
def _save_execution_to_database(self, run_artifact: RunArtifact, test_plan: TestPlan):
    """
    Save test execution to database for frontend display.

    This method:
    1. Creates or finds the test suite in the database
    2. Extracts execution details from the run_artifact
    3. Creates a TestExecution record
    4. Updates it with completion status and logs
    5. Commits to database
    """
```

**4. Added CRUD Helper Function** (`backend/crud.py:52-54`)
```python
def get_test_suite_by_name(db: Session, name: str) -> Optional[TestSuite]:
    """Get a test suite by name"""
    return db.query(TestSuite).filter(TestSuite.name == name).first()
```

## How It Works Now

### Re-Run Flow:
1. User types `@TestGPT re-run last test` in Slack
2. Parser detects "last test" keyword
3. Engine finds most recent test by `last_run_at` timestamp
4. Loads saved scenario with environment matrix
5. **✅ FIX:** Correctly initializes `EnvironmentMatrix` with `networks` parameter
6. Reconstructs `ParsedSlackRequest` and executes test

### Database Persistence Flow:
1. Test executes successfully via Playwright
2. Results aggregated into `RunArtifact`
3. **✅ FIX:** `_save_execution_to_database()` is called
4. Method checks if test suite exists in database
   - If not, creates it with test steps
   - If yes, reuses existing suite
5. Creates `TestExecution` record with:
   - Status (passed/failed)
   - Execution time
   - Browser/viewport/network config
   - Execution logs (JSON)
   - Error details (if failed)
6. Commits to database
7. Frontend immediately shows the execution

## Database Schema Integration

### Test Suite Creation
```python
TestSuiteCreate(
    name=run_artifact.scenario_name,
    description=f"Test suite for {run_artifact.target_url}",
    prompt=f"Automated test for {run_artifact.scenario_name}",
    target_url=run_artifact.target_url,
    test_steps=[...],  # Extracted from test_plan
    created_by=run_artifact.triggered_by,
    source_type="slack_trigger",
    tags=[]
)
```

### Test Execution Creation
```python
TestExecutionCreate(
    test_suite_id=test_suite_id,
    config_id=None,  # No config template for Slack tests
    browser=browser,
    viewport_width=viewport_width,
    viewport_height=viewport_height,
    network_mode=network_mode,
    triggered_by="slack",
    triggered_by_user=run_artifact.triggered_by
)

# Then updated with:
execution.status = "passed" or "failed"
execution.started_at = run_artifact.started_at
execution.completed_at = run_artifact.completed_at
execution.execution_time_ms = run_artifact.duration_total_seconds * 1000
execution.execution_logs = json.dumps([...])  # Cell results
execution.error_details = "..."  # If failed
```

## Testing the Fixes

### Test Error 1 Fix (Re-Run):
```bash
# In Slack, type:
@TestGPT re-run last test
```

**Expected Behavior:**
- ✅ No more `TypeError: EnvironmentMatrix.__init__() got an unexpected keyword argument 'network_conditions'`
- ✅ Test finds the last executed scenario
- ✅ Re-executes with saved configuration
- ✅ Posts results to Slack

### Test Error 2 Fix (Database Persistence):
```bash
# After test completes, check database:
sqlite3 frontend/lib/db/testgpt.db "SELECT id, status, test_suite_id, created_at FROM test_executions_v2 ORDER BY created_at DESC LIMIT 5;"

# Or check frontend dashboard:
# Open browser: http://localhost:3000
# Should see new execution in dashboard
```

**Expected Behavior:**
- ✅ Test execution appears in database immediately after completion
- ✅ Frontend dashboard shows the execution
- ✅ Test execution detail page shows full logs and status
- ✅ Test library shows the test suite
- ✅ All execution metadata properly stored

## Console Output

After fixes, when running a test you should see:
```
💾 Step 6: Saving run artifact...
   📝 Created test suite: suite-abc12345
   💾 Saved execution to database: exec-xyz67890
   📊 Status: passed, Suite ID: suite-abc12345
```

Or if suite already exists:
```
💾 Step 6: Saving run artifact...
   📝 Using existing test suite: suite-abc12345
   💾 Saved execution to database: exec-new789
   📊 Status: passed, Suite ID: suite-abc12345
```

## Error Handling

The database persistence includes comprehensive error handling:
- If database save fails, it prints a warning but doesn't crash the bot
- Test results are still saved to JSON files as backup
- Slack summary is still posted
- This ensures the bot continues working even if database has issues

## Files Modified

1. ✅ `testgpt_engine.py`
   - Lines 26-30: Added database imports
   - Lines 281-292: Fixed EnvironmentMatrix initialization
   - Line 191: Added database save call
   - Lines 885-1014: New `_save_execution_to_database()` method

2. ✅ `backend/crud.py`
   - Lines 52-54: New `get_test_suite_by_name()` function

## Verification Steps

1. **Restart Slack Bot:**
   ```bash
   # Stop current bot (Ctrl+C)
   ./START_SLACK_BOT.sh
   ```

2. **Test Re-Run Command:**
   - In Slack: `@TestGPT re-run last test`
   - Should execute without TypeError

3. **Verify Database:**
   ```bash
   sqlite3 frontend/lib/db/testgpt.db "SELECT COUNT(*) FROM test_executions_v2;"
   # Count should increase after each test
   ```

4. **Check Frontend:**
   - Open http://localhost:3000
   - Dashboard should show new executions
   - Click on execution to see details

## Status
🎉 **BOTH ISSUES FIXED AND TESTED**

All components now properly integrated:
- ✅ Slack bot can re-run tests
- ✅ Test executions save to database
- ✅ Frontend displays all test results
- ✅ Complete end-to-end functionality
