# TestGPT Test Persistence - Quick Start Guide

## What Was Built

A complete test persistence and re-run capability system consisting of:

### Backend (Python + FastAPI)
- ✅ REST API server with 20+ endpoints
- ✅ SQLAlchemy database models
- ✅ CRUD operations for tests, configs, and executions
- ✅ Test runner service with configuration support
- ✅ 6 pre-seeded configuration templates

### Frontend (Next.js + TypeScript)
- ✅ Test Library page - View all saved tests
- ✅ Test Details page - View test info and history
- ✅ Test Runner page - Execute tests with custom configs
- ✅ API client for backend communication

### Database Schema
- ✅ `test_suites` - Saved test scenarios
- ✅ `configuration_templates` - Reusable configs
- ✅ `test_executions_v2` - Execution records
- ✅ `execution_steps` - Step-level results

## Installation (5 minutes)

### Step 1: Setup
```bash
# Navigate to project
cd /Users/akashsingh/Desktop/TestGPT

# Run setup script
bash setup_persistence.sh
```

This will:
- Install SQLAlchemy and dependencies
- Initialize SQLite database
- Create 6 default configuration templates
- Setup frontend dependencies

### Step 2: Start Backend
```bash
# Terminal 1: Start API server
bash start_backend.sh
```

Server will start at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Step 3: Start Frontend
```bash
# Terminal 2: Start Next.js
cd frontend
npm run dev
```

Frontend will start at:
- Dashboard: http://localhost:3000
- Test Library: http://localhost:3000/test-library

### Step 4: Verify Installation
```bash
# Terminal 3: Test API
python test_backend_api.py
```

Should see: "✅ ALL TESTS PASSED!"

## Usage Examples

### 1. Create a Test Suite via API

```bash
curl -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Homepage Signup Test",
    "description": "Test user signup flow",
    "prompt": "Test signup on example.com",
    "target_url": "https://example.com",
    "test_steps": [
      {
        "step_number": 1,
        "action": "navigate",
        "target": "https://example.com",
        "expected_outcome": "Page loads"
      }
    ],
    "tags": ["signup", "smoke"]
  }'
```

### 2. List All Test Suites

```bash
curl http://localhost:8000/api/tests
```

### 3. Run a Test

```bash
curl -X POST http://localhost:8000/api/tests/{test_id}/run \
  -H "Content-Type: application/json" \
  -d '{
    "browser": "chrome",
    "viewport_width": 1920,
    "viewport_height": 1080,
    "network_mode": "online",
    "triggered_by": "manual"
  }'
```

### 4. Use Frontend UI

1. Open http://localhost:3000/test-library
2. Click "Create New Test" or view existing tests
3. Click on a test to see details and history
4. Click "Run" to execute with custom configuration
5. Select browser, viewport, network conditions
6. Click "Run Test" - redirects to execution page

### 5. View Configuration Templates

```bash
curl http://localhost:8000/api/configs
```

Default templates:
- **Regression Suite** - Comprehensive cross-browser testing
- **Smoke Tests** - Quick desktop-only validation
- **Mobile Testing** - Mobile viewports with network conditions
- **Cross-Browser** - All browsers, standard viewport
- **Performance Testing** - Network condition focus with video
- **Quick Debug** - Single config for debugging

## Key Files Created

```
TestGPT/
├── backend/
│   ├── database.py              # SQLAlchemy models
│   ├── schemas.py               # Pydantic request/response models
│   ├── crud.py                  # Database operations
│   ├── test_runner_service.py   # Test execution with configs
│   ├── seed_data.py             # Database initialization
│   └── api/
│       └── main.py              # FastAPI server
│
├── frontend/
│   ├── lib/
│   │   └── api/
│   │       └── client.ts        # API client
│   └── app/(dashboard)/
│       └── test-library/        # Test management UI
│           ├── page.tsx         # List view
│           ├── [testId]/
│           │   ├── page.tsx     # Details view
│           │   └── run/
│           │       └── page.tsx # Run config UI
│
├── setup_persistence.sh         # Setup script
├── start_backend.sh             # Backend startup script
├── test_backend_api.py          # API test suite
└── PERSISTENCE_AND_RERUN_IMPLEMENTATION.md
```

## Configuration File Example

Create `testgpt.config.yml`:

```yaml
test_suites:
  regression:
    browsers: [chrome, firefox, safari]
    viewports:
      - mobile: { width: 375, height: 667 }
      - desktop: { width: 1920, height: 1080 }
    network_modes: [online, slow3g]

default_timeout: 30000
screenshot_on_failure: true
```

## Integration with Existing TestGPT

### Save Tests from Slack

In `testgpt_engine.py` or `main.py`:

```python
from backend.database import SessionLocal
from backend.crud import create_test_suite
from backend.schemas import TestSuiteCreate

# After generating test
db = SessionLocal()

suite = TestSuiteCreate(
    name=scenario_name,
    prompt=user_message,
    target_url=target_url,
    test_steps=steps,
    created_by=slack_user_id,
    source_type="slack_trigger",
    tags=["slack"]
)

db_suite = create_test_suite(db, suite)
db.close()

# Return test ID to user
return f"Test saved! ID: {db_suite.id}"
```

### Re-run from Slack

```python
# Parse "re-run [test name]" command
if message.startswith("re-run"):
    test_name = message.replace("re-run", "").strip()

    # Find test
    suites = crud.get_test_suites(db, search=test_name, limit=1)

    if suites:
        # Execute test
        execution = await runner.execute_test_with_config(
            execution_id,
            test_suite_dict,
            config_dict
        )
```

## API Endpoints Reference

### Test Suites
- `POST /api/tests` - Create test suite
- `GET /api/tests` - List test suites (with filters)
- `GET /api/tests/{id}` - Get test details
- `PUT /api/tests/{id}` - Update test
- `DELETE /api/tests/{id}` - Delete test

### Configurations
- `POST /api/configs` - Create config template
- `GET /api/configs` - List configs
- `GET /api/configs/{id}` - Get config
- `PUT /api/configs/{id}` - Update config
- `DELETE /api/configs/{id}` - Delete config

### Executions
- `POST /api/tests/{id}/run` - Run test
- `GET /api/executions` - List executions
- `GET /api/executions/{id}` - Get execution details
- `GET /api/tests/{id}/history` - Get test history
- `POST /api/tests/batch/run` - Run multiple tests

### Statistics
- `GET /api/statistics` - Get overall statistics

## Troubleshooting

### Backend won't start
```bash
# Check dependencies
pip install sqlalchemy alembic

# Reinitialize database
python backend/seed_data.py
```

### Frontend won't connect
```bash
# Check backend is running
curl http://localhost:8000/health

# Set API URL if needed
export NEXT_PUBLIC_API_URL=http://localhost:8000
cd frontend && npm run dev
```

### Tests not executing
```bash
# Check MCP server
npx playwright install

# Check logs
cat logs/latest.log
```

## Next Steps

1. **Integrate with Slack**: Modify `main.py` to save tests after creation
2. **Add authentication**: Implement JWT tokens for API security
3. **Add scheduling**: Cron-like test scheduling
4. **Visual regression**: Screenshot comparison
5. **Performance tracking**: Monitor execution times

## Documentation

Full documentation: [PERSISTENCE_AND_RERUN_IMPLEMENTATION.md](PERSISTENCE_AND_RERUN_IMPLEMENTATION.md)

## Support

- API Docs: http://localhost:8000/docs
- Issues: Check logs in `logs/` directory
- Database: `frontend/lib/db/testgpt.db`

---

**Status**: ✅ Implementation complete and ready to use!
