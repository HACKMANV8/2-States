# TestGPT Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           SLACK USER                                 │
│  "test pointblank.club responsive on safari and iphone"            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SLACK BOT (slack_agent_testgpt.py)              │
│  • Receives @mention                                                 │
│  • Extracts message                                                  │
│  • Calls TestGPT Engine                                             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   TESTGPT ENGINE (testgpt_engine.py)                │
│  Main orchestrator - coordinates all components                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  REQUEST PARSER  │  │  PLAN BUILDER    │  │  TEST EXECUTOR   │
│                  │  │                  │  │                  │
│ Natural Language │  │ Matrix Expansion │  │ Playwright MCP   │
│ → Structured     │  │ Scenario → Cells │  │ Test Execution   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  CONFIG          │  │  MODELS          │  │  PERSISTENCE     │
│                  │  │                  │  │                  │
│ 10 Viewports     │  │ Complete Data    │  │ Scenarios        │
│ 4 Browsers       │  │ Structures       │  │ Run Artifacts    │
│ 3 Networks       │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
          │                                             │
          └─────────────┬───────────────────────────────┘
                        ▼
          ┌─────────────────────────────┐
          │   RESULT FORMATTER          │
          │                             │
          │  Aggregation + Priorities   │
          │  Slack Summary Generation   │
          └──────────────┬──────────────┘
                         │
                         ▼
          ┌─────────────────────────────┐
          │   SLACK OUTPUT              │
          │                             │
          │  Formatted Test Results     │
          │  With Environment Breakdown │
          └─────────────────────────────┘
```

---

## Data Flow (7 Steps)

```
Step 1: PARSE
─────────────
Input:  "test pointblank.club responsive on safari and iphone"
Parser: SlackRequestParser
Output: ParsedSlackRequest
        ├─ target_urls: ["https://pointblank.club"]
        ├─ flows: ["landing"]
        ├─ required_viewports: ["iphone-13-pro", "ipad-air", "desktop-standard"]
        ├─ required_browsers: ["webkit-ios", "webkit-desktop", "chromium-desktop"]
        └─ required_networks: ["normal"]


Step 2: BUILD TEST PLAN
────────────────────────
Builder: TestPlanBuilder
Matrix:  3 viewports × 3 browsers × 1 network = 9 cells
Output:  TestPlan
         ├─ scenario_id: "scenario-pointblank-club-landing-331"
         ├─ scenario_name: "Pointblank.Club - Landing - Cross-Browser Test"
         ├─ flows: [TestFlow with deterministic steps]
         └─ matrix_cells: [9 × MatrixCell]
                           ├─ Cell 1: iphone-13-pro + webkit-ios + normal
                           ├─ Cell 2: iphone-13-pro + webkit-desktop + normal
                           └─ ... (7 more)


Step 3: SAVE SCENARIO
─────────────────────
Storage: PersistenceLayer
Output:  ./testgpt_data/scenarios/scenario-pointblank-club-landing-331.json
         (Complete scenario definition for re-running)


Step 4: EXECUTE TESTS
─────────────────────
Executor: TestExecutor
Process: For each MatrixCell:
         1. Configure browser context (viewport, browser, network)
         2. Execute test steps
         3. Capture screenshots on failures
         4. Collect console errors, network logs
         5. Determine pass/fail and priority
Output:  [9 × CellResult]


Step 5: AGGREGATE RESULTS
─────────────────────────
Formatter: ResultFormatter
Process:  1. Calculate overall status (PASS/FAIL/PARTIAL)
          2. Group failures by priority (P0/P1/P2)
          3. Calculate per-dimension stats (viewport/browser/network)
          4. Generate failure summaries
Output:   RunArtifact
          ├─ run_id: "run-20251031-153547-..."
          ├─ overall_status: PARTIAL
          ├─ passed_cells: 8
          ├─ failed_cells: 1
          ├─ cell_results: [9 × CellResult]
          └─ failures_by_priority: {P0: [cell-ids], P1: [], P2: []}


Step 6: SAVE RUN ARTIFACT
─────────────────────────
Storage: PersistenceLayer
Output:  ./testgpt_data/runs/run-20251031-153547-....json
         (Complete results with evidence for dashboard)


Step 7: FORMAT & POST
─────────────────────
Formatter: ResultFormatter
Output:   Slack-formatted text
          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          🤖 TestGPT QA Run Complete

          Scenario: Pointblank.Club - Landing - Cross-Browser Test
          Status: ⚠️ PARTIAL (8/9 runs passed)

          ━━━ CRITICAL FAILURES ━━━
          🔴 P0: Safari (iOS) / desktop-standard / normal
             → Pricing modal does not open on click

          ━━━ ENVIRONMENT BREAKDOWN ━━━
          Viewports: [stats]
          Browsers: [stats]
          ...

          📊 Full report: [dashboard link]
          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Component Responsibilities

### 1. Request Parser (`request_parser.py`)
**Input:** Natural language Slack message
**Output:** ParsedSlackRequest (structured requirements)
**Key Functions:**
- Extract URLs, flows, environment keywords
- Detect re-run requests
- Apply selection logic (keywords → profiles)
- Generate scenario names and IDs

### 2. Test Plan Builder (`test_plan_builder.py`)
**Input:** ParsedSlackRequest
**Output:** TestPlan with expanded matrix
**Key Functions:**
- Build test flows with deterministic steps
- Expand Cartesian product (F × V × B × N)
- Generate unique cell IDs
- Estimate execution time

### 3. Test Executor (`test_executor.py`)
**Input:** TestPlan
**Output:** List of CellResults
**Key Functions:**
- Execute each matrix cell
- Configure browser context per cell
- Collect evidence (screenshots, errors, logs)
- Determine failure priority (P0/P1/P2)

### 4. Result Formatter (`result_formatter.py`)
**Input:** List of CellResults
**Output:** RunArtifact + Slack summary
**Key Functions:**
- Aggregate results across cells
- Group failures by priority
- Calculate per-dimension stats
- Format Slack output

### 5. Persistence Layer (`persistence.py`)
**Input:** Scenarios, Run Artifacts
**Output:** JSON files in `./testgpt_data/`
**Key Functions:**
- Save/load scenarios
- Save/load run artifacts
- Search by name, URL, tags
- Update scenario last_run timestamp

### 6. TestGPT Engine (`testgpt_engine.py`)
**Input:** Slack message, user ID
**Output:** Formatted Slack summary
**Key Functions:**
- Orchestrate all components
- Handle re-run logic
- Manage scenario lifecycle
- Generate mock results (when no MCP)

---

## Data Models Hierarchy

```
ScenarioDefinition
├─ scenario_id: string
├─ scenario_name: string
├─ target_url: string
├─ flows: List[TestFlow]
│  └─ steps: List[TestStep]
│     ├─ action: ActionType (navigate, click, assert, etc.)
│     ├─ target: string (selector or URL)
│     └─ expected_outcome: string
└─ environment_matrix: EnvironmentMatrix
   ├─ viewports: List[string]
   ├─ browsers: List[string]
   └─ networks: List[string]

TestPlan
├─ test_plan_id: string
├─ scenario_id: string
├─ matrix_cells: List[MatrixCell]
│  ├─ cell_id: string
│  ├─ viewport: ViewportProfile
│  ├─ browser: BrowserProfile
│  ├─ network: NetworkProfile
│  └─ steps: List[TestStep]
└─ total_cells_to_execute: int

RunArtifact
├─ run_id: string
├─ overall_status: TestStatus (PASS/FAIL/PARTIAL)
├─ cell_results: List[CellResult]
│  ├─ cell_id: string
│  ├─ status: TestStatus
│  ├─ step_results: List[StepResult]
│  ├─ screenshots: List[Screenshot]
│  ├─ console_errors: List[ConsoleError]
│  └─ failure_priority: FailurePriority (P0/P1/P2)
└─ failures_by_priority: FailuresByPriority
   ├─ P0: List[cell_id]
   ├─ P1: List[cell_id]
   └─ P2: List[cell_id]
```

---

## Configuration Structure

```
VIEWPORT_PROFILES = {
    "iphone-se": ViewportProfile(375×667, mobile, 2.0x),
    "iphone-13-pro": ViewportProfile(390×844, mobile, 3.0x),
    "android-medium": ViewportProfile(412×915, mobile, 2.5x),
    "ipad-air": ViewportProfile(820×1180, tablet, 2.0x),
    "desktop-standard": ViewportProfile(1920×1080, desktop, 1.0x),
    ... (10 total)
}

BROWSER_PROFILES = {
    "chromium-desktop": BrowserProfile(chromium, desktop),
    "webkit-desktop": BrowserProfile(webkit, desktop),
    "webkit-ios": BrowserProfile(webkit, mobile),
    "firefox-desktop": BrowserProfile(firefox, desktop)
}

NETWORK_PROFILES = {
    "normal": NetworkProfile(50ms, 10Mbps, 0% loss),
    "slow-3g": NetworkProfile(400ms, 400Kbps, 0% loss),
    "flaky-edge": NetworkProfile(200ms, 1Mbps, 2% loss)
}
```

---

## Matrix Expansion Example

```
Request: "test responsive on safari and chrome"

Parsing:
  flows = ["landing"]
  viewports = ["iphone-13-pro", "ipad-air", "desktop-standard"]
  browsers = ["webkit-ios", "webkit-desktop", "chromium-desktop"]
  networks = ["normal"]

Matrix Expansion:
  1 flow × 3 viewports × 3 browsers × 1 network = 9 cells

Cells Generated:
  1. landing_iphone-13-pro_webkit-ios_normal_20251031-153547
  2. landing_iphone-13-pro_webkit-desktop_normal_20251031-153547
  3. landing_iphone-13-pro_chromium-desktop_normal_20251031-153547
  4. landing_ipad-air_webkit-ios_normal_20251031-153547
  5. landing_ipad-air_webkit-desktop_normal_20251031-153547
  6. landing_ipad-air_chromium-desktop_normal_20251031-153547
  7. landing_desktop-standard_webkit-ios_normal_20251031-153547
  8. landing_desktop-standard_webkit-desktop_normal_20251031-153547
  9. landing_desktop-standard_chromium-desktop_normal_20251031-153547
```

---

## Failure Priority Algorithm

```python
def determine_priority(cell: MatrixCell) -> FailurePriority:
    is_normal_network = (cell.network.name == "normal")
    is_standard_viewport = (cell.viewport.name in [
        "iphone-13-pro", "ipad-air", "desktop-standard"
    ])

    if is_normal_network and is_standard_viewport:
        return FailurePriority.P0  # Critical: fails on baseline
    elif not is_normal_network:
        return FailurePriority.P1  # Performance: network issue
    else:
        return FailurePriority.P2  # Edge case: unusual viewport
```

---

## File Structure

```
TestGPT/
├── Core Implementation
│   ├── models.py                  (500 lines)
│   ├── config.py                  (250 lines)
│   ├── agent_instructions.py      (300 lines)
│   ├── request_parser.py          (300 lines)
│   ├── test_plan_builder.py       (350 lines)
│   ├── test_executor.py           (450 lines)
│   ├── result_formatter.py        (400 lines)
│   ├── persistence.py             (300 lines)
│   ├── testgpt_engine.py          (350 lines)
│   └── slack_agent_testgpt.py     (200 lines)
│
├── Testing & Demo
│   └── test_testgpt.py
│
├── Documentation
│   ├── TESTGPT_README.md          (User guide)
│   ├── IMPLEMENTATION_COMPLETE.md (Spec compliance)
│   ├── SUMMARY.md                 (Quick overview)
│   ├── ARCHITECTURE.md            (This file)
│   └── README.md                  (Updated)
│
├── Legacy Examples
│   ├── slack_agent.py             (Original simple bot)
│   ├── 01_basic_context7_agent.py
│   └── ... (other examples)
│
└── Generated Data
    └── testgpt_data/
        ├── scenarios/             (Saved test definitions)
        ├── runs/                  (Execution results)
        └── plans/                 (Test plans)
```

---

## Extension Points

### Add New Viewport Profile
```python
# In config.py
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

### Add Custom Test Flow
```python
# In agent_instructions.py
def get_custom_checkout_flow():
    return {
        "flow_name": "E-commerce Checkout",
        "steps": [
            {"action": "navigate", "target": "/products", ...},
            {"action": "click", "target": "button.add-to-cart", ...},
            {"action": "click", "target": "a.checkout", ...},
            {"action": "fill", "target": "input[name='email']", ...},
            ...
        ]
    }
```

### Add API Validation (Future)
```python
# In test_executor.py
async def _validate_api(self, endpoint):
    # Call HTTP MCP to validate backend
    response = await self.api_mcp.get(endpoint)
    assert response.status == 200
    assert "expected_field" in response.json()
```

---

## Performance Characteristics

### Sequential Execution (Current)
```
18 cells × 5 seconds/cell = 90 seconds total
```

### Parallel Execution (Future)
```
18 cells ÷ 4 parallel ÷ 5 seconds/cell = ~22 seconds total
(4× speedup)
```

---

**Architecture designed for:**
- ✅ Scalability (easy to add profiles/flows)
- ✅ Maintainability (clean separation of concerns)
- ✅ Testability (each component independently testable)
- ✅ Extensibility (clear extension points)
- ✅ Reliability (deterministic, repeatable tests)
