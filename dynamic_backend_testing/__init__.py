"""
Dynamic Backend API Testing with FastMCP

This module provides a flexible orchestration system that dynamically loads,
wraps, and tests user-submitted backend APIs as MCP servers using FastMCP.

Key Features:
- Accept dynamic user inputs (repo URLs, branches, PRs)
- Checkout and load user API code at runtime
- Auto-generate MCP wrappers from OpenAPI specs
- Manage server lifecycle dynamically
- Integrate with Agno agents for automated testing

Components:
- RepoManager: Git operations, repo checkout
- APIDiscoveryService: Inspect apps, extract OpenAPI specs
- MCPGenerator: Generate MCP tools from API specs
- DynamicServerManager: Manage server lifecycle
- Orchestrator: Main coordination logic

Usage:
    from dynamic_backend_testing import DynamicBackendOrchestrator

    orchestrator = DynamicBackendOrchestrator()
    result = await orchestrator.test_repo(
        repo_url="https://github.com/user/api-repo",
        branch="feature-branch"
    )
"""

__version__ = "1.0.0"
__author__ = "AI Agent Team"

from .orchestrator import DynamicBackendOrchestrator
from .repo_manager import RepoManager
from .api_discovery import APIDiscoveryService
from .mcp_generator import MCPGenerator
from .dynamic_server_manager import DynamicServerManager

__all__ = [
    "DynamicBackendOrchestrator",
    "RepoManager",
    "APIDiscoveryService",
    "MCPGenerator",
    "DynamicServerManager",
]
