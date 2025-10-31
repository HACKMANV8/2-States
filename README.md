# AI Agent Framework with MCP Integration

Complete AI agent examples using Agno framework with Model Context Protocol (MCP) integration. Includes Slack bot, web automation, documentation lookup, and file system operations.

## Features

- **AI-Powered**: Uses Claude Sonnet 4 for intelligent task understanding
- **Multiple MCP Servers**: Context7 docs, Filesystem, Playwright web automation
- **Slack Integration**: Production bot that responds to mentions
- **Persistent Sessions**: Maintains state across tasks
- **Example Agents**: 5 complete examples + live demos

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env with your tokens
cp .env.example .env
# Edit .env with your API keys

# Run the bot
python slack_agent.py
```

## Examples Included

### 1. Slack Production Bot
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

