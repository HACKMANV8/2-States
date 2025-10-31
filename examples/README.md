# Dynamic Backend Testing Examples

This directory contains example scripts demonstrating how to use the Dynamic Backend Testing System.

## Examples Included

### 1. Test GitHub Repository (`test_github_repo.py`)

Shows how to test an API from a GitHub repository.

**Features:**
- Test local sample API (quick demo)
- Test real GitHub repository
- Interactive selection
- Comprehensive output formatting

**Usage:**
```bash
python examples/test_github_repo.py

# Select option:
# 1. Test local sample API (quick demo)
# 2. Test real GitHub repository (requires editing)
```

**Example Output:**
```
╔══════════════════════════════════════════════════════════════════════╗
║          Example: Test GitHub Repository                            ║
╚══════════════════════════════════════════════════════════════════════╝

📝 Test Configuration:
======================================================================
Testing: Local sample API (backend_api/sample_api.py)
Module: backend_api.sample_api:app
Test Suite: Smoke tests
======================================================================

🚀 Starting test...
[1/6] Discovering API...
[2/6] Generating MCP wrapper...
...

======================================================================
TEST RESULTS
======================================================================
Status: completed
API Framework: fastapi
Tests Run: 5
Passed: 5
Failed: 0
Overall Success: ✅ YES
```

### 2. Test Pull Request (`test_pr.py`)

Shows how to test a GitHub PR before merging (perfect for CI/CD).

**Features:**
- PR testing with argument parsing
- CI/CD integration ready
- Exit codes for automation
- Detailed test reporting

**Usage:**
```bash
# With arguments (for real testing)
python examples/test_pr.py \
  --repo https://github.com/user/repo \
  --pr 123 \
  --app-module main:app

# Without arguments (shows example output)
python examples/test_pr.py
```

**CI/CD Integration:**

**GitHub Actions:**
```yaml
name: Test PR
on: [pull_request]
jobs:
  test-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Test PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python examples/test_pr.py \
            --repo ${{ github.repository }} \
            --pr ${{ github.event.pull_request.number }}
```

**GitLab CI:**
```yaml
test-pr:
  script:
    - pip install -r requirements.txt
    - python examples/test_pr.py --repo $CI_REPOSITORY_URL --pr $CI_MERGE_REQUEST_IID
  only:
    - merge_requests
```

## Requirements

```bash
# All examples require
pip install -r requirements.txt

# And environment variable
export ANTHROPIC_API_KEY=your_key_here
```

## Creating Your Own Examples

### Basic Template

```python
import asyncio
from pathlib import Path
from dynamic_backend_testing import DynamicBackendOrchestrator

async def my_test_example():
    orchestrator = DynamicBackendOrchestrator()

    # Test a repo
    result = await orchestrator.test_repo(
        repo_url="https://github.com/user/repo",
        branch="main",
        test_suite="smoke"
    )

    # Display results
    print(f"Status: {result['status']}")
    print(f"Success: {result['overall_success']}")

    return result

if __name__ == "__main__":
    result = asyncio.run(my_test_example())
    sys.exit(0 if result['overall_success'] else 1)
```

### Advanced Template with Custom Tests

```python
from dynamic_backend_testing import DynamicBackendOrchestrator

class MyCustomOrchestrator(DynamicBackendOrchestrator):
    async def _run_custom_tests(self, agent, api_spec):
        """Your custom test logic."""
        results = []

        # Example: Test only POST endpoints
        post_endpoints = [
            e for e in api_spec['endpoints']
            if e['method'] == 'POST'
        ]

        for endpoint in post_endpoints:
            # Test each POST endpoint
            result = await self._test_endpoint(agent, endpoint)
            results.append(result)

        return results

# Use your custom orchestrator
orchestrator = MyCustomOrchestrator()
result = await orchestrator.test_repo(
    repo_url="...",
    test_suite="custom"  # Uses your _run_custom_tests
)
```

## Tips & Best Practices

### 1. Testing Local APIs

For faster iteration during development:

```python
result = await orchestrator.test_local(
    api_path=Path("/path/to/your/api"),
    app_module="app:application",
    test_suite="smoke"  # Quick tests
)
```

### 2. Cleanup Control

Keep repos for debugging:

```python
result = await orchestrator.test_repo(
    repo_url="...",
    cleanup=False  # Don't delete cloned repo
)

# Repo will be in workspace_root/repo_name
# Default: /tmp/api_testing_workspace/
```

### 3. Custom Workspace

Use a specific directory for cloned repos:

```python
orchestrator = DynamicBackendOrchestrator(
    workspace_root=Path("/my/custom/workspace")
)
```

### 4. Error Handling

```python
try:
    result = await orchestrator.test_repo(repo_url="...")

    if result['status'] == 'failed':
        print(f"Error: {result['error']}")
    elif result['overall_success']:
        print("All tests passed!")
    else:
        print(f"Some tests failed: {result['failed_count']}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

### 5. Parallel Testing

Test multiple branches in parallel:

```python
async def test_all_branches():
    branches = ["main", "develop", "feature-1"]

    # Create separate orchestrators to avoid port conflicts
    tasks = [
        orchestrator.test_repo(repo_url="...", branch=b)
        for b in branches
    ]

    results = await asyncio.gather(*tasks)
    return results
```

## Troubleshooting

### Example won't run

```bash
# Ensure you're in the project root
cd /path/to/2-States

# Ensure dependencies are installed
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key
```

### "Module not found" error

```bash
# Run from project root
python examples/test_github_repo.py

# Not from examples directory
cd examples
python test_github_repo.py  # Won't work!
```

### Tests failing

```python
# Check the result dictionary for details
if not result['overall_success']:
    for test in result['test_results']:
        if not test['success']:
            print(f"Failed: {test['endpoint']}")
            print(f"Error: {test.get('error')}")
```

## More Information

- See [../dynamic_backend_testing/README.md](../dynamic_backend_testing/README.md) for system documentation
- See [../DYNAMIC_SYSTEM_IMPLEMENTATION.md](../DYNAMIC_SYSTEM_IMPLEMENTATION.md) for architecture
- See [../FINAL_IMPLEMENTATION_SUMMARY.md](../FINAL_IMPLEMENTATION_SUMMARY.md) for complete summary
