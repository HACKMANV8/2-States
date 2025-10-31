"""
Enhanced Slack Bot with Agno Agent Integration + Backend API Testing

This is an enhanced version of slack_agent.py that includes BOTH:
- Playwright MCP for web automation
- FastMCP for backend API testing

When mentioned in Slack, the bot can:
- Perform web automation tasks (via Playwright)
- Test backend APIs (via FastMCP)
- Do both in combination!

Usage:
    1. Set up environment variables in .env:
       - SLACK_BOT_TOKEN
       - SLACK_APP_TOKEN
       - ANTHROPIC_API_KEY

    2. Run: python slack_agent.py

Example Slack commands:
    @bot search Google for "best restaurants"
    @bot test the backend API health
    @bot run smoke tests on all endpoints
    @bot create a test user named 'testuser'
    @bot go to example.com and take a screenshot, then test the /health endpoint
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

# Add backend_api to path
sys.path.insert(0, str(Path(__file__).parent / "backend_api"))

from server_launcher import BackendServerManager

load_dotenv()

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Global variables for MCP connections (persistent across mentions)
playwright_mcp_tools = None
backend_mcp_tools = None
backend_manager = None
agent = None


async def initialize_backend_server():
    """
    Initialize and start the backend API server.

    This runs once when the Slack bot starts.
    """
    global backend_manager

    if backend_manager is not None:
        return backend_manager

    print("🚀 Starting backend API server for testing...")

    backend_manager = BackendServerManager(
        api_host="127.0.0.1",
        api_port=8000,
        auto_start_backend=True
    )

    # Start the backend server
    if backend_manager.start_backend_server():
        print("✅ Backend API server started successfully")
        return backend_manager
    else:
        print("❌ Failed to start backend API server")
        return None


async def initialize_agent():
    """
    Initialize the agent with BOTH Playwright and Backend Testing MCP tools.

    This combines web automation and API testing capabilities in a single agent.
    """
    global playwright_mcp_tools, backend_mcp_tools, agent, backend_manager

    if agent is not None:
        return agent

    print("🔧 Initializing Multi-Capability Agno Agent...")
    print("=" * 70)

    # Step 1: Initialize backend server
    print("\n[1/4] Starting backend API server...")
    backend_manager = await initialize_backend_server()
    if not backend_manager:
        raise RuntimeError("Failed to initialize backend server")

    # Step 2: Connect to Playwright MCP
    print("\n[2/4] Connecting to Playwright MCP...")
    playwright_mcp_tools = MCPTools(command="npx -y @playwright/mcp@latest")
    await playwright_mcp_tools.connect()
    print("✅ Playwright MCP connected")

    # Step 3: Connect to Backend Testing MCP (FastMCP)
    print("\n[3/4] Connecting to Backend API Testing MCP (FastMCP)...")
    backend_mcp_command = backend_manager.get_mcp_command()
    print(f"   Command: {backend_mcp_command}")

    backend_mcp_tools = MCPTools(command=backend_mcp_command)
    await backend_mcp_tools.connect()
    print("✅ Backend API Testing MCP connected")

    # Step 4: Create agent with BOTH tool sets
    print("\n[4/4] Creating agent with dual capabilities...")
    agent = Agent(
        name="SlackWebAndAPIAgent",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[playwright_mcp_tools, backend_mcp_tools],  # ← Both MCP tools!
        instructions="""You are a powerful automation assistant with dual capabilities:

**Web Automation (Playwright):**
- Navigate to websites
- Search for information
- Fill out forms
- Take screenshots
- Click buttons and links
- Extract data from pages

**Backend API Testing (FastMCP):**
- Test API endpoints (GET, POST, PUT, DELETE)
- Validate request/response behavior
- Run CRUD operation tests
- Execute smoke test suites
- Check error handling
- Verify data integrity
- Generate test reports

You can combine both capabilities! For example:
- Test a web page AND its backend API
- Verify frontend changes correspond to API responses
- Perform end-to-end testing

When testing APIs, use these tools:
- check_api_health() - Health check
- list_users(), get_user(), create_user(), update_user(), delete_user() - User management
- list_products(), get_product() - Product management
- search() - Search functionality
- get_statistics() - System statistics
- run_user_crud_test() - Complete CRUD test
- run_api_smoke_test() - Smoke test all endpoints

Be helpful, thorough, and clearly describe what you're doing.
If the task is unclear, ask for clarification.
        """,
        markdown=True
    )

    print("✅ Agent initialized with web automation AND API testing capabilities!")
    print("=" * 70)
    return agent


async def run_agent_task(user_message: str) -> str:
    """
    Run the agent with the user's message.

    The agent will automatically choose the appropriate tools based on the task.

    Args:
        user_message: The message from the user

    Returns:
        The agent's response
    """
    agent = await initialize_agent()

    try:
        print(f"\n📝 Processing: {user_message}")
        response = await agent.arun(user_message)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return f"{error_msg}\n\nPlease try again or rephrase your request."


@app.event("app_mention")
def handle_mention(event, say):
    """
    Handle when the bot is mentioned in Slack.

    The bot can now handle both web automation and API testing requests!
    """
    channel = event["channel"]
    user_text = event.get("text", "")

    # Extract the actual message (remove the bot mention)
    parts = user_text.split(">", 1)
    if len(parts) > 1:
        user_message = parts[1].strip()
    else:
        user_message = user_text.strip()

    if not user_message:
        say(
            text=(
                "👋 Hi! I can help with:\n"
                "• Web automation (search, navigate, screenshot)\n"
                "• Backend API testing (test endpoints, run test suites)\n"
                "\nExample commands:\n"
                "`@bot search Google for 'best restaurants'`\n"
                "`@bot test the backend API health`\n"
                "`@bot run smoke tests on all endpoints`"
            ),
            channel=channel
        )
        return

    print(f"📝 Received message: {user_message}")

    # Send initial acknowledgment
    say(text=f"🤖 Got it! Working on: '{user_message}'...", channel=channel)

    # Run the agent task
    try:
        result = asyncio.run(run_agent_task(user_message))

        # Post result back to Slack
        print(f"✅ Agent completed. Posting results...")
        say(text=f"✅ Done!\n\n{result}", channel=channel)

    except Exception as e:
        error_msg = f"❌ Error running task: {str(e)}"
        print(error_msg)
        say(text=error_msg, channel=channel)


async def cleanup():
    """Clean up MCP connections and backend server on shutdown."""
    global playwright_mcp_tools, backend_mcp_tools, backend_manager

    print("\n🔌 Closing connections and stopping servers...")

    if playwright_mcp_tools:
        print("   Closing Playwright MCP...")
        await playwright_mcp_tools.close()

    if backend_mcp_tools:
        print("   Closing Backend Testing MCP...")
        await backend_mcp_tools.close()

    if backend_manager:
        print("   Stopping backend API server...")
        backend_manager.stop_backend_server()

    print("✅ All connections closed and servers stopped")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  Enhanced Slack Bot with Agno Integration                           ║
║  • Playwright MCP (Web Automation)                                   ║
║  • FastMCP (Backend API Testing)                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    # Verify environment variables
    required_env_vars = {
        "SLACK_BOT_TOKEN": "Slack bot token",
        "SLACK_APP_TOKEN": "Slack app token",
        "ANTHROPIC_API_KEY": "Anthropic API key"
    }

    missing_vars = []
    for var_name, description in required_env_vars.items():
        if not os.environ.get(var_name):
            print(f"❌ Error: {var_name} not found in environment!")
            missing_vars.append(var_name)

    if missing_vars:
        print(f"\nMissing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables.")
        exit(1)

    print("✅ All environment variables found")

    print("\n⚡️ Starting enhanced Slack bot...")
    print("💡 Capabilities:")
    print("   • Web automation via Playwright")
    print("   • Backend API testing via FastMCP")
    print("\n💬 Mention the bot in any channel to use it")
    print("=" * 70)

    try:
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        handler.start()
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down...")
        asyncio.run(cleanup())
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        asyncio.run(cleanup())
