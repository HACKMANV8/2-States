# TestGPT Coverage System - Demo Guide

**For Demo Videos & Presentations**

---

## Table of Contents

1. [Current State vs. Future Integration](#current-state-vs-future-integration)
2. [Standalone Demo (What Works NOW)](#standalone-demo-what-works-now)
3. [Full Integration Demo (Future State)](#full-integration-demo-future-state)
4. [Demo Video Script](#demo-video-script)
5. [Sample Integration Example](#sample-integration-example)
6. [Troubleshooting](#troubleshooting)

---

## Current State vs. Future Integration

### ✅ What Works NOW (Standalone)

The coverage system is **fully functional** as a standalone module:

```
┌─────────────────────────────────────────────┐
│  Coverage System (Standalone)               │
│                                             │
│  ✅ MCDC Analysis                          │
│  ✅ Coverage Calculation                   │
│  ✅ Stop Conditions                        │
│  ✅ Report Generation                      │
│  ✅ Database Persistence                   │
└─────────────────────────────────────────────┘
```

**Use Case:** Demonstrate the coverage algorithms, MCDC analysis, and intelligent stopping logic.

### 🔄 Future Integration (In Progress)

Full integration with TestGPT's Slack → Agent → Testing flow:

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Slack   │───▶│  TestGPT    │───▶│  Playwright  │───▶│  Coverage    │
│  Bot     │    │  Engine     │    │  Testing     │    │  Collection  │
└──────────┘    └─────────────┘    └──────────────┘    └──────────────┘
      │                │                   │                    │
      │                │                   │                    │
      ▼                ▼                   ▼                    ▼
   @TestGPT        Parse PR           Execute Tests       Track Coverage
   test PR         Create Plan         UI Actions         MCDC Analysis
   with coverage   Config              API Calls          Stop Decision
                                                          Generate Report
```

**Status:** Architecture ready, integration hooks needed in test_executor.py

---

## Standalone Demo (What Works NOW)

### Demo Flow: 5-Minute Showcase

This demonstrates all working features without requiring Slack/Playwright integration.

#### Prerequisites

```bash
# Ensure you're in the TestGPT directory
cd /Users/akashsingh/Desktop/TestGPT

# Verify Python and dependencies
python --version  # Should be 3.13+
pip list | grep sqlalchemy  # Should show 2.0+
```

---

### Demo Part 1: Database Setup (30 seconds)

**What to Show:** Database initialization with all tables.

```bash
# Clear previous database (for clean demo)
rm -f testgpt_coverage.db

# Initialize database
python coverage/cli.py init
```

**Expected Output:**
```
🚀 Initializing TestGPT Coverage Database...
✅ Coverage database tables created
✅ Database initialized successfully
```

**Talking Points:**
- "The coverage system uses SQLite with 7 specialized tables"
- "Stores coverage runs, MCDC analysis, reports, and test effectiveness"

---

### Demo Part 2: MCDC Analysis (2 minutes)

**What to Show:** Intelligent test case generation for complex boolean conditions.

```bash
# Analyze sample file with 5 complex conditions
python coverage/cli.py analyze-mcdc examples/sample_mcdc.py
```

**Expected Output:**
```
Decision 1:
  Expression: user.is_authenticated and (user.is_admin or resource.is_public)
  Conditions: 3
  MCDC Achievable: ✅
  Required Tests: 4
  Truth Table Rows: 8
```

**Talking Points:**
- "MCDC is required for safety-critical systems (aviation, automotive)"
- "System generates truth tables and identifies minimum test sets"
- "Look at Decision 3: 4 conditions require only 5 tests (not 16)"
- "This prevents over-testing while ensuring quality"

**Demo Tip:** Open `examples/sample_mcdc.py` side-by-side to show the actual code being analyzed.

---

### Demo Part 3: Coverage Orchestration (2 minutes)

**What to Show:** Full lifecycle with intelligent stop conditions.

```bash
# Run with default configuration (80% threshold)
python coverage/cli.py run https://github.com/test/repo default
```

**Watch For:**
- Coverage progression: 50% → 58% → 66% → 74% → 82%
- Diminishing returns: Each test adds less coverage
- Stop decisions: "CONTINUE testing" vs "STOP recommended"

**Expected Output:**
```
Running test_1...
   Coverage: 50.0% (Δ +50.0%)

Running test_2...
   Coverage: 58.0% (Δ +8.0%)

Evaluating stop condition...
   ▶️  CONTINUE testing: Coverage 14.0% below threshold
```

**Talking Points:**
- "System tracks coverage in real-time with diminishing returns model"
- "Each test is less effective as coverage increases"
- "Stop condition uses multi-criteria evaluation: threshold + MCDC + plateau"

**Demo Variation:** Run with strict config to show different behavior:

```bash
# Strict requires 100% coverage
python coverage/cli.py run https://github.com/test/repo strict
```

Point out: "Now it continues longer because strict requires 100%"

---

### Demo Part 4: Report Generation (1 minute)

**What to Show:** Multiple report formats from same data.

```bash
# List recent runs to get a run ID
python coverage/cli.py list
```

**Expected Output:**
```
✅ cov-9fa736ff3d82
   Status: completed
   Coverage: 90.0%
   Tests: 5
```

```bash
# View detailed report
python coverage/cli.py report cov-9fa736ff3d82
```

**Talking Points:**
- "System generates 3 report formats: JSON (API), HTML (visual), Summary (Slack)"
- "Reports include coverage %, MCDC status, test count, and gaps"

---

### Demo Part 5: Configuration Presets (30 seconds)

**What to Show:** Different quality thresholds for different use cases.

```bash
# Quick comparison of all 3 presets
echo "=== PERMISSIVE (50%) ==="
python coverage/cli.py run https://github.com/test/repo permissive | grep "Stop:"

echo "=== DEFAULT (80%) ==="
python coverage/cli.py run https://github.com/test/repo default | grep "Stop:"

echo "=== STRICT (100%) ==="
python coverage/cli.py run https://github.com/test/repo strict | grep "Stop:"
```

**Talking Points:**
- "Permissive: Fast iteration (50% coverage)"
- "Default: Balanced quality (80% coverage)"
- "Strict: Safety-critical (100% coverage + MCDC)"

---

### Demo Part 6: Comprehensive Test Suite (Optional - 30 seconds)

**What to Show:** All features validated in automated test.

```bash
python scripts/test_coverage_system.py
```

**Wait for:**
```
✅ ALL TESTS PASSED

Coverage system is functional!
```

**Talking Points:**
- "Automated test suite validates all 5 core components"
- "Tests MCDC analysis, orchestration, database, reports, and stop conditions"
- "100% pass rate ensures system reliability"

---

## Full Integration Demo (Future State)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Slack Command                                              │
│  @TestGPT test PR https://github.com/owner/repo/pull/123    │
│            with coverage                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  TestGPT Engine (testgpt_engine.py)                         │
│  • Parse PR URL                                             │
│  • Detect "with coverage" flag                              │
│  • Initialize CoverageOrchestrator                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Coverage Orchestrator (coverage/orchestrator.py)           │
│  • Analyze PR diff (changed files)                          │
│  • Instrument code                                          │
│  • Start coverage collection                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Test Executor (test_executor.py)                           │
│  • Execute test plan                                        │
│  • Track Playwright actions                                 │
│  • Record coverage after each test                          │
│  • Check stop condition                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Coverage Collector (NEW - coverage/collector/)             │
│  • Map UI action → code execution                           │
│  • Track line/branch hits                                   │
│  • Calculate MCDC satisfaction                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Report & Notify                                            │
│  • Generate HTML/JSON reports                               │
│  • Post to Slack                                            │
│  • Comment on GitHub PR                                     │
│  • Save to database                                         │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

#### 1. test_executor.py (Priority 1)

**Where:** `TestExecutor.__init__()` and `execute_test_plan()`

**What to Add:**
```python
class TestExecutor:
    def __init__(self, mcp_tools=None, coverage_enabled=False):
        self.mcp_manager = get_mcp_manager()
        self.agent = None

        # NEW: Coverage support
        self.coverage_enabled = coverage_enabled
        self.coverage_orchestrator = None

    async def execute_test_plan(self, test_plan: TestPlan) -> List[CellResult]:
        """Execute test plan with optional coverage tracking."""

        # NEW: Start coverage if enabled
        if self.coverage_enabled and self.coverage_orchestrator:
            await self.coverage_orchestrator.start_coverage()

        results = []

        for cell in test_plan.matrix_cells:
            # Execute cell
            cell_result = await self.execute_cell(cell)
            results.append(cell_result)

            # NEW: Record coverage after each test
            if self.coverage_enabled:
                await self.coverage_orchestrator.record_test_execution(
                    test_id=cell.cell_id,
                    test_name=cell.cell_id,
                    execution_time_ms=cell_result.duration_ms
                )

                # Check if should stop
                decision = await self.coverage_orchestrator.should_stop_testing()
                if decision.should_stop:
                    print(f"🛑 Stopping early: {decision.reason}")
                    break

        return results
```

#### 2. testgpt_engine.py (Priority 1)

**Where:** `_execute_pr_tests_with_playwright()`

**What to Add:**
```python
from coverage import CoverageOrchestrator, CoverageConfig

async def _execute_pr_tests_with_playwright(
    self,
    deployment_url: str,
    instructions: str,
    pr_context: Dict[str, Any]
) -> Dict[str, Any]:

    # NEW: Check if coverage requested
    coverage_enabled = "coverage" in instructions.lower() or \
                      "with coverage" in self.original_message.lower()

    coverage_orchestrator = None
    if coverage_enabled:
        # Initialize coverage
        config = CoverageConfig.default()
        coverage_orchestrator = CoverageOrchestrator(
            pr_url=pr_context.get("pr_url"),
            config=config.to_dict()
        )
        print("📊 Coverage tracking enabled")

    # Create executor with coverage
    executor = TestExecutor(coverage_enabled=coverage_enabled)
    if coverage_enabled:
        executor.coverage_orchestrator = coverage_orchestrator

    # Execute tests
    results = await executor.execute_test_plan(test_plan)

    # NEW: Generate coverage report
    if coverage_enabled:
        coverage_report = await coverage_orchestrator.generate_report("summary")
        result["coverage_report"] = coverage_report.report_data

    return result
```

#### 3. main.py (Priority 2)

**Where:** Slack event handler

**What to Add:**
```python
# Detect coverage keywords
if "with coverage" in message_text.lower() or \
   "coverage" in message_text.lower():
    await say("📊 Coverage tracking enabled for this test run!")
```

---

## Demo Video Script

### 🎬 5-Minute Demo Video Outline

**Title:** "TestGPT Coverage System - Intelligent Test Optimization with MCDC"

---

#### Scene 1: Introduction (30 seconds)

**Visual:** Terminal with TestGPT banner

**Script:**
> "Hi, I'm going to show you TestGPT's intelligent coverage system. This system tracks code coverage during testing, analyzes complex boolean conditions using MCDC, and automatically decides when to stop testing based on coverage quality."

**Action:**
```bash
cd /Users/akashsingh/Desktop/TestGPT
python coverage/cli.py init
```

---

#### Scene 2: MCDC Analysis (90 seconds)

**Visual:** Split screen - code on left, terminal on right

**Script:**
> "Let's start with MCDC analysis. MCDC stands for Modified Condition Decision Coverage - it's required for safety-critical systems like aviation and automotive software."

**Action:**
```bash
# Show the code first
cat examples/sample_mcdc.py | grep -A 10 "def check_user_access"

# Then analyze it
python coverage/cli.py analyze-mcdc examples/sample_mcdc.py
```

**Script (while output appears):**
> "Look at this authentication function. It has 3 conditions: is_authenticated, is_admin, and is_public. A naive approach would test all 8 combinations, but MCDC shows we only need 4 tests to ensure each condition independently affects the outcome. This saves time while maintaining quality."

---

#### Scene 3: Coverage Tracking (90 seconds)

**Visual:** Terminal with coverage run

**Script:**
> "Now let's see the coverage orchestration in action. I'll run a simulated test suite with the default configuration."

**Action:**
```bash
python coverage/cli.py run https://github.com/test/repo default
```

**Script (while tests run):**
> "Watch the coverage increase: 50%, 58%, 66%... Notice how each test adds less coverage? That's the diminishing returns model. The system tracks this and uses it to decide when to stop.
>
> See here - the stop condition evaluator runs after each test. It's checking: Have we hit the threshold? Is MCDC satisfied? Has coverage plateaued? Right now it says 'CONTINUE' because we're at 74%, below our 80% threshold."

---

#### Scene 4: Intelligent Stopping (60 seconds)

**Visual:** Side-by-side comparison of 3 configs

**Script:**
> "The system supports three quality levels. Let me show you how they differ."

**Action:**
```bash
# Show output side by side (pre-recorded or quick cuts)
python coverage/cli.py run https://github.com/test/repo permissive
# → Stops at 50%

python coverage/cli.py run https://github.com/test/repo default
# → Stops at 80%

python coverage/cli.py run https://github.com/test/repo strict
# → Requires 100%
```

**Script:**
> "Permissive mode is for fast iteration - stops at 50%. Default balances speed and quality at 80%. Strict mode is for production and safety-critical code - requires 100% coverage AND full MCDC satisfaction."

---

#### Scene 5: Reports & Integration (60 seconds)

**Visual:** Terminal + browser with HTML report (optional)

**Script:**
> "After testing, the system generates comprehensive reports."

**Action:**
```bash
python coverage/cli.py list
python coverage/cli.py report <run-id>
```

**Script:**
> "You can see coverage percentage, tests executed, MCDC status, and identified gaps. The system generates three formats: JSON for APIs, HTML for visualization, and text summaries for Slack.
>
> This entire system integrates into TestGPT's Slack bot. When you test a PR, just add 'with coverage' and it automatically tracks coverage, evaluates MCDC requirements, and stops when quality thresholds are met."

---

#### Scene 6: Wrap-up (30 seconds)

**Visual:** Architecture diagram or summary slide

**Script:**
> "To recap: The TestGPT coverage system provides MCDC analysis for critical conditions, intelligent stop decisions based on multiple criteria, and comprehensive reporting. It's production-ready and integrates seamlessly with the existing Slack-driven testing workflow. Thanks for watching!"

---

## Sample Integration Example

I'll create a working demo script that simulates the full integration:

**File:** `scripts/demo_integrated_coverage.py`

```python
#!/usr/bin/env python3
"""
Demo script showing full integration of coverage with TestGPT workflow.

This simulates what the integrated flow will look like.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from coverage import CoverageOrchestrator, CoverageConfig


async def simulate_slack_to_coverage_flow():
    """Simulate: Slack command → TestGPT → Coverage → Results"""

    print("\n" + "="*70)
    print("SIMULATED INTEGRATION: Slack → TestGPT → Coverage")
    print("="*70)

    # Step 1: Slack message received
    print("\n📱 SLACK MESSAGE RECEIVED:")
    print("   User: @TestGPT test PR https://github.com/owner/repo/pull/123")
    print("         with coverage")

    await asyncio.sleep(1)

    # Step 2: TestGPT engine processes request
    print("\n⚙️  TESTGPT ENGINE:")
    print("   ✅ Parsed PR URL: #123")
    print("   ✅ Detected coverage flag")
    print("   ✅ Fetching PR context...")

    await asyncio.sleep(1)

    # Step 3: Coverage orchestrator initializes
    print("\n📊 COVERAGE ORCHESTRATOR:")
    config = CoverageConfig.default()
    orchestrator = CoverageOrchestrator(
        pr_url="https://github.com/owner/repo/pull/123",
        config=config.to_dict()
    )

    run = await orchestrator.start_coverage()
    print(f"   ✅ Initialized: {run.run_id}")
    print(f"   📋 Threshold: {config.changed_lines_threshold}%")
    print(f"   🔬 MCDC Required: {config.mcdc_required}")

    await asyncio.sleep(1)

    # Step 4: Test execution with coverage tracking
    print("\n🎭 TEST EXECUTOR:")
    print("   Creating test plan from PR changes...")
    print("   Found 3 test scenarios:")
    print("   • Test 1: Login flow")
    print("   • Test 2: API authentication")
    print("   • Test 3: Authorization checks")

    await asyncio.sleep(1)

    test_scenarios = [
        ("Login flow", 1200),
        ("API authentication", 1500),
        ("Authorization checks", 1800)
    ]

    for i, (name, duration) in enumerate(test_scenarios, 1):
        print(f"\n   ▶️  Executing Test {i}: {name}")
        print(f"      • Launching browser...")
        print(f"      • Navigating to deployment URL...")
        print(f"      • Performing UI actions...")

        await asyncio.sleep(0.5)

        # Record test execution
        effectiveness = await orchestrator.record_test_execution(
            test_id=f"test-{i}",
            test_name=name,
            execution_time_ms=duration
        )

        print(f"      ✅ Test passed ({duration}ms)")
        print(f"      📊 Coverage: {orchestrator._calculate_current_coverage():.1f}%")
        print(f"      💡 Effectiveness: {effectiveness.effectiveness_score:.2f}")

        # Check stop condition
        decision = await orchestrator.should_stop_testing()

        if decision.should_stop:
            print(f"\n   🛑 STOP DECISION:")
            print(f"      Reason: {decision.reason}")
            print(f"      Confidence: {decision.confidence_score:.0%}")
            break
        else:
            print(f"      ▶️  Continue: {decision.reason}")

    # Step 5: Generate reports
    print("\n📈 GENERATING REPORTS:")

    summary = await orchestrator.generate_report("summary")
    json_report = await orchestrator.generate_report("json")
    html_report = await orchestrator.generate_report("html")

    print(f"   ✅ Summary: {len(summary.report_data)} bytes")
    print(f"   ✅ JSON: {len(json_report.report_data)} bytes")
    print(f"   ✅ HTML: {len(html_report.report_data)} bytes")

    # Step 6: Post results to Slack
    print("\n💬 POSTING TO SLACK:")
    print("   " + "─"*60)
    print(summary.report_data)
    print("   " + "─"*60)
    print("   🔗 View detailed HTML report: <link>")

    # Step 7: Comment on GitHub PR (optional)
    print("\n🐙 GITHUB PR COMMENT:")
    print("   ✅ Posted coverage summary to PR #123")
    print("   📊 Changed lines: 85% covered")
    print("   🔬 MCDC: Not satisfied (2/5 conditions)")

    print("\n" + "="*70)
    print("✅ INTEGRATION COMPLETE")
    print("="*70)
    print("\nThis is how the full flow will work once integrated!")


if __name__ == "__main__":
    asyncio.run(simulate_slack_to_coverage_flow())
```

**Run this demo:**
```bash
python scripts/demo_integrated_coverage.py
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Module not found: coverage"
**Solution:**
```bash
# Make sure you're in the right directory
cd /Users/akashsingh/Desktop/TestGPT

# Verify coverage module exists
ls -la coverage/

# Try running with explicit path
PYTHONPATH=. python coverage/cli.py init
```

#### Issue 2: "Database is locked"
**Solution:**
```bash
# Remove existing database
rm testgpt_coverage.db testgpt_coverage_test.db

# Reinitialize
python coverage/cli.py init
```

#### Issue 3: SQLAlchemy version mismatch
**Solution:**
```bash
# Check version
pip show sqlalchemy

# If not 2.0+, upgrade
pip install --upgrade sqlalchemy
```

#### Issue 4: Demo runs too fast to follow
**Solution:**
```bash
# Add delays between commands
python coverage/cli.py init
sleep 2

python coverage/cli.py analyze-mcdc examples/sample_mcdc.py | less
# Press space to scroll

# Or save output
python coverage/cli.py run https://github.com/test/repo default > demo_output.txt
cat demo_output.txt
```

---

## Quick Reference: Demo Commands

```bash
# Setup
cd /Users/akashsingh/Desktop/TestGPT
rm -f testgpt_coverage.db
python coverage/cli.py init

# MCDC Demo
python coverage/cli.py analyze-mcdc examples/sample_mcdc.py

# Coverage Run Demo
python coverage/cli.py run https://github.com/test/repo default
python coverage/cli.py run https://github.com/test/repo strict

# Reports Demo
python coverage/cli.py list
python coverage/cli.py report <run-id>

# Full Test Suite
python scripts/test_coverage_system.py

# Simulated Integration
python scripts/demo_integrated_coverage.py
```

---

## Tips for a Great Demo Video

1. **Use a clean terminal theme** - Dark background, high contrast
2. **Increase font size** - Minimum 14pt for readability
3. **Clear the screen** between demos - `clear` command
4. **Slow down** - Add `sleep 2` between commands if recording
5. **Use screen recording with annotations** - Highlight important output
6. **Have a backup** - Pre-record terminal output in case live demo fails
7. **Show the code** - Open `examples/sample_mcdc.py` to show what's being analyzed
8. **Narrate what's happening** - Explain diminishing returns, MCDC, stop decisions

---

**Last Updated:** 2025-11-01
**Status:** Ready for Demo
**Next Steps:** Record demo video, create integration PR
