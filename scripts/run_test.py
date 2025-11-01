"""Quick test of the Context7 agent"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.anthropic import Claude

load_dotenv()

async def quick_test():
    print("Testing Agno + Claude + MCP...")
    print(f"API Key present: {bool(os.getenv('ANTHROPIC_API_KEY'))}")

    # Simple test without MCP first
    print("\n1. Testing Claude model...")
    simple_agent = Agent(
        name="TestAgent",
        model=Claude(id="claude-sonnet-4-20250514"),
    )
    response = await simple_agent.arun("Say 'Hello from Claude!' and nothing else.")
    print(f"Response: {response.content if hasattr(response, 'content') else response}")

    print("\n Basic agent works!")
    print("\nNow you can run the full examples:")
    print("  python 01_basic_context7_agent.py")
    print("  python 02_filesystem_agent.py")
    print("  python 03_multi_agent_team.py")
    print("  streamlit run 04_streamlit_app.py")

if __name__ == "__main__":
    asyncio.run(quick_test())
