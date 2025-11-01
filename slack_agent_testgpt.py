"""
TestGPT Slack Bot - Multi-Environment QA Testing

Advanced Slack bot that performs comprehensive QA testing across:
- Multiple viewports (iPhone, iPad, desktop, etc.)
- Multiple browsers (Chrome, Safari/WebKit, Firefox)
- Multiple network conditions (normal, slow 3G, flaky)

When mentioned in Slack, the bot:
1. Parses the test request
2. Builds a test matrix (scenario × viewport × browser × network)
3. Executes all combinations using Playwright MCP
4. Aggregates results and prioritizes failures
5. Posts formatted summary back to Slack
6. Saves scenarios for re-running
"""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
import os
from dotenv import load_dotenv
from agno.tools.mcp import MCPTools

# Import TestGPT engine
from testgpt_engine import TestGPTEngine

load_dotenv()

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Global variables
mcp_tools = None
testgpt_engine = None


async def initialize_testgpt():
    """Initialize the TestGPT engine with Playwright MCP tools."""
    global mcp_tools, testgpt_engine

    if testgpt_engine is not None:
        return testgpt_engine

    print("\n" + "=" * 70)
    print(" Initializing TestGPT Engine")
    print("=" * 70)

    # Connect to Playwright MCP
    print(" Connecting to Playwright MCP...")
    mcp_tools = MCPTools(command="npx -y @playwright/mcp@latest")
    await mcp_tools.connect()
    print(" Playwright MCP connected\n")

    # Create TestGPT engine
    print(" Initializing TestGPT orchestration engine...")
    testgpt_engine = TestGPTEngine(mcp_tools=mcp_tools, storage_dir="./testgpt_data")
    print(" TestGPT engine initialized\n")

    print("=" * 70)
    print(" TestGPT Ready for Multi-Environment Testing")
    print("=" * 70 + "\n")

    return testgpt_engine


async def run_testgpt_task(user_message: str, user_id: str) -> str:
    """
    Run a TestGPT task from user message.

    Args:
        user_message: The test request from user
        user_id: Slack user ID

    Returns:
        Formatted test results
    """
    engine = await initialize_testgpt()

    try:
        # Special commands
        if "list scenarios" in user_message.lower() or "show scenarios" in user_message.lower():
            return engine.get_scenario_library()

        if "help" in user_message.lower() and len(user_message.split()) < 5:
            return get_help_message()

        # Process test request
        result = await engine.process_test_request(user_message, user_id)
        return result

    except Exception as e:
        return f" Error: {str(e)}\n\nPlease try again or rephrase your request."


@app.event("app_mention")
def handle_mention(event, say):
    """Handle when the bot is mentioned in Slack."""
    channel = event["channel"]
    user_id = event.get("user", "unknown")
    user_text = event.get("text", "")

    # Extract the actual message (remove the bot mention)
    parts = user_text.split(">", 1)
    if len(parts) > 1:
        user_message = parts[1].strip()
    else:
        user_message = user_text.strip()

    if not user_message:
        say(text=get_welcome_message(), channel=channel)
        return

    print(f"\n Received message from user {user_id}: {user_message}")

    # Send initial acknowledgment
    say(text=f" TestGPT received your request!\n\nAnalyzing: '{user_message}'\n\nProcessing...", channel=channel)

    # Run TestGPT task
    try:
        result = asyncio.run(run_testgpt_task(user_message, user_id))

        # Post result back to Slack
        print(f" TestGPT completed. Posting results to Slack...")
        say(text=result, channel=channel)

    except Exception as e:
        error_msg = f" Error running TestGPT: {str(e)}"
        print(error_msg)
        say(text=error_msg, channel=channel)


def get_welcome_message() -> str:
    """Get welcome message for bot."""
    return """ **Welcome to TestGPT!**

I'm your AI-powered QA testing assistant. I can run comprehensive cross-browser,
cross-device, and cross-network tests on your websites.

**Example commands:**

• `test pointblank.club responsive on safari and iphone`
• `run checkout flow on chrome desktop and ipad under slow network`
• `check if pricing modal works on brave and safari`
• `test landing page on mobile and desktop with bad network`
• `re-run pointblank responsive test`
• `list scenarios` - See all saved test scenarios

**What I test:**
 Multiple viewports (iPhone, iPad, desktop, etc.)
 Multiple browsers (Chrome, Safari, Firefox)
 Network conditions (normal, slow 3G, flaky)
 Responsive design issues
 Cross-browser compatibility
 Performance under network constraints

Try mentioning me with a test request!
"""


def get_help_message() -> str:
    """Get help message."""
    return """ **TestGPT Help**

**How to use:**
Mention me with a natural language test request. I'll automatically:
1. Parse what you want to test
2. Build a test matrix (multiple viewports × browsers × networks)
3. Run all combinations
4. Report failures by priority

**Keywords I understand:**

*Viewports:*
• mobile, iPhone, iPad, tablet, desktop, responsive

*Browsers:*
• Safari, Chrome, Brave, Firefox, cross-browser, iOS

*Networks:*
• slow network, bad network, 3G, flaky, unstable

**Example requests:**

• "test pointblank.club on safari iphone and chrome desktop"
  → Tests 2 browser × 2 viewport combinations

• "check responsive behavior under slow network"
  → Tests mobile+tablet+desktop on slow 3G

• "run landing page test on safari and brave"
  → Cross-browser test with Safari + Chromium

**Special features:**

• All tests are automatically saved for re-running
• Type `list scenarios` to see saved tests
• Type `re-run [name]` to re-execute a saved test
• Safari failures are prioritized (our demo showcase)

**Demo site:** pointblank.club
• Pre-configured for demonstrating Safari vs Chrome issues
• Always includes Safari when testing this site
"""


async def cleanup():
    """Clean up MCP connection on shutdown."""
    global mcp_tools
    if mcp_tools:
        print("\n Closing Playwright MCP connection...")
        await mcp_tools.close()
        print(" Connection closed")


if __name__ == "__main__":
    print("""

                                                                      
  TestGPT - Multi-Environment QA Testing Agent                       
                                                                      
  Powered by: Agno + Playwright MCP + Claude Sonnet 4                
                                                                      

    """)

    # Verify environment variables
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print(" Error: SLACK_BOT_TOKEN not found in environment!")
        exit(1)

    if not os.environ.get("SLACK_APP_TOKEN"):
        print(" Error: SLACK_APP_TOKEN not found in environment!")
        exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(" Error: ANTHROPIC_API_KEY not found in environment!")
        exit(1)

    print(" All environment variables found")
    print("\n Starting TestGPT Slack bot...")
    print(" Mention the bot in any channel to trigger QA testing")
    print("=" * 70)

    try:
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        handler.start()
    except KeyboardInterrupt:
        print("\n\n  Shutting down...")
        asyncio.run(cleanup())
        print(" Goodbye!")
    except Exception as e:
        print(f"\n Error: {e}")
        asyncio.run(cleanup())
