"""
Interactive Streamlit App with Agno + MCP Integration

This Streamlit application provides an interactive interface to chat with
AI agents powered by MCP servers for documentation and code analysis.

Based on: Medium Article - Streamlit Integration
"""

import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Agno MCP Agent Assistant",
    page_icon="🤖",
    layout="wide"
)


async def initialize_agents():
    """
    Initialize agents with MCP tools.

    Returns:
        tuple: (coordinator_agent, mcp_tools_list)
    """
    # Context7 MCP for documentation
    context7_tools = MCPTools(command="npx -y @upstash/context7-mcp@latest")
    await context7_tools.connect()

    # Create documentation agent
    doc_agent = Agent(
        name="DocExpert",
        role="Documentation specialist",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[context7_tools],
        instructions="""
You are a documentation specialist with access to live library documentation via Context7.
Provide accurate, up-to-date information about programming libraries with code examples.
        """,
        markdown=True
    )

    # Create coordinator
    coordinator = Agent(
        name="Assistant",
        role="Helpful AI assistant with documentation access",
        model=Claude(id="claude-sonnet-4-20250514"),
        team=[doc_agent],
        instructions="""
You are a helpful AI assistant with access to live documentation.
When users ask about programming libraries or APIs, use your DocExpert teammate.
Provide clear, accurate, and helpful responses.
        """,
        markdown=True
    )

    return coordinator, [context7_tools]


async def get_agent_response(agent, user_message):
    """
    Get response from the agent.

    Args:
        agent: The Agno agent
        user_message: User's message

    Returns:
        str: Agent's response
    """
    response = await agent.arun(user_message)
    return response.content if hasattr(response, 'content') else str(response)


def main():
    """Main Streamlit application."""

    # Title and description
    st.title("🤖 Agno MCP Agent Assistant")
    st.markdown("""
    Chat with an AI assistant powered by **Agno** framework and **Model Context Protocol (MCP)**.
    The assistant has access to live documentation via Context7 MCP server.
    """)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check for API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("❌ ANTHROPIC_API_KEY not found!")
            st.info("Please create a `.env` file with your Anthropic API key.")
            st.stop()
        else:
            st.success("✅ API Key loaded")

        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This app demonstrates:
        - **Agno Framework**: Multi-agent orchestration
        - **MCP Integration**: Live documentation access
        - **Context7**: Programming library docs
        """)

        st.markdown("---")
        st.header("💡 Example Queries")
        st.markdown("""
        - "How do I use Agno MCP tools?"
        - "Show me FastAPI examples"
        - "Explain Python async/await"
        - "What is the Agno framework?"
        """)

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.agent = None
        st.session_state.mcp_tools = None

    # Initialize agent on first run
    if st.session_state.agent is None:
        with st.spinner("🔄 Initializing MCP Agent..."):
            try:
                # Run async initialization
                agent, mcp_tools = asyncio.run(initialize_agents())
                st.session_state.agent = agent
                st.session_state.mcp_tools = mcp_tools
                st.success("✅ Agent initialized successfully!")
            except Exception as e:
                st.error(f"❌ Error initializing agent: {str(e)}")
                st.stop()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about programming..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Get response from agent
                    response = asyncio.run(
                        get_agent_response(st.session_state.agent, prompt)
                    )

                    # Display response
                    st.markdown(response)

                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


if __name__ == "__main__":
    main()
