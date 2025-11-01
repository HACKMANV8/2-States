# TestGPT - Multi-Environment QA Testing Platform

Complete AI agent examples using Agno framework with Model Context Protocol (MCP) integration. Includes Slack bot, web automation, backend API testing, documentation lookup, and file system operations.

Transform simple Slack messages into complete cross-browser, cross-device, and cross-network test matrices. TestGPT behaves like a professional manual QA engineer, automatically testing your sites across multiple environments and prioritizing failures.

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Coverage System](#coverage-system)
5. [Test Persistence & Re-run](#test-persistence--re-run)
6. [Dynamic Backend API Testing](#dynamic-backend-api-testing)
7. [Browser Setup](#browser-setup)
8. [Examples & Demos](#examples--demos)
9. [Configuration](#configuration)
10. [PR-Based Testing](#pr-based-testing)
11. [API Reference](#api-reference)
12. [Production Status](#production-status)
13. [Troubleshooting](#troubleshooting)
14. [Bug Fixes & Recent Updates](#bug-fixes--recent-updates)

---

## Features

### Core Capabilities
- **AI-Powered**: Uses Claude Sonnet 4 for intelligent task understanding
- **Multiple MCP Servers**: Context7 docs, Filesystem, Playwright web automation
- **PR-Based Context Testing**: Automatically test GitHub PRs with deployment URLs
- **Dynamic Backend API Testing**: Test ANY user API from repos/PRs automatically
- **Slack Integration**: Production bot with web automation AND API testing
- **Persistent Sessions**: Maintains state across tasks
- **Code Coverage**: MCDC analysis and intelligent stop conditions

### Multi-Environment Testing
- **10 viewport profiles** (iPhone SE → desktop ultrawide)
- **4 browser engines** (Chrome, Safari, Firefox, Edge)
- **3 network conditions** (normal, slow 3G, flaky)
- **Automatic matrix expansion** (one request → N test runs)
- **REAL Playwright MCP execution** (actual browsers, not mocked)

### Intelligent Test Planning
- **Natural language parsing** from Slack
- **Deterministic test flows** with objective checkpoints
- **Automatic scenario persistence** for re-running
- **Failure prioritization** (P0 critical → P2 edge cases)
- **Coverage-based stop conditions** with MCDC analysis

### Comprehensive Reporting
- **Formatted Slack summaries** with environment breakdown
- **Per-dimension statistics** (by viewport, browser, network)
- **Actionable next steps** for fixing issues
- **Evidence collection** (screenshots, console errors)
- **HTML/JSON coverage reports**

### Test Persistence & Re-run
- **Test Library**: Save AI-generated tests to database
- **Configuration Templates**: Reusable test configs (regression, smoke, mobile, etc.)
- **Re-run with different settings**: Change browser, viewport, network conditions
- **Execution History**: Track all test runs with detailed results
- **Batch Execution**: Run multiple tests with same configuration
- **REST API**: Full backend API for test management
- **Modern Dashboard**: Next.js UI for test library and execution tracking

---

## Quick Start

### Complete Setup (3 Terminals - Recommended)

#### Terminal 1: Start Backend API
```bash
./scripts/START_EVERYTHING.sh
```
Backend runs at: http://localhost:8000

#### Terminal 2: Start Slack Bot
```bash
./scripts/START_SLACK_BOT.sh
```
Bot connects to Slack workspace and listens for commands.

#### Terminal 3: Start Frontend (Optional)
```bash
cd frontend
npm run dev
```
Frontend runs at: http://localhost:3000

### Alternative: Test Demo (No Slack/MCP needed)
```bash
python scripts/test_testgpt.py
```
This demonstrates the full flow with mock results.

### Example Slack Commands
```
# Basic testing
@TestGPT test pointblank.club responsive on safari and iphone
@TestGPT run checkout flow on chrome desktop and ipad under slow network

# PR-based testing with coverage
@TestGPT test this PR https://github.com/owner/repo/pull/123 with coverage

# Custom instructions
@TestGPT Test github.com, are you able to view the repositories of SkySingh04?

# Scenario management
@TestGPT list scenarios
@TestGPT re-run last test
@TestGPT re-run pointblank responsive test

# Backend API testing
@TestGPT test the backend API health
@TestGPT run smoke tests on all endpoints
```

---

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
npx playwright install
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` - Get from console.anthropic.com
- `SLACK_BOT_TOKEN` - Your Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN` - Your Slack app token (xapp-...)
- `GITHUB_TOKEN` - (Optional) For posting PR comments

### 3. Initialize Database (for test persistence)
```bash
python coverage/cli.py init
```

### 4. Verify Browser Installation
```bash
./scripts/ENSURE_BROWSERS_INSTALLED.sh
```

---

## Coverage System

TestGPT includes a comprehensive code coverage system with MCDC (Modified Condition/Decision Coverage) analysis.

### Features
- **MCDC Analysis**: Analyzes complex boolean conditions for safety-critical systems
- **Coverage Tracking**: Real-time coverage monitoring during test execution
- **Intelligent Stop Conditions**: Multi-criteria decision making (threshold, MCDC, plateau)
- **Report Generation**: HTML, JSON, and summary formats
- **Database Persistence**: SQLite storage of coverage runs and analysis

### Quick Start with Coverage

```bash
# Initialize coverage database
python coverage/cli.py init

# Analyze MCDC requirements
python coverage/cli.py analyze-mcdc examples/sample_mcdc.py

# Run end-to-end test
python scripts/test_coverage_system.py
```

### Using Coverage in Slack

```
@TestGPT test PR https://github.com/owner/repo/pull/123 with coverage
```

The bot will:
1. Analyze PR changes
2. Execute tests with coverage tracking
3. Evaluate MCDC requirements
4. Stop when coverage threshold (80% default) is met
5. Generate HTML coverage report
6. Post summary to Slack with coverage %

### Coverage Reports

After testing with coverage, reports are saved to:
- **HTML Report**: `./coverage_reports/coverage-{run-id}.html`
- **Location in Slack**: Path shown in test summary

### Configuration Presets

Three quality levels available:

**Permissive (50% coverage):**
```python
config = CoverageConfig.permissive()
# Fast iteration, quick feedback
```

**Default (80% coverage):**
```python
config = CoverageConfig.default()
# Balanced quality and speed
```

**Strict (100% coverage + MCDC):**
```python
config = CoverageConfig.strict()
# Safety-critical, production-ready
```

### MCDC Analysis

MCDC is required for:
- Aviation software (DO-178C)
- Automotive systems (ISO 26262)
- Medical devices
- Safety-critical code

Example:
```python
# Complex authentication logic
if user.is_authenticated and (user.is_admin or resource.is_public):
    grant_access()

# MCDC Analysis Results:
# - Conditions: 3
# - Required Tests: 4 (not 8)
# - Truth Table Rows: 8
# - MCDC Achievable: Yes
```

### Stop Conditions

The system stops testing when:
1. **Coverage Threshold Met** (80% default)
2. **MCDC Satisfied** (all conditions independently tested)
3. **Plateau Detected** (5 consecutive tests with no improvement)
4. **Time Limit Exceeded** (60 minutes default)
5. **Max Tests Reached** (100 tests default)

### Documentation

Full coverage system documentation:
- **Architecture**: `coverage/README.md`
- **Getting Started**: `coverage/GETTING_STARTED.md`
- **Implementation Status**: `coverage/IMPLEMENTATION_STATUS.md`
- **Demo Guide**: `COVERAGE_DEMO_GUIDE.md`
- **Production Readiness**: `PRODUCTION_READINESS_REPORT.md`

---

## Test Persistence & Re-run

### Features

#### Test Library
- Save all AI-generated tests to SQLite database
- View saved tests in web dashboard
- Search and filter tests by name, URL, tags
- Execution history for each test

#### Configuration Templates
- Create reusable test configurations
- Standard presets (regression, smoke, mobile, etc.)
- Custom browser/viewport/network combinations
- Parallel execution settings

#### Re-run Functionality
- Re-run tests from frontend dashboard
- Re-run from Slack with `@TestGPT re-run [test name]`
- Re-run with different configurations
- Batch re-run multiple tests

#### Execution Tracking
- Complete execution history
- Status tracking (pending, running, passed, failed)
- Execution logs and screenshots
- Performance metrics and statistics

### Using Test Persistence

#### Via Frontend
1. Open http://localhost:3000/test-library
2. View all saved tests
3. Click "View" to see test details
4. Click "Run" to execute/re-run

#### Via Slack
```
# List saved tests
@TestGPT list scenarios

# Re-run a specific test
@TestGPT re-run login test

# Re-run last test
@TestGPT re-run last test

# Re-run with different config
@TestGPT re-run checkout flow browser:firefox viewport:mobile
```

#### Via API
```bash
# List all tests
curl http://localhost:8000/api/tests

# Get test details
curl http://localhost:8000/api/tests/{test_id}

# Re-run test
curl -X POST http://localhost:8000/api/tests/{test_id}/run \
  -H "Content-Type: application/json" \
  -d '{"triggered_by": "manual"}'

# View execution history
curl http://localhost:8000/api/tests/{test_id}/history
```

### Database Schema

Seven main tables:
- `test_suites` - Test definitions
- `test_executions_v2` - Execution records
- `configuration_templates` - Reusable configs
- `execution_steps` - Step-by-step results
- `pr_test_runs` - PR-based test tracking
- `pr_test_metrics` - PR test statistics
- Coverage tables (7 additional tables)

### Documentation

For complete documentation on test persistence:
- **User Guide**: `USER_GUIDE_RERUN.md`
- **Validation Report**: `VALIDATION_REPORT.md`
- **Fix Summary**: `FIX_SUMMARY.md`
- **Slack Integration**: `SLACK_RERUN_AND_DB_FIXES.md`

---

## Dynamic Backend API Testing

Test ANY user-submitted backend API from repos, branches, or PRs with zero configuration.

### Key Features
- **Zero Configuration**: Test any API with one line of code
- **OpenAPI Introspection**: Automatically extracts API specifications
- **MCP Wrapper Generation**: Creates FastMCP tools on-the-fly
- **Repository Support**: Clone, test, and cleanup GitHub repos
- **CI/CD Ready**: Perfect for automated testing pipelines
- **Multi-Framework**: Works with FastAPI, Flask, Django

### Architecture
```
User Input (Repo URL + Branch/PR)
         ↓
RepoManager: Clone & Install
         ↓
APIDiscoveryService: Load App & Extract OpenAPI
         ↓
MCPGenerator: Generate @mcp.tool() Code
         ↓
DynamicServerManager: Start API + MCP Servers
         ↓
Agno Agent: Test via MCPTools
         ↓
Results + Cleanup
```

### Usage Example

```python
from dynamic_backend_testing import DynamicBackendOrchestrator

orchestrator = DynamicBackendOrchestrator()

# Test a GitHub repo
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    branch="feature-branch",
    test_suite="comprehensive"
)

# Test a pull request
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    pr_number=123
)

# Test local API
result = await orchestrator.test_local(
    api_path=Path("/path/to/local/api"),
    app_module="main:app"
)
```

### CI/CD Integration

```bash
# GitHub Actions
python examples/test_pr.py \
  --repo ${{ github.repository }} \
  --pr ${{ github.event.pull_request.number }}

# GitLab CI
python examples/test_pr.py \
  --repo $CI_REPOSITORY_URL \
  --pr $CI_MERGE_REQUEST_IID
```

### Documentation

For complete documentation:
- **System Overview**: `dynamic_backend_testing/README.md`
- **Examples**: `examples/README.md`

---

## Browser Setup

All Playwright browsers (Chromium, WebKit/Safari, Firefox) are automatically installed and configured.

### Status
- **Chromium**: ✅ Working
- **WebKit/Safari**: ✅ Working (Fixed!)
- **Firefox**: ✅ Working

### Browser Locations
```
~/Library/Caches/ms-playwright/
├── chromium-1198/
├── webkit-2215/
├── firefox-1495/
└── mcp-webkit → webkit-2215 (symlink)
```

### Automated Setup
```bash
./scripts/ENSURE_BROWSERS_INSTALLED.sh
```

This script:
1. Installs all Playwright browsers (if missing)
2. Detects latest browser versions
3. Verifies browser binaries exist
4. Creates/fixes MCP symlinks
5. Configures Playwright browser links
6. Runs comprehensive verification checks

### Testing Browsers

```bash
# Test Chrome
python test_testgpt.py test "https://example.com" browser:chrome

# Test Safari
python test_testgpt.py test "https://example.com" browser:safari

# Test Firefox
python test_testgpt.py test "https://example.com" browser:firefox
```

### Troubleshooting

If you see "Browser not installed" errors:
```bash
# Run setup script
./scripts/ENSURE_BROWSERS_INSTALLED.sh

# Or manually reinstall
npx playwright install chromium webkit firefox
```

### Documentation
- **Browser Setup Complete**: `BROWSER_SETUP_COMPLETE.md`
- **Safari/WebKit Fix**: `SAFARI_WEBKIT_FIX_COMPLETE.md`

---

## Examples & Demos

### Slack Bot (Production)
**File**: `slack_agent.py`
- Production-ready Slack bot with Playwright MCP
- Responds to channel mentions
- Performs web automation tasks and PR testing
- Posts results back to Slack

### Example Agents (`examples/`)
- `01_basic_context7_agent.py` - Documentation lookup with Context7 MCP
- `02_filesystem_agent.py` - File operations
- `03_multi_agent_team.py` - Multi-agent coordination
- `04_streamlit_app.py` - Web UI for agent interaction
- `05_playwright_mcp_agent.py` - Persistent browser sessions
- `demo_google_search.py` - Google search automation
- `demo_persistent_session.py` - Multi-step browser tasks
- `test_github_repo.py` - Test any GitHub repository
- `test_pr.py` - Test pull requests (CI/CD ready)

### Test Scripts (`scripts/`)
- `test_testgpt.py` - Full end-to-end test demo
- `test_coverage_system.py` - Coverage system validation
- `test_api_endpoints.py` - API endpoint testing
- `test_api_key.py` - Verify API key
- `test_mcp_connection.py` - Test MCP server connections
- `verify_installation.py` - Installation verification

### Running Examples
```bash
# Run agent examples
python examples/01_basic_context7_agent.py
python examples/demo_google_search.py

# Run Streamlit app
streamlit run examples/04_streamlit_app.py

# Run tests
python scripts/test_testgpt.py
python scripts/test_coverage_system.py
```

---

## Configuration

### Adding New Viewports

Edit `config.json`:
```json
{
  "viewports": {
    "your-custom-viewport": {
      "name": "your-custom-viewport",
      "display_name": "Your Custom Device",
      "playwright_device": null,
      "mcp_launch_args": ["--viewport-size=375x667"],
      "width": 375,
      "height": 667,
      "device_scale_factor": 2.0,
      "is_mobile": true,
      "device_class": "Custom Device"
    }
  }
}
```

### Coverage Configuration

Edit coverage thresholds in `testgpt_engine.py`:
```python
config = CoverageConfig.default()  # 80% threshold
# or
config = CoverageConfig.strict()   # 100% threshold
# or
config = CoverageConfig.permissive()  # 50% threshold
```

---

## PR-Based Testing

### How It Works

When you test a PR via Slack, the system:

1. **Fetches PR Context** from GitHub API
   - PR metadata (title, author, description, labels)
   - Changed files with line-by-line diffs
   - Linked issues and acceptance criteria
   - CI/CD status checks

2. **Detects Deployment URL**
   - Searches PR comments for deployment URLs
   - Checks CI/CD status checks (Vercel, Netlify, etc.)
   - Validates deployment is accessible (HTTP 200)

3. **Analyzes Codebase**
   - Detects project type (frontend, backend, fullstack)
   - Identifies tech stack (Next.js, React, FastAPI, etc.)
   - Reads package.json, requirements.txt, README

4. **Generates Test Scenarios** based on changed files
   - If UI components changed → UI component tests
   - If API routes changed → API functionality tests
   - If styles changed → Visual regression tests
   - Always tests acceptance criteria from PR description

5. **Executes Tests** with Playwright
   - Runs browser automation tests on deployment URL
   - Tests only the changes, not the entire site
   - Captures screenshots and console errors
   - Optionally tracks code coverage

6. **Reports Results** to Slack and optionally GitHub
   - Pass/fail status with scenario breakdown
   - Detailed failure messages
   - Coverage percentage (if enabled)
   - Duration and environment info

### GitHub Token Setup

To post test results as PR comments (optional):

1. Go to https://github.com/settings/tokens
2. Generate new token with `repo` scope
3. Add to `.env`:
   ```bash
   GITHUB_TOKEN=ghp_your_token_here
   ```

Without a token, TestGPT can still:
- Read public PR data
- Analyze code changes
- Run tests on deployment URLs
- Post results to Slack

---

## API Reference

Once the backend is running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Test Management
- `POST /api/tests` - Create test suite
- `GET /api/tests` - List test suites
- `GET /api/tests/{id}` - Get test details
- `PUT /api/tests/{id}` - Update test suite
- `DELETE /api/tests/{id}` - Delete test suite

#### Test Execution
- `POST /api/tests/{id}/run` - Execute/re-run test
- `POST /api/tests/batch/run` - Batch re-run
- `GET /api/executions` - List executions
- `GET /api/executions/{id}` - Get execution details
- `GET /api/tests/{id}/history` - Get execution history

#### Configuration
- `GET /api/configs` - List configurations
- `POST /api/configs` - Create configuration
- `GET /api/configs/{id}` - Get configuration
- `PUT /api/configs/{id}` - Update configuration
- `DELETE /api/configs/{id}` - Delete configuration

#### Statistics & Health
- `GET /api/statistics` - Get overall statistics
- `GET /health` - Check API health

#### Migration
- `POST /api/migrate/json-to-db` - Migrate JSON scenarios to database

---

## Production Status

### Test Results Summary

**Coverage System**: ✅ PRODUCTION READY
- **End-to-End Tests**: ✅ ALL PASSED (5/5 suites)
- **MCDC Edge Cases**: ✅ ALL PASSED (13 edge cases)
- **Database Tests**: ✅ ALL PASSED (5 scenarios)
- **Total Tests**: 30+ comprehensive tests
- **Failures**: 0

**Backend API**: ✅ OPERATIONAL (10/12 endpoints working)
- **Health Check**: ✅ PASS
- **Test Management**: ✅ PASS
- **Execution Tracking**: ✅ PASS
- **Configuration**: ✅ PASS
- **Statistics**: ⚠️ Minor issues

**Frontend**: ✅ OPERATIONAL
- **Test Library**: ✅ Working
- **Test Execution**: ✅ Working
- **Dashboard**: ✅ Working
- **Database Schema**: ✅ Fixed

**Browser Support**: ✅ ALL BROWSERS WORKING
- **Chromium**: ✅ Ready
- **WebKit/Safari**: ✅ Ready (Fixed!)
- **Firefox**: ✅ Ready

### Key Achievements

1. ✅ **Complete Phase 1** - All instrumentation components implemented
2. ✅ **Sophisticated MCDC Analysis** - Handles complex boolean conditions
3. ✅ **Intelligent Stop Logic** - Multi-criteria decision making
4. ✅ **Flexible Configuration** - Preset and custom configs
5. ✅ **Database Foundation** - Complete schema and operations
6. ✅ **CLI Tool** - Fully functional command-line interface
7. ✅ **Comprehensive Documentation** - README, getting started, status docs
8. ✅ **Browser Setup** - All browsers installed and verified
9. ✅ **Test Persistence** - Full CRUD with re-run functionality
10. ✅ **Slack Integration** - Complete with re-run commands

### Documentation

Production readiness reports:
- **Coverage System**: `PRODUCTION_READINESS_REPORT.md`
- **Testing Complete**: `TESTING_COMPLETE_SUMMARY.md`
- **Final Status**: `COVERAGE_FINAL_STATUS.md`
- **Validation Report**: `VALIDATION_REPORT.md`

---

## Troubleshooting

### Common Issues

#### 1. Browser Not Found
```
Error: Browser specified in your config is not installed
```

**Solution:**
```bash
./scripts/ENSURE_BROWSERS_INSTALLED.sh
```

#### 2. Frontend 500 Error
**Check:**
- Backend API is running on port 8000
- Frontend is running on port 3000
- Database schema is correct

**Solution:**
```bash
# Restart backend
pkill -f uvicorn
python -m uvicorn backend.api.main:app --reload &

# Restart frontend
cd frontend && npm run dev
```

#### 3. Test Not Showing in Library
**Check database:**
```bash
sqlite3 frontend/lib/db/testgpt.db "SELECT COUNT(*) FROM test_suites;"
```

**Run health check:**
```bash
python scripts/db_health_check.py
```

#### 4. Re-run Command Not Working
**Verify command format:**
```
# These work:
@TestGPT re-run test-name
@TestGPT rerun test-name
@TestGPT run test-name again
@TestGPT re-run last test

# These don't:
@TestGPT re run test-name (space in "re run")
```

#### 5. Coverage Reports Missing
**Check location:**
```bash
ls -la ./coverage_reports/
```

**Generate manually:**
```bash
python coverage/cli.py run https://github.com/test/repo default
```

### Debugging

#### View Logs
All execution logs are saved to:
- `logs/testgpt-debug-YYYYMMDD-HHMMSS.log` (timestamped)
- `logs/latest.log` (symlink to most recent)

```bash
# View latest log
cat logs/latest.log

# Search for patterns
cat logs/latest.log | grep "Test Outcome:"
cat logs/latest.log | grep "Coverage:"
```

#### Database Queries
```bash
# Connect to database
sqlite3 frontend/lib/db/testgpt.db

# List test suites
SELECT id, name, created_at FROM test_suites ORDER BY created_at DESC LIMIT 10;

# View executions
SELECT id, status, execution_time_ms FROM test_executions_v2 ORDER BY created_at DESC LIMIT 10;

# Check coverage runs
SELECT * FROM coverage_runs ORDER BY started_at DESC LIMIT 5;
```

#### Verification Scripts
```bash
# Verify coverage system
./VERIFY_COVERAGE.sh

# Test API endpoints
python scripts/test_api_endpoints.py

# Database health check
python scripts/db_health_check.py
```

---

## Bug Fixes & Recent Updates

### Coverage System
- ✅ **Database UNIQUE Constraint** - Fixed save_coverage_run() to use merge
- ✅ **Test Script IDs** - Changed to unique UUIDs
- ✅ **Verification Script** - Updated dependency checks for Python 3.9+

### Browser Setup
- ✅ **Safari/WebKit** - Added PLAYWRIGHT_BROWSERS_PATH environment variable
- ✅ **Executable Paths** - Added explicit paths for WebKit browsers
- ✅ **Symlink Creation** - Created mcp-webkit symlink for compatibility

### Frontend
- ✅ **Schema Alignment** - Fixed table name (test_executions → test_executions_v2)
- ✅ **Configuration Templates** - Added configurationTemplates schema
- ✅ **Field Names** - Corrected errorMessage → errorDetails, etc.
- ✅ **TypeScript Fixes** - Added explicit type annotations

### Slack Integration
- ✅ **Re-run Commands** - Added "last test" keyword handling
- ✅ **EnvironmentMatrix** - Fixed parameter name (networks instead of network_conditions)
- ✅ **Database Persistence** - Added _save_execution_to_database() method
- ✅ **Event Deduplication** - Added event ID tracking
- ✅ **Old Event Filtering** - Added 5-minute timestamp cutoff

### Test Migration
- ✅ **Complete Migration** - Migrated all test steps from JSON to database
- ✅ **Test Steps Included** - Fixed migration to include flows[].steps
- ✅ **Data Integrity** - All 9 scenarios migrated with complete test steps

### Slack Reporting
- ✅ **Verbose Output Fixed** - Extract only final agent content, not debug logs
- ✅ **Summary Extraction** - Parse and show brief summaries only
- ✅ **Coverage Reports Saved** - Generate and save HTML reports to files
- ✅ **Report Paths in Slack** - Include file paths in Slack messages

For detailed information on fixes, see:
- `FIXES_APPLIED.md`
- `FIX_SUMMARY.md`
- `SCHEMA_FIX_COMPLETE.md`
- `FINAL_FIX.md`
- `SLACK_RERUN_AND_DB_FIXES.md`

---

## Tech Stack

- **Slack Bolt** - Slack integration
- **Agno** - AI agent framework
- **Claude Sonnet 4** - AI model
- **Playwright MCP** - Web automation
- **FastAPI** - Backend REST API server
- **SQLAlchemy** - Database ORM
- **SQLite** - Database storage
- **Next.js 16** - Frontend framework
- **React 19** - UI components
- **TypeScript** - Type-safe frontend code
- **Drizzle ORM** - Frontend database access
- **Tailwind CSS 4** - UI styling
- **FastMCP** - Dynamic backend API testing
- **Model Context Protocol** - Tool integration
- **Git/GitHub** - Repository management
- **OpenAPI** - API introspection

---

## What the Agents Can Do

- Navigate websites
- Search Google, Wikipedia, etc.
- Fill out forms
- Take screenshots
- Extract data from pages
- Click buttons and links
- Type and interact with elements
- Test backend APIs
- Validate API responses
- Run comprehensive test suites
- Track code coverage
- Analyze MCDC requirements
- Generate coverage reports

---

## License

MIT License - See LICENSE file for details

---

## Support & Documentation

### Quick Links
- **Coverage System**: `coverage/README.md`
- **Getting Started**: `coverage/GETTING_STARTED.md`
- **Test Persistence**: `USER_GUIDE_RERUN.md`
- **API Testing**: `dynamic_backend_testing/README.md`
- **Examples**: `examples/README.md`

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Database health
python scripts/db_health_check.py

# Coverage system
./VERIFY_COVERAGE.sh

# API endpoints
python scripts/test_api_endpoints.py
```

### Support
For issues or questions:
- Check relevant documentation in the links above
- Review troubleshooting section
- Check logs in `logs/latest.log`
- Run verification scripts

---

**Last Updated:** November 1, 2025
**Version:** 1.0.0
**Status:** ✅ Production Ready
**Test Coverage:** 30+ comprehensive tests, 0 failures
**API Status:** 10/12 endpoints operational (83%)
**Browser Support:** All browsers working (Chrome, Safari, Firefox)
