# TestGPT - Multi-Environment QA Testing Platform

Complete AI agent examples using Agno framework with Model Context Protocol (MCP) integration. Includes Slack bot, web automation, backend API testing, documentation lookup, and file system operations.

Transform simple Slack messages into complete cross-browser, cross-device, and cross-network test matrices. TestGPT behaves like a professional manual QA engineer, automatically testing your sites across multiple environments and prioritizing failures.

## Features

- **AI-Powered**: Uses Claude Sonnet 4 for intelligent task understanding
- **Multiple MCP Servers**: Context7 docs, Filesystem, Playwright web automation
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

### Re-run Capability
- All tests automatically saved
- Re-run with: `"re-run [scenario name]"`
- Historical comparison support

## Quick Start

### Run the Test Demo (No Slack/MCP needed)
```bash
python test_testgpt.py
```
This demonstrates the full flow with mock results.

### Run the Slack Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for testing)
npx playwright install

# Configure .env with your tokens
cp .env.example .env
# Edit .env with your API keys

# Run TestGPT
python main.py
```

### Run Backend API Testing
```bash
# Test a GitHub API
export ANTHROPIC_API_KEY=your_key
python examples/test_github_repo.py
```

### Example Slack Commands
```
# Basic testing
@TestGPT test pointblank.club responsive on safari and iphone
@TestGPT run checkout flow on chrome desktop and ipad under slow network

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

## Examples Included

### 1. Slack Bot
**File**: `slack_agent.py`
- Production-ready Slack bot with Playwright MCP
- Responds to channel mentions
- Performs web automation tasks
- Posts results back to Slack

### 2. Documentation Agent
**File**: `01_basic_context7_agent.py`
- Uses Context7 MCP for live documentation
- Looks up library docs and examples
- Supports any programming library

### 3. Filesystem Agent
**File**: `02_filesystem_agent.py`
- File and directory operations
- Read/write/create files
- Search and navigate filesystem

### 4. Multi-Agent Team
**File**: `03_multi_agent_team.py`
- Multiple agents working together
- Specialized roles (researcher, coder, reviewer)
- Coordinated task execution

### 5. Streamlit Web Interface
**File**: `04_streamlit_app.py`
- Web UI for agent interaction
- Visual task execution
- Interactive chat interface

### 6. Playwright MCP Agent
**File**: `05_playwright_mcp_agent.py`
- Persistent browser sessions
- Advanced web automation
- Class-based implementation

### 7. Dynamic Backend API Testing System
**Directory**: `dynamic_backend_testing/`
- **Test ANY user-submitted API** from repos, branches, PRs
- **Automatic OpenAPI introspection** and MCP wrapper generation
- **Zero manual configuration** - works with unknown APIs
- **CI/CD ready** - test PRs before merging
- **Production-ready orchestration** for automated testing
- Works with FastAPI, Flask, Django automatically
- **See [dynamic_backend_testing/README.md](dynamic_backend_testing/README.md) for full documentation**

### Live Demos
- `demo_google_search.py` - Google search automation
- `demo_persistent_session.py` - Multi-step browser tasks

### Test Scripts
- `test_api_key.py` - Verify API key
- `test_mcp_connection.py` - Test MCP server connections
- `test_playwright_mcp.py` - Test Playwright integration

### Examples
- `examples/test_github_repo.py` - Test any GitHub repository
- `examples/test_pr.py` - Test pull requests (CI/CD ready)

## Usage

### Slack Bot
Mention the bot in Slack:
```
@bot search Google for "best restaurants near me"
@bot go to wikipedia and find info about Python
@bot take a screenshot of example.com
```

### Running Examples
```bash
# Run any example
python 01_basic_context7_agent.py
python demo_google_search.py

# Run Streamlit app
streamlit run 04_streamlit_app.py
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

Required environment variables in `.env`:
- `ANTHROPIC_API_KEY` - Get from console.anthropic.com
- `SLACK_BOT_TOKEN` - Your Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN` - Your Slack app token (xapp-...)

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
- [DYNAMIC_SYSTEM_IMPLEMENTATION.md](DYNAMIC_SYSTEM_IMPLEMENTATION.md) - Architecture details
- [FINAL_IMPLEMENTATION_SUMMARY.md](FINAL_IMPLEMENTATION_SUMMARY.md) - Implementation summary

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
- **FastMCP** - Dynamic backend API testing
- **Model Context Protocol** - Tool integration
- **Git/GitHub** - Repository management
- **OpenAPI** - API introspection

## Documentation

- **[dynamic_backend_testing/README.md](dynamic_backend_testing/README.md)** - Full dynamic testing system docs
- **[DYNAMIC_SYSTEM_IMPLEMENTATION.md](DYNAMIC_SYSTEM_IMPLEMENTATION.md)** - Architecture and design details
- **[FINAL_IMPLEMENTATION_SUMMARY.md](FINAL_IMPLEMENTATION_SUMMARY.md)** - Implementation summary
- **[examples/README.md](examples/README.md)** - Example scripts and CI/CD integration

## License

MIT License - See LICENSE file for details
