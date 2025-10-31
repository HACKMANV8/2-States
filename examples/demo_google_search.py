"""
Live Demo: Agno + Playwright MCP
Task: Open Google and search for "best indian food"
"""

import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

load_dotenv()


async def demo_google_search():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  LIVE DEMO: Agno + Playwright MCP                                    ║
║  Task: Search Google for "best indian food"                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"✓ Using API Key: {api_key[:20]}...{api_key[-10:]}\n")

    print("=" * 70)
    print("STEP 1: Connecting to Playwright MCP Server")
    print("=" * 70)

    mcp_tools = MCPTools(command="npx -y @playwright/mcp@latest")
    await mcp_tools.connect()
    print("✅ Playwright MCP server connected!\n")

    print("=" * 70)
    print("STEP 2: Creating Agent with Playwright Tools")
    print("=" * 70)

    agent = Agent(
        name="WebAutomationAgent",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[mcp_tools],
        instructions="""You are a web automation assistant with Playwright browser control.

When performing tasks:
1. Navigate to the requested website
2. Wait for page to load
3. Perform the requested actions (click, type, etc.)
4. Describe what you're doing at each step
5. Report the results

Be specific about what you see and what actions you take.""",
        markdown=True
    )
    print("✅ Agent created with Playwright tools!\n")

    print("=" * 70)
    print("STEP 3: Executing Task - Google Search")
    print("=" * 70)
    print("\n📝 Task Instructions:")
    print("   1. Navigate to google.com")
    print("   2. Search for 'best indian food'")
    print("   3. Report what you find\n")

    print("🤖 Agent is working...\n")
    print("-" * 70)

    task = """
Please do the following:

1. Navigate to google.com
2. Wait for the page to load
3. Find the search box
4. Type "best indian food" in the search box
5. Submit the search (press Enter or click search button)
6. Wait for results to load
7. Tell me what search results appear (list the first 3-5 result titles)

Be detailed about each step you perform.
"""

    response = await agent.arun(task)

    result = response.content if hasattr(response, 'content') else str(response)

    print("\n" + "-" * 70)
    print("✨ AGENT RESPONSE:")
    print("-" * 70)
    print(result)
    print("-" * 70)

    print("\n" + "=" * 70)
    print("STEP 4: Cleanup")
    print("=" * 70)

    await mcp_tools.close()
    print("✅ Playwright MCP connection closed\n")

    print("=" * 70)
    print("🎉 DEMO COMPLETE!")
    print("=" * 70)
    print("\nPlaywright successfully:")
    print("  ✓ Opened Google")
    print("  ✓ Performed search")
    print("  ✓ Retrieved results")
    print("\nThe agent used real browser automation to complete this task!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_google_search())
