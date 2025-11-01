"""
Multi-Agent Team with MCP Integration

This example demonstrates how to create a team of specialized agents,
each with access to different MCP servers for specific tasks.

Based on: Medium Article - Multi-Agent MCP Integration
"""

import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

# Load environment variables
load_dotenv()


async def create_research_team():
    """
    Create a team of specialized agents with different MCP capabilities.

    Returns:
        Agent: A coordinator agent that manages the team
    """

    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables.")
        return None

    print(" Creating Multi-Agent Research Team...")
    print("=" * 60)

    # 1. Documentation Agent with Context7 MCP
    print("\n Setting up Documentation Agent with Context7...")
    context7_tools = MCPTools(command="npx -y @upstash/context7-mcp@latest")
    await context7_tools.connect()
    print(" Context7 MCP connected")

    doc_agent = Agent(
        name="DocExpert",
        role="Documentation and code reference specialist",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[context7_tools],
        instructions="""
You are a documentation specialist with access to Context7.

Your responsibilities:
1. Fetch accurate, up-to-date documentation for programming libraries
2. Provide code examples and best practices
3. Explain API usage and parameters
4. Use the resolve-library-id and get-library-docs tools when needed

Always cite your sources and provide clear, concise explanations.
        """,
        markdown=True
    )

    # 2. Filesystem Agent for local code analysis
    print(" Setting up Filesystem Agent...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filesystem_tools = MCPTools(
        command=f"npx -y @modelcontextprotocol/server-filesystem {current_dir}"
    )
    await filesystem_tools.connect()
    print(" Filesystem MCP connected")

    code_agent = Agent(
        name="CodeAnalyzer",
        role="Local codebase analysis specialist",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[filesystem_tools],
        instructions="""
You are a code analysis specialist with filesystem access.

Your responsibilities:
1. Explore and analyze local code files
2. Find patterns, dependencies, and code structure
3. Review file contents and provide summaries
4. Identify issues or improvement opportunities

Be thorough and provide actionable insights.
        """,
        markdown=True
    )

    # 3. Coordinator Agent (Team Leader)
    print(" Setting up Coordinator Agent...")
    coordinator = Agent(
        name="ResearchCoordinator",
        role="Research team coordinator and synthesizer",
        model=Claude(id="claude-sonnet-4-20250514"),
        team=[doc_agent, code_agent],
        instructions="""
You are a research coordinator managing a team of specialized agents.

Your team consists of:
1. DocExpert - Fetches library documentation and API references
2. CodeAnalyzer - Analyzes local code files and structure

Your responsibilities:
1. Analyze user queries and determine which agents to involve
2. Delegate tasks to appropriate team members
3. Synthesize information from multiple agents
4. Provide comprehensive, well-organized answers

Approach:
- For documentation questions: Use DocExpert
- For local code questions: Use CodeAnalyzer
- For complex questions: Coordinate between both agents
- Always provide a clear, unified response

Present your findings in a well-structured format with clear sections.
        """,
        markdown=True
    )

    print(" Team setup complete!")
    print("\nTeam Members:")
    print("  1.  DocExpert (Context7 MCP)")
    print("  2.  CodeAnalyzer (Filesystem MCP)")
    print("  3.  ResearchCoordinator (Team Lead)")

    return coordinator, [context7_tools, filesystem_tools]


async def main():
    """Main function to run the multi-agent team."""

    print("""
    
      Multi-Agent Research Team with MCP Integration          
      Combines documentation and code analysis capabilities   
    
    """)

    # Create the research team
    result = await create_research_team()
    if result is None:
        return

    coordinator, mcp_tools_list = result

    try:
        print("\n" + "=" * 60)
        print(" Research Team Ready!")
        print("=" * 60)

        # Example research questions
        questions = [
            "How does the Agno framework implement MCP tools? Check the documentation and analyze any local files related to this.",
            "What Python files do we have in this project and what do they do?",
            "Explain how to use async/await in Python with Agno agents, and check if we have any examples in our local files.",
            "Compare the Context7 MCP integration approach in the official docs vs our implementation"
        ]

        print("\nExample research questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q[:80]}...")

        print(f"{len(questions) + 1}. Enter custom question")

        choice = input("\nSelect a question (1-5): ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(questions):
            question = questions[int(choice) - 1]
        else:
            question = input("Enter your research question: ").strip()

        if not question:
            print("No question provided. Exiting.")
            return

        print(f"\n Research Question:")
        print(f"   {question}")
        print("=" * 60)
        print("\n Team is collaborating...\n")

        # Run the coordinator agent
        response = await coordinator.arun(question)

        print("\n" + "=" * 60)
        print(" Team Research Results:")
        print("=" * 60)
        print(response.content if hasattr(response, 'content') else str(response))
        print("\n" + "=" * 60)

    finally:
        # Close all MCP connections
        print("\n Closing all MCP connections...")
        for mcp_tool in mcp_tools_list:
            await mcp_tool.close()
        print(" All connections closed")


if __name__ == "__main__":
    asyncio.run(main())
