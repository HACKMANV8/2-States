"""
Filesystem Agent with MCP Integration

This example demonstrates how to create an AI agent that can explore
and analyze files using the Filesystem MCP server.

Based on: Agno MCP Documentation - Filesystem Example
"""

import asyncio
import os
from pathlib import Path
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

# Load environment variables
load_dotenv()


async def run_agent(message: str, directory_path: str) -> None:
    """
    Run the filesystem agent with the given message.

    Args:
        message: The question or task for the agent
        directory_path: The directory the agent can explore
    """

    # Verify the directory exists
    if not os.path.exists(directory_path):
        print(f"ERROR: Directory '{directory_path}' does not exist.")
        return

    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your Anthropic API key.")
        return

    print(f"🚀 Initializing Filesystem Agent...")
    print(f"📁 Directory: {directory_path}")
    print("=" * 60)

    # Initialize and connect to the MCP server to access the filesystem
    print("\n📡 Connecting to Filesystem MCP server...")
    mcp_tools = MCPTools(
        command=f"npx -y @modelcontextprotocol/server-filesystem {directory_path}"
    )
    await mcp_tools.connect()

    try:
        print("✅ Successfully connected to Filesystem MCP server")

        agent = Agent(
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[mcp_tools],
            instructions=dedent("""\
                You are a filesystem assistant. Help users explore files and directories.

                - Navigate the filesystem to answer questions
                - Use the list_allowed_directories tool to find directories that you can access
                - Provide clear context about files you examine
                - Use headings to organize your responses
                - Be concise and focus on relevant information\
            """),
            markdown=True
        )

        print("\n" + "=" * 60)
        print("🤖 Agent ready!")
        print("=" * 60)
        print(f"\n📝 Task: {message}")
        print("=" * 60)
        print("\n💭 Agent is working...\n")

        # Run the agent
        response = await agent.arun(message)

        print("\n" + "=" * 60)
        print("✨ Agent Response:")
        print("=" * 60)
        print(response.content if hasattr(response, 'content') else str(response))
        print("\n" + "=" * 60)

    finally:
        # Always close the connection when done
        print("\n🔌 Closing MCP connection...")
        await mcp_tools.close()
        print("✅ Connection closed")


async def main():
    """Main function to run filesystem agent examples."""

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  Agno Filesystem Agent with MCP Integration             ║
    ║  Explores and analyzes files in a directory              ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Get the current project directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"\nCurrent project directory: {current_dir}")
    print("\nExample tasks:")
    print("1. List all Python files in this directory")
    print("2. Summarize the requirements.txt file")
    print("3. Count the number of files")
    print("4. Find all files containing 'agno'")
    print("5. Enter custom task")

    choice = input("\nSelect a task (1-5): ").strip()

    tasks = {
        "1": "List all Python files in this directory",
        "2": "Read and summarize the requirements.txt file",
        "3": "Count the total number of files in this directory",
        "4": "Find all files that contain the word 'agno' in their content or filename"
    }

    if choice in tasks:
        task = tasks[choice]
    elif choice == "5":
        task = input("Enter your task: ").strip()
    else:
        task = "List all files and give me a summary of this directory"

    if not task:
        print("No task provided. Exiting.")
        return

    # Run the agent
    await run_agent(task, current_dir)


if __name__ == "__main__":
    asyncio.run(main())
