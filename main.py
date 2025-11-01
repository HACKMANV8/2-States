"""
TestGPT Main Entrypoint

Central application launcher that handles:
- Slack bot integration (current)
- GitHub webhook triggers (future)
- Web UI triggers (future)
- API endpoints (future)

This is the single entrypoint for running TestGPT.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_banner():
    """Print TestGPT banner."""
    print("""

                                                                      
  TestGPT - Multi-Environment QA Testing Platform                    
                                                                      
  Powered by: Agno + Playwright MCP + Claude Sonnet 4                
                                                                      

    """)


def verify_environment():
    """Verify all required environment variables are present."""
    required_vars = {
        "SLACK_BOT_TOKEN": "Slack Bot Token (xoxb-...)",
        "SLACK_APP_TOKEN": "Slack App Token (xapp-...)",
        "ANTHROPIC_API_KEY": "Anthropic API Key (sk-ant-...)"
    }

    missing = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing.append(f"   {var} - {description}")

    if missing:
        print(" Missing required environment variables:\n")
        print("\n".join(missing))
        print("\n Please configure these in your .env file")
        return False

    print(" All environment variables found")
    return True


async def start_slack_bot():
    """Start the Slack bot listener."""
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    from agno.tools.mcp import MCPTools
    from testgpt_engine import TestGPTEngine
    import warnings
    import sys

    # Suppress MCP async generator cleanup warnings (cosmetic issue with stdio connections)
    def asyncio_exception_handler(loop, context):
        exception = context.get("exception")
        message = context.get("message", "")

        # Suppress specific MCP cleanup errors that are cosmetic
        if exception and isinstance(exception, RuntimeError):
            if "cancel scope" in str(exception):
                return  # Silently ignore

        # Suppress async generator cleanup warnings
        if "asyncgen" in str(context) or "stdio_client" in str(message):
            return  # Silently ignore

        # For other errors, use default handling
        loop.default_exception_handler(context)

    # Set the exception handler for the event loop
    import asyncio
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(asyncio_exception_handler)

    print("\n Starting TestGPT Slack bot...")
    print(" Mention the bot in any channel to trigger QA testing")
    print("=" * 70)

    # Initialize Slack app
    app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

    # Global variables for MCP and engine
    mcp_tools = None
    testgpt_engine = None

    async def initialize_testgpt():
        """Initialize the TestGPT engine with Playwright MCP tools."""
        nonlocal mcp_tools, testgpt_engine

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
        """Run a TestGPT task from user message."""
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
            import traceback
            error_details = traceback.format_exc()
            print(f" Error in run_testgpt_task: {error_details}")
            return f" Error: {str(e)}\n\nPlease try again or rephrase your request."

    # Track processed events to prevent duplicates
    processed_events = set()

    @app.event("app_mention")
    def handle_mention(event, say):
        """Handle when the bot is mentioned in Slack."""
        import time

        # Get event timestamp
        event_id = event.get("event_ts") or event.get("ts")
        event_ts = float(event_id) if event_id else time.time()
        current_time = time.time()

        # Ignore events older than 5 minutes (300 seconds)
        # This prevents processing old messages if bot restarts or Slack retries
        age_seconds = current_time - event_ts
        if age_seconds > 300:
            print(f"  Skipping old event (age: {age_seconds:.1f}s): {event_id}")
            return

        # Deduplicate events (Slack may retry)
        if event_id in processed_events:
            print(f"  Skipping duplicate event: {event_id}")
            return

        processed_events.add(event_id)
        # Keep only last 1000 event IDs to prevent memory leak
        if len(processed_events) > 1000:
            processed_events.clear()

        channel = event["channel"]
        user_id = event.get("user", "unknown")
        user_text = event.get("text", "")

        print(f"\n Event ID: {event_id}, Age: {age_seconds:.1f}s")

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
            import traceback
            error_details = traceback.format_exc()
            print(f" Error in handle_mention: {error_details}")
            error_msg = f" Error running TestGPT: {str(e)}"
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
• `list scenarios` - See all saved test scenarios

**What I test:**
 Multiple viewports (iPhone, iPad, desktop, etc.)
 Multiple browsers (Chrome, Safari, Firefox)
 Network conditions (normal, slow 3G, flaky)

Try mentioning me with a test request!
"""

    def get_help_message() -> str:
        """Get help message."""
        return """ **TestGPT Help**

**How to use:**
Mention me with a natural language test request.

**Example requests:**
• "test pointblank.club on safari iphone and chrome desktop"
• "check responsive behavior under slow network"
• "run landing page test on safari and brave"

**Special commands:**
• `list scenarios` - See saved tests
• `re-run [name]` - Re-execute a saved test

**Demo site:** pointblank.club
"""

    # Start the bot
    try:
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        handler.start()
    except KeyboardInterrupt:
        print("\n\n  Shutting down...")
        # Cleanup will happen automatically
        print(" Goodbye!")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()


async def start_github_webhooks():
    """Start GitHub webhook listener (future)."""
    print("\n GitHub webhooks not yet implemented")
    print("   Will be available in future version")


async def start_web_ui():
    """Start web UI server (future)."""
    print("\n Web UI not yet implemented")
    print("   Will be available in future version")


def main():
    """Main entrypoint."""
    print_banner()

    # Verify environment
    if not verify_environment():
        sys.exit(1)

    # Parse command line arguments (future: support different modes)
    mode = "slack"  # Default to Slack bot for now

    if len(sys.argv) > 1:
        mode = sys.argv[1]

    print(f"\n Starting in mode: {mode}")

    # Start appropriate service
    if mode == "slack":
        asyncio.run(start_slack_bot())
    elif mode == "github":
        asyncio.run(start_github_webhooks())
    elif mode == "web":
        asyncio.run(start_web_ui())
    else:
        print(f" Unknown mode: {mode}")
        print("\nAvailable modes:")
        print("  - slack (default)")
        print("  - github (coming soon)")
        print("  - web (coming soon)")
        sys.exit(1)


if __name__ == "__main__":
    main()
