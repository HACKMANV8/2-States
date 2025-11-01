"""
Test Playwright MCP Connection

Verifies that Playwright MCP server can be installed and connected.
This test doesn't require an API key - just verifies MCP server access.
"""

import asyncio
from agno.tools.mcp import MCPTools


async def test_playwright_mcp_connection():
    print("=" * 70)
    print("PLAYWRIGHT MCP CONNECTION TEST")
    print("=" * 70)

    print("\n[TEST 1] Installing and connecting to Playwright MCP server...")
    print("(This may take a minute on first run - downloading packages)")
    print("-" * 70)

    try:
        # Connect to Playwright MCP server
        mcp_tools = MCPTools(
            command="npx -y @playwright/mcp@latest"
        )

        await mcp_tools.connect()
        print(" Playwright MCP server connected successfully!")

        # Check available tools
        print("\n[TEST 2] Available Playwright tools:")
        print("-" * 70)

        if hasattr(mcp_tools, 'tools') and mcp_tools.tools:
            print(f"Found {len(mcp_tools.tools)} tools:\n")
            for i, tool in enumerate(mcp_tools.tools, 1):
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                tool_desc = tool.description if hasattr(tool, 'description') else "No description"
                print(f"{i}. {tool_name}")
                print(f"   {tool_desc[:100]}...")
                print()
        else:
            # Try alternative way to access tools
            print("Tools not directly accessible via .tools attribute")
            print("But connection successful - tools available to agent")

        # Close connection
        print("\n[TEST 3] Closing connection...")
        print("-" * 70)
        await mcp_tools.close()
        print(" Connection closed successfully")

        print("\n" + "=" * 70)
        print("SUCCESS: Playwright MCP is ready to use!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Add your ANTHROPIC_API_KEY to .env")
        print("2. Run: python 05_playwright_mcp_agent.py")
        print("=" * 70)

    except Exception as e:
        print(f" Error: {e}")
        print("\nTroubleshooting:")
        print("- Ensure Node.js and npm are installed")
        print("- Check internet connection")
        print("- Try running: npx -y @playwright/mcp@latest")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(test_playwright_mcp_connection())
