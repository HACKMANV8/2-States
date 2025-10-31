# TestGPT - Multi-Environment QA Testing System

**AI-powered QA agent that performs comprehensive cross-browser, cross-device, and cross-network testing like a professional manual QA engineer.**

## What is TestGPT?

TestGPT transforms simple Slack messages into comprehensive multi-environment QA test runs. It automatically:

- **Tests across multiple viewports** (iPhone SE, iPhone 13 Pro, iPad, desktop variations)
- **Tests across multiple browsers** (Chrome/Chromium, Safari/WebKit, Firefox)
- **Tests across network conditions** (normal broadband, slow 3G, flaky/unstable)
- **Identifies responsive design issues** and browser-specific bugs
- **Prioritizes failures** (critical bugs vs performance issues vs edge cases)
- **Saves scenarios** for easy re-running
- **Formats results** with actionable next steps

## Quick Start

### 1. Run the Test Demo (No Slack/MCP needed)

```bash
python test_testgpt.py
```

This demonstrates the full flow with mock results.

### 2. Run the Slack Bot

```bash
python slack_agent_testgpt.py
```

Then mention the bot in Slack:
```
@TestGPT test pointblank.club responsive on safari and iphone
```

## Example Usage

### Test Cross-Browser Responsive Behavior
```
@TestGPT run responsive tests on pointblank.club with safari and chrome
```

**What happens:**
1. Parses request → identifies target URL, flows, environments
2. Builds matrix: 3 viewports × 2 browsers × 1 network = 6 test runs
3. Executes all combinations using Playwright
4. Reports Safari failures vs Chrome successes
5. Saves scenario for re-running

### Test Under Slow Network
```
@TestGPT test checkout flow on slow 3G network
```

**What happens:**
1. Creates matrix with normal + slow 3G networks
2. Tests same flow in both conditions
3. Identifies performance issues (spinners stuck, timeouts)
4. Prioritizes network-specific failures as P1

### Re-run a Saved Test
```
@TestGPT re-run pointblank responsive test
```

**What happens:**
1. Finds matching saved scenario
2. Executes with same matrix configuration
3. Compares to previous run
4. Reports new failures or improvements

## Architecture

```
Slack Message
    ↓
SlackRequestParser (request_parser.py)
    ↓ ParsedSlackRequest
TestPlanBuilder (test_plan_builder.py)
    ↓ TestPlan with Matrix Cells
TestExecutor (test_executor.py)
    ↓ CellResults (via Playwright MCP)
ResultFormatter (result_formatter.py)
    ↓ RunArtifact + Slack Summary
PersistenceLayer (persistence.py)
    ↓ Saved to ./testgpt_data/
Slack Output
```

## Core Components

### 1. Models (`models.py`)
Complete data structures for:
- Scenarios and test plans
- Environment profiles (viewport, browser, network)
- Execution results (step-by-step, with evidence)
- Run artifacts for dashboard rendering

### 2. Configuration (`config.py`)
Standard catalogs:
- **10 viewport profiles** (iPhone SE → desktop ultrawide)
- **4 browser profiles** (Chromium, WebKit, Firefox)
- **3 network profiles** (normal, slow 3G, flaky)

### 3. Request Parser (`request_parser.py`)
Natural language understanding:
- Extracts URLs, flows, environment requirements
- Detects re-run requests
- Applies selection logic (keywords → profiles)

### 4. Test Plan Builder (`test_plan_builder.py`)
Matrix expansion:
- Builds deterministic test flows
- Expands Cartesian product: Flows × Viewports × Browsers × Networks
- Generates unique cell IDs

### 5. Test Executor (`test_executor.py`)
Playwright MCP integration:
- Executes each matrix cell independently
- Configures viewport, browser, network per cell
- Collects screenshots, console errors, network logs
- Determines failure priority (P0/P1/P2)

### 6. Result Formatter (`result_formatter.py`)
Aggregation and reporting:
- Aggregates cell results into run artifacts
- Groups failures by priority
- Formats Slack summaries with environment breakdown
- Generates actionable next steps

### 7. Persistence Layer (`persistence.py`)
Storage (JSON file-based):
- Saves scenarios for re-running
- Saves run artifacts for audit/dashboard
- Supports search by name, URL, tags

### 8. TestGPT Engine (`testgpt_engine.py`)
Main orchestrator:
- Coordinates all components
- Handles re-run logic
- Manages scenario lifecycle

## Environment Profiles

### Viewports
| Profile | Size | Device Class | Why It Matters |
|---------|------|--------------|----------------|
| `iphone-se` | 375×667 | Budget iOS | Smallest iPhone; catches cutoff |
| `iphone-13-pro` | 390×844 | Standard iOS | Most common iPhone viewport |
| `android-medium` | 412×915 | Mid-range Android | Galaxy S-class |
| `ipad-air` | 820×1180 | Tablet portrait | Often forgotten in responsive design |
| `desktop-standard` | 1920×1080 | Desktop baseline | Most common desktop resolution |

### Browsers
| Profile | Engine | Display Name | Platform |
|---------|--------|--------------|----------|
| `chromium-desktop` | Chromium | Chrome (Desktop) | Desktop |
| `webkit-desktop` | WebKit | Safari (macOS) | Desktop |
| `webkit-ios` | WebKit | Safari (iOS) | Mobile |
| `firefox-desktop` | Gecko | Firefox (Desktop) | Desktop |

### Networks
| Profile | Display Name | Conditions | Catches |
|---------|--------------|------------|---------|
| `normal` | Good Broadband | 50ms latency, 10Mbps | Baseline; any failure here is critical |
| `slow-3g` | Slow 3G | 400ms latency, 400Kbps | Spinners stuck, lazy-load failures |
| `flaky-edge` | Flaky/Unstable | 200ms latency, 2% packet loss | Button clicks don't register, silent failures |

## Failure Prioritization

### P0: Critical
- Fails on **normal network** + **standard viewport**
- Example: "Safari iOS: CTA button not visible in viewport"
- **Action required immediately**

### P1: Performance Issue
- Fails on **slow network**, passes on normal
- Example: "Page load timeout after 10 seconds on slow 3G"
- **Optimize for slow networks**

### P2: Edge Case
- Fails on **edge viewports** only
- Example: "Layout broken on ultrawide desktop"
- **Lower priority, niche issue**

## Slack Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 TestGPT QA Run Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario: Pointblank.club - Landing Page - Responsive Test
Target: https://pointblank.club
Run ID: run-20251031-143022
Status: ❌ FAIL (8/12 runs passed)

━━━ CRITICAL FAILURES ━━━

🔴 P0: Safari (iOS) / iPhone 13 Pro / Normal Network
   → Hero CTA button not visible in viewport
   → Button rendered 356px below fold
   → Screenshot: [link]

━━━ PASSES ━━━

✅ Chrome (Desktop): 6 runs passed

━━━ ENVIRONMENT BREAKDOWN ━━━

Viewports:
  • iPhone 13 Pro: 4/8 runs passed ⚠️
  • Desktop: 4/4 runs passed ✅

Browsers:
  • Chromium: 6/6 runs passed ✅
  • WebKit: 2/6 runs passed ❌

Network:
  • Normal: 6/9 runs passed ⚠️
  • Slow 3G: 2/3 runs passed ⚠️

━━━ NEXT STEPS ━━━

→ Fix Safari iOS: Adjust hero section height calculation
→ Re-run this test: "re-run pointblank responsive test"

📊 Full report: [dashboard link]
```

## Files Generated

### `testgpt_data/scenarios/*.json`
Saved scenario definitions for re-running:
```json
{
  "scenario_id": "scenario-pointblank-club-landing-3",
  "scenario_name": "Pointblank.club - Landing Page - Responsive Test",
  "target_url": "https://pointblank.club",
  "flows": [...],
  "environment_matrix": {...},
  "tags": ["pointblank", "demo", "responsive", "safari"]
}
```

### `testgpt_data/runs/*.json`
Complete run artifacts with all results:
```json
{
  "run_id": "run-20251031-143022",
  "overall_status": "FAIL",
  "total_cells": 12,
  "passed_cells": 8,
  "failed_cells": 4,
  "cell_results": [...],
  "failures_by_priority": {...}
}
```

## Demonstration: pointblank.club

**pointblank.club** is the canonical demo target. TestGPT is pre-configured to:

1. **Always include Safari** when testing this site
2. **Highlight Safari failures** vs Chrome successes
3. **Test responsive behavior** by default
4. **Report Safari issues first** in results

This demonstrates TestGPT catching real cross-browser issues.

## Extending TestGPT

### Add New Viewport Profiles
Edit `config.py`:
```python
"pixel-7-pro": ViewportProfile(
    name="pixel-7-pro",
    width=412,
    height=915,
    device_class="Google Pixel",
    description="Latest Pixel phone",
    device_scale_factor=2.6,
    is_mobile=True
)
```

### Add Custom Test Flows
Edit `agent_instructions.py`:
```python
def get_custom_flow():
    return {
        "flow_name": "Custom Checkout Flow",
        "steps": [...]
    }
```

### Add API Validation (Future)
When API MCP is available:
```python
# In test_executor.py
async def _validate_api_response(self, endpoint):
    # Call API MCP to validate backend
    pass
```

## Requirements

```
slack-bolt>=1.18.0
python-dotenv>=1.0.0
agno>=0.1.0  # AI agent framework
```

## Environment Variables

```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
ANTHROPIC_API_KEY=sk-...
```

## Next Steps

1. **Run the test demo** to see how it works
2. **Start the Slack bot** for live testing
3. **Test pointblank.club** to see Safari failures
4. **Save and re-run scenarios** to track regressions
5. **Build a dashboard** to visualize run artifacts

## Implementation Status

✅ Complete multi-environment test matrix
✅ Slack natural language parsing
✅ Viewport/browser/network catalogs
✅ Test plan building with matrix expansion
✅ Result aggregation and prioritization
✅ Slack summary formatting
✅ Persistence layer for scenarios/runs
✅ Re-run capability

🚧 Future enhancements:
- Real Playwright MCP execution (currently mocked)
- API validation via HTTP MCP
- Database state checking via Postgres MCP
- Dashboard UI for visualizing results
- Real device testing (iOS/Android containers)
- Parallel execution optimization

---

**Built according to TestGPT specification v1.0**
