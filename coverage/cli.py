#!/usr/bin/env python3
"""
TestGPT Coverage CLI - Command-line interface for coverage system.

Usage:
    python coverage/cli.py init                  # Initialize database
    python coverage/cli.py analyze-pr <pr_url>   # Analyze PR diff
    python coverage/cli.py analyze-mcdc <file>   # Analyze MCDC in file
    python coverage/cli.py run <pr_url>          # Full coverage run
    python coverage/cli.py report <run_id>       # Generate report
    python coverage/cli.py list                  # List recent runs
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coverage.orchestrator import CoverageOrchestrator
from coverage.config import CoverageConfig
from coverage.database import CoverageDatabase
from coverage.instrumentation.pr_diff_analyzer import PRDiffAnalyzer
from coverage.instrumentation.mcdc_analyzer import MCDCAnalyzer


class CoverageCLI:
    """Command-line interface for coverage system."""

    def __init__(self):
        """Initialize CLI."""
        self.db = CoverageDatabase()

    def cmd_init(self):
        """Initialize database."""
        print(" Initializing TestGPT Coverage Database...")
        self.db.create_tables()
        print(" Database initialized successfully")

    async def cmd_analyze_pr(self, pr_url: str):
        """Analyze PR diff."""
        print(f"\n{'='*70}")
        print(f" Analyzing PR: {pr_url}")
        print(f"{'='*70}\n")

        analyzer = PRDiffAnalyzer()
        summary = await analyzer.analyze_pr(pr_url)

        print(f"\n{'='*70}")
        print(f"ANALYSIS RESULTS")
        print(f"{'='*70}")
        print(f"PR Number: {summary.pr_number}")
        print(f"Changed Files: {len(summary.changed_files)}")
        print(f"Total Changes: {len(summary.code_changes)}")
        print(f"Changed Functions: {len(summary.changed_functions)}")
        print(f"Lines Added: {summary.total_lines_added}")
        print(f"Lines Deleted: {summary.total_lines_deleted}")
        print(f"Lines Modified: {summary.total_lines_modified}")
        print(f"Critical Changes: {len(summary.critical_changes)}")

        if summary.critical_changes:
            print(f"\n Critical Changes:")
            for change in summary.critical_changes[:5]:
                print(f"   • {change.file_path}:{change.line_start}-{change.line_end}")
                if change.function_name:
                    print(f"     Function: {change.function_name}")

        if summary.changed_functions:
            print(f"\n Changed Functions:")
            for func in summary.changed_functions[:10]:
                print(f"   • {func.function_name} in {func.file_path}")
                print(f"     Lines: {func.line_start}-{func.line_end}, "
                      f"Complexity: {func.complexity}")

    async def cmd_analyze_mcdc(self, file_path: str):
        """Analyze MCDC in a file."""
        print(f"\n{'='*70}")
        print(f" Analyzing MCDC in: {file_path}")
        print(f"{'='*70}\n")

        # Read file
        with open(file_path, 'r') as f:
            code = f.read()

        # Detect language
        language = "python" if file_path.endswith('.py') else "javascript"

        # Analyze
        analyzer = MCDCAnalyzer()
        results = analyzer.analyze_file(file_path, code, language)

        print(f"\n{'='*70}")
        print(f"MCDC ANALYSIS RESULTS")
        print(f"{'='*70}")
        print(f"Decisions Found: {len(results)}")

        for i, result in enumerate(results, 1):
            print(f"\nDecision {i}:")
            print(f"  Expression: {result.decision.full_expression}")
            print(f"  Line: {result.decision.line_number}")
            print(f"  Conditions: {len(result.decision.conditions)}")
            print(f"  Complexity: {result.decision.complexity}")
            print(f"  MCDC Achievable: {'' if result.is_achievable else ''}")

            if result.is_achievable:
                print(f"  Required Tests: {result.minimum_test_count}")
                print(f"  Truth Table Rows: {len(result.truth_table)}")

                # Show sample test cases
                if result.required_test_cases:
                    print(f"\n  Sample Test Cases:")
                    for test in result.required_test_cases[:3]:
                        conditions_str = ', '.join([
                            f"{k}={v}" for k, v in test.condition_values.items()
                        ])
                        print(f"    • {test.test_id}: {conditions_str} "
                              f"→ {test.expected_outcome}")
            else:
                print(f"  Reason: {result.reason}")

    async def cmd_run(self, pr_url: str, config_name: str = "default"):
        """Run full coverage collection."""
        print(f"\n{'='*70}")
        print(f" Starting Coverage Run")
        print(f"{'='*70}\n")

        # Load configuration
        if config_name == "strict":
            config = CoverageConfig.strict()
        elif config_name == "permissive":
            config = CoverageConfig.permissive()
        else:
            config = CoverageConfig.default()

        # Create orchestrator
        orchestrator = CoverageOrchestrator(
            pr_url=pr_url,
            config=config.to_dict()
        )

        # Start coverage
        run = await orchestrator.start_coverage()

        print(f"{'='*70}")
        print(f"COVERAGE RUN STARTED")
        print(f"{'='*70}")
        print(f"Run ID: {run.run_id}")
        print(f"Status: {run.status.value}")
        print(f"Config: {config_name}")

        # Simulate some tests
        print(f"\n{'='*70}")
        print(f"SIMULATING TEST EXECUTION")
        print(f"{'='*70}\n")

        for i in range(5):
            test_name = f"test_{i+1}"
            print(f"Running {test_name}...")

            effectiveness = await orchestrator.record_test_execution(
                test_id=f"test-{i+1}",
                test_name=test_name,
                execution_time_ms=1000 + (i * 100)
            )

            # Check if should stop
            decision = await orchestrator.should_stop_testing()
            if decision.should_stop:
                print(f"\n{'='*70}")
                print(f"STOPPING: {decision.reason}")
                print(f"{'='*70}\n")
                break

        # Generate report
        print(f"\n{'='*70}")
        print(f"GENERATING REPORT")
        print(f"{'='*70}\n")

        report = await orchestrator.generate_report(report_type="json")

        print(f" Coverage run complete!")
        print(f"   Run ID: {run.run_id}")
        print(f"   Report ID: {report.report_id}")
        print(f"   Coverage: {orchestrator.coverage_run.overall_coverage_percent:.1f}%")
        print(f"   Tests: {orchestrator.test_count}")

        # Save to database
        self.db.save_coverage_run(orchestrator.coverage_run)
        print(f"\n Saved to database")

    def cmd_report(self, run_id: str):
        """Generate report for a run."""
        print(f"\n{'='*70}")
        print(f" Coverage Report: {run_id}")
        print(f"{'='*70}\n")

        run = self.db.get_coverage_run(run_id)

        if not run:
            print(f" Run not found: {run_id}")
            return

        print(f"Run ID: {run.run_id}")
        print(f"PR URL: {run.pr_url or 'N/A'}")
        print(f"Status: {run.status}")
        print(f"Started: {run.started_at}")
        print(f"Completed: {run.completed_at or 'Running...'}")
        print(f"\nCoverage Metrics:")
        print(f"  Overall: {run.overall_coverage_percent:.1f}%")
        print(f"  Changed Lines: {run.changed_lines_covered}/{run.changed_lines_total}")
        print(f"  Branches: {run.branches_covered}/{run.branches_total}")
        print(f"  MCDC Satisfied: {'' if run.mcdc_satisfied else ''}")
        print(f"  Tests Run: {run.test_count}")

        if run.stop_reason:
            print(f"\nStop Reason: {run.stop_reason}")

    def cmd_list(self, limit: int = 10):
        """List recent coverage runs."""
        print(f"\n{'='*70}")
        print(f" Recent Coverage Runs")
        print(f"{'='*70}\n")

        runs = self.db.get_recent_runs(limit=limit)

        if not runs:
            print("No coverage runs found. Initialize database with 'init' command.")
            return

        for run in runs:
            status_emoji = {
                'running': '',
                'completed': '',
                'failed': '',
                'stopped': ''
            }.get(run.status, '')

            print(f"{status_emoji} {run.run_id}")
            print(f"   Status: {run.status}")
            print(f"   Started: {run.started_at}")
            print(f"   Coverage: {run.overall_coverage_percent:.1f}%")
            print(f"   Tests: {run.test_count}")
            print()

    def print_usage(self):
        """Print usage information."""
        print("""
TestGPT Coverage CLI

Usage:
    python coverage/cli.py <command> [arguments]

Commands:
    init                        Initialize coverage database
    analyze-pr <pr_url>         Analyze PR diff and show changes
    analyze-mcdc <file_path>    Analyze MCDC requirements in file
    run <pr_url> [config]       Run full coverage collection
                                Config: default, strict, permissive
    report <run_id>             Show coverage report for run
    list [limit]                List recent coverage runs

Examples:
    python coverage/cli.py init
    python coverage/cli.py analyze-pr https://github.com/owner/repo/pull/123
    python coverage/cli.py analyze-mcdc examples/sample.py
    python coverage/cli.py run https://github.com/owner/repo/pull/123 strict
    python coverage/cli.py report cov-abc123
    python coverage/cli.py list 20
        """)


async def main():
    """Main CLI entry point."""
    cli = CoverageCLI()

    if len(sys.argv) < 2:
        cli.print_usage()
        return

    command = sys.argv[1]

    try:
        if command == "init":
            cli.cmd_init()

        elif command == "analyze-pr":
            if len(sys.argv) < 3:
                print(" Error: PR URL required")
                print("Usage: python coverage/cli.py analyze-pr <pr_url>")
                return
            await cli.cmd_analyze_pr(sys.argv[2])

        elif command == "analyze-mcdc":
            if len(sys.argv) < 3:
                print(" Error: File path required")
                print("Usage: python coverage/cli.py analyze-mcdc <file_path>")
                return
            await cli.cmd_analyze_mcdc(sys.argv[2])

        elif command == "run":
            if len(sys.argv) < 3:
                print(" Error: PR URL required")
                print("Usage: python coverage/cli.py run <pr_url> [config]")
                return
            pr_url = sys.argv[2]
            config_name = sys.argv[3] if len(sys.argv) > 3 else "default"
            await cli.cmd_run(pr_url, config_name)

        elif command == "report":
            if len(sys.argv) < 3:
                print(" Error: Run ID required")
                print("Usage: python coverage/cli.py report <run_id>")
                return
            cli.cmd_report(sys.argv[2])

        elif command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            cli.cmd_list(limit)

        else:
            print(f" Unknown command: {command}")
            cli.print_usage()

    except KeyboardInterrupt:
        print("\n\n  Interrupted by user")
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
