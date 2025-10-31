## Dynamic Backend API Testing System

**Automatically test ANY user-submitted backend API from repos, branches, or PRs.**

This system dynamically loads, wraps, and tests arbitrary Python REST APIs using FastMCP and the Agno framework. Unlike the static `backend_api/` system which requires manual wrapper creation, this system works with **any** user API through automatic OpenAPI introspection and code generation.

## Quick Start

```python
from dynamic_backend_testing import DynamicBackendOrchestrator

orchestrator = DynamicBackendOrchestrator()

# Test a GitHub repo
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    branch="feature-branch"
)

# Test a pull request
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    pr_number=123
)

# Test local API
result = await orchestrator.test_local(
    api_path=Path("/path/to/local/api"),
    app_module="main:app"
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   User Input                                 │
│         (Repo URL, Branch, PR, Local Path)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 RepoManager                                  │
│  • Git clone/checkout                                        │
│  • Dependency installation                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             APIDiscoveryService                              │
│  • Dynamic app loading (importlib)                           │
│  • Framework detection                                       │
│  • OpenAPI spec extraction                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               MCPGenerator                                   │
│  • Parse OpenAPI specs                                       │
│  • Generate @mcp.tool() code                                 │
│  • Minimal boilerplate                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          DynamicServerManager                                │
│  • Start user's API server                                   │
│  • Launch FastMCP MCP server                                 │
│  • Health checks                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Agno Agent + MCPTools                              │
│  • Automated API testing                                     │
│  • Response validation                                       │
│  • Test reporting                                            │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. RepoManager
Handles Git operations:
- Clone repositories from URLs
- Checkout branches, PRs, or commits
- Install dependencies from requirements.txt
- Manage workspace and cleanup

```python
from dynamic_backend_testing import RepoManager

manager = RepoManager()
repo_path = await manager.clone_repo(
    "https://github.com/user/api",
    branch="main"
)
await manager.install_dependencies(repo_path)
```

### 2. APIDiscoveryService
Discovers and introspects APIs:
- Dynamic app loading with `importlib`
- Auto-detection of app location
- Framework detection (FastAPI, Flask, Django)
- OpenAPI spec extraction
- Endpoint discovery

```python
from dynamic_backend_testing import APIDiscoveryService

discovery = APIDiscoveryService()
api_spec = await discovery.discover_api(
    repo_path=Path("/path/to/repo"),
    app_module="main:app",
    auto_detect=True
)

# Returns:
# - framework: "fastapi" | "flask" | "django"
# - openapi_spec: Full OpenAPI JSON
# - endpoints: List of all endpoints
# - app_instance: Loaded app
```

### 3. MCPGenerator
Generates FastMCP wrapper code:
- Parses OpenAPI schemas
- Generates Python functions with `@mcp.tool()` decorators
- Adds type hints from OpenAPI
- Creates httpx API calls
- Minimal boilerplate

```python
from dynamic_backend_testing import MCPGenerator

generator = MCPGenerator()
wrapper_code = generator.generate_mcp_wrapper(
    api_spec=discovered_api,
    api_base_url="http://localhost:8000"
)

# Returns ready-to-execute Python code:
# @mcp.tool()
# async def list_users(limit: int = 100) -> Dict[str, Any]:
#     ...
```

### 4. DynamicServerManager
Manages server lifecycle:
- Starts user's API server (FastAPI/Flask/etc.)
- Writes generated wrapper to temp file
- Launches FastMCP MCP server
- Health checks both servers
- Provides MCP command for Agno

```python
from dynamic_backend_testing import DynamicServerManager

manager = DynamicServerManager()
await manager.start_user_api(repo_path, app_module, framework)
await manager.start_mcp_server(wrapper_code, api_url)

# Get MCP command for Agno
mcp_command = manager.get_mcp_command()
```

### 5. DynamicBackendOrchestrator
Main coordination logic:
- Orchestrates all components
- End-to-end testing workflow
- Result aggregation
- Automatic cleanup

```python
from dynamic_backend_testing import DynamicBackendOrchestrator

orchestrator = DynamicBackendOrchestrator()
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api",
    branch="feature-branch",
    test_suite="comprehensive"
)
```

## Usage Examples

### Example 1: Test GitHub Repository

```python
import asyncio
from dynamic_backend_testing import DynamicBackendOrchestrator

async def main():
    orchestrator = DynamicBackendOrchestrator()

    result = await orchestrator.test_repo(
        repo_url="https://github.com/myorg/my-api",
        branch="feature/new-endpoints",
        app_module="main:app",
        test_suite="comprehensive"
    )

    print(f"Status: {result['status']}")
    print(f"Tests: {result['passed_count']}/{len(result['test_results'])} passed")

asyncio.run(main())
```

### Example 2: Test Pull Request (CI/CD)

```python
# Perfect for GitHub Actions, GitLab CI, etc.
import os
import sys

result = await orchestrator.test_repo(
    repo_url=os.environ['CI_REPO_URL'],
    pr_number=int(os.environ['PR_NUMBER']),
    test_suite="comprehensive"
)

# Exit with appropriate code
sys.exit(0 if result['overall_success'] else 1)
```

### Example 3: Test Local API

```python
# Test during development without committing
result = await orchestrator.test_local(
    api_path=Path("/Users/me/my-api"),
    app_module="app:application",
    test_suite="smoke"
)
```

### Example 4: Custom Test Suite

```python
# Extend the orchestrator for custom testing
class CustomOrchestrator(DynamicBackendOrchestrator):
    async def _run_custom_tests(self, agent, api_spec):
        # Your custom test logic
        pass

orchestrator = CustomOrchestrator()
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api",
    test_suite="custom"
)
```

## Comparison: Static vs Dynamic

| Feature | Static (backend_api/) | Dynamic (dynamic_backend_testing/) |
|---------|----------------------|-----------------------------------|
| **Manual wrapper** | ✅ Simple | ❌ Not needed |
| **Works with any API** | ❌ No | ✅ Yes |
| **Auto-generates tools** | ❌ No | ✅ Yes |
| **Supports repos/PRs** | ❌ No | ✅ Yes |
| **OpenAPI introspection** | ❌ No | ✅ Yes |
| **CI/CD ready** | ⚠️ Limited | ✅ Yes |
| **Complexity** | Simple | Moderate |
| **Best for** | Known APIs | Unknown/dynamic APIs |

## Installation

```bash
# Core dependencies (already in requirements.txt)
pip install agno anthropic fastapi uvicorn fastmcp httpx pytest

# The dynamic system requires no additional dependencies!
```

## Running Examples

```bash
# Test local sample API
python examples/test_github_repo.py

# Test a PR (update with real repo/PR)
python examples/test_pr.py --repo https://github.com/user/repo --pr 123
```

## How It Works

### Complete Workflow

1. **Clone Repository** (RepoManager)
   ```python
   repo_path = await repo_manager.clone_repo(repo_url, branch="main")
   ```

2. **Install Dependencies**
   ```python
   await repo_manager.install_dependencies(repo_path)
   ```

3. **Discover API** (APIDiscoveryService)
   ```python
   # Dynamically load app
   api_spec = await discovery.discover_api(repo_path, "main:app")
   # Extract OpenAPI spec
   # Discover endpoints
   ```

4. **Generate MCP Wrapper** (MCPGenerator)
   ```python
   # Parse OpenAPI
   # Generate @mcp.tool() functions
   wrapper_code = generator.generate_mcp_wrapper(api_spec, api_url)
   ```

5. **Start Servers** (DynamicServerManager)
   ```python
   # Start user's API
   await server_manager.start_user_api(repo_path, app_module, framework)
   # Start FastMCP MCP server
   await server_manager.start_mcp_server(wrapper_code, api_url)
   ```

6. **Test with Agno Agent**
   ```python
   # Connect to MCP
   mcp_tools = MCPTools(command=server_manager.get_mcp_command())
   await mcp_tools.connect()

   # Create agent
   agent = Agent(tools=[mcp_tools])

   # Run tests
   await agent.arun("Test all endpoints")
   ```

7. **Cleanup**
   ```python
   await server_manager.stop_all()
   repo_manager.cleanup(repo_path)
   ```

## API Reference

### DynamicBackendOrchestrator

```python
class DynamicBackendOrchestrator:
    """Main interface for dynamic API testing."""

    async def test_repo(
        repo_url: str,
        branch: Optional[str] = None,
        pr_number: Optional[int] = None,
        app_module: str = "main:app",
        test_suite: str = "smoke",
        auto_detect: bool = True,
        cleanup: bool = True
    ) -> Dict[str, Any]:
        """Test API from Git repository."""

    async def test_local(
        api_path: Path,
        app_module: str = "main:app",
        test_suite: str = "smoke"
    ) -> Dict[str, Any]:
        """Test local API without cloning."""
```

### Test Result Structure

```python
{
    "status": "completed" | "failed",
    "repo_info": {
        "remote_url": str,
        "current_branch": str,
        "current_commit": str,
        "commit_message": str
    },
    "api_info": {
        "framework": "fastapi" | "flask" | "django",
        "title": str,
        "version": str,
        "description": str
    },
    "endpoints": [
        {"path": "/users", "method": "GET"},
        ...
    ],
    "test_results": [
        {
            "endpoint": "GET /users",
            "test_type": "smoke",
            "success": True,
            "details": "..."
        },
        ...
    ],
    "overall_success": bool,
    "passed_count": int,
    "failed_count": int,
    "error": str  # if failed
}
```

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_api_key

# Optional
WORKSPACE_ROOT=/path/to/workspace  # Where repos are cloned
API_HOST=127.0.0.1                 # API server host
API_PORT=8000                      # API server port
```

### Custom Configuration

```python
orchestrator = DynamicBackendOrchestrator(
    anthropic_api_key="your_key",
    workspace_root=Path("/custom/workspace")
)
```

## Troubleshooting

### Issue: App Not Found

```
Error: Could not load application instance
```

**Solution:**
- Specify `app_module` explicitly: `app_module="main:app"`
- Enable auto-detection: `auto_detect=True`
- Check common locations: main.py, app.py, api.py

### Issue: Framework Not Detected

```
Warning: Unknown framework
```

**Solution:**
- The system supports FastAPI, Flask, and Django
- For other frameworks, consider extending APIDiscoveryService
- File an issue with your framework details

### Issue: MCP Server Won't Start

```
Error: FastMCP server failed to start
```

**Solution:**
- Check that fastmcp is installed: `pip install fastmcp`
- Verify the generated wrapper has no syntax errors
- Check server logs for details

### Issue: Tests Failing

```
Tests: 0/5 passed
```

**Solution:**
- Ensure ANTHROPIC_API_KEY is set
- Verify API server is running
- Check that endpoints are accessible
- Review agent logs for details

## Advanced Usage

### Custom Test Logic

```python
class CustomOrchestrator(DynamicBackendOrchestrator):
    async def _run_custom_tests(self, agent, api_spec):
        """Implement your custom test logic."""
        results = []

        # Example: Test authentication
        for endpoint in api_spec['endpoints']:
            if 'auth' in endpoint['path']:
                result = await self._test_auth_endpoint(agent, endpoint)
                results.append(result)

        return results
```

### Integration with CI/CD

**GitHub Actions:**
```yaml
name: API Tests
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test API
        run: |
          python examples/test_pr.py \
            --repo ${{ github.repository }} \
            --pr ${{ github.event.pull_request.number }}
```

**GitLab CI:**
```yaml
test_api:
  script:
    - python examples/test_pr.py --repo $CI_REPOSITORY_URL --pr $CI_MERGE_REQUEST_IID
  only:
    - merge_requests
```

## Extending the System

### Add New Framework Support

```python
# In api_discovery.py
async def _extract_my_framework_openapi(self, app_instance):
    """Extract OpenAPI from your framework."""
    # Your implementation
    pass
```

### Add Custom MCP Tools

```python
# In mcp_generator.py
def _generate_custom_tool(self, endpoint):
    """Generate custom tool beyond OpenAPI."""
    # Your implementation
    pass
```

## FAQ

**Q: Does this work with non-Python APIs?**
A: Currently only Python (FastAPI, Flask, Django). Extending to other languages would require new discovery/wrapper logic.

**Q: Can I test GraphQL APIs?**
A: Not yet, but it's on the roadmap. The system focuses on REST APIs with OpenAPI specs.

**Q: How does cleanup work?**
A: The orchestrator automatically stops servers and optionally deletes cloned repos. Use `cleanup=False` to keep repos for debugging.

**Q: Can I run multiple tests in parallel?**
A: Yes, create multiple orchestrator instances with different ports to avoid conflicts.

## License

Same as parent project.

## Support

- See parent README for general support
- Check [DYNAMIC_SYSTEM_IMPLEMENTATION.md](../DYNAMIC_SYSTEM_IMPLEMENTATION.md) for architecture details
- File issues on GitHub
