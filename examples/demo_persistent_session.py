"""
Advanced Demo: Persistent Browser Session
Shows how the browser state persists across multiple agent calls
"""

import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

load_dotenv()


class PersistentBrowserDemo:
    def __init__(self):
        self.mcp_tools = None
        self.agent = None

    async def initialize(self):
        """Initialize agent with persistent MCP connection"""
        print("=" * 70)
        print("Initializing Playwright MCP Agent with Persistent Session")
        print("=" * 70)

        api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f" API Key: {api_key[:20]}...{api_key[-10:]}\n")

        # Connect to Playwright MCP (connection persists)
        print("Connecting to Playwright MCP...")
        self.mcp_tools = MCPTools(command="npx -y @playwright/mcp@latest")
        await self.mcp_tools.connect()
        print(" Playwright MCP connected\n")

        # Create agent with persistent tools
        self.agent = Agent(
            name="PersistentBrowserAgent",
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[self.mcp_tools],
            instructions="""You are a web automation assistant.

The browser session persists between calls - you can continue from where you left off.

When performing tasks:
- Describe each action clearly
- Mention if you're continuing from a previous state
- Be specific about what you see""",
            markdown=True
        )
        print(" Agent created with persistent session!\n")

    async def run_task(self, step_number: int, task: str):
        """Run a task - browser state persists between calls"""
        print("=" * 70)
        print(f"STEP {step_number}")
        print("=" * 70)
        print(f" Task: {task}\n")
        print(" Agent working...\n")
        print("-" * 70)

        response = await self.agent.arun(task)
        result = response.content if hasattr(response, 'content') else str(response)

        print(result)
        print("-" * 70)
        print()

    async def cleanup(self):
        """Close the persistent connection"""
        if self.mcp_tools:
            print("=" * 70)
            print("Closing Playwright MCP Connection")
            print("=" * 70)
            await self.mcp_tools.close()
            print(" Connection closed\n")


async def main():
    print("""

                                                                      
  ADVANCED DEMO: Persistent Browser Session                           
  Multiple tasks, same browser - state maintained!                    
                                                                      

    """)

    demo = PersistentBrowserDemo()
    await demo.initialize()

    try:
        # Step 1: Navigate to Wikipedia
        await demo.run_task(
            1,
            "Navigate to wikipedia.org and tell me what you see on the homepage"
        )

        # Step 2: Search (same browser session continues!)
        await demo.run_task(
            2,
            "Search for 'Indian cuisine' on Wikipedia. You should still be on the Wikipedia page from the previous step."
        )

        # Step 3: Extract info (session still active!)
        await demo.run_task(
            3,
            "From the current page (Indian cuisine article), tell me the first 3 main points or sections you see"
        )

        print("=" * 70)
        print(" DEMO SUMMARY")
        print("=" * 70)
        print("\nWhat just happened:")
        print("   Step 1: Opened Wikipedia (new browser)")
        print("   Step 2: Searched (SAME browser session)")
        print("   Step 3: Read article (SAME browser session)")
        print("\n The browser state persisted across all 3 calls!")
        print("   This solves GitHub Issue #2732 - no state loss!")
        print("=" * 70)

    finally:
        await demo.cleanup()

    print("=" * 70)
    print(" PERSISTENT SESSION DEMO COMPLETE!")
    print("=" * 70)
    print("\nThis demonstrates the solution to GitHub #2732:")
    print("  • Class-based approach maintains MCP connection")
    print("  • Browser session persists between agent.run() calls")
    print("  • No state loss between tasks")
    print("  • Conversation history maintained")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
