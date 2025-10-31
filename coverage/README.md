# TestGPT Code Coverage System

## Overview

A comprehensive code coverage system for TestGPT that tracks what code is executed during Playwright/MCP testing, implements MCDC (Modified Condition/Decision Coverage) analysis, and intelligently determines when to stop testing based on coverage metrics.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TestGPT Coverage System                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────▼────────┐  ┌────────▼──────┐  ┌────────▼────────┐
    │ Instrumentation│  │   Runtime      │  │   Analysis &    │
    │     Layer      │  │   Collector    │  │   Reporting     │
    └────────────────┘  └────────────────┘  └─────────────────┘
            │                    │                    │
            │                    │                    │
    ┌───────▼────────┐  ┌────────▼──────┐  ┌────────▼────────┐
    │ • Instrumenter │  │ • PW Mapper   │  │ • Stop Engine   │
    │ • PR Diff      │  │ • Aggregator  │  │ • Gap Analyzer  │
    │ • MCDC         │  │ • MCP Bridge  │  │ • Report Gen    │
    └────────────────┘  └────────────────┘  └─────────────────┘
```

## System Components

### 1. Code Instrumentation Layer
- **Dynamic Code Instrumenter**: Injects coverage tracking into JS/TS/Python code
- **PR Diff Analyzer**: Identifies changed code blocks requiring coverage
- **MCDC Analyzer**: Analyzes complex boolean conditions for MCDC requirements

### 2. Runtime Coverage Collector
- **Playwright Action-to-Code Mapper**: Maps UI actions to backend code execution
- **Real-time Coverage Aggregator**: Merges coverage data across test runs
- **MCP Coverage Bridge**: Tracks MCP server invocations and code paths

### 3. Intelligent Test Completion System
- **Stop Condition Engine**: Multi-criteria decision for when to stop testing
- **Smart Test Generator**: Suggests tests to fill coverage gaps
- **Convergence Detector**: Identifies when coverage plateaus

### 4. Coverage Analysis Engine
- **Change-Focused Calculator**: PR-specific coverage metrics
- **Path Coverage Analyzer**: Control flow and critical path analysis
- **Mutation Testing**: Optional mutation analysis for test effectiveness

### 5. Reporting System
- **Visual Coverage Reporter**: HTML reports with line-by-line visualization
- **Coverage Metrics Dashboard**: Real-time coverage tracking
- **Actionable Insights Generator**: Risk assessment and recommendations

## Integration Points

### With Existing TestGPT Components

1. **test_executor.py**: Hook into test execution to collect coverage
2. **pr_testing/**: Integrate with PR analysis to identify changed files
3. **testgpt_engine.py**: Add coverage data to test results
4. **backend/**: Store coverage data in database
5. **frontend/**: Display coverage reports in UI

## Database Schema

```sql
-- Coverage runs track overall coverage collection
CREATE TABLE coverage_runs (
    run_id VARCHAR PRIMARY KEY,
    pr_id VARCHAR,
    pr_url VARCHAR,
    repo_url VARCHAR,
    branch_name VARCHAR,
    commit_sha VARCHAR,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR,  -- running, completed, failed
    stop_reason VARCHAR,  -- threshold_met, plateau, time_limit, manual
    overall_coverage_percent FLOAT,
    changed_lines_covered INTEGER,
    changed_lines_total INTEGER,
    mcdc_satisfied BOOLEAN,
    test_count INTEGER
);

-- Coverage data stores line-level coverage
CREATE TABLE coverage_data (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR REFERENCES coverage_runs(run_id),
    file_path VARCHAR,
    line_number INTEGER,
    hit_count INTEGER,
    branch_id VARCHAR,
    branch_taken BOOLEAN,
    test_id VARCHAR,
    timestamp TIMESTAMP
);

-- MCDC analysis tracks condition coverage
CREATE TABLE mcdc_analysis (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR REFERENCES coverage_runs(run_id),
    file_path VARCHAR,
    line_number INTEGER,
    condition_id VARCHAR,
    condition_text TEXT,
    truth_table_json TEXT,
    required_tests_json TEXT,
    completed_tests_json TEXT,
    satisfaction_percent FLOAT,
    is_satisfied BOOLEAN
);

-- Stop decisions log why testing stopped
CREATE TABLE stop_decisions (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR REFERENCES coverage_runs(run_id),
    decision_time TIMESTAMP,
    should_stop BOOLEAN,
    reason VARCHAR,
    confidence_score FLOAT,
    metrics_json TEXT
);

-- Coverage gaps track untested code
CREATE TABLE coverage_gaps (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR REFERENCES coverage_runs(run_id),
    file_path VARCHAR,
    line_start INTEGER,
    line_end INTEGER,
    gap_type VARCHAR,  -- uncovered_lines, uncovered_branch, uncovered_condition
    priority VARCHAR,  -- critical, high, medium, low
    suggested_test TEXT,
    risk_score FLOAT
);

-- Coverage reports store generated reports
CREATE TABLE coverage_reports (
    report_id VARCHAR PRIMARY KEY,
    run_id VARCHAR REFERENCES coverage_runs(run_id),
    report_type VARCHAR,  -- html, json, summary
    report_url VARCHAR,
    generated_at TIMESTAMP,
    metrics_json TEXT
);

-- Test effectiveness tracks coverage per test
CREATE TABLE test_effectiveness (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR REFERENCES coverage_runs(run_id),
    test_id VARCHAR,
    test_name VARCHAR,
    coverage_delta_lines INTEGER,
    coverage_delta_branches INTEGER,
    unique_coverage_lines INTEGER,
    execution_time_ms INTEGER,
    effectiveness_score FLOAT
);
```

## Configuration

### Coverage Thresholds

```yaml
coverage:
  thresholds:
    changed_lines: 80  # % of changed lines that must be covered
    new_lines: 100     # % of newly added lines that must be covered
    branches: 100      # % of new branches that must be covered
    mcdc: true         # MCDC must be satisfied for complex conditions

  stop_conditions:
    plateau_tests: 5   # Stop if no improvement in last N tests
    time_limit_minutes: 60  # Maximum time to spend on coverage
    min_coverage_percent: 80  # Minimum acceptable coverage

  priorities:
    critical_files:    # Files requiring 100% coverage
      - "*/auth/*"
      - "*/payment/*"
      - "*/security/*"

    exclude_patterns:  # Files to exclude from coverage
      - "*/tests/*"
      - "*/migrations/*"
      - "*/__pycache__/*"
```

## Usage

### 1. Enable Coverage for PR Testing

```python
from coverage import CoverageOrchestrator

orchestrator = CoverageOrchestrator(
    pr_url="https://github.com/owner/repo/pull/123",
    config={
        "changed_lines_threshold": 80,
        "mcdc_required": True,
        "max_tests": 50
    }
)

# Start coverage collection
await orchestrator.start_coverage()

# Run tests (existing TestGPT flow)
results = await testgpt_engine.execute_pr_tests(pr_url)

# Stop when coverage is sufficient
decision = await orchestrator.should_stop_testing()
if decision.should_stop:
    print(f"Stopping: {decision.reason}")

# Generate report
report = await orchestrator.generate_report()
```

### 2. View Coverage Reports

```bash
# CLI
python -m coverage.cli report --run-id=<run_id>

# Web UI
http://localhost:3000/coverage/<run_id>
```

### 3. Integration with Slack Bot

```
# Enable coverage tracking
@TestGPT test this PR with coverage: https://github.com/owner/repo/pull/123

# View coverage report
@TestGPT show coverage for PR 123
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Database schema setup
- [ ] Core instrumentation engine
- [ ] PR diff analyzer integration
- [ ] Basic coverage collection

### Phase 2: MCDC & Analysis (Week 2)
- [ ] MCDC condition parser
- [ ] Truth table generator
- [ ] Path coverage analyzer
- [ ] Coverage aggregation

### Phase 3: Intelligent Stopping (Week 3)
- [ ] Stop condition engine
- [ ] Coverage gap detector
- [ ] Test suggestion generator
- [ ] Convergence detection

### Phase 4: Reporting & UI (Week 4)
- [ ] HTML report generator
- [ ] Dashboard integration
- [ ] Slack notifications
- [ ] API endpoints

### Phase 5: Optimization (Week 5)
- [ ] Performance tuning
- [ ] Caching layer
- [ ] Parallel collection
- [ ] Memory optimization

## Key Features

### MCDC Coverage
- Parses complex boolean conditions
- Generates truth tables automatically
- Identifies minimum test sets for MCDC
- Reports partial MCDC satisfaction

### Intelligent Stop Conditions
- Multi-criteria evaluation (coverage %, MCDC, plateau)
- Adaptive thresholds based on PR complexity
- Early stopping to save resources
- Confidence scoring for decisions

### PR-Focused Coverage
- Only tracks changed code
- Weighted by code criticality
- Dependency graph for indirect changes
- Historical bug density analysis

### Real-time Feedback
- Live coverage updates during test execution
- Immediate gap identification
- Dynamic test prioritization
- Progressive reporting

## Performance Characteristics

- **Overhead**: < 10% test execution time increase
- **Memory**: Bounded by repository size (streaming for large codebases)
- **Latency**: Real-time coverage updates (< 1s delay)
- **Scalability**: Handles monorepos with 10K+ files

## Security Considerations

- Instrumented code preserves original behavior
- No sensitive data in coverage reports
- Sandboxed execution for untrusted code
- Access controls on coverage data

## Future Enhancements

1. **ML-Based Predictions**: Predict coverage impact before testing
2. **Cross-PR Analysis**: Learn from historical coverage patterns
3. **Visual Regression**: Correlate coverage with visual changes
4. **Performance Coverage**: Track performance-critical paths
5. **Security Coverage**: Highlight security-sensitive code coverage
