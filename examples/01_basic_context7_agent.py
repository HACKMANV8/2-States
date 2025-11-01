"""
Basic Agno Agent with Context7 MCP Server Integration

This example demonstrates how to create an AI agent that can fetch
live documentation from programming libraries using the Context7 MCP server.

Based on: Agno MCP Documentation
"""

import asyncio
import os
from dotenv import load_dotenv
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.anthropic import Claude

# Load environment variables
load_dotenv()


async def main():
    """
    Run the Context7 documentation agent.

    This agent can answer questions about programming libraries by fetching
    up-to-date documentation using the Context7 MCP server.
    """

    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your Anthropic API key.")
        return

    print(" Initializing Context7 MCP Agent...")
    print("=" * 60)

    # MCP server command for Context7 (public library docs)
    # This uses npx to run the Context7 MCP server without installation
    command = "npx -y @upstash/context7-mcp@latest"

    # Initialize and connect to the MCP server
    print("\n Connecting to Context7 MCP server...")
    async with MCPTools(command=command) as mcp_tools:
        print(" Successfully connected to Context7 MCP server")

        # Create an Agno agent with the MCP tools
        agent = Agent(
            name="Context7 Doc Agent",
            role="An AI agent that provides up-to-date library documentation "
                 "and code snippets using Context7 MCP.",
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[mcp_tools],
            instructions='''
You are a programming assistant with access to Context7 (a tool that fetches live documentation).

When a user asks for documentation:
1. Identify the library name (the first word/phrase of the query).
2. Use the `resolve-library-id` tool with that name to get the internal library ID.
3. Take the rest of the query as the documentation topic.
4. Use the `get-library-docs` tool with the library ID and topic to fetch relevant docs.
5. Limit results to about 5000 tokens (unless the user asks for a different amount).
6. Present the information clearly with any code snippets.

If the user asks a general question, answer it directly without using tools.
            ''',
            markdown=True
        )

        print("\n" + "=" * 60)
        print(" Agent ready! You can now ask questions about libraries.")
        print("=" * 60)

        # Example queries to demonstrate the agent
        queries = [
            "agno MCP tools usage",
            "How do I use async/await in Python?",
            "FastAPI dependency injection examples"
        ]

        # Ask user which query to run
        print("\nExample queries:")
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
        print(f"{len(queries) + 1}. Enter custom query")

        choice = input("\nSelect a query (1-4): ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(queries):
            question = queries[int(choice) - 1]
        else:
            question = input("Enter your question: ").strip()

        if not question:
            print("No question provided. Exiting.")
            return

        print(f"\n Question: {question}")
        print("=" * 60)
        print("\n Agent is thinking...\n")

        # Run the agent with the question
        response = await agent.arun(question)

        print("\n" + "=" * 60)
        print(" Agent Response:")
        print("=" * 60)
        print(response.content if hasattr(response, 'content') else str(response))
        print("\n" + "=" * 60)


if __name__ == "__main__":
    print("""
    
      Agno Agent with Context7 MCP Integration                
      Fetches live documentation for programming libraries    
    
    """)

    asyncio.run(main())
