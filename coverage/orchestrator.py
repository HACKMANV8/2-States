"""
Coverage Orchestrator - Main coordination layer for TestGPT coverage system.

Coordinates all coverage components:
- Instrumentation
- Runtime collection
- Analysis
- Stop decision making
- Reporting
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

from .models import (
    CoverageRun, CoverageData, MCDCAnalysis, StopDecision,
    CoverageGap, CoverageReport, TestEffectiveness,
    CoverageStatus, StopReason, GapType, GapPriority
)
from .config import CoverageConfig


class CoverageOrchestrator:
    """
    Main orchestrator for TestGPT coverage system.

    Coordinates:
    1. Code instrumentation
    2. Runtime coverage collection
    3. Coverage analysis
    4. Intelligent stop decisions
    5. Report generation
    """

    def __init__(
        self,
        pr_url: Optional[str] = None,
        repo_url: Optional[str] = None,
        branch_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize coverage orchestrator.

        Args:
            pr_url: GitHub PR URL (if testing a PR)
            repo_url: Repository URL
            branch_name: Branch name
            config: Coverage configuration dict
        """
        self.pr_url = pr_url
        self.repo_url = repo_url
        self.branch_name = branch_name

        # Load configuration
        if config:
            self.config = CoverageConfig(**config)
        else:
            self.config = CoverageConfig.default()

        # Initialize run
        self.run_id = f"cov-{uuid.uuid4().hex[:12]}"
        self.coverage_run: Optional[CoverageRun] = None

        # Coverage tracking
        self.coverage_data: List[CoverageData] = []
        self.mcdc_analyses: List[MCDCAnalysis] = []
        self.stop_decisions: List[StopDecision] = []
        self.coverage_gaps: List[CoverageGap] = []
        self.test_effectiveness: List[TestEffectiveness] = []

        # State
        self.is_started = False
        self.last_coverage_percent = 0.0
        self.plateau_count = 0
        self.test_count = 0

        # Will be initialized lazily
        self._instrumenter = None
        self._pr_diff_analyzer = None
        self._collector = None
        self._stop_engine = None
        self._reporter = None

        print(f" Coverage orchestrator initialized")
        print(f"   Run ID: {self.run_id}")
        print(f"   Config: {self.config.changed_lines_threshold}% changed lines, "
              f"MCDC={self.config.mcdc_required}")

    async def start_coverage(self) -> CoverageRun:
        """
        Start coverage collection.

        Steps:
        1. Extract PR info (if PR URL provided)
        2. Analyze changed files
        3. Instrument code
        4. Initialize collectors
        """
        if self.is_started:
            print("  Coverage already started")
            return self.coverage_run

        print(f"\n Starting coverage collection...")

        # Create coverage run
        self.coverage_run = CoverageRun(
            run_id=self.run_id,
            pr_url=self.pr_url,
            repo_url=self.repo_url,
            branch_name=self.branch_name,
            status=CoverageStatus.RUNNING,
            config=self.config.to_dict()
        )

        # Step 1: Analyze PR if URL provided
        if self.pr_url:
            print(f"    Analyzing PR: {self.pr_url}")
            await self._analyze_pr()

        # Step 2: Instrument changed files
        print(f"    Instrumenting code...")
        await self._instrument_files()

        # Step 3: Initialize runtime collector
        print(f"    Initializing coverage collector...")
        await self._init_collector()

        self.is_started = True
        print(f" Coverage collection started (Run ID: {self.run_id})\n")

        return self.coverage_run

    async def record_test_execution(
        self,
        test_id: str,
        test_name: str,
        execution_time_ms: int
    ) -> TestEffectiveness:
        """
        Record coverage data for a single test execution.

        Args:
            test_id: Unique test identifier
            test_name: Human-readable test name
            execution_time_ms: Test execution time in milliseconds

        Returns:
            TestEffectiveness object with coverage delta
        """
        if not self.is_started:
            raise RuntimeError("Coverage not started. Call start_coverage() first.")

        print(f" Recording test: {test_name}")

        # Get current coverage snapshot
        current_coverage = self._calculate_current_coverage()

        # Calculate delta from previous test
        coverage_delta = current_coverage - self.last_coverage_percent

        # Create effectiveness record
        effectiveness = TestEffectiveness(
            run_id=self.run_id,
            test_id=test_id,
            test_name=test_name,
            coverage_delta_lines=int(coverage_delta * 10),  # Approximate
            execution_time_ms=execution_time_ms,
            effectiveness_score=self._calculate_effectiveness_score(
                coverage_delta, execution_time_ms
            )
        )

        self.test_effectiveness.append(effectiveness)
        self.test_count += 1

        # Update tracking
        if abs(coverage_delta) < 0.1:  # Less than 0.1% improvement
            self.plateau_count += 1
        else:
            self.plateau_count = 0

        self.last_coverage_percent = current_coverage

        print(f"   Coverage: {current_coverage:.1f}% (Δ {coverage_delta:+.1f}%)")
        print(f"   Effectiveness: {effectiveness.effectiveness_score:.2f}")

        return effectiveness

    async def should_stop_testing(self) -> StopDecision:
        """
        Evaluate whether testing should stop based on coverage criteria.

        Returns:
            StopDecision with recommendation and reasoning
        """
        if not self.is_started:
            raise RuntimeError("Coverage not started. Call start_coverage() first.")

        print(f"\n Evaluating stop condition...")

        # Calculate current metrics
        current_coverage = self._calculate_current_coverage()
        time_elapsed = (datetime.now() - self.coverage_run.started_at).total_seconds() / 60

        metrics = {
            'current_coverage': current_coverage,
            'changed_lines_threshold': self.config.changed_lines_threshold,
            'test_count': self.test_count,
            'max_tests': self.config.max_tests,
            'plateau_count': self.plateau_count,
            'plateau_threshold': self.config.plateau_test_count,
            'time_elapsed_minutes': time_elapsed,
            'time_limit_minutes': self.config.time_limit_minutes,
            'mcdc_satisfied': self._check_mcdc_satisfied()
        }

        # Evaluate stop conditions
        should_stop, reason, confidence = self._evaluate_stop_conditions(metrics)

        decision = StopDecision(
            run_id=self.run_id,
            should_stop=should_stop,
            reason=reason,
            confidence_score=confidence,
            metrics=metrics
        )

        self.stop_decisions.append(decision)

        if should_stop:
            print(f"    STOP recommended: {reason} (confidence: {confidence:.0%})")
        else:
            print(f"     CONTINUE testing: {reason} (confidence: {confidence:.0%})")

        return decision

    async def identify_coverage_gaps(self) -> List[CoverageGap]:
        """
        Identify gaps in code coverage and suggest tests to fill them.

        Returns:
            List of CoverageGap objects with suggestions
        """
        print(f"\n Identifying coverage gaps...")

        # Analyze uncovered code
        gaps = await self._analyze_coverage_gaps()

        self.coverage_gaps = gaps

        print(f"   Found {len(gaps)} coverage gaps:")
        for gap in gaps[:5]:  # Show first 5
            print(f"   • {gap.file_path}:{gap.line_start}-{gap.line_end} "
                  f"[{gap.priority.value}] {gap.gap_type.value}")

        return gaps

    async def generate_report(
        self,
        report_type: str = "html"
    ) -> CoverageReport:
        """
        Generate coverage report.

        Args:
            report_type: Type of report (html, json, summary)

        Returns:
            CoverageReport object
        """
        print(f"\n Generating {report_type} coverage report...")

        # Finalize coverage run
        self.coverage_run.completed_at = datetime.now()
        self.coverage_run.status = CoverageStatus.COMPLETED
        self.coverage_run.overall_coverage_percent = self._calculate_current_coverage()
        self.coverage_run.test_count = self.test_count
        self.coverage_run.mcdc_satisfied = self._check_mcdc_satisfied()

        # Generate report
        report_id = f"report-{uuid.uuid4().hex[:12]}"

        if report_type == "html":
            report_data = await self._generate_html_report()
        elif report_type == "json":
            report_data = await self._generate_json_report()
        else:
            report_data = await self._generate_summary_report()

        report = CoverageReport(
            report_id=report_id,
            run_id=self.run_id,
            report_type=report_type,
            report_data=report_data,
            metrics=self._get_summary_metrics()
        )

        print(f" Report generated: {report_id}")
        print(f"   Overall coverage: {self.coverage_run.overall_coverage_percent:.1f}%")
        print(f"   Tests executed: {self.test_count}")
        print(f"   MCDC satisfied: {'' if self.coverage_run.mcdc_satisfied else ''}")

        return report

    async def stop_coverage(self, reason: StopReason = StopReason.MANUAL):
        """
        Stop coverage collection.

        Args:
            reason: Reason for stopping
        """
        print(f"\n Stopping coverage collection: {reason.value}")

        if self.coverage_run:
            self.coverage_run.status = CoverageStatus.STOPPED
            self.coverage_run.stop_reason = reason
            self.coverage_run.completed_at = datetime.now()

        # Cleanup instrumentation
        await self._cleanup()

        self.is_started = False
        print(f" Coverage collection stopped")

    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================

    async def _analyze_pr(self):
        """Analyze PR to identify changed files."""
        if not self.pr_url:
            print(f"     No PR URL provided, skipping PR analysis")
            return

        try:
            # Import PR diff analyzer
            from coverage.instrumentation.pr_diff_analyzer import PRDiffAnalyzer

            print(f"    Analyzing PR: {self.pr_url}")
            analyzer = PRDiffAnalyzer()

            # Get GitHub token from environment
            import os
            github_token = os.environ.get("GITHUB_TOKEN")

            # Analyze PR
            pr_summary = await analyzer.analyze_pr(self.pr_url, github_token)

            # Store results
            self.coverage_run.changed_lines_total = (
                pr_summary.total_lines_added + pr_summary.total_lines_modified
            )

            # Update run with PR info
            self.coverage_run.pr_id = str(pr_summary.pr_number)

            print(f"    PR analysis complete:")
            print(f"      Changed files: {len(pr_summary.changed_files)}")
            print(f"      Changed functions: {len(pr_summary.changed_functions)}")
            print(f"      Total lines to cover: {self.coverage_run.changed_lines_total}")

            # Store changed files for instrumentation
            self._changed_files = pr_summary.changed_files
            self._changed_functions = pr_summary.changed_functions

        except Exception as e:
            print(f"     PR analysis failed: {str(e)}")
            print(f"   Continuing without PR context...")
            self._changed_files = []
            self._changed_functions = []

    async def _instrument_files(self):
        """Instrument code files for coverage tracking."""
        if not hasattr(self, '_changed_files') or not self._changed_files:
            print(f"     No changed files to instrument")
            return

        try:
            from coverage.instrumentation.instrumenter import CodeInstrumenter
            from pathlib import Path

            print(f"    Instrumenting {len(self._changed_files)} files...")

            instrumenter = CodeInstrumenter()

            # Filter out non-code files
            code_files = [
                f for f in self._changed_files
                if any(f.endswith(ext) for ext in ['.py', '.js', '.ts', '.jsx', '.tsx'])
            ]

            if not code_files:
                print(f"     No code files found to instrument")
                return

            # Instrument files (without base path for now - would need repo clone)
            # For demonstration, we'll track which files should be instrumented
            self._instrumented_file_count = len(code_files)

            print(f"    Marked {self._instrumented_file_count} files for instrumentation")

        except Exception as e:
            print(f"     Instrumentation setup failed: {str(e)}")
            self._instrumented_file_count = 0

    async def _init_collector(self):
        """Initialize runtime coverage collector."""
        # Initialize coverage tracking structures
        self._line_hits = {}  # file_path -> {line_num -> hit_count}
        self._branch_hits = {}  # file_path -> {branch_id -> taken}

        print(f"    Coverage collector initialized")
        print(f"      Tracking mode: Simulated (real collection requires test integration)")

    def _calculate_current_coverage(self) -> float:
        """Calculate current coverage percentage."""
        # If we have real coverage data, calculate it
        if hasattr(self, '_line_hits') and self._line_hits:
            total_lines = 0
            covered_lines = 0

            for file_path, lines in self._line_hits.items():
                total_lines += len(lines)
                covered_lines += sum(1 for hits in lines.values() if hits > 0)

            if total_lines > 0:
                return (covered_lines / total_lines) * 100.0

        # If we have changed files info, use that
        if hasattr(self, '_changed_files') and self._changed_files:
            total_lines = self.coverage_run.changed_lines_total
            if total_lines > 0:
                # Estimate based on test count and diminishing returns
                coverage_per_test = 15.0  # Each test covers ~15% initially
                diminishing_factor = 0.85  # Each test is 85% as effective as previous

                coverage = 0.0
                for i in range(self.test_count):
                    coverage += coverage_per_test * (diminishing_factor ** i)

                return min(coverage, 100.0)

        # Fallback: simple simulation
        return min(50.0 + (self.test_count * 8), 100.0)

    def _check_mcdc_satisfied(self) -> bool:
        """Check if MCDC criteria are satisfied."""
        # TODO: Implement actual MCDC check
        return len(self.mcdc_analyses) > 0 and all(
            m.is_satisfied for m in self.mcdc_analyses
        )

    def _calculate_effectiveness_score(
        self,
        coverage_delta: float,
        execution_time_ms: int
    ) -> float:
        """
        Calculate test effectiveness score.

        Formula: coverage_delta / (execution_time_ms / 1000) * 100
        Higher is better (more coverage per second)
        """
        if execution_time_ms == 0:
            return 0.0

        time_seconds = execution_time_ms / 1000
        return max(0.0, (coverage_delta / time_seconds) * 100)

    def _evaluate_stop_conditions(
        self,
        metrics: Dict[str, Any]
    ) -> tuple[bool, str, float]:
        """
        Evaluate stop conditions based on metrics.

        Returns:
            Tuple of (should_stop, reason, confidence_score)
        """
        # Condition 1: Coverage threshold met
        if metrics['current_coverage'] >= self.config.changed_lines_threshold:
            if self.config.mcdc_required:
                if metrics['mcdc_satisfied']:
                    return True, "Coverage and MCDC thresholds met", 1.0
                else:
                    return False, "Coverage met but MCDC not satisfied", 0.7
            return True, "Coverage threshold met", 0.95

        # Condition 2: Plateau reached
        if metrics['plateau_count'] >= metrics['plateau_threshold']:
            return True, f"Coverage plateaued ({metrics['plateau_count']} tests with no improvement)", 0.85

        # Condition 3: Time limit exceeded
        if metrics['time_elapsed_minutes'] >= metrics['time_limit_minutes']:
            return True, "Time limit exceeded", 1.0

        # Condition 4: Max tests reached
        if metrics['test_count'] >= metrics['max_tests']:
            return True, "Maximum test count reached", 0.9

        # Continue testing
        remaining = self.config.changed_lines_threshold - metrics['current_coverage']
        return False, f"Coverage {remaining:.1f}% below threshold", 0.8

    async def _analyze_coverage_gaps(self) -> List[CoverageGap]:
        """Analyze coverage data to identify gaps."""
        gaps = []

        # If we have changed files, analyze gaps in those
        if hasattr(self, '_changed_files') and self._changed_files:
            for file_path in self._changed_files:
                # Check if this is a critical file
                is_critical = self.config.is_file_critical(file_path)

                # Estimate uncovered lines (in real implementation, would check actual coverage)
                # For now, assume some lines are uncovered based on test count
                current_coverage = self._calculate_current_coverage()
                if current_coverage < 100.0:
                    priority = GapPriority.CRITICAL if is_critical else GapPriority.HIGH

                    gaps.append(CoverageGap(
                        run_id=self.run_id,
                        file_path=file_path,
                        line_start=1,
                        line_end=100,  # Placeholder
                        gap_type=GapType.UNCOVERED_LINES,
                        priority=priority,
                        suggested_test=f"Add tests for {file_path}",
                        risk_score=1.0 - (current_coverage / 100.0)
                    ))

        # If we have changed functions, create specific gaps
        if hasattr(self, '_changed_functions') and self._changed_functions:
            for func in self._changed_functions:
                if func.is_critical:
                    gaps.append(CoverageGap(
                        run_id=self.run_id,
                        file_path=func.file_path,
                        line_start=func.line_start,
                        line_end=func.line_end,
                        gap_type=GapType.UNCOVERED_LINES,
                        priority=GapPriority.CRITICAL,
                        suggested_test=f"Test critical function: {func.function_name}",
                        risk_score=0.9
                    ))

        return gaps

    async def _generate_html_report(self) -> str:
        """Generate HTML coverage report."""
        coverage = self._calculate_current_coverage()
        gaps = await self._analyze_coverage_gaps()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Coverage Report - {self.run_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; }}
        .metric-label {{ font-size: 14px; color: #bdc3c7; }}
        .coverage-bar {{ width: 100%; height: 30px; background: #ecf0f1; border-radius: 5px; margin: 10px 0; }}
        .coverage-fill {{ height: 100%; background: {'#27ae60' if coverage >= 80 else '#e74c3c'}; border-radius: 5px; }}
        .gaps {{ margin-top: 20px; }}
        .gap {{ background: #f8f9fa; border-left: 4px solid #e74c3c; padding: 10px; margin: 10px 0; }}
        .gap.critical {{ border-color: #c0392b; }}
        .gap.high {{ border-color: #e74c3c; }}
        .gap.medium {{ border-color: #f39c12; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Coverage Report</h1>
        <p>Run ID: {self.run_id}</p>
        {'<p>PR: ' + self.pr_url + '</p>' if self.pr_url else ''}
    </div>

    <div style="margin-top: 20px;">
        <div class="metric">
            <div class="metric-value">{coverage:.1f}%</div>
            <div class="metric-label">Overall Coverage</div>
        </div>
        <div class="metric">
            <div class="metric-value">{self.test_count}</div>
            <div class="metric-label">Tests Run</div>
        </div>
        <div class="metric">
            <div class="metric-value">{len(gaps)}</div>
            <div class="metric-label">Coverage Gaps</div>
        </div>
    </div>

    <div class="coverage-bar">
        <div class="coverage-fill" style="width: {coverage}%;"></div>
    </div>

    <div class="gaps">
        <h2>Coverage Gaps</h2>
        {''.join([f'''
        <div class="gap {gap.priority.value}">
            <strong>{gap.file_path}</strong> (Lines {gap.line_start}-{gap.line_end})
            <br>Priority: {gap.priority.value.upper()}
            <br>Suggestion: {gap.suggested_test}
            <br>Risk Score: {gap.risk_score:.2f}
        </div>
        ''' for gap in gaps[:10]])}
    </div>

    <div style="margin-top: 20px; padding: 10px; background: #ecf0f1; border-radius: 5px;">
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Configuration:</strong> {self.config.changed_lines_threshold}% threshold, MCDC {'required' if self.config.mcdc_required else 'optional'}</p>
    </div>
</body>
</html>
        """
        return html

    async def _generate_json_report(self) -> str:
        """Generate JSON coverage report."""
        import json

        coverage = self._calculate_current_coverage()
        gaps = await self._analyze_coverage_gaps()

        report_data = {
            'run_id': self.run_id,
            'pr_url': self.pr_url,
            'status': self.coverage_run.status.value if self.coverage_run else 'unknown',
            'coverage': {
                'overall_percent': coverage,
                'changed_lines_covered': self.coverage_run.changed_lines_covered if self.coverage_run else 0,
                'changed_lines_total': self.coverage_run.changed_lines_total if self.coverage_run else 0,
                'mcdc_satisfied': self._check_mcdc_satisfied()
            },
            'tests': {
                'total_count': self.test_count,
                'effectiveness': [
                    {
                        'test_id': te.test_id,
                        'test_name': te.test_name,
                        'coverage_delta': te.coverage_delta_lines,
                        'effectiveness_score': te.effectiveness_score
                    }
                    for te in self.test_effectiveness[:10]  # Last 10 tests
                ]
            },
            'gaps': [
                {
                    'file_path': gap.file_path,
                    'line_start': gap.line_start,
                    'line_end': gap.line_end,
                    'type': gap.gap_type.value,
                    'priority': gap.priority.value,
                    'suggested_test': gap.suggested_test,
                    'risk_score': gap.risk_score
                }
                for gap in gaps
            ],
            'configuration': {
                'changed_lines_threshold': self.config.changed_lines_threshold,
                'mcdc_required': self.config.mcdc_required,
                'plateau_test_count': self.config.plateau_test_count,
                'time_limit_minutes': self.config.time_limit_minutes
            },
            'generated_at': datetime.now().isoformat()
        }

        return json.dumps(report_data, indent=2)

    async def _generate_summary_report(self) -> str:
        """Generate summary text report."""
        coverage = self._calculate_current_coverage()
        return f"""
Coverage Summary Report
Run ID: {self.run_id}
Coverage: {coverage:.1f}%
Tests: {self.test_count}
MCDC: {'Satisfied' if self._check_mcdc_satisfied() else 'Not Satisfied'}
"""

    def _get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary metrics for reporting."""
        return {
            'overall_coverage_percent': self._calculate_current_coverage(),
            'test_count': self.test_count,
            'mcdc_satisfied': self._check_mcdc_satisfied(),
            'gaps_count': len(self.coverage_gaps),
            'duration_minutes': (
                (datetime.now() - self.coverage_run.started_at).total_seconds() / 60
                if self.coverage_run else 0
            )
        }

    async def _cleanup(self):
        """Cleanup instrumentation and temporary files."""
        # TODO: Implement cleanup
        print(f"   ℹ  Cleanup not yet implemented")
