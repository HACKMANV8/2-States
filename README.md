# TestGPT - Multi-Environment QA Testing Platform

Complete AI agent examples using Agno framework with Model Context Protocol (MCP) integration. Includes Slack bot, web automation, backend API testing, documentation lookup, and file system operations.

Transform simple Slack messages into complete cross-browser, cross-device, and cross-network test matrices. TestGPT behaves like a professional manual QA engineer, automatically testing your sites across multiple environments and prioritizing failures.

## Features

- **AI-Powered**: Uses Claude Sonnet 4 for intelligent task understanding
- **Multiple MCP Servers**: Context7 docs, Filesystem, Playwright web automation
- **PR-Based Context Testing**: Automatically test GitHub PRs with deployment URLs (NEW!)
- **Dynamic Backend API Testing**: Test ANY user API from repos/PRs automatically
- **Slack Integration**: Production bot with web automation AND API testing
- **Persistent Sessions**: Maintains state across tasks
- **Example Agents**: 6 complete examples + live demos + CI/CD examples

### Multi-Environment Testing
- **10 viewport profiles** (iPhone SE → desktop ultrawide)
- **4 browser engines** (Chrome, Safari, Firefox)
- **3 network conditions** (normal, slow 3G, flaky)
- **Automatic matrix expansion** (one request → N test runs)
- **REAL Playwright MCP execution** (actual browsers, not mocked)

### Intelligent Test Planning
- **Natural language parsing** from Slack
- **Deterministic test flows** with objective checkpoints
- **Automatic scenario persistence** for re-running
- **Failure prioritization** (P0 critical → P2 edge cases)

### Comprehensive Reporting
- **Formatted Slack summaries** with environment breakdown
- **Per-dimension statistics** (by viewport, browser, network)
- **Actionable next steps** for fixing issues
- **Evidence collection** (screenshots, console errors)

### Test Persistence & Re-run (NEW!)
- **Test Library**: Save AI-generated tests to database
- **Configuration Templates**: Reusable test configs (regression, smoke, mobile, etc.)
- **Re-run with different settings**: Change browser, viewport, network conditions
- **Execution History**: Track all test runs with detailed results
- **Batch Execution**: Run multiple tests with same configuration
- **REST API**: Full backend API for test management
- **Modern Dashboard**: Next.js UI for test library and execution tracking

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
npm run dev
```
Frontend runs at: http://localhost:3000/pr-tests

### Alternative: Test Demo (No Slack/MCP needed)
```bash
python scripts/test_testgpt.py
```
This demonstrates the full flow with mock results.

### Environment Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
npx playwright install
```

2. **Configure .env**
```bash
cp .env.example .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` - Get from console.anthropic.com
- `SLACK_BOT_TOKEN` - Your Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN` - Your Slack app token (xapp-...)
- `GITHUB_TOKEN` - (Optional) For posting PR comments

### Example Slack Commands
```
# Basic testing
@TestGPT test pointblank.club responsive on safari and iphone
@TestGPT run checkout flow on chrome desktop and ipad under slow network

# PR-based testing (NEW!)
@TestGPT test this PR https://github.com/owner/repo/pull/123
@TestGPT test out this PR: https://github.com/owner/repo/pull/456
@TestGPT check this PR https://github.com/owner/repo/pull/789

# Custom instructions
@TestGPT Test github.com, are you able to view the repositories of SkySingh04?
@TestGPT Test careers.pointblank.club and check if the job listings load

# Scenario management
@TestGPT list scenarios
@TestGPT re-run pointblank responsive test

# Backend API testing
@TestGPT test the backend API health
@TestGPT run smoke tests on all endpoints
```

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
- `test_api_key.py` - Verify API key
- `test_mcp_connection.py` - Test MCP server connections
- `test_playwright_mcp.py` - Test Playwright integration
- `verify_installation.py` - Installation verification

### Setup Scripts (`scripts/`)
- `START_EVERYTHING.sh` - Start backend API server
- `START_SLACK_BOT.sh` - Start Slack bot
- `RUN_FULL_TEST.sh` - Run comprehensive test suite
- `setup_persistence.sh` - Setup test persistence system

### Dynamic Backend API Testing
**Directory**: `dynamic_backend_testing/`
- Test ANY user-submitted API from repos, branches, PRs
- Automatic OpenAPI introspection and MCP wrapper generation
- Zero manual configuration - works with unknown APIs
- CI/CD ready - test PRs before merging
- See [dynamic_backend_testing/README.md](dynamic_backend_testing/README.md) for full documentation

## Usage

### Running Examples
```bash
# Run agent examples
python examples/01_basic_context7_agent.py
python examples/demo_google_search.py

# Run Streamlit app
streamlit run examples/04_streamlit_app.py

# Run tests
python scripts/test_testgpt.py
```

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

And `config.py`:
```python
"your-custom-viewport": ViewportProfile(
    name="your-custom-viewport",
    width=375,
    height=667,
    display_name="Your Custom Device",
    playwright_device=None,
    device_scale_factor=2.0,
    is_mobile=True,
    device_class="Custom Device",
    description="Your custom device description"
)
```

## Dynamic Backend API Testing

The dynamic backend testing system automatically tests user-submitted APIs with zero configuration.

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

### Components

**RepoManager** - Git operations (clone, checkout, dependency installation)
**APIDiscoveryService** - API discovery and OpenAPI extraction
**MCPGenerator** - Dynamic MCP tool code generation
**DynamicServerManager** - Server lifecycle management
**DynamicBackendOrchestrator** - End-to-end coordination

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

if result['overall_success']:
    print(f"✅ All {len(result['test_results'])} tests passed")
```

### CI/CD Integration

```bash
# Test a pull request
python examples/test_pr.py \
  --repo https://github.com/user/repo \
  --pr 123
```

For complete documentation, see:
- [dynamic_backend_testing/README.md](dynamic_backend_testing/README.md) - Full system documentation

## Bug Fixes & Improvements

### Recent Fixes

#### Test Status Detection Fixed
**Issue:** Tests marked as FAILED despite agent reporting SUCCESS
**Fix:** Added multiple status indicator formats
**Location:** `test_executor.py:505-530`

#### MCP Server Isolation Fixed
**Issue:** Different browsers testing on same MCP instance
**Fix:** Added MCP cleanup after each cell execution
**Location:** `test_executor.py:239-244`, `mcp_manager.py:172-192`

#### Subdomain URL Support Fixed
**Issue:** careers.pointblank.club → pointblank.club
**Fix:** Improved URL extraction regex to handle subdomains
**Location:** `request_parser.py:148-177`

#### Custom User Instructions Support
**Issue:** Agent only performed generic tests
**Fix:** Thread user's raw message to agent instructions
**Location:** `test_executor.py:283-296`

#### Old Event Filtering
**Issue:** Bot processing messages from 5+ minutes ago
**Fix:** Added timestamp-based filtering (5-minute cutoff)
**Location:** `main.py:134-144`

#### Event Deduplication
**Issue:** Slack bot processing same message multiple times
**Fix:** Added event ID tracking with deduplication
**Location:** `main.py:126-141`

#### MCP Cleanup Warnings Suppressed
**Issue:** Cosmetic RuntimeError warnings on shutdown
**Fix:** Added try/except wrappers and asyncio exception handler
**Location:** `testgpt_engine.py:163-177`, `main.py:67-87`

#### API Discovery Enhanced
**Issue:** Failed to load apps from nested directories (e.g., src/app/main.py)
**Fix:** Added intelligent path resolution and environment variable setup
**Location:** `dynamic_backend_testing/api_discovery.py`

## Debugging

### View Logs
All execution logs are saved to:
- `logs/testgpt-debug-YYYYMMDD-HHMMSS.log` (timestamped)
- `logs/latest.log` (symlink to most recent)

```bash
# View latest log
cat logs/latest.log

# Search for specific patterns
cat logs/latest.log | grep "Test Outcome:"
cat logs/latest.log | grep "✅ Autonomous execution completed"
```

### What Gets Logged
- MCP server launch commands
- Connection status for each viewport/browser
- Full agent instructions sent
- Complete agent responses
- All tool calls and results
- Detailed error traces with stack traces

## Tech Stack

- **Slack Bolt** - Slack integration
- **Agno** - AI agent framework
- **Claude Sonnet 4** - AI model
- **Playwright MCP** - Web automation
- **FastAPI** - Backend REST API server
- **SQLAlchemy** - Database ORM
- **SQLite** - Database storage
- **Next.js** - Frontend framework
- **TypeScript** - Type-safe frontend code
- **Drizzle ORM** - Frontend database access
- **Tailwind CSS** - UI styling
- **FastMCP** - Dynamic backend API testing
- **Model Context Protocol** - Tool integration
- **Git/GitHub** - Repository management
- **OpenAPI** - API introspection

## PR-Based Testing

### How It Works

When you test a PR via Slack (`@TestGPT test this PR: <url>`), the system:

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

6. **Reports Results** to Slack
   - Pass/fail status with scenario breakdown
   - Detailed failure messages
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

It just won't be able to post GitHub PR comments.

## Documentation

For architecture details, see:
- `dynamic_backend_testing/README.md` - Dynamic API testing system
- `examples/README.md` - Example scripts and CI/CD integration

## API Reference

Once the backend is running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Main API endpoints:
- `POST /api/tests` - Create test suite
- `GET /api/tests` - List test suites
- `GET /api/tests/{id}` - Get test details
- `POST /api/tests/{id}/run` - Execute test
- `GET /api/configs` - List configuration templates
- `GET /api/executions` - List test executions
- `GET /api/statistics` - Get test statistics

## License

MIT License - See LICENSE file for details
