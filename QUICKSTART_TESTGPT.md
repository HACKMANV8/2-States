# TestGPT Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Run the Test Demo

```bash
python test_testgpt.py
```

**What you'll see:**
- ✅ Request parsing in action
- ✅ Matrix expansion (18 cells for comprehensive test)
- ✅ Simulated test execution with Safari failures
- ✅ Formatted Slack summaries
- ✅ Saved scenarios and run artifacts

**Output location:** `./testgpt_data_test/`

---

### Step 2: Inspect Generated Data

```bash
# List saved scenarios
ls testgpt_data_test/scenarios/

# View a scenario definition
cat testgpt_data_test/scenarios/scenario-pointblank-club-landing-332.json

# List run artifacts
ls testgpt_data_test/runs/

# View a run artifact
cat testgpt_data_test/runs/run-*.json
```

**You'll see:**
- Complete scenario definitions with flows and steps
- Run artifacts with cell results and failure priorities
- Environment matrices and execution evidence

---

### Step 3: Start the Slack Bot (Optional)

```bash
# Make sure .env is configured with your tokens
python slack_agent_testgpt.py
```

**Then in Slack:**

```
@TestGPT test pointblank.club responsive on safari and iphone
```

**Expected behavior:**
1. Bot acknowledges request
2. Builds test matrix (9-18 cells)
3. Executes tests (currently mocked)
4. Posts formatted results with failures highlighted

---

## 💡 Example Commands to Try

### Test Responsive Behavior
```
@TestGPT test pointblank.club responsive on safari and iphone
```
**Creates:** 3 viewports × 2+ browsers = 6+ test runs

### Cross-Browser Testing
```
@TestGPT run landing page on safari and chrome
```
**Creates:** 2 browsers × multiple viewports

### Network Condition Testing
```
@TestGPT test checkout flow under slow network
```
**Creates:** 2 network profiles (normal + slow 3G)

### Comprehensive Test
```
@TestGPT run responsive safari/iphone vs chrome/desktop tests on pointblank.club under bad network
```
**Creates:** 3 viewports × 3 browsers × 2 networks = 18 test runs

### List Saved Scenarios
```
@TestGPT list scenarios
```
**Shows:** All saved test scenarios with re-run commands

### Re-run a Test
```
@TestGPT re-run pointblank responsive test
```
**Finds:** Matching scenario and re-executes

---

## 📊 Understanding the Output

### Slack Summary Structure

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 TestGPT QA Run Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario: Pointblank.Club - Landing - Cross-Browser Test
Target: https://pointblank.club
Run ID: run-20251031-153547-6d51c8
Status: ⚠️ PARTIAL (9/18 runs passed)
```
↑ **Header:** Scenario name, target URL, run ID, overall status

```
━━━ CRITICAL FAILURES ━━━

🔴 P0: Safari (iOS) / iPhone 13 Pro / Normal Network
   → Hero CTA button not visible in viewport
   → Button rendered 356px below fold
```
↑ **Failures:** P0 (critical) failures listed first with environment context

```
━━━ ENVIRONMENT BREAKDOWN ━━━

Viewports:
  • iPhone 13 Pro: 3/6 runs passed ⚠️
  • iPad Air: 3/6 runs passed ⚠️

Browsers:
  • Safari (iOS): 3/6 runs passed ⚠️
  • Chrome (Desktop): 4/6 runs passed ⚠️
```
↑ **Breakdown:** Per-dimension statistics showing where issues occur

```
━━━ NEXT STEPS ━━━

→ Fix Safari iOS: Adjust hero section height
→ Re-run this test: "re-run pointblank test"

📊 Full report: https://dashboard.testgpt.dev/runs/run-xxx
```
↑ **Actions:** Specific guidance for fixing issues + re-run command

---

## 🔍 What Gets Created

### Scenario Definition
**Location:** `testgpt_data/scenarios/scenario-*.json`

**Contains:**
```json
{
  "scenario_id": "scenario-pointblank-club-landing-332",
  "scenario_name": "Pointblank.Club - Landing - Cross-Browser Test",
  "target_url": "https://pointblank.club",
  "flows": [
    {
      "flow_name": "Landing Page Load and Hero CTA Visibility",
      "steps": [
        {
          "step_number": 1,
          "action": "navigate",
          "target": "https://pointblank.club",
          "expected_outcome": "Page loads with status 200"
        }
      ]
    }
  ],
  "environment_matrix": {
    "viewports": ["iphone-13-pro", "ipad-air", "desktop-standard"],
    "browsers": ["webkit-ios", "webkit-desktop", "chromium-desktop"],
    "networks": ["normal"]
  }
}
```

### Run Artifact
**Location:** `testgpt_data/runs/run-*.json`

**Contains:**
```json
{
  "run_id": "run-20251031-153547-6d51c8",
  "overall_status": "PARTIAL",
  "total_cells": 9,
  "passed_cells": 8,
  "failed_cells": 1,
  "cell_results": [
    {
      "cell_id": "landing_iphone-13-pro_webkit-ios_normal_...",
      "viewport": "iphone-13-pro",
      "browser": "webkit-ios",
      "network": "normal",
      "status": "FAIL",
      "failure_summary": "Safari (iOS) on iPhone: CTA not visible",
      "failure_priority": "P0",
      "step_results": [...]
    }
  ]
}
```

---

## 🎯 Key Features to Notice

### 1. Natural Language Understanding
You say: "responsive safari and chrome"
TestGPT understands:
- Test responsive = use mobile + tablet + desktop viewports
- Safari = include webkit-ios and webkit-desktop
- Chrome = include chromium-desktop
- Creates 3 × 3 = 9 test runs

### 2. Automatic Matrix Expansion
Single request → Multiple test runs
- Each combination gets unique cell ID
- All cells tracked independently
- Results aggregated intelligently

### 3. Failure Prioritization
- **P0 (🔴):** Fails on normal network + standard viewport (CRITICAL)
- **P1 (🟡):** Fails on slow network only (PERFORMANCE)
- **P2 (🟠):** Fails on edge viewport only (EDGE CASE)

### 4. Safari Focus
For pointblank.club:
- Safari automatically included
- Safari failures reported first
- Safari vs Chrome comparison explicit

### 5. Re-run Capability
Every test automatically saved:
- Stable scenario ID
- Complete step list
- Environment matrix preserved
- Re-run with plain English command

---

## 📁 Directory Structure After Running

```
TestGPT/
├── testgpt_data_test/          (Created by test_testgpt.py)
│   ├── scenarios/
│   │   ├── scenario-pointblank-club-landing-131.json
│   │   ├── scenario-pointblank-club-landing-331.json
│   │   └── scenario-pointblank-club-landing-332.json
│   ├── runs/
│   │   ├── run-20251031-153547-6d51c8.json
│   │   ├── run-20251031-153547-30d918.json
│   │   └── run-20251031-153547-bb0655.json
│   └── plans/
│
└── testgpt_data/               (Created by Slack bot)
    ├── scenarios/
    ├── runs/
    └── plans/
```

---

## 🐛 Troubleshooting

### Test script fails with import error
**Fix:** Make sure you're in the TestGPT directory
```bash
cd /Users/akashsingh/Desktop/TestGPT
python test_testgpt.py
```

### Slack bot doesn't respond
**Check:**
1. Bot is running (`python slack_agent_testgpt.py`)
2. Bot is invited to the channel
3. `.env` has correct tokens

### No scenarios saved
**Reason:** Test script uses `testgpt_data_test/` to avoid conflicts
**Location:** Check `./testgpt_data_test/scenarios/`

---

## 🎓 Learning Path

### 1. Start with Test Demo
```bash
python test_testgpt.py
```
Watch the full flow execute with logs

### 2. Inspect Generated Data
```bash
cat testgpt_data_test/scenarios/*.json | head -50
```
See the data structures

### 3. Read Architecture
```bash
cat ARCHITECTURE.md
```
Understand component relationships

### 4. Try Different Requests
Modify `test_testgpt.py` to test different scenarios

### 5. Connect Real Playwright
Uncomment MCP execution in `test_executor.py`

---

## 🚢 Next Steps

### Make it Production-Ready

1. **Connect Real Playwright MCP** (2-4 hours)
   - Implement actual browser automation in `test_executor.py`
   - Replace mock results with real execution

2. **Build Dashboard UI** (1-2 days)
   - Render run artifacts visually
   - Show heatmap of matrix results
   - Screenshot gallery

3. **Add Parallel Execution** (2-3 hours)
   - Use `asyncio.gather()` for concurrent cells
   - 4× speedup

4. **Deploy to Production**
   - Host Slack bot on server
   - Set up persistent storage (PostgreSQL)
   - Configure monitoring

---

## 📚 Documentation

- **[TESTGPT_README.md](TESTGPT_README.md)** - Complete user guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Spec compliance
- **[SUMMARY.md](SUMMARY.md)** - Quick overview

---

## 💬 Example Session

```bash
$ python test_testgpt.py

╔════════════════════════════════════════════════════════════╗
║  TestGPT Engine Test Suite                                 ║
╚════════════════════════════════════════════════════════════╝

================================================================================
TEST: Pointblank.club Safari vs Chrome Responsive Test
================================================================================

🚀 TestGPT Processing Request
───────────────────────────────
Message: Run responsive Safari/iPhone vs Chrome/Desktop tests on pointblank.club
User: test-user

📋 Step 1: Parsing Slack request...
   Target URL: https://pointblank.club
   Flows: landing
   Viewports: iphone-13-pro, ipad-air, desktop-standard
   Browsers: webkit-ios, webkit-desktop, chromium-desktop
   Networks: slow-3g, normal

🏗️  Step 2: Building test plan with matrix expansion...
   Scenario: Pointblank.Club - Landing - Cross-Browser Test
   Matrix cells: 18
   Estimated duration: 2 minutes

💾 Step 3: Saving scenario definition...
   Saved: scenario-pointblank-club-landing-332.json

⚠️  Step 4: Executing tests (mock mode)...
   Completed 18 cells

📊 Step 5: Aggregating results...
   Overall status: PARTIAL
   Pass rate: 9/18

✍️  Step 7: Formatting Slack summary...

✅ TestGPT Processing Complete

[Formatted Slack output displayed...]
```

---

**Ready to test? Run `python test_testgpt.py` now!**
