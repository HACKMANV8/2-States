# Quick Reference Guide - Dynamic Backend Testing

**Last Updated**: October 31, 2025

## 🚀 Quick Start (30 seconds)

```bash
# 1. Set your API key
export ANTHROPIC_API_KEY=your_key_here

# 2. Test a GitHub repo
python examples/test_github_repo.py

# 3. Test a PR (CI/CD)
python examples/test_pr.py --repo https://github.com/user/repo --pr 123
```

## 📁 What You Have

### Production System
```
dynamic_backend_testing/     ← THE backend testing system
├── orchestrator.py          ← Main entry point
├── repo_manager.py          ← Git operations
├── api_discovery.py         ← API introspection
├── mcp_generator.py         ← Code generation
├── dynamic_server_manager.py ← Server lifecycle
└── README.md                ← Full docs
```

### Examples
```
examples/
├── test_github_repo.py      ← Test any GitHub repo
├── test_pr.py               ← Test PRs (CI/CD ready)
└── README.md                ← Usage guide
```

### Enhanced Slack Bot
```
slack_agent.py               ← Web automation + API testing
```

## 💡 Common Use Cases

### 1. Test a GitHub Repository

```python
from dynamic_backend_testing import DynamicBackendOrchestrator

orchestrator = DynamicBackendOrchestrator()

# Test main branch
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    branch="main"
)

# Test feature branch
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    branch="feature/new-endpoints"
)
```

### 2. Test a Pull Request (CI/CD)

```python
# Perfect for GitHub Actions, GitLab CI
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/api-repo",
    pr_number=123,
    test_suite="comprehensive"
)

# Exit with proper code for CI/CD
sys.exit(0 if result['overall_success'] else 1)
```

### 3. Test Local API

```python
result = await orchestrator.test_local(
    api_path=Path("/path/to/your/api"),
    app_module="main:app"
)
```

### 4. Use with Slack Bot

```bash
# Start Slack bot
python slack_agent.py

# In Slack:
@bot test the backend API health
@bot run smoke tests on all endpoints
@bot create a test user and verify it was created
```

## 🎯 Test Suite Options

### Smoke Test (Quick)
```python
test_suite="smoke"  # Tests 5 key endpoints (~15 seconds)
```

### Comprehensive Test (Thorough)
```python
test_suite="comprehensive"  # Tests all endpoints (~2-5 minutes)
```

## 📊 Understanding Results

```python
result = {
    'status': 'success',              # success | failed | error
    'overall_success': True,          # Boolean: all tests passed?

    'repo_info': {
        'remote_url': '...',
        'current_branch': 'main',
        'current_commit': 'abc123...'
    },

    'api_info': {
        'framework': 'fastapi',       # fastapi | flask | django
        'title': 'My API',
        'version': '1.0.0'
    },

    'endpoints': [                    # List of discovered endpoints
        {'path': '/users', 'method': 'GET', ...},
        {'path': '/users', 'method': 'POST', ...}
    ],

    'test_results': [                 # Individual test results
        {
            'endpoint': 'GET /users',
            'success': True,
            'status_code': 200,
            'response_time': 0.05
        }
    ],

    'passed_count': 15,
    'failed_count': 0
}
```

## 🔧 Configuration Options

### Full Options

```python
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/repo",
    branch="main",                    # Or specify branch
    pr_number=None,                   # Or specify PR number
    app_module="main:app",           # Where to find the app
    auto_detect=True,                 # Auto-find app location
    test_suite="comprehensive",       # smoke | comprehensive
    cleanup=True,                     # Clean up after testing
    install_deps=True,                # Install requirements.txt
    use_venv=False                    # Use virtual environment
)
```

### Minimal (Auto-detect everything)

```python
result = await orchestrator.test_repo(
    repo_url="https://github.com/user/repo"
)
# System will auto-detect framework, find app, run smoke tests
```

## 🏗️ Supported Frameworks

### ✅ Fully Supported
- **FastAPI** - Full OpenAPI support
- **Flask** - Via Flask-RESTX or Flasgger
- **Django** - Via Django REST Framework

### 📝 Example Apps

**FastAPI:**
```python
# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello"}
```

**Flask:**
```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def root():
    return {"message": "Hello"}
```

## 🚨 Troubleshooting

### Issue: "App not found"
```python
# Solution: Specify app location
app_module="main:app"  # For app = FastAPI() in main.py
app_module="backend.app:create_app"  # For factory pattern
```

### Issue: "Framework not detected"
```python
# Solution: System supports FastAPI, Flask, Django
# Make sure your app uses one of these frameworks
```

### Issue: "MCP server won't start"
```bash
# Solution: Install FastMCP
pip install fastmcp
```

### Issue: "Tests fail"
```bash
# 1. Check API key is set
echo $ANTHROPIC_API_KEY

# 2. Check API server logs
# Look at output from orchestrator.test_repo()

# 3. Try local testing first
python examples/test_github_repo.py
```

## 📖 Documentation Map

### For Quick Start
- `QUICK_REFERENCE.md` ← You are here
- `examples/test_github_repo.py` - Working example

### For Deep Dive
- `dynamic_backend_testing/README.md` - Complete system docs
- `DYNAMIC_SYSTEM_IMPLEMENTATION.md` - Architecture details
- `FINAL_IMPLEMENTATION_SUMMARY.md` - What was built

### For Understanding Changes
- `CLEANUP_SUMMARY.md` - What was removed and why
- `FINAL_STATE_VERIFICATION.md` - Current state verification

## 🎓 Learning Path

### Level 1: Run Examples (5 minutes)
```bash
python examples/test_github_repo.py
```

### Level 2: Test Your API (15 minutes)
```python
# Edit examples/test_github_repo.py
# Update repo URL to your API
```

### Level 3: Use in CI/CD (30 minutes)
```yaml
# .github/workflows/test.yml
- name: Test API
  run: python examples/test_pr.py --repo ${{ github.repository }} --pr ${{ github.event.number }}
```

### Level 4: Customize Tests (1 hour)
```python
# Create custom test orchestrator
from dynamic_backend_testing import DynamicBackendOrchestrator

class MyCustomOrchestrator(DynamicBackendOrchestrator):
    async def my_custom_test_suite(self, agent):
        # Your custom tests
        pass
```

## 💻 Command Line Usage

### Test GitHub Repo
```bash
python -c "
import asyncio
from dynamic_backend_testing import DynamicBackendOrchestrator

async def main():
    orchestrator = DynamicBackendOrchestrator()
    result = await orchestrator.test_repo('https://github.com/user/repo')
    print(f'Success: {result[\"overall_success\"]}')

asyncio.run(main())
"
```

### Test PR
```bash
python examples/test_pr.py \
  --repo https://github.com/user/repo \
  --pr 123 \
  --test-suite comprehensive
```

## 🔐 Security Notes

⚠️ **Important**: This system executes arbitrary user code
- Run in isolated environments (containers, VMs)
- Always use `cleanup=True` in production
- Consider sandboxing for untrusted repos
- Review dependencies before installation

## 📈 Performance Tips

### Faster Testing
```python
# Use smoke tests instead of comprehensive
test_suite="smoke"

# Disable dependency installation if cached
install_deps=False

# Use local clone if testing multiple times
cleanup=False  # Keep cloned repo
```

### Parallel Testing
```python
# Test multiple branches concurrently
import asyncio

tasks = [
    orchestrator.test_repo(url, branch="main"),
    orchestrator.test_repo(url, branch="develop"),
    orchestrator.test_repo(url, branch="feature-x")
]

results = await asyncio.gather(*tasks)
```

## 🎯 Real-World Workflows

### Workflow 1: PR Validation
```yaml
# .github/workflows/api-test.yml
name: API Tests
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test API
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          pip install -r requirements.txt
          python examples/test_pr.py \
            --repo ${{ github.repository }} \
            --pr ${{ github.event.number }}
```

### Workflow 2: Nightly Testing
```python
# test_all_branches.py
branches = ["main", "develop", "staging", "production"]

for branch in branches:
    result = await orchestrator.test_repo(url, branch=branch)
    send_report(branch, result)  # Email/Slack notification
```

### Workflow 3: Local Development
```bash
# Start your API locally
cd ~/my-api
uvicorn main:app --reload

# Test it
python -c "
from pathlib import Path
from dynamic_backend_testing import DynamicBackendOrchestrator

orchestrator = DynamicBackendOrchestrator()
result = orchestrator.test_local(Path('~/my-api'))
"
```

## 🔗 Integration Examples

### With pytest
```python
# tests/test_my_api.py
import pytest
from dynamic_backend_testing import DynamicBackendOrchestrator

@pytest.mark.asyncio
async def test_api_health():
    orchestrator = DynamicBackendOrchestrator()
    result = await orchestrator.test_repo("https://github.com/user/repo")
    assert result['overall_success']
```

### With pre-commit hook
```bash
# .git/hooks/pre-commit
python examples/test_pr.py --repo $(git remote get-url origin)
```

## 📞 Getting Help

1. **Check documentation**: `dynamic_backend_testing/README.md`
2. **Run verification**: `python verify_installation.py`
3. **Check examples**: `examples/` directory
4. **Review logs**: Check orchestrator output for detailed errors

## ✨ What Makes This Special

✅ **Zero Configuration** - Test any API with one line
✅ **Auto-Detection** - Finds framework, app, endpoints automatically
✅ **Auto-Generation** - Creates MCP wrappers from OpenAPI specs
✅ **Production Ready** - CI/CD integration, error handling, cleanup
✅ **Agno Compliant** - Follows official MCP architecture
✅ **Multi-Framework** - FastAPI, Flask, Django support

---

**Ready to test your first API?**
```bash
python examples/test_github_repo.py
```

**Questions?** Check `dynamic_backend_testing/README.md` for complete documentation.
# TestGPT Quick Reference

Quick reference for TestGPT features, configuration, and usage.

---

## 🌐 Supported Browsers

| Browser | Profile ID | Usage |
|---------|------------|-------|
| **Chrome (Desktop)** | `chromium-desktop` | Default browser |
| **Safari (macOS)** | `webkit-desktop` | Desktop Safari testing |
| **Safari (iOS)** | `webkit-ios` | Mobile iOS testing |
| **Firefox (Desktop)** | `firefox-desktop` | Firefox testing |

**Auto-selection rules:**
- `pointblank.club` → Always tests Safari iOS, Safari macOS, Chrome
- "Safari" in message → Safari (macOS)
- "iPhone" or "iOS" → Safari (iOS)
- "Chrome" → Chrome
- "cross-browser" → Chrome + Safari (macOS)
- Default → Chrome

**📄 Full docs:** [SUPPORTED_BROWSERS.md](./SUPPORTED_BROWSERS.md)

---

## 📱 Supported Viewports

### Mobile
- **iPhone SE** (375×667) - Smallest iOS
- **iPhone 13 Pro** (390×844) - Standard iOS
- **iPhone 13 Pro Landscape** (844×390)
- **Android Small** (360×640) - Budget Android
- **Android Medium** (412×915) - Standard Android

### Tablet
- **iPad Air** (820×1180) - Portrait
- **iPad Air Landscape** (1180×820)

### Desktop
- **Desktop Standard** (1920×1080) - Most common
- **Desktop Ultrawide** (2560×1440) - Large displays
- **Desktop Small** (1366×768) - Laptops

**Auto-selection rules:**
- "iPhone" → iPhone 13 Pro
- "iPad" → iPad Air
- "Android" → Android Medium
- "desktop" → Desktop Standard
- "responsive" → iPhone 13 Pro + iPad Air + Desktop Standard

---

## 📡 Network Conditions

| Profile | Description | Use Case |
|---------|-------------|----------|
| **normal** | Good broadband (50ms latency) | Default baseline |
| **slow-3g** | Slow mobile (400ms, 400kbps) | Slow connections |
| **flaky-edge** | Unstable connection (2% packet loss) | Edge cases |

**Auto-selection:**
- Always includes `normal`
- "slow" or "3G" → adds `slow-3g`
- "flaky" or "unstable" → adds `flaky-edge`

---

## 🚀 Usage Examples

### Slack Commands

```
@TestGPT test pointblank.club
→ Tests: Safari iOS, Safari macOS, Chrome on desktop

@TestGPT test mysite.com on iPhone
→ Tests: Safari iOS on iPhone 13 Pro

@TestGPT test mysite.com responsive
→ Tests: iPhone, iPad, Desktop on Chrome

@TestGPT test checkout flow on mobile with slow network
→ Tests: iPhone with slow-3g network

@TestGPT cross-browser test
→ Tests: Chrome + Safari on desktop
```

---

## 🔧 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers (one-time)
npx playwright install

# 3. Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."

# 4. Run TestGPT
python main.py
```

---

## 📊 How It Works

```
Slack Message
    ↓
Claude API Parser (extracts viewports/browsers/networks)
    ↓
Test Plan Builder (creates matrix of environment combinations)
    ↓
Dynamic MCP Manager (launches separate MCP server for each combo)
    ↓
Test Executor (runs autonomous AI agent for each environment)
    ↓
Results Aggregator (collects pass/fail for all environments)
    ↓
Slack Summary (formatted results with screenshots)
```

---

## 🐛 Debugging

**View logs:**
```bash
cat logs/latest.log
```

**Check MCP servers:**
```bash
ps aux | grep playwright
```

**Test single cell:**
```python
from testgpt_engine import TestGPTEngine

engine = TestGPTEngine()
result = await engine.process_test_request(
    "test pointblank.club on iPhone"
)
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `config.py` | Viewport/browser/network profiles |
| `config.json` | MCP launch arguments |
| `viewport_parser_claude.py` | Claude API parser |
| `mcp_manager.py` | Dynamic MCP server management |
| `test_executor.py` | Test execution engine |
| `testgpt_engine.py` | Main orchestration |
| `main.py` | Entry point (Slack bot) |

---

## 🔗 Documentation Links

- **[SUPPORTED_BROWSERS.md](./SUPPORTED_BROWSERS.md)** - Full browser documentation
- **[DYNAMIC_MULTI_VIEWPORT.md](./DYNAMIC_MULTI_VIEWPORT.md)** - Multi-viewport architecture
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Complete implementation guide
- **[DEBUG_GUIDE.md](./DEBUG_GUIDE.md)** - Debugging and troubleshooting
- **[README.md](./README.md)** - Project overview

---

## ⚙️ Configuration

**Add new viewport:**
Edit `config.py` and `config.json`:
```python
# config.py
"my-device": ViewportProfile(
    name="my-device",
    width=1024,
    height=768,
    display_name="My Custom Device",
    playwright_device="iPad",  # or None
    ...
)
```

```json
// config.json
"my-device": {
  "name": "my-device",
  "mcp_launch_args": ["--device=iPad"],
  ...
}
```

**Add new browser:**
Add to `BROWSER_PROFILES` in `config.py` and update `config.json`.

---

## 🎯 Pro Tips

1. **Always test pointblank.club with Safari** - Auto-enabled for this site
2. **Use "responsive" keyword** - Tests 3 viewports automatically
3. **Check logs for details** - `logs/latest.log` shows full execution
4. **Browsers are pre-installed** - Agent shouldn't call browser_install
5. **Each test gets clean state** - No context carryover between tests

---

**Last updated:** 2025-10-31
**Version:** 1.0 (Dynamic Multi-Viewport)
