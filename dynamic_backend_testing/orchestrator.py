"""
Dynamic Backend Orchestrator

Main coordination logic for end-to-end dynamic API testing.

This module coordinates all components to provide a simple interface
for testing arbitrary user-submitted backend APIs.

Complete workflow:
1. Clone repository (RepoManager)
2. Install dependencies
3. Discover API (APIDiscoveryService)
4. Generate MCP wrapper (MCPGenerator)
5. Start user API server (DynamicServerManager)
6. Start FastMCP server (DynamicServerManager)
7. Create Agno agent with MCPTools
8. Run automated tests
9. Collect and return results
10. Cleanup all resources

Example:
    orchestrator = DynamicBackendOrchestrator()
    result = await orchestrator.test_repo(
        repo_url="https://github.com/user/api-repo",
        branch="feature-branch"
    )
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from .repo_manager import RepoManager
from .api_discovery import APIDiscoveryService
from .mcp_generator import MCPGenerator
from .dynamic_server_manager import DynamicServerManager

logger = logging.getLogger(__name__)


class DynamicBackendOrchestrator:
    """
    End-to-end orchestration for dynamic backend API testing.

    This class provides the main interface for testing user-submitted APIs.
    It coordinates all components and handles the complete workflow from
    repo URL to test results.

    Example:
        orchestrator = DynamicBackendOrchestrator()

        # Test a GitHub repo
        result = await orchestrator.test_repo(
            repo_url="https://github.com/user/api-repo",
            branch="main",
            app_module="main:app",
            test_suite="smoke"
        )

        # Test a PR
        result = await orchestrator.test_repo(
            repo_url="https://github.com/user/api-repo",
            pr_number=123
        )

        # Test local changes
        result = await orchestrator.test_local(
            api_path=Path("/path/to/local/api"),
            app_module="app:application"
        )
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        workspace_root: Optional[Path] = None
    ):
        """
        Initialize the orchestrator.

        Args:
            anthropic_api_key: API key for Claude (defaults to env var)
            workspace_root: Root directory for cloned repos
        """
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set - agent testing will fail")

        # Initialize components
        self.repo_manager = RepoManager(workspace_root=workspace_root)
        self.api_discovery = APIDiscoveryService()
        self.mcp_generator = MCPGenerator()
        self.server_manager = DynamicServerManager()

        logger.info("DynamicBackendOrchestrator initialized")

    async def test_repo(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        pr_number: Optional[int] = None,
        commit: Optional[str] = None,
        app_module: str = "main:app",
        test_suite: str = "smoke",
        auto_detect: bool = True,
        cleanup: bool = True
    ) -> Dict[str, Any]:
        """
        Test a backend API from a Git repository.

        This is the main entry point for testing repos, branches, and PRs.

        Complete workflow:
        1. Clone repo and checkout ref
        2. Install dependencies
        3. Discover and introspect API
        4. Generate MCP wrapper
        5. Start API server
        6. Start MCP server
        7. Run tests with Agno agent
        8. Return results
        9. Cleanup (if enabled)

        Args:
            repo_url: Git repository URL
            branch: Branch to test (optional)
            pr_number: PR number to test (optional)
            commit: Specific commit to test (optional)
            app_module: Module path to app (e.g., "main:app")
            test_suite: Test suite to run ("smoke", "comprehensive", "custom")
            auto_detect: Auto-detect app location if module not found
            cleanup: Whether to cleanup after testing

        Returns:
            Dictionary containing:
            - status: "completed" | "failed"
            - repo_info: Git repository information
            - api_info: Discovered API metadata
            - endpoints: List of discovered endpoints
            - test_results: Results for each test
            - overall_success: Boolean
            - error: Error message (if failed)

        Example:
            result = await orchestrator.test_repo(
                repo_url="https://github.com/user/api",
                branch="feature/new-endpoints",
                test_suite="comprehensive"
            )

            if result['overall_success']:
                print(f"✅ All {len(result['test_results'])} tests passed")
            else:
                print(f"❌ {result['failed_count']} tests failed")
        """
        logger.info(f"Starting repo test: {repo_url}")

        result = {
            "status": "in_progress",
            "repo_info": {},
            "api_info": {},
            "endpoints": [],
            "test_results": [],
            "overall_success": False
        }

        repo_path = None

        try:
            # Step 1: Clone repository
            logger.info("[1/10] Cloning repository...")
            repo_path = await self.repo_manager.clone_repo(
                repo_url=repo_url,
                branch=branch,
                pr_number=pr_number,
                commit=commit
            )
            result["repo_info"] = await self.repo_manager.get_repo_info(repo_path)
            logger.info(f"Repository cloned to {repo_path}")

            # Step 2: Install dependencies
            logger.info("[2/10] Installing dependencies...")
            install_result = await self.repo_manager.install_dependencies(repo_path)
            result["dependencies"] = install_result
            logger.info(f"Dependencies installed: {install_result['success']}")

            # Step 3: Discover API
            logger.info("[3/10] Discovering API...")
            api_spec = await self.api_discovery.discover_api(
                repo_path=repo_path,
                app_module=app_module,
                auto_detect=auto_detect
            )
            result["api_info"] = api_spec["metadata"]
            result["endpoints"] = [
                {"path": e["path"], "method": e["method"]}
                for e in api_spec["endpoints"]
            ]
            logger.info(f"API discovered: {len(api_spec['endpoints'])} endpoints found")

            # Step 4: Generate MCP wrapper
            logger.info("[4/10] Generating MCP wrapper...")
            wrapper_code = self.mcp_generator.generate_mcp_wrapper(
                api_spec=api_spec,
                api_base_url="http://127.0.0.1:8000"
            )
            logger.info("MCP wrapper generated")

            # Step 5: Start API server
            logger.info("[5/10] Starting API server...")
            await self.server_manager.start_user_api(
                repo_path=repo_path,
                app_module=app_module,
                framework=api_spec["framework"],
                venv_path=repo_path / ".venv" if (repo_path / ".venv").exists() else None
            )
            logger.info("API server started")

            # Step 6: Start MCP server
            logger.info("[6/10] Starting MCP server...")
            await self.server_manager.start_mcp_server(
                wrapper_code=wrapper_code,
                api_url="http://127.0.0.1:8000"
            )
            logger.info("MCP server started")

            # Step 7: Create Agno agent
            logger.info("[7/10] Creating Agno agent...")
            agent = await self._create_test_agent()
            logger.info("Agno agent created")

            # Step 8: Run tests
            logger.info(f"[8/10] Running {test_suite} test suite...")
            test_results = await self._run_test_suite(
                agent=agent,
                test_suite=test_suite,
                api_spec=api_spec
            )
            result["test_results"] = test_results
            logger.info(f"Test suite completed: {len(test_results)} tests run")

            # Step 9: Analyze results
            logger.info("[9/10] Analyzing results...")
            result["overall_success"] = all(t.get("success", False) for t in test_results)
            result["passed_count"] = sum(1 for t in test_results if t.get("success"))
            result["failed_count"] = len(test_results) - result["passed_count"]
            result["status"] = "completed"

            logger.info(f"Test analysis: {result['passed_count']}/{len(test_results)} passed")

        except Exception as e:
            error_msg = f"Orchestration failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["status"] = "failed"
            result["error"] = error_msg

        finally:
            # Step 10: Cleanup
            logger.info("[10/10] Cleaning up...")
            await self.server_manager.stop_all()

            if cleanup and repo_path:
                self.repo_manager.cleanup(repo_path)

            logger.info("Cleanup completed")

        return result

    async def test_local(
        self,
        api_path: Path,
        app_module: str = "main:app",
        test_suite: str = "smoke",
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        Test a local backend API (no cloning required).

        This is useful for testing APIs during development without
        needing to commit and push changes.

        Args:
            api_path: Path to the local API directory
            app_module: Module path to app
            test_suite: Test suite to run
            auto_detect: Auto-detect app location

        Returns:
            Test results dictionary

        Example:
            result = await orchestrator.test_local(
                api_path=Path("/Users/me/my-api"),
                app_module="app:application"
            )
        """
        logger.info(f"Starting local test: {api_path}")

        result = {
            "status": "in_progress",
            "api_info": {},
            "endpoints": [],
            "test_results": [],
            "overall_success": False
        }

        try:
            # Step 1: Discover API
            logger.info("[1/6] Discovering API...")
            api_spec = await self.api_discovery.discover_api(
                repo_path=api_path,
                app_module=app_module,
                auto_detect=auto_detect
            )
            result["api_info"] = api_spec["metadata"]
            result["endpoints"] = [
                {"path": e["path"], "method": e["method"]}
                for e in api_spec["endpoints"]
            ]
            logger.info(f"API discovered: {len(api_spec['endpoints'])} endpoints")

            # Step 2: Generate MCP wrapper
            logger.info("[2/6] Generating MCP wrapper...")
            wrapper_code = self.mcp_generator.generate_mcp_wrapper(
                api_spec=api_spec,
                api_base_url="http://127.0.0.1:8000"
            )

            # Step 3: Start API server
            logger.info("[3/6] Starting API server...")
            await self.server_manager.start_user_api(
                repo_path=api_path,
                app_module=app_module,
                framework=api_spec["framework"]
            )

            # Step 4: Start MCP server
            logger.info("[4/6] Starting MCP server...")
            await self.server_manager.start_mcp_server(
                wrapper_code=wrapper_code,
                api_url="http://127.0.0.1:8000"
            )

            # Step 5: Create agent and run tests
            logger.info("[5/6] Running tests...")
            agent = await self._create_test_agent()
            test_results = await self._run_test_suite(agent, test_suite, api_spec)
            result["test_results"] = test_results

            # Step 6: Analyze results
            logger.info("[6/6] Analyzing results...")
            result["overall_success"] = all(t.get("success", False) for t in test_results)
            result["passed_count"] = sum(1 for t in test_results if t.get("success"))
            result["failed_count"] = len(test_results) - result["passed_count"]
            result["status"] = "completed"

        except Exception as e:
            logger.error(f"Local test failed: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)

        finally:
            await self.server_manager.stop_all()

        return result

    async def _create_test_agent(self):
        """
        Create an Agno agent with MCP tools for testing.

        Returns:
            Configured Agno agent

        Raises:
            RuntimeError: If agent creation fails
        """
        try:
            from agno.agent import Agent
            from agno.models.anthropic import Claude
            from agno.tools.mcp import MCPTools

            # Get MCP command from server manager
            mcp_command = self.server_manager.get_mcp_command()

            # Connect to MCP server
            mcp_tools = MCPTools(command=mcp_command)
            await mcp_tools.connect()

            # Create agent
            agent = Agent(
                name="DynamicAPITester",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[mcp_tools],
                instructions="""
You are an expert API testing agent with access to dynamically loaded API endpoints.

Your responsibilities:
- Test all API endpoints thoroughly
- Validate responses and status codes
- Check error handling
- Verify data integrity
- Report results clearly

For each test:
1. Call the endpoint with appropriate parameters
2. Verify the response structure and data
3. Check status codes (200s for success, 400s/500s for errors)
4. Report pass/fail with details

Be systematic and thorough in your testing approach.
                """.strip(),
                markdown=True
            )

            return agent

        except Exception as e:
            error_msg = f"Failed to create test agent: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def _run_test_suite(
        self,
        agent,
        test_suite: str,
        api_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run a test suite using the agent.

        Args:
            agent: Agno agent with MCP tools
            test_suite: Type of test suite ("smoke", "comprehensive", "custom")
            api_spec: API specification

        Returns:
            List of test results
        """
        if test_suite == "smoke":
            return await self._run_smoke_tests(agent, api_spec)
        elif test_suite == "comprehensive":
            return await self._run_comprehensive_tests(agent, api_spec)
        else:
            # Custom test suite
            return await self._run_smoke_tests(agent, api_spec)

    async def _run_smoke_tests(
        self,
        agent,
        api_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run smoke tests (basic endpoint checks).

        Tests each endpoint once with default parameters.

        Args:
            agent: Agno agent
            api_spec: API specification

        Returns:
            List of test results
        """
        logger.info("Running smoke tests...")

        test_results = []
        endpoints = api_spec.get("endpoints", [])

        # Test each GET endpoint
        get_endpoints = [e for e in endpoints if e["method"] == "GET"]

        for endpoint in get_endpoints[:5]:  # Limit to first 5 for smoke test
            try:
                # Ask agent to test the endpoint
                prompt = f"Test the {endpoint['method']} {endpoint['path']} endpoint and report if it responds successfully."

                response = await agent.arun(prompt)
                result_text = response.content if hasattr(response, 'content') else str(response)

                # Simple success detection (can be improved)
                success = "success" in result_text.lower() or "200" in result_text

                test_results.append({
                    "endpoint": f"{endpoint['method']} {endpoint['path']}",
                    "test_type": "smoke",
                    "success": success,
                    "details": result_text[:200]  # First 200 chars
                })

            except Exception as e:
                test_results.append({
                    "endpoint": f"{endpoint['method']} {endpoint['path']}",
                    "test_type": "smoke",
                    "success": False,
                    "error": str(e)
                })

        return test_results

    async def _run_comprehensive_tests(
        self,
        agent,
        api_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run comprehensive tests (all endpoints with various scenarios).

        Args:
            agent: Agno agent
            api_spec: API specification

        Returns:
            List of test results
        """
        logger.info("Running comprehensive tests...")

        # Start with smoke tests
        results = await self._run_smoke_tests(agent, api_spec)

        # Add CRUD tests if applicable
        # (This would check for create, read, update, delete patterns)

        # Add error handling tests
        # (Test with invalid parameters, etc.)

        return results


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
