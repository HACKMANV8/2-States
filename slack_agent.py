"""
Slack Bot with Agno Agent Integration

When mentioned in Slack, triggers AI agent with Playwright MCP capabilities
and posts results back to the Slack channel.
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

load_dotenv()

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Global variables for MCP connection (persistent across mentions)
mcp_tools = None
agent = None


async def initialize_agent():
    """Initialize the agent with Playwright MCP tools (once)."""
    global mcp_tools, agent

    if agent is not None:
        return agent

    print("🔧 Initializing Playwright MCP Agent...")

    # Connect to Playwright MCP
    mcp_tools = MCPTools(command="npx -y @playwright/mcp@latest")
    await mcp_tools.connect()
    print("✅ Playwright MCP connected")

    # Create agent with Playwright tools
    agent = Agent(
        name="SlackWebAgent",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[mcp_tools],
        instructions="""You are a helpful web automation assistant running in Slack.

When users ask you to do web tasks:
- Navigate to websites
- Search for information
- Extract data from pages
- Fill out forms
- Take screenshots

Be concise and helpful. Always describe what you're doing.

If the task is unclear, ask for clarification.""",
        markdown=True
    )

    print("✅ Agent initialized")
    return agent


async def run_agent_task(user_message: str) -> str:
    """
    Run the agent with the user's message.

    Args:
        user_message: The message from the user

    Returns:
        The agent's response
    """
    agent = await initialize_agent()

    try:
        response = await agent.arun(user_message)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try again or rephrase your request."


@app.event("app_mention")
def handle_mention(event, say):
    """Handle when the bot is mentioned in Slack."""
    channel = event["channel"]
    user_text = event.get("text", "")

    # Extract the actual message (remove the bot mention)
    # Format: "<@BOT_ID> actual message here"
    parts = user_text.split(">", 1)
    if len(parts) > 1:
        user_message = parts[1].strip()
    else:
        user_message = user_text.strip()

    if not user_message:
        say(text="👋 Hi! Mention me with a task and I'll help you with web automation!", channel=channel)
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
    """Clean up MCP connection on shutdown."""
    global mcp_tools
    if mcp_tools:
        print("\n🔌 Closing Playwright MCP connection...")
        await mcp_tools.close()
        print("✅ Connection closed")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  Slack Bot with Agno + Playwright MCP Integration                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    # Verify environment variables
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("❌ Error: SLACK_BOT_TOKEN not found in environment!")
        exit(1)

    if not os.environ.get("SLACK_APP_TOKEN"):
        print("❌ Error: SLACK_APP_TOKEN not found in environment!")
        exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment!")
        exit(1)

    print("✅ All environment variables found")
    print("\n⚡️ Starting Slack bot...")
    print("💡 Mention the bot in any channel to trigger the agent")
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
