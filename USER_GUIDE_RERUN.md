# TestGPT: Viewing Past Runs and Re-running Tests

**Complete Guide to Test Storage and Re-run Features**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [View Past Test Runs](#view-past-test-runs)
3. [Re-run Tests](#re-run-tests)
4. [Advanced Features](#advanced-features)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

TestGPT automatically saves every test you run. Here's the fastest way to view and re-run:

**Frontend (Recommended):**
1. Open http://localhost:3000/test-library
2. Click any test to see details and history
3. Click "Run" to re-run

**Slack:**
```
@TestGPT list scenarios
@TestGPT re-run [test name]
```

**API:**
```bash
# List all tests
curl http://localhost:8000/api/tests

# Re-run a test
curl -X POST http://localhost:8000/api/tests/{test_id}/run \
  -H "Content-Type: application/json" \
  -d '{"triggered_by": "manual"}'
```

---

## View Past Test Runs

### Method 1: Frontend Dashboard (Best for Browsing)

#### Test Library
**URL:** http://localhost:3000/test-library

**What you'll see:**
- All saved test suites in card format
- Test name, URL, and description
- Tags (e.g., "login", "authentication")
- Creation date and last run time
- Quick actions: View and Run buttons

**Features:**
- Search tests by name or URL
- Filter by tags
- Sort by date created/last run
- Paginated results

#### Test Executions Page
**URL:** http://localhost:3000/test-executions

**What you'll see:**
- All test execution history
- Status badges (Pending, Running, Passed, Failed)
- Execution time
- Trigger source (Slack, GitHub, Manual)
- GitHub PR info (if applicable)
- Error messages (for failed tests)

#### Individual Test Details
**URL:** http://localhost:3000/test-library/{test_id}

**What you'll see:**
- Complete test steps with actions and expected outcomes
- Full execution history timeline
- Pass/fail statistics
- Configuration used
- Screenshots and videos (if captured)
- Re-run button with configuration options

---

### Method 2: API (Best for Automation)

#### List All Test Suites

```bash
curl http://localhost:8000/api/tests
```

**Response:**
```json
[
  {
    "id": "suite-7b8b4a5c",
    "name": "API Test Suite - Login Flow",
    "description": "Test suite created via API for testing storage",
    "target_url": "https://example.com/login",
    "created_at": "2025-11-01T02:43:44.123Z",
    "last_run": "2025-11-01T02:43:45.456Z",
    "tags": ["login", "authentication", "api-test"]
  }
]
```

**Filters available:**
```bash
# Search by name
curl "http://localhost:8000/api/tests?search=login"

# Filter by tags
curl "http://localhost:8000/api/tests?tags=authentication,login"

# Pagination
curl "http://localhost:8000/api/tests?skip=0&limit=10"
```

#### Get Test Details

```bash
curl http://localhost:8000/api/tests/{test_id}
```

**Response includes:**
- Full test configuration
- All test steps with actions and targets
- Metadata (created_by, source_type, tags)

#### View Execution History

```bash
curl http://localhost:8000/api/tests/{test_id}/history
```

**Response:**
```json
{
  "test_suite_id": "suite-7b8b4a5c",
  "test_suite_name": "API Test Suite - Login Flow",
  "executions": [
    {
      "id": "exec-2f8e2f68",
      "status": "pending",
      "started_at": "2025-11-01T02:43:45.123Z",
      "completed_at": "2025-11-01T02:43:47.456Z",
      "execution_time_ms": 2333,
      "browser": "chrome",
      "triggered_by": "manual"
    }
  ],
  "total_runs": 1,
  "passed_runs": 0,
  "failed_runs": 0
}
```

#### List All Executions

```bash
curl http://localhost:8000/api/executions
```

**Filters available:**
```bash
# By status
curl "http://localhost:8000/api/executions?status=passed"

# By test suite
curl "http://localhost:8000/api/executions?test_suite_id=suite-7b8b4a5c"

# Recent executions
curl "http://localhost:8000/api/executions?limit=10"
```

#### Get Execution Details

```bash
curl http://localhost:8000/api/executions/{execution_id}
```

**Response includes:**
- Execution status and timing
- Browser and configuration used
- Screenshots and videos
- Error details (if failed)
- Complete execution logs

#### Get Statistics

```bash
curl http://localhost:8000/api/statistics
```

**Response:**
```json
{
  "total_test_suites": 1,
  "total_executions": 1,
  "passed_executions": 0,
  "failed_executions": 0,
  "running_executions": 0,
  "average_execution_time_ms": null,
  "most_run_test": {
    "id": "suite-7b8b4a5c",
    "name": "API Test Suite - Login Flow",
    "run_count": 1
  },
  "recent_failures": []
}
```

---

### Method 3: Slack (Best for Quick Checks)

#### List Saved Tests

```
@TestGPT list scenarios
```

**Bot responds with:**
- List of all saved test scenarios
- Scenario IDs and names
- Quick re-run instructions

#### View Test Details

```
@TestGPT show test [test_name]
@TestGPT test details [scenario_id]
```

---

### Method 4: Database (Best for Advanced Queries)

#### Connect to Database

```bash
sqlite3 frontend/lib/db/testgpt.db
```

#### Useful Queries

**List all test suites:**
```sql
SELECT id, name, target_url, created_at
FROM test_suites
ORDER BY created_at DESC;
```

**View execution history:**
```sql
SELECT
    e.id,
    e.status,
    e.execution_time_ms,
    e.browser,
    e.created_at,
    s.name as test_name
FROM test_executions_v2 e
LEFT JOIN test_suites s ON e.test_suite_id = s.id
ORDER BY e.created_at DESC
LIMIT 10;
```

**Get test statistics:**
```sql
SELECT
    s.id,
    s.name,
    COUNT(e.id) as total_runs,
    SUM(CASE WHEN e.status = 'passed' THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN e.status = 'failed' THEN 1 ELSE 0 END) as failed,
    AVG(e.execution_time_ms) as avg_time_ms
FROM test_suites s
LEFT JOIN test_executions_v2 e ON s.id = e.test_suite_id
GROUP BY s.id
ORDER BY total_runs DESC;
```

---

## Re-run Tests

### Method 1: Frontend (Recommended)

#### From Test Library Page

1. Go to http://localhost:3000/test-library
2. Find your test in the grid
3. Click the **"Run"** button
4. Test executes with last used configuration
5. View results immediately

#### From Test Details Page

1. Go to http://localhost:3000/test-library/{test_id}
2. Review test steps and history
3. Click **"Re-run Test"** button
4. **Optional:** Click "Configure" to change settings:
   - Browser (Chrome, Firefox, Safari, Edge)
   - Viewport (Desktop, Tablet, Mobile)
   - Network (Online, Fast 3G, Slow 3G)
5. Click "Run"
6. Watch real-time status updates
7. View results when complete

#### Batch Re-run Multiple Tests

1. Go to http://localhost:3000/test-library
2. Select multiple tests using checkboxes
3. Click "Run Selected Tests"
4. Choose configuration template
5. Monitor progress (X of Y completed)
6. View individual results

---

### Method 2: API (Recommended for Automation)

#### Basic Re-run

```bash
curl -X POST http://localhost:8000/api/tests/{test_id}/run \
  -H "Content-Type: application/json" \
  -d '{
    "triggered_by": "manual"
  }'
```

**Response:**
```json
{
  "id": "exec-abc123",
  "test_suite_id": "suite-7b8b4a5c",
  "status": "pending",
  "browser": "chrome",
  "triggered_by": "manual",
  "created_at": "2025-11-01T02:43:44.123Z"
}
```

#### Re-run with Custom Configuration

```bash
curl -X POST http://localhost:8000/api/tests/{test_id}/run \
  -H "Content-Type: application/json" \
  -d '{
    "browser": "firefox",
    "viewport_width": 768,
    "viewport_height": 1024,
    "network_mode": "slow3g",
    "triggered_by": "manual",
    "triggered_by_user": "john@example.com"
  }'
```

**Available options:**
- `browser`: "chrome", "firefox", "safari", "edge"
- `viewport_width`: Number (e.g., 1920, 768, 375)
- `viewport_height`: Number (e.g., 1080, 1024, 667)
- `network_mode`: "online", "fast3g", "slow3g"
- `config_id`: ID of saved configuration template (optional)
- `triggered_by`: "manual", "slack", "github"
- `triggered_by_user`: String (optional, for tracking)

#### Batch Re-run

```bash
curl -X POST http://localhost:8000/api/tests/batch/run \
  -H "Content-Type: application/json" \
  -d '{
    "test_suite_ids": ["suite-abc123", "suite-def456", "suite-ghi789"],
    "config_id": "config-xyz",
    "triggered_by": "manual"
  }'
```

**Response:**
```json
{
  "batch_id": "batch-exec-123",
  "execution_ids": ["exec-1", "exec-2", "exec-3"],
  "total_tests": 3,
  "status": "pending"
}
```

#### Monitor Execution

```bash
# Poll for status updates
curl http://localhost:8000/api/executions/{execution_id}
```

**Status progression:**
1. `pending` - Queued for execution
2. `running` - Currently executing
3. `passed` - Completed successfully
4. `failed` - Completed with failures

---

### Method 3: Slack (Recommended for Quick Re-runs)

#### Basic Re-run

```
@TestGPT re-run [test name]
@TestGPT rerun [test name]
@TestGPT run [test name] again
```

**Example:**
```
@TestGPT re-run login test
@TestGPT re-run scenario-abc123
```

**Bot responds with:**
- Confirmation that test is starting
- Real-time progress updates
- Final results with pass/fail status
- Link to view full results

#### Re-run with Configuration

```
@TestGPT re-run [test name] browser:firefox
@TestGPT re-run [test name] viewport:mobile
@TestGPT re-run [test name] network:slow3g
```

**Example:**
```
@TestGPT re-run checkout flow browser:firefox viewport:tablet network:slow3g
```

#### Re-run Last Test

```
@TestGPT re-run last test
@TestGPT run again
```

#### Re-run All Failed Tests

```
@TestGPT re-run all failed tests
@TestGPT re-run failures
```

---

## Advanced Features

### Configuration Templates

Create reusable configuration templates for consistent test execution.

#### Via API

**Create configuration:**
```bash
curl -X POST http://localhost:8000/api/configs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile Testing Config",
    "description": "Configuration for mobile device testing",
    "browsers": ["chrome", "safari"],
    "viewports": [
      {"width": 375, "height": 667, "device_name": "iPhone SE"},
      {"width": 414, "height": 896, "device_name": "iPhone 11"}
    ],
    "network_modes": ["online", "fast3g"],
    "screenshot_on_failure": true,
    "video_recording": false,
    "parallel_execution": true,
    "max_workers": 4,
    "default_timeout": 30000
  }'
```

**List configurations:**
```bash
curl http://localhost:8000/api/configs
```

**Use configuration when re-running:**
```bash
curl -X POST http://localhost:8000/api/tests/{test_id}/run \
  -H "Content-Type: application/json" \
  -d '{
    "config_id": "config-abc123",
    "triggered_by": "manual"
  }'
```

### Execution History Analysis

#### Compare Multiple Runs

```bash
# Get history
curl http://localhost:8000/api/tests/{test_id}/history?limit=10

# Compare execution times
# Compare pass/fail rates
# Identify flaky tests
```

#### Track Performance Over Time

```sql
-- Database query for performance trends
SELECT
    DATE(created_at) as date,
    AVG(execution_time_ms) as avg_time,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed
FROM test_executions_v2
WHERE test_suite_id = 'suite-abc123'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Scheduled Re-runs (Coming Soon)

```bash
# Schedule daily re-run
curl -X POST http://localhost:8000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "test_suite_id": "suite-abc123",
    "cron": "0 9 * * *",
    "config_id": "config-xyz"
  }'
```

---

## Troubleshooting

### Test Not Showing in Library

**Check if test was actually stored:**
```bash
curl http://localhost:8000/api/tests | grep "test_name"
```

**Common causes:**
- Test failed before completion
- Storage not configured correctly
- Database connection issue

**Solution:**
```bash
# Run database health check
python scripts/db_health_check.py

# Check logs
tail -f logs/latest.log
```

### Re-run Not Working

**Check test exists:**
```bash
curl http://localhost:8000/api/tests/{test_id}
```

**Check API server is running:**
```bash
curl http://localhost:8000/health
```

**Common causes:**
- Invalid test_id
- API server not running
- Configuration error

**Solution:**
```bash
# Restart API server
pkill -f "uvicorn backend.api.main"
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload &

# Verify
curl http://localhost:8000/health
```

### Execution Stuck in "Running" State

**Check execution status:**
```bash
curl http://localhost:8000/api/executions/{execution_id}
```

**Common causes:**
- Background task crashed
- Browser/Playwright issue
- Network timeout

**Solution:**
```bash
# Check execution logs
sqlite3 frontend/lib/db/testgpt.db "SELECT * FROM test_executions_v2 WHERE id = 'exec-abc123';"

# Manually mark as failed if needed
sqlite3 frontend/lib/db/testgpt.db "UPDATE test_executions_v2 SET status = 'failed', error_details = 'Timeout' WHERE id = 'exec-abc123';"
```

### Frontend Not Displaying Tests

**Check API connection:**
```bash
curl http://localhost:8000/api/tests
```

**Check frontend is running:**
```bash
curl http://localhost:3000
```

**Common causes:**
- API server not running on port 8000
- Frontend not running on port 3000
- CORS issues

**Solution:**
```bash
# Start API server
cd /Users/akashsingh/Desktop/TestGPT
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload &

# Start frontend
cd frontend
npm run dev &

# Verify both running
curl http://localhost:8000/health
curl http://localhost:3000
```

### Slack Commands Not Working

**Check bot is running:**
```bash
ps aux | grep slack_agent
```

**Check re-run pattern:**
```
# These work:
@TestGPT re-run test-name
@TestGPT rerun test-name
@TestGPT run test-name again

# These don't work:
@TestGPT re run test-name (space in "re run")
@TestGPT restart test-name (use "re-run" instead)
```

---

## Best Practices

### Naming Tests

**Good names:**
- "Login Flow - Desktop Chrome"
- "Checkout Process - Mobile Safari"
- "Homepage Load - Slow Network"

**Bad names:**
- "Test 1"
- "New test"
- "Untitled"

### Organizing with Tags

```bash
# Create test with tags
curl -X POST http://localhost:8000/api/tests \
  -d '{
    "name": "Login Test",
    "tags": ["authentication", "critical", "smoke-test", "frontend"]
  }'

# Find all authentication tests
curl "http://localhost:8000/api/tests?tags=authentication"
```

### Regular Re-runs

**Daily smoke tests:**
```bash
# Get all tests tagged "smoke-test"
# Re-run them daily
# Monitor pass rate
```

**After deployments:**
```bash
# Get all tests tagged "critical"
# Re-run immediately after deploy
# Block deploy if failures
```

---

## API Reference Quick Links

### Test Management
- `GET /api/tests` - List all tests
- `POST /api/tests` - Create new test
- `GET /api/tests/{id}` - Get test details
- `PUT /api/tests/{id}` - Update test
- `DELETE /api/tests/{id}` - Delete test

### Test Execution
- `POST /api/tests/{id}/run` - Run/re-run test
- `POST /api/tests/batch/run` - Batch re-run
- `GET /api/executions` - List executions
- `GET /api/executions/{id}` - Get execution details
- `GET /api/tests/{id}/history` - Get test history

### Configuration
- `GET /api/configs` - List configurations
- `POST /api/configs` - Create configuration
- `GET /api/configs/{id}` - Get configuration
- `PUT /api/configs/{id}` - Update configuration
- `DELETE /api/configs/{id}` - Delete configuration

### Statistics
- `GET /api/statistics` - Get overall statistics

### Health
- `GET /health` - Check API health

---

## Support

**Documentation:** `/VALIDATION_REPORT.md`
**Database Health Check:** `python scripts/db_health_check.py`
**API Test Suite:** `python scripts/test_api_endpoints.py`

**Questions?** Check the validation report for detailed system status and troubleshooting tips.

---

**Last Updated:** November 1, 2025
**Version:** 1.0.0
**Status:** ✅ 100% Operational (12/12 tests passing)
