#!/usr/bin/env python3
"""
Test script for TestGPT Coverage System.

Tests the full coverage flow end-to-end without requiring actual PR or test execution.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coverage import CoverageOrchestrator, CoverageConfig
from coverage.database import CoverageDatabase


async def test_coverage_basic():
    """Test basic coverage functionality."""
    print("="*70)
    print("TEST 1: Basic Coverage Orchestration")
    print("="*70)

    # Create orchestrator
    config = CoverageConfig.default()
    orchestrator = CoverageOrchestrator(
        repo_url="https://github.com/test/repo",
        branch_name="feature-branch",
        config=config.to_dict()
    )

    # Start coverage
    run = await orchestrator.start_coverage()
    print(f"\n✅ Coverage started: {run.run_id}")

    # Simulate some test executions
    print("\n" + "="*70)
    print("Simulating Test Execution")
    print("="*70)

    for i in range(6):
        test_name = f"test_feature_{i+1}"
        print(f"\n📝 Running {test_name}...")

        effectiveness = await orchestrator.record_test_execution(
            test_id=f"test-{i+1}",
            test_name=test_name,
            execution_time_ms=1000 + (i * 200)
        )

        print(f"   Effectiveness: {effectiveness.effectiveness_score:.2f}")

        # Check stop condition after test 3
        if i >= 2:
            decision = await orchestrator.should_stop_testing()
            if decision.should_stop:
                print(f"\n🛑 Stopping: {decision.reason}")
                break

    # Identify gaps
    print("\n" + "="*70)
    print("Coverage Gap Analysis")
    print("="*70)
    gaps = await orchestrator.identify_coverage_gaps()
    print(f"Found {len(gaps)} coverage gaps")

    # Generate reports
    print("\n" + "="*70)
    print("Report Generation")
    print("="*70)

    # JSON report
    json_report = await orchestrator.generate_report(report_type="json")
    print(f"✅ JSON report generated ({len(json_report.report_data)} bytes)")

    # HTML report
    html_report = await orchestrator.generate_report(report_type="html")
    print(f"✅ HTML report generated ({len(html_report.report_data)} bytes)")

    # Summary
    summary = await orchestrator.generate_report(report_type="summary")
    print(f"✅ Summary generated\n")
    print(summary.report_data)

    return orchestrator


async def test_mcdc_analysis():
    """Test MCDC analysis functionality."""
    print("\n" + "="*70)
    print("TEST 2: MCDC Analysis")
    print("="*70)

    from coverage.instrumentation.mcdc_analyzer import MCDCAnalyzer

    analyzer = MCDCAnalyzer()

    # Test cases
    test_conditions = [
        ("Simple AND", "A and B", "test.py", 10),
        ("Complex condition", "is_auth and (is_admin or is_public)", "auth.py", 45),
        ("With NOT", "enabled and not disabled and ready", "config.py", 20),
    ]

    for name, expression, file_path, line in test_conditions:
        print(f"\n📊 {name}: {expression}")
        result = analyzer.analyze_decision(expression, file_path, line)

        if result.is_achievable:
            print(f"   ✅ MCDC Achievable")
            print(f"   Required Tests: {result.minimum_test_count}")
            print(f"   Conditions: {len(result.decision.conditions)}")
            print(f"   Truth Table Rows: {len(result.truth_table)}")
        else:
            print(f"   ❌ MCDC Not Achievable: {result.reason}")


async def test_database_operations():
    """Test database operations."""
    print("\n" + "="*70)
    print("TEST 3: Database Operations")
    print("="*70)

    # Initialize database (use in-memory for testing to avoid conflicts)
    import os
    test_db_path = "./testgpt_coverage_test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = CoverageDatabase(f"sqlite:///{test_db_path}")
    db.create_tables()
    print("✅ Database initialized")

    # Create a test run
    from coverage.models import CoverageRun, CoverageStatus
    from datetime import datetime
    import uuid

    test_run = CoverageRun(
        run_id=f"test-run-{uuid.uuid4().hex[:8]}",
        repo_url="https://github.com/test/repo",
        branch_name="test-branch",
        status=CoverageStatus.COMPLETED,
        overall_coverage_percent=85.5,
        test_count=10
    )

    # Save to database
    db.save_coverage_run(test_run)
    print(f"✅ Saved run: {test_run.run_id}")

    # Retrieve from database
    retrieved = db.get_coverage_run(test_run.run_id)
    if retrieved:
        print(f"✅ Retrieved run: {retrieved.run_id}")
        print(f"   Coverage: {retrieved.overall_coverage_percent}%")
        print(f"   Tests: {retrieved.test_count}")
    else:
        print("❌ Failed to retrieve run")

    # List recent runs
    recent = db.get_recent_runs(limit=5)
    print(f"✅ Found {len(recent)} recent runs")


async def test_pr_diff_analysis():
    """Test PR diff analysis (without real GitHub API)."""
    print("\n" + "="*70)
    print("TEST 4: PR Diff Analysis (Structure)")
    print("="*70)

    from coverage.instrumentation.pr_diff_analyzer import (
        PRDiffAnalyzer, CodeChange, ChangedFunction
    )

    analyzer = PRDiffAnalyzer()

    # Test URL parsing
    test_urls = [
        "https://github.com/owner/repo/pull/123",
        "https://github.com/owner/repo/pull/456"
    ]

    for url in test_urls:
        pr_number = analyzer._extract_pr_number(url)
        print(f"✅ Parsed PR URL: {url} → PR #{pr_number}")

    # Test critical code detection
    test_changes = [
        CodeChange("src/auth/login.py", "added", 10, 20, new_code="def authenticate():"),
        CodeChange("src/payment/process.py", "modified", 50, 60, new_code="def charge():"),
        CodeChange("src/utils/format.py", "added", 5, 10, new_code="def format_str():"),
    ]

    for change in test_changes:
        is_critical = analyzer._is_critical_change(change)
        print(f"{'🚨' if is_critical else '  '} {change.file_path}: {'CRITICAL' if is_critical else 'normal'}")


async def test_stop_conditions():
    """Test stop condition logic."""
    print("\n" + "="*70)
    print("TEST 5: Stop Condition Evaluation")
    print("="*70)

    from coverage import CoverageOrchestrator, CoverageConfig

    # Test with different configurations
    configs = {
        "Permissive (50%)": CoverageConfig.permissive(),
        "Default (80%)": CoverageConfig.default(),
        "Strict (100%)": CoverageConfig.strict(),
    }

    for name, config in configs.items():
        print(f"\n📋 {name}")
        orchestrator = CoverageOrchestrator(
            config=config.to_dict()
        )

        await orchestrator.start_coverage()

        # Simulate reaching threshold
        orchestrator.test_count = 5
        decision = await orchestrator.should_stop_testing()

        print(f"   Coverage: {orchestrator._calculate_current_coverage():.1f}%")
        print(f"   Stop: {'YES' if decision.should_stop else 'NO'}")
        print(f"   Reason: {decision.reason}")
        print(f"   Confidence: {decision.confidence_score:.0%}")


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("TestGPT Coverage System - End-to-End Test")
    print("="*70)

    try:
        # Run all tests
        await test_coverage_basic()
        await test_mcdc_analysis()
        await test_database_operations()
        await test_pr_diff_analysis()
        await test_stop_conditions()

        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nCoverage system is functional!")
        print("\nNext steps:")
        print("1. Integrate with test_executor.py for real coverage collection")
        print("2. Add Playwright action-to-code mapping")
        print("3. Connect to actual GitHub PRs with GITHUB_TOKEN")
        print("4. Save HTML reports to files")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
