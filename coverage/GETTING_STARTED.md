# Getting Started with TestGPT Coverage System

## Overview

The TestGPT Coverage System tracks code coverage during Playwright-based tests, implements MCDC analysis, and intelligently determines when to stop testing.

## Installation

### 1. Install Dependencies

```bash
cd /Users/ahanamurthy/Documents/TestGpt/2-States

# Install Python dependencies
pip install sqlalchemy astor

# Optional: For advanced features
pip install coverage  # Python coverage
# npm install @babel/core istanbul  # JS coverage
```

### 2. Initialize Database

```bash
python coverage/cli.py init
```

This creates the SQLite database with all necessary tables.

## Quick Start

### Example 1: Analyze PR Changes

Analyze what code changed in a GitHub PR:

```bash
python coverage/cli.py analyze-pr https://github.com/owner/repo/pull/123
```

**Output:**
```
📋 Analyzing PR: https://github.com/owner/repo/pull/123
   Found 5 changed files

======================================================================
ANALYSIS RESULTS
======================================================================
PR Number: 123
Changed Files: 5
Total Changes: 23
Changed Functions: 12
Lines Added: 145
Lines Deleted: 32
Lines Modified: 89
Critical Changes: 2

🚨 Critical Changes:
   • src/auth/login.py:45-67
     Function: validate_credentials

🔧 Changed Functions:
   • validate_credentials in src/auth/login.py
     Lines: 45-67, Complexity: 8
   • process_payment in src/payment/processor.py
     Lines: 102-134, Complexity: 12
```

### Example 2: MCDC Analysis

Analyze boolean conditions in a file to determine required test cases:

```bash
python coverage/cli.py analyze-mcdc examples/sample_conditions.py
```

**Sample File** (`examples/sample_conditions.py`):
```python
def check_access(user, resource):
    # Complex condition requiring MCDC
    if user.is_authenticated and (user.is_admin or resource.is_public):
        return True
    return False
```

**Output:**
```
🔍 Analyzing MCDC in: examples/sample_conditions.py
   Found 1 decisions

======================================================================
MCDC ANALYSIS RESULTS
======================================================================
Decisions Found: 1

Decision 1:
  Expression: user.is_authenticated and (user.is_admin or resource.is_public)
  Line: 3
  Conditions: 3
  Complexity: 3
  MCDC Achievable: ✅
  Required Tests: 6
  Truth Table Rows: 8

  Sample Test Cases:
    • T1: C1=True, C2=True, C3=True → True
    • T2: C1=True, C2=False, C3=True → True
    • T3: C1=False, C2=True, C3=True → False
```

### Example 3: Full Coverage Run (Simulated)

Run a complete coverage collection (currently simulated):

```bash
python coverage/cli.py run https://github.com/owner/repo/pull/123 strict
```

**Output:**
```
🚀 Starting Coverage Run
======================================================================

✅ Coverage orchestrator initialized
   Run ID: cov-abc123def456
   Config: 100% changed lines, MCDC=True

   📋 Analyzing PR: https://github.com/owner/repo/pull/123
   🔧 Instrumenting code...
   📊 Initializing coverage collector...

✅ Coverage collection started (Run ID: cov-abc123def456)

======================================================================
SIMULATING TEST EXECUTION
======================================================================

Running test_1...
📝 Recording test: test_1
   Coverage: 55.0% (Δ +55.0%)
   Effectiveness: 0.55

🤔 Evaluating stop condition...
   ▶️  CONTINUE testing: Coverage 45.0% below threshold (confidence: 80%)

Running test_2...
📝 Recording test: test_2
   Coverage: 60.0% (Δ +5.0%)
   Effectiveness: 0.05

🤔 Evaluating stop condition...
   🛑 STOP recommended: Coverage threshold met (confidence: 100%)

======================================================================
GENERATING REPORT
======================================================================

✅ Coverage run complete!
   Run ID: cov-abc123def456
   Report ID: report-xyz789
   Coverage: 100.0%
   Tests: 2

💾 Saved to database
```

### Example 4: View Coverage Reports

List recent coverage runs:

```bash
python coverage/cli.py list
```

View detailed report:

```bash
python coverage/cli.py report cov-abc123def456
```

## Integration with TestGPT

### Step 1: Enable Coverage in PR Tests

```python
# In your test script
from coverage import CoverageOrchestrator

# Start coverage collection
orchestrator = CoverageOrchestrator(
    pr_url="https://github.com/owner/repo/pull/123",
    config={
        "changed_lines_threshold": 80,
        "mcdc_required": True
    }
)

await orchestrator.start_coverage()

# Run your tests
await testgpt_engine.execute_pr_tests(pr_url)

# Check if should stop
decision = await orchestrator.should_stop_testing()
if decision.should_stop:
    print(f"Stopping: {decision.reason}")

# Generate report
report = await orchestrator.generate_report()
```

### Step 2: View Coverage in Slack

```
@TestGPT test this PR with coverage: https://github.com/owner/repo/pull/123

# Later...
@TestGPT show coverage for PR 123
```

## Configuration

### Preset Configurations

**Default Configuration** (Balanced):
```python
config = CoverageConfig.default()
# - 80% changed lines coverage
# - 100% new lines coverage
# - MCDC required
# - 5-test plateau detection
# - 60 minute time limit
```

**Strict Configuration** (High Quality):
```python
config = CoverageConfig.strict()
# - 100% changed lines coverage
# - 100% new lines coverage
# - MCDC required
# - 5-test plateau detection
# - 100% minimum coverage
```

**Permissive Configuration** (Fast Iteration):
```python
config = CoverageConfig.permissive()
# - 50% changed lines coverage
# - 70% new lines coverage
# - MCDC optional
# - 50% minimum coverage
```

### Custom Configuration

```python
from coverage import CoverageConfig

config = CoverageConfig(
    changed_lines_threshold=85.0,  # 85% coverage
    new_lines_threshold=100.0,     # 100% for new code
    mcdc_required=True,
    plateau_test_count=3,          # Stop after 3 tests with no improvement
    time_limit_minutes=30,         # 30 minute limit
    max_tests=50,                  # Max 50 tests
    critical_file_patterns=[
        "*/auth/*",
        "*/payment/*",
        "*/security/*"
    ]
)
```

## Understanding MCDC

### What is MCDC?

Modified Condition/Decision Coverage (MCDC) is a code coverage criterion that requires:

1. Each condition in a decision independently affects the outcome
2. All possible outcomes of each condition are tested

### Example

```python
# Decision with 2 conditions
if A and B:
    do_something()
```

**Truth Table:**
| Test | A | B | Outcome |
|------|---|---|---------|
| T1   | T | T | True    |
| T2   | T | F | False   |
| T3   | F | T | False   |
| T4   | F | F | False   |

**MCDC Requirement:**
- To show A is independent: T1 (A=T, B=T → True) vs T3 (A=F, B=T → False)
- To show B is independent: T1 (A=T, B=T → True) vs T2 (A=T, B=F → False)

**Minimum Tests for MCDC:** 3 tests (T1, T2, T3)

### Why MCDC?

- **Safety-critical systems**: Required by DO-178C (aviation), ISO 26262 (automotive)
- **High-quality testing**: Ensures all logical paths are tested
- **Bug detection**: Finds edge cases in complex conditions

## Stop Conditions

The system automatically stops testing when:

1. **Coverage Threshold Met**: Changed lines coverage reaches target (default: 80%)
2. **MCDC Satisfied**: All boolean conditions meet MCDC criteria
3. **Plateau Detected**: No improvement in last N tests (default: 5)
4. **Time Limit**: Maximum time exceeded (default: 60 minutes)
5. **Max Tests**: Maximum test count reached (default: 100)

### Stop Decision Example

```python
decision = await orchestrator.should_stop_testing()

if decision.should_stop:
    print(f"Reason: {decision.reason}")
    print(f"Confidence: {decision.confidence_score:.0%}")
    print(f"Metrics: {decision.metrics}")
```

## Coverage Reports

### JSON Report

```python
report = await orchestrator.generate_report(report_type="json")
```

**Output:**
```json
{
  "run_id": "cov-abc123",
  "coverage_percent": 85.5,
  "test_count": 12,
  "mcdc_satisfied": true,
  "gaps": [
    {
      "file": "src/auth.py",
      "lines": "45-67",
      "type": "uncovered_branch",
      "priority": "high"
    }
  ]
}
```

### HTML Report

```python
report = await orchestrator.generate_report(report_type="html")
```

Generates an HTML report with:
- Line-by-line coverage visualization
- Color-coded heat map
- Gap identification
- MCDC status

### Summary Report

```python
report = await orchestrator.generate_report(report_type="summary")
```

## Troubleshooting

### Issue: "Database not initialized"

**Solution:**
```bash
python coverage/cli.py init
```

### Issue: "Unsupported file type"

**Solution:** Currently supports Python (.py), JavaScript (.js), and TypeScript (.ts). Other languages coming soon.

### Issue: "MCDC too complex"

**Solution:** The analyzer limits conditions to 8 (configurable). Simplify boolean expressions or increase limit:
```python
analyzer = MCDCAnalyzer(max_conditions=12)
```

### Issue: "Coverage not increasing"

**Possible causes:**
- Instrumentation not applied
- Runtime collector not integrated
- Tests not executing changed code

**Debug:**
```python
# Check instrumentation
print(orchestrator._instrumented_files)

# Check coverage data
print(orchestrator.coverage_data)
```

## Next Steps

1. **Explore Examples**: Try the sample commands above
2. **Read Architecture**: Review `coverage/README.md`
3. **Check Status**: See `coverage/IMPLEMENTATION_STATUS.md`
4. **Integrate**: Add coverage to your test flows
5. **Customize**: Adjust configuration for your needs

## API Reference

### CoverageOrchestrator

```python
orchestrator = CoverageOrchestrator(
    pr_url="https://github.com/owner/repo/pull/123",
    config={"changed_lines_threshold": 80}
)

# Start coverage
await orchestrator.start_coverage()

# Record test execution
await orchestrator.record_test_execution(
    test_id="test-1",
    test_name="Login flow test",
    execution_time_ms=1500
)

# Check if should stop
decision = await orchestrator.should_stop_testing()

# Identify gaps
gaps = await orchestrator.identify_coverage_gaps()

# Generate report
report = await orchestrator.generate_report()

# Stop coverage
await orchestrator.stop_coverage()
```

## Contributing

See project guidelines for contributing to the coverage system.

## Support

For issues or questions:
- Check `IMPLEMENTATION_STATUS.md` for known limitations
- Review test examples in `examples/`
- File GitHub issues for bugs
