# Quick Start Guide

Get started with TestGPT in 5 minutes! Choose your path:
- **Path A**: Slack Bot with Web Automation (Playwright)
- **Path B**: Backend API Testing (FastMCP)
- **Path C**: Both Combined (Full-Stack Testing)

---

## Prerequisites

1. Python 3.10+ installed
2. Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
3. (For Slack bot) Slack workspace with bot permissions

## Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY=your_key
# - SLACK_BOT_TOKEN=xoxb-... (for Slack bot)
# - SLACK_APP_TOKEN=xapp-... (for Slack bot)
```

---

## Path A: Slack Bot with Web Automation

### 1. Run the Slack Bot

```bash
source venv/bin/activate
python slack_agent.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  Slack Bot with Agno + Playwright MCP Integration                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

✅ All environment variables found

⚡️ Starting Slack bot...
💡 Mention the bot in any channel to trigger the agent
======================================================================
⚡️ Bot is running!
```

### 2. Use the Bot in Slack

1. Go to your Slack workspace
2. Mention the bot in any channel: `@YourBotName your task`
3. Bot responds with results

**Example Commands:**
```
@bot search Google for "best pizza near me"
@bot go to wikipedia and find info about AI
@bot navigate to example.com and take a screenshot
```

### 3. What Happens

1. Bot receives mention
2. Sends: "🤖 Got it! Working on..."
3. AI agent executes task with browser (Playwright)
4. Bot posts results back to Slack

### 4. Stop the Bot

Press `Ctrl+C` in terminal

---

## Path B: Backend API Testing

### 1. Run the Backend Testing Agent

```bash
# This will:
# 1. Start the sample FastAPI backend
# 2. Connect to FastMCP MCP server
# 3. Create an AI agent with API testing tools
# 4. Let you run interactive tests

python 06_backend_api_testing_agent.py
```

### 2. Select an Example

- **Option 1**: Basic API testing (health checks, list users, stats)
- **Option 2**: Comprehensive testing (smoke tests, CRUD tests)
- **Option 3**: Error handling testing
- **Option 4**: See Slack integration pattern
- **Option 5**: Interactive mode (type your own test commands)

### 3. Try Interactive Mode

```bash
# Select option 5 for interactive mode

# Example commands to try:
🧪 Test command: Check if the API is healthy
🧪 Test command: List all users in the system
🧪 Test command: Run a complete smoke test on all endpoints
🧪 Test command: Create a test user named 'testuser' with email test@example.com
🧪 Test command: Search for products under $50
```

### 4. Run Automated Tests

```bash
# Run the full test suite
pytest tests/test_backend_api.py -v

# Run specific test
pytest tests/test_backend_api.py::test_health_check -v

# Run with output
pytest tests/test_backend_api.py -v -s
```

### 5. Available MCP Tools

When the agent connects to FastMCP, these tools become available:

**Health & Status**
- `check_api_health()` - Check API health
- `get_api_info()` - Get API version info

**User Management (CRUD)**
- `list_users(active_only, limit)` - List users
- `get_user(user_id)` - Get specific user
- `create_user(username, email)` - Create user
- `update_user(user_id, ...)` - Update user
- `delete_user(user_id)` - Delete user

**Products**
- `list_products(...)` - List products with filters
- `get_product(product_id)` - Get specific product

**Search & Analytics**
- `search(query, search_type)` - Search users/products
- `get_statistics()` - Get system stats

**Test Suites**
- `run_user_crud_test()` - Complete CRUD test cycle
- `run_api_smoke_test()` - Test all major endpoints

---

## Path C: Full-Stack Testing (Web + API)

### 1. Run the Enhanced Slack Bot

```bash
# This bot has BOTH Playwright AND Backend API testing
python slack_agent.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  Enhanced Slack Bot with Agno Integration                           ║
║  • Playwright MCP (Web Automation)                                   ║
║  • FastMCP (Backend API Testing)                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

✅ All environment variables found

⚡️ Starting enhanced Slack bot...
💡 Capabilities:
   • Web automation via Playwright
   • Backend API testing via FastMCP

💬 Mention the bot in any channel to use it
======================================================================
```

### 2. Use Both Capabilities

**Web Automation Commands:**
```
@bot search Google for "restaurants"
@bot take a screenshot of example.com
```

**API Testing Commands:**
```
@bot test the backend API health
@bot run smoke tests on all endpoints
@bot create a test user and verify it
```

**Combined Commands:**
```
@bot test the homepage AND the /api/health endpoint
@bot verify the login page works and then test the user API
```

---

## Architecture Overview

### Path A: Web Automation Only
```
Slack → Agno Agent → Playwright MCP → Web Automation → Results
```

### Path B: API Testing Only
```
FastAPI Backend → FastMCP → Agno Agent → API Tests → Results
```

### Path C: Full-Stack Testing
```
                    ┌─→ Playwright MCP → Web Testing
Agno Agent → Tools ─┤
                    └─→ FastMCP → Backend API Testing
```

---

## Quick Examples

### Example 1: Basic Agent Usage (API Testing)

```python
from backend_api.server_launcher import BackendServerManager
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

# 1. Start backend server
manager = BackendServerManager()
manager.start_backend_server()

# 2. Connect to FastMCP
mcp_tools = MCPTools(command=manager.get_mcp_command())
await mcp_tools.connect()

# 3. Create agent
agent = Agent(
    name="APITester",
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[mcp_tools],
    instructions="Test APIs thoroughly"
)

# 4. Run tests
result = await agent.arun("Run a smoke test on all endpoints")
print(result.content)
```

### Example 2: Test Your Own API

**Option 1: Modify the sample API**
Edit `backend_api/sample_api.py` to match your API endpoints.

**Option 2: Point to your running API**
```python
# In backend_api/fastmcp_wrapper.py
API_BASE_URL = "http://localhost:3000"  # Your API URL
```

**Option 3: Create custom FastMCP wrapper**
```python
from fastmcp import FastMCP
import httpx

mcp = FastMCP(name="My API")

@mcp.tool()
async def test_my_endpoint() -> dict:
    """Test my custom endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://my-api.com/endpoint")
        return {"status": response.status_code, "data": response.json()}

mcp.run()
```

---

## Troubleshooting

### Slack Bot Issues

**Bot not responding?**
- Check bot is running
- Ensure bot invited to channel
- Verify .env has all tokens (SLACK_BOT_TOKEN, SLACK_APP_TOKEN)

**Connection errors?**
- Check Slack app permissions
- Verify ANTHROPIC_API_KEY is valid
- See README.md for full docs

### Backend API Issues

**Port already in use:**
```bash
# Error: Port 8000 already in use

# Solution 1: Kill existing process
lsof -ti:8000 | xargs kill -9

# Solution 2: Use different port
# In server_launcher.py, change api_port=8001
```

**FastMCP not found:**
```bash
# Install FastMCP
pip install fastmcp

# Or reinstall all dependencies
pip install -r requirements.txt
```

**Agent not seeing tools:**
```python
# Ensure connection is established BEFORE creating agent
await mcp_tools.connect()  # ← Must call this first

agent = Agent(tools=[mcp_tools])  # ← Then create agent
```

**Backend won't start:**
```bash
# Check logs
python backend_api/sample_api.py

# Verify dependencies
pip install fastapi uvicorn

# Check if Python path is correct
which python
```

---

## Next Steps

1. **Read Full Documentation**: See [README.md](README.md) for complete guide
2. **Explore Examples**: Open `06_backend_api_testing_agent.py` to see all examples
3. **Run Tests**: Check out `tests/test_backend_api.py` for pytest examples
4. **Customize**: Modify the sample API or create your own FastMCP wrapper
5. **Integrate**: Add backend testing to your Slack bot or CI/CD pipeline

## Resources

- [Agno Documentation](https://docs.agno.com)
- [Agno MCP Guide](https://docs.agno.com/concepts/tools/mcp/overview)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastAPI](https://fastapi.tiangolo.com)
- [Playwright](https://playwright.dev)

## Support

- Check [backend_api/README.md](backend_api/README.md) for API testing details
- Review example code in `06_backend_api_testing_agent.py`
- Examine test cases in `tests/test_backend_api.py`
- See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick command reference

Happy testing! 🧪
