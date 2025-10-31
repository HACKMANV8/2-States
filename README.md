# TestGPT - Multi-Environment QA Testing System

**🚀 NEW: TestGPT is now a comprehensive multi-environment QA testing platform!**

Transform simple Slack messages into complete cross-browser, cross-device, and cross-network test matrices. TestGPT behaves like a professional manual QA engineer, automatically testing your sites across multiple environments and prioritizing failures.

## Quick Links

- **📖 [TestGPT Documentation](TESTGPT_README.md)** - Complete guide to the new system
- **✅ [Implementation Summary](IMPLEMENTATION_COMPLETE.md)** - Full specification compliance report
- **🧪 [Original Examples](#original-examples)** - Simple AI agent examples (legacy)

## TestGPT Features

### 🎯 Multi-Environment Testing
- **10 viewport profiles** (iPhone SE → desktop ultrawide)
- **4 browser engines** (Chrome, Safari, Firefox)
- **3 network conditions** (normal, slow 3G, flaky)
- **Automatic matrix expansion** (one request → N test runs)
- **REAL Playwright MCP execution** (actual browsers, not mocked)

### 🧠 Intelligent Test Planning
- **Natural language parsing** from Slack
- **Deterministic test flows** with objective checkpoints
- **Automatic scenario persistence** for re-running
- **Failure prioritization** (P0 critical → P2 edge cases)

### 📊 Comprehensive Reporting
- **Formatted Slack summaries** with environment breakdown
- **Per-dimension statistics** (by viewport, browser, network)
- **Actionable next steps** for fixing issues
- **Evidence collection** (screenshots, console errors)

### 🔄 Re-run Capability
- All tests automatically saved
- Re-run with: `"re-run [scenario name]"`
- Historical comparison support

## Quick Start

### Run TestGPT Demo
```bash
# Test the full system with mock results
python test_testgpt.py
```

### Run TestGPT Slack Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env with your tokens
cp .env.example .env
# Edit .env with your API keys

# Run the new TestGPT bot
python slack_agent_testgpt.py
```

### Example Slack Commands
```
@TestGPT test pointblank.club responsive on safari and iphone
@TestGPT run checkout flow on chrome desktop and ipad under slow network
@TestGPT list scenarios
@TestGPT re-run pointblank responsive test
```

---

## Original Examples

The following are the original simple AI agent examples (legacy).
For the new TestGPT system, see documentation above.

### 1. Original Slack Bot (Legacy)
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

### Live Demos
- `demo_google_search.py` - Google search automation
- `demo_persistent_session.py` - Multi-step browser tasks

### Test Scripts
- `test_api_key.py` - Verify API key
- `test_mcp_connection.py` - Test MCP server connections
- `test_playwright_mcp.py` - Test Playwright integration

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

## Configuration

Required environment variables in `.env`:
- `ANTHROPIC_API_KEY` - Get from console.anthropic.com
- `SLACK_BOT_TOKEN` - Your Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN` - Your Slack app token (xapp-...)

## Architecture

```
Slack → Agno Agent → Playwright MCP → Web Automation → Results
```

## Tech Stack

- Slack Bolt - Slack integration
- Agno - AI agent framework
- Claude Sonnet 4 - AI model
- Playwright MCP - Web automation
- Model Context Protocol - Tool integration

