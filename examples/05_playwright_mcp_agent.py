"""
Playwright MCP Agent with Persistent Browser Session

This solves the issue from GitHub #2732 - maintaining browser state
across multiple agent interactions using Playwright MCP.

Based on: https://github.com/agno-agi/agno/issues/2732
"""

import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

load_dotenv()


class PlaywrightMCPAgent:
    """
    Class-based approach to maintain persistent MCP session and browser state.

    This ensures the same browser session is reused across multiple agent calls,
    solving the state management problem mentioned in the GitHub issue.
    """

    def __init__(self):
        self.mcp_tools = None
        self.agent = None
        self._initialized = False

    async def initialize(self):
        """Initialize MCP connection and agent (call once)."""
        if self._initialized:
            print("  Already initialized, skipping...")
            return

        print(" Initializing Playwright MCP Agent...")
        print("-" * 70)

        # Connect to Playwright MCP server
        print(" Connecting to Playwright MCP server...")
        self.mcp_tools = MCPTools(
            command="npx -y @playwright/mcp@latest"
        )

        await self.mcp_tools.connect()
        print(" Playwright MCP server connected")

        # Create agent with persistent MCP tools
        print(" Creating agent with Playwright tools...")
        self.agent = Agent(
            name="PlaywrightAgent",
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[self.mcp_tools],
            instructions="""
You are a web automation assistant with Playwright browser control capabilities.

You can:
- Navigate to websites
- Fill out forms
- Click buttons and links
- Extract information from pages
- Take screenshots
- Maintain state across multiple interactions

Important: The browser session persists between calls, so you can continue where you left off.
            """,
            markdown=True
        )

        self._initialized = True
        print(" Agent ready with persistent browser session!\n")

    async def run(self, task: str):
        """
        Execute a task using the agent.

        The browser state persists between calls to this method.
        """
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        print(f" Task: {task}")
        print("-" * 70)

        response = await self.agent.arun(task)
        result = response.content if hasattr(response, 'content') else str(response)

        print(f"\n Response:\n{result}")
        print("-" * 70)

        return result

    async def cleanup(self):
        """Close the MCP connection and clean up resources."""
        if self.mcp_tools:
            print("\n Closing Playwright MCP connection...")
            await self.mcp_tools.close()
            print(" Connection closed")

        self._initialized = False


async def example_multi_step_workflow():
    """
    Example: Multi-step web automation with persistent browser state.

    This demonstrates solving the GitHub issue - breaking down complex tasks
    into multiple steps while maintaining the same browser session.
    """

    print("""
    
      Playwright MCP Agent - Persistent Browser Session Example      
      Solves: GitHub Issue #2732                                      
    
    """)

    # Create and initialize the agent
    agent_manager = PlaywrightMCPAgent()
    await agent_manager.initialize()

    try:
        # Step 1: Navigate to a website
        print("\n[STEP 1] Navigate to website")
        print("=" * 70)
        await agent_manager.run(
            "Navigate to example.com and tell me what you see"
        )

        # Step 2: Perform action on the same page (state persists!)
        print("\n[STEP 2] Continue with the same browser session")
        print("=" * 70)
        await agent_manager.run(
            "Take a screenshot of the page and describe the main heading"
        )

        # Step 3: Another action on the same session
        print("\n[STEP 3] Another action - state still maintained")
        print("=" * 70)
        await agent_manager.run(
            "Find all links on the page and list them"
        )

        print("\n" + "=" * 70)
        print(" Multi-step workflow completed with persistent session!")
        print("=" * 70)

    finally:
        # Always clean up
        await agent_manager.cleanup()


async def example_form_filling():
    """
    Example: Form filling across multiple steps.

    Demonstrates the use case from the GitHub issue - filling complex forms
    that require multiple interactions.
    """

    print("""
    
      Form Filling Example - Persistent Session                      
    
    """)

    agent_manager = PlaywrightMCPAgent()
    await agent_manager.initialize()

    try:
        # Example form filling workflow
        tasks = [
            "Navigate to a demo form website (you can use a test form site)",
            "Fill in the name field with 'John Doe'",
            "Fill in the email field with 'john@example.com'",
            "Submit the form",
        ]

        for i, task in enumerate(tasks, 1):
            print(f"\n[STEP {i}] {task}")
            print("=" * 70)
            await agent_manager.run(task)

        print("\n Form filling workflow completed!")

    finally:
        await agent_manager.cleanup()


async def interactive_mode():
    """
    Interactive mode - send multiple commands while maintaining browser state.
    """

    print("""
    
      Interactive Playwright Agent                                    
      Browser state persists between commands                         
    
    """)

    agent_manager = PlaywrightMCPAgent()
    await agent_manager.initialize()

    print("\nEnter commands (or 'quit' to exit):")
    print("Example commands:")
    print("  - Navigate to google.com")
    print("  - Search for 'Anthropic Claude'")
    print("  - Take a screenshot")
    print("  - Click the first result")
    print()

    try:
        while True:
            command = input(" Command: ").strip()

            if command.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break

            if not command:
                continue

            await agent_manager.run(command)
            print()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        await agent_manager.cleanup()


async def main():
    """Main function with mode selection."""

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your Anthropic API key.")
        return

    print("\nSelect mode:")
    print("1. Multi-step workflow demo (automated)")
    print("2. Form filling demo (automated)")
    print("3. Interactive mode (manual commands)")

    choice = input("\nYour choice (1-3): ").strip()

    if choice == "1":
        await example_multi_step_workflow()
    elif choice == "2":
        await example_form_filling()
    elif choice == "3":
        await interactive_mode()
    else:
        print("Invalid choice. Running multi-step workflow demo...")
        await example_multi_step_workflow()


if __name__ == "__main__":
    asyncio.run(main())
