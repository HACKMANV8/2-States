# Dynamic Backend API Testing System - Implementation

## Overview

This document describes the **dynamic orchestration system** that automatically loads, wraps, and tests user-submitted backend APIs as MCP servers using FastMCP.

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     User Input                                  │
│  (Repo URL, Branch, PR, Local Path)                            │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                   RepoManager                                   │
│  • Clone repository                                             │
│  • Checkout branch/PR                                           │
│  • Install dependencies                                         │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│               APIDiscoveryService                               │
│  • Load app dynamically (importlib)                             │
│  • Detect framework (FastAPI/Flask/etc.)                        │
│  • Extract OpenAPI spec                                         │
│  • Discover endpoints                                           │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                  MCPGenerator                                   │
│  • Generate MCP tools from OpenAPI specs                        │
│  • Create dynamic FastMCP wrapper                               │
│  • Map endpoints to MCP tool functions                          │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│             DynamicServerManager                                │
│  • Start FastAPI server for user API                            │
│  • Launch FastMCP MCP server                                    │
│  • Manage lifecycle                                             │
│  • Generate MCP command for Agno                                │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│              Agno Agent Integration                             │
│  • Connect via MCPTools                                         │
│  • Test API endpoints as MCP tools                              │
│  • Validate responses                                           │
│  • Generate test reports                                        │
└────────────────────────────────────────────────────────────────┘
```

## Components Created

### 1. **RepoManager** (`repo_manager.py`) ✅ COMPLETE

Handles Git operations:

```python
from dynamic_backend_testing import RepoManager

manager = RepoManager()

# Clone repo with branch
repo_path = await manager.clone_repo(
    "https://github.com/user/api-repo",
    branch="feature-branch"
)

# Or checkout PR
repo_path = await manager.clone_repo(
    "https://github.com/user/api-repo",
    pr_number=123
)

# Install dependencies
await manager.install_dependencies(repo_path)

# Get repo info
info = await manager.get_repo_info(repo_path)

# Cleanup
manager.cleanup(repo_path)
```

**Features:**
- Clone from any Git URL (HTTPS/SSH)
- Checkout branches, PRs, or specific commits
- Auto-install dependencies from requirements.txt
- Optional virtual environment creation
- Workspace management and cleanup

### 2. **APIDiscoveryService** (`api_discovery.py`) ✅ COMPLETE

Discovers and introspects APIs:

```python
from dynamic_backend_testing import APIDiscoveryService

discovery = APIDiscoveryService()

# Discover API in cloned repo
result = await discovery.discover_api(
    repo_path=Path("/path/to/repo"),
    app_module="main:app",  # or auto-detect
    auto_detect=True
)

# Result contains:
# - framework: "fastapi" | "flask" | "django" | "unknown"
# - openapi_spec: Full OpenAPI specification
# - endpoints: List of discovered endpoints
# - app_instance: The loaded app
# - metadata: Additional info
```

**Features:**
- Dynamic app loading with importlib
- Auto-detection of app location (main.py, app.py, etc.)
- Framework detection (FastAPI, Flask, Django)
- OpenAPI spec extraction (FastAPI native, Flask-RESTX, etc.)
- Fallback endpoint introspection if no OpenAPI
- Support for factory patterns (create_app())

### 3. **MCPGenerator** (`mcp_generator.py`) 🚧 TO IMPLEMENT

Generates MCP tools from OpenAPI specs:

```python
from dynamic_backend_testing import MCPGenerator

generator = MCPGenerator()

# Generate MCP wrapper from discovered API
mcp_wrapper_code = generator.generate_mcp_wrapper(
    api_spec=discovered_api,
    api_base_url="http://localhost:8000"
)

# Save generated wrapper
wrapper_path = generator.save_wrapper(mcp_wrapper_code, output_dir)

# The generated wrapper will have:
# - @mcp.tool() decorated functions for each endpoint
# - Automatic parameter mapping from OpenAPI schemas
# - Request/response handling
# - Error handling
```

**Key Implementation Details:**

```python
class MCPGenerator:
    """
    Generates FastMCP wrappers from OpenAPI specifications.

    This class:
    1. Parses OpenAPI specs to extract endpoint info
    2. Generates Python code with @mcp.tool() decorators
    3. Maps OpenAPI parameters to Python function parameters
    4. Adds type hints based on OpenAPI schemas
    5. Generates httpx calls to the actual API
    """

    def generate_mcp_wrapper(
        self,
        api_spec: Dict[str, Any],
        api_base_url: str
    ) -> str:
        """
        Generate complete FastMCP wrapper code.

        For each endpoint in OpenAPI spec:
        1. Create a function with proper parameters
        2. Add @mcp.tool() decorator
        3. Add docstring from OpenAPI description
        4. Add type hints from OpenAPI schemas
        5. Generate httpx request code
        6. Handle response parsing

        Returns:
            Complete Python code as string
        """
        # Extract endpoints from OpenAPI spec
        endpoints = api_spec["endpoints"]

        # Generate imports
        code = self._generate_imports()

        # Initialize FastMCP
        code += self._generate_mcp_init(api_spec["metadata"])

        # Generate tool for each endpoint
        for endpoint in endpoints:
            code += self._generate_tool_function(endpoint, api_base_url)

        # Add main() function
        code += self._generate_main()

        return code

    def _generate_tool_function(
        self,
        endpoint: Dict[str, Any],
        api_base_url: str
    ) -> str:
        """
        Generate a single MCP tool function.

        Example output:
        ```python
        @mcp.tool()
        async def list_users(
            active_only: bool = False,
            limit: int = 100
        ) -> Dict[str, Any]:
            '''
            List all users in the system.

            Args:
                active_only: Filter to only active users
                limit: Maximum number of users

            Returns:
                List of user objects
            '''
            params = {"active_only": active_only, "limit": limit}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api_base_url}/users",
                    params=params
                )
                return {
                    "status_code": response.status_code,
                    "data": response.json()
                }
        ```
        """
        pass  # Implementation details
```

### 4. **DynamicServerManager** (`dynamic_server_manager.py`) 🚧 TO IMPLEMENT

Manages server lifecycle for arbitrary APIs:

```python
from dynamic_backend_testing import DynamicServerManager

manager = DynamicServerManager()

# Start user's API server
api_process = await manager.start_user_api(
    repo_path=Path("/path/to/repo"),
    app_module="main:app",
    host="127.0.0.1",
    port=8000
)

# Generate and start FastMCP server
mcp_process = await manager.start_mcp_server(
    wrapper_code=generated_wrapper,
    api_url="http://localhost:8000"
)

# Get MCP command for Agno
mcp_command = manager.get_mcp_command()

# Use with Agno
mcp_tools = MCPTools(command=mcp_command)
await mcp_tools.connect()

# Cleanup
await manager.stop_all()
```

**Key Implementation:**

```python
class DynamicServerManager:
    """
    Manages lifecycle of dynamically loaded API servers.

    Responsibilities:
    1. Start user's API server (FastAPI/Flask)
    2. Write generated MCP wrapper to temp file
    3. Start FastMCP server with the wrapper
    4. Health check both servers
    5. Provide MCP command for Agno integration
    6. Graceful shutdown
    """

    async def start_user_api(
        self,
        repo_path: Path,
        app_module: str,
        host: str = "127.0.0.1",
        port: int = 8000
    ) -> subprocess.Popen:
        """
        Start the user's API server.

        Uses uvicorn for ASGI apps (FastAPI, Starlette)
        or Flask's built-in server for Flask apps.

        Returns process handle for lifecycle management.
        """
        # Detect framework
        # Start appropriate server
        # Wait for health check
        # Return process
        pass

    async def start_mcp_server(
        self,
        wrapper_code: str,
        api_url: str
    ) -> Tuple[Path, subprocess.Popen]:
        """
        Start FastMCP server with generated wrapper.

        1. Write wrapper code to temp file
        2. Start: python <wrapper_file>.py
        3. Return (wrapper_path, process)
        """
        # Create temp file
        wrapper_path = self._create_temp_wrapper(wrapper_code)

        # Start FastMCP server
        process = subprocess.Popen(
            [sys.executable, str(wrapper_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for MCP server to be ready
        await self._wait_for_mcp_ready(process)

        return wrapper_path, process
```

### 5. **Orchestrator** (`orchestrator.py`) 🚧 TO IMPLEMENT

Main coordination logic:

```python
from dynamic_backend_testing import DynamicBackendOrchestrator

orchestrator = DynamicBackendOrchestrator()

# Test a repo end-to-end
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    branch="feature-branch",
    test_suite="comprehensive"  # or "smoke", "custom"
)

# Result contains:
# - repo_info: Git information
# - api_info: Discovered API metadata
# - endpoints_tested: Number of endpoints
# - test_results: Detailed results per endpoint
# - overall_success: Boolean
```

**Complete Flow:**

```python
class DynamicBackendOrchestrator:
    """
    End-to-end orchestration for dynamic API testing.

    Coordinates all components to:
    1. Clone repo
    2. Discover API
    3. Generate MCP wrapper
    4. Start servers
    5. Test with Agno agent
    6. Cleanup
    """

    async def test_repo(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        pr_number: Optional[int] = None,
        app_module: str = "main:app",
        test_suite: str = "smoke"
    ) -> Dict[str, Any]:
        """
        Test a user repo end-to-end.

        Complete workflow:
        1. Clone repo (RepoManager)
        2. Install dependencies
        3. Discover API (APIDiscoveryService)
        4. Generate MCP wrapper (MCPGenerator)
        5. Start user API server (DynamicServerManager)
        6. Start FastMCP server (DynamicServerManager)
        7. Create Agno agent with MCPTools
        8. Run tests
        9. Collect results
        10. Cleanup
        """
        results = {
            "status": "in_progress",
            "repo_info": {},
            "api_info": {},
            "test_results": []
        }

        try:
            # Step 1-2: Clone and setup
            repo_manager = RepoManager()
            repo_path = await repo_manager.clone_repo(repo_url, branch, pr_number)
            await repo_manager.install_dependencies(repo_path)
            results["repo_info"] = await repo_manager.get_repo_info(repo_path)

            # Step 3: Discover API
            discovery = APIDiscoveryService()
            api_spec = await discovery.discover_api(repo_path, app_module)
            results["api_info"] = api_spec["metadata"]

            # Step 4: Generate MCP wrapper
            generator = MCPGenerator()
            wrapper_code = generator.generate_mcp_wrapper(
                api_spec,
                "http://localhost:8000"
            )

            # Step 5-6: Start servers
            server_manager = DynamicServerManager()
            await server_manager.start_user_api(repo_path, app_module)
            await server_manager.start_mcp_server(wrapper_code, "http://localhost:8000")

            # Step 7: Create Agno agent
            from agno.agent import Agent
            from agno.models.anthropic import Claude
            from agno.tools.mcp import MCPTools

            mcp_tools = MCPTools(command=server_manager.get_mcp_command())
            await mcp_tools.connect()

            agent = Agent(
                name="DynamicAPITester",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[mcp_tools],
                instructions="Test all API endpoints thoroughly"
            )

            # Step 8: Run tests
            if test_suite == "smoke":
                test_results = await self._run_smoke_tests(agent, api_spec)
            elif test_suite == "comprehensive":
                test_results = await self._run_comprehensive_tests(agent, api_spec)

            results["test_results"] = test_results
            results["status"] = "completed"

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)

        finally:
            # Step 10: Cleanup
            await server_manager.stop_all()
            repo_manager.cleanup(repo_path)

        return results
```

## Usage Examples

### Example 1: Test GitHub Repo

```python
import asyncio
from dynamic_backend_testing import DynamicBackendOrchestrator

async def main():
    orchestrator = DynamicBackendOrchestrator()

    # Test a feature branch
    result = await orchestrator.test_repo(
        repo_url="https://github.com/myorg/my-api",
        branch="feature/new-endpoints",
        test_suite="comprehensive"
    )

    print(f"Status: {result['status']}")
    print(f"Endpoints tested: {len(result['test_results'])}")
    print(f"Success rate: {result['success_rate']}%")

asyncio.run(main())
```

### Example 2: Test Pull Request

```python
# Test a PR before merging
result = await orchestrator.test_repo(
    repo_url="https://github.com/myorg/my-api",
    pr_number=456,
    test_suite="smoke"
)

if result['overall_success']:
    print("✅ PR tests passed - safe to merge")
else:
    print("❌ PR tests failed:")
    for test in result['test_results']:
        if not test['success']:
            print(f"  - {test['endpoint']}: {test['error']}")
```

### Example 3: CI/CD Integration

```python
# In your CI/CD pipeline
import sys

result = await orchestrator.test_repo(
    repo_url=os.environ['CI_REPO_URL'],
    branch=os.environ['CI_BRANCH'],
    app_module=os.environ.get('API_MODULE', 'main:app')
)

# Exit with appropriate code
sys.exit(0 if result['overall_success'] else 1)
```

### Example 4: Local Development

```python
# Test local changes
from pathlib import Path

# Option 1: Use local path (no cloning)
orchestrator = DynamicBackendOrchestrator()
result = await orchestrator.test_local(
    api_path=Path("/Users/me/my-api"),
    app_module="app:application"
)

# Option 2: Test uncommitted changes
# (commit to temp branch first, then test)
```

## Implementation Status

| Component | Status | File |
|-----------|--------|------|
| RepoManager | ✅ Complete | `repo_manager.py` |
| APIDiscoveryService | ✅ Complete | `api_discovery.py` |
| MCPGenerator | 🚧 To Implement | `mcp_generator.py` |
| DynamicServerManager | 🚧 To Implement | `dynamic_server_manager.py` |
| Orchestrator | 🚧 To Implement | `orchestrator.py` |
| Examples | 🚧 To Implement | `examples/` |
| Tests | 🚧 To Implement | `tests/test_dynamic_*.py` |
| Documentation | 🚧 To Implement | `README.md` |

## Key Advantages Over Static System

### Static System (backend_api/)
- ✅ Simple to understand
- ✅ Fast for known APIs
- ❌ Requires manual wrapper creation
- ❌ Only works with sample API
- ❌ No support for repos/PRs
- ❌ Manual endpoint mapping

### Dynamic System (dynamic_backend_testing/)
- ✅ Works with ANY user API
- ✅ Auto-generates MCP wrappers
- ✅ Supports repos, branches, PRs
- ✅ OpenAPI introspection
- ✅ Minimal boilerplate
- ✅ Production-ready for CI/CD
- ⚠️ More complex internally
- ⚠️ Requires careful error handling

## Next Steps

1. **Implement MCPGenerator** ✏️
   - Parse OpenAPI schemas
   - Generate Python code with type hints
   - Create @mcp.tool() functions
   - Handle edge cases (file uploads, authentication, etc.)

2. **Implement DynamicServerManager** 🖥️
   - Server process management
   - Health checking
   - Port allocation
   - Graceful shutdown

3. **Implement Orchestrator** 🎭
   - End-to-end coordination
   - Test suite execution
   - Result aggregation
   - Error recovery

4. **Create Examples** 📚
   - Test GitHub repo
   - Test PR
   - CI/CD integration
   - Local development

5. **Write Tests** 🧪
   - Unit tests for each component
   - Integration tests
   - End-to-end tests
   - Mock external dependencies

6. **Documentation** 📖
   - Complete README
   - Architecture diagrams
   - API reference
   - Troubleshooting guide

## Current Progress

✅ **Completed:**
- Project structure
- RepoManager (full Git operations)
- APIDiscoveryService (app loading, OpenAPI extraction)
- Design documentation
- Architecture planning

🚧 **In Progress:**
- Creating remaining components

📋 **Planned:**
- Example implementations
- Test suites
- Complete documentation
