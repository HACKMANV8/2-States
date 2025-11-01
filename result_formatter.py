"""
Result formatter for TestGPT.

Aggregates test results and formats Slack summaries.
Implements result packaging from specification Section 5 and TODO 6.
"""

from typing import List, Dict
from collections import defaultdict
from models import (
    CellResult, RunArtifact, TestStatus, FailurePriority,
    SlackSummary, SlackFailureDetail, SlackEnvironmentBreakdown,
    FailuresByPriority, EnvironmentSummary
)
from config import get_browser


class ResultFormatter:
    """
    Formats test results into human-readable Slack summaries.

    Aggregates cell results, prioritizes failures, and generates
    structured Slack output according to specification.
    """

    def aggregate_results(
        self,
        cell_results: List[CellResult],
        scenario_name: str,
        target_url: str,
        run_id: str
    ) -> RunArtifact:
        """
        Aggregate cell results into a RunArtifact.

        Args:
            cell_results: List of CellResult from execution
            scenario_name: Name of the scenario
            target_url: Target URL tested
            run_id: Unique run identifier

        Returns:
            RunArtifact with complete aggregated results
        """
        # Calculate overall stats
        total_cells = len(cell_results)
        passed_cells = len([r for r in cell_results if r.status == TestStatus.PASS])
        failed_cells = len([r for r in cell_results if r.status == TestStatus.FAIL])
        timed_out_cells = len([r for r in cell_results if r.status == TestStatus.TIMEOUT])

        # Determine overall status
        if passed_cells == total_cells:
            overall_status = TestStatus.PASS
        elif passed_cells == 0:
            overall_status = TestStatus.FAIL
        else:
            overall_status = TestStatus.PARTIAL

        # Group failures by priority
        failures_by_priority = self._group_failures_by_priority(cell_results)

        # Create environment summary
        env_summary = self._create_environment_summary(cell_results)

        # Calculate duration
        if cell_results:
            earliest_start = min(r.started_at for r in cell_results)
            latest_end = max(r.completed_at for r in cell_results)
            duration_seconds = int((latest_end - earliest_start).total_seconds())
            started_at = earliest_start
            completed_at = latest_end
        else:
            from datetime import datetime
            started_at = completed_at = datetime.now()
            duration_seconds = 0

        return RunArtifact(
            run_id=run_id,
            test_plan_id="",  # Will be filled by caller
            scenario_id="",   # Will be filled by caller
            scenario_name=scenario_name,
            target_url=target_url,
            triggered_by="slack-user",
            triggered_at=started_at,
            started_at=started_at,
            completed_at=completed_at,
            duration_total_seconds=duration_seconds,
            overall_status=overall_status,
            total_cells=total_cells,
            passed_cells=passed_cells,
            failed_cells=failed_cells,
            timed_out_cells=timed_out_cells,
            environment_summary=env_summary,
            cell_results=cell_results,
            failures_by_priority=failures_by_priority,
            artifacts_storage_path=f"s3://testgpt-artifacts/{run_id}/"
        )

    def format_slack_summary(
        self,
        run_artifact: RunArtifact,
        dashboard_base_url: str = "https://dashboard.testgpt.dev"
    ) -> str:
        """
        Format RunArtifact into Slack message text.

        Implements Deliverable C structure from specification TODO 6.

        Args:
            run_artifact: Complete run artifact
            dashboard_base_url: Base URL for dashboard links

        Returns:
            Formatted Slack message text
        """
        # Build status emoji and summary
        if run_artifact.overall_status == TestStatus.PASS:
            status_emoji = ""
            status_text = "PASS"
        elif run_artifact.overall_status == TestStatus.FAIL:
            status_emoji = ""
            status_text = "FAIL"
        else:
            status_emoji = ""
            status_text = "PARTIAL"

        pass_rate = f"{run_artifact.passed_cells}/{run_artifact.total_cells}"

        # Build message
        lines = [
            "",
            " TestGPT QA Run Complete",
            "",
            "",
            f"Scenario: {run_artifact.scenario_name}",
            f"Target: {run_artifact.target_url}",
            f"Run ID: {run_artifact.run_id}",
            f"Status: {status_emoji} {status_text} ({pass_rate} runs passed)",
            ""
        ]

        # Add critical failures section
        if run_artifact.failed_cells > 0:
            lines.extend(self._format_failures_section(run_artifact))

        # Add passes section
        if run_artifact.passed_cells > 0:
            lines.extend(self._format_passes_section(run_artifact))

        # Add environment breakdown
        lines.extend(self._format_environment_breakdown(run_artifact))

        # Add next steps
        lines.extend(self._format_next_steps(run_artifact))

        # Add dashboard link
        dashboard_link = f"{dashboard_base_url}/runs/{run_artifact.run_id}"
        lines.extend([
            "",
            f" Full report: {dashboard_link}"
        ])

        return "\n".join(lines)

    def _group_failures_by_priority(self, cell_results: List[CellResult]) -> FailuresByPriority:
        """Group failed cells by priority level."""
        failures = FailuresByPriority()

        for result in cell_results:
            if result.status in [TestStatus.FAIL, TestStatus.ERROR]:
                if result.failure_priority == FailurePriority.P0:
                    failures.P0.append(result.cell_id)
                elif result.failure_priority == FailurePriority.P1:
                    failures.P1.append(result.cell_id)
                elif result.failure_priority == FailurePriority.P2:
                    failures.P2.append(result.cell_id)

        return failures

    def _create_environment_summary(self, cell_results: List[CellResult]) -> EnvironmentSummary:
        """Create summary of tested environments."""
        viewports = set()
        browsers = set()
        networks = set()

        for result in cell_results:
            viewports.add(result.viewport)
            browsers.add(result.browser)
            networks.add(result.network)

        return EnvironmentSummary(
            viewports_tested=sorted(list(viewports)),
            browsers_tested=sorted(list(browsers)),
            networks_tested=sorted(list(networks))
        )

    def _format_failures_section(self, run_artifact: RunArtifact) -> List[str]:
        """Format the critical failures section."""
        lines = [
            " CRITICAL FAILURES ",
            ""
        ]

        # Get failed cells by priority
        failed_cells = [r for r in run_artifact.cell_results if r.status in [TestStatus.FAIL, TestStatus.ERROR]]

        # Sort by priority (P0 first, then P1, then P2)
        priority_order = {FailurePriority.P0: 0, FailurePriority.P1: 1, FailurePriority.P2: 2}
        failed_cells.sort(key=lambda r: priority_order.get(r.failure_priority, 3))

        # Show top 5 failures
        for result in failed_cells[:5]:
            priority_emoji = "" if result.failure_priority == FailurePriority.P0 else "🟡"

            # Get browser display name
            try:
                browser_display = get_browser(result.browser).display_name
            except:
                browser_display = result.browser

            lines.extend([
                f"{priority_emoji} {result.failure_priority.value}: {browser_display} / {result.viewport} / {result.network}",
                f"   → {result.failure_summary}",
            ])

            # Add screenshot link if available
            if result.screenshots:
                lines.append(f"   → Screenshot: {result.screenshots[0].url}")

            lines.append("")

        return lines

    def _format_passes_section(self, run_artifact: RunArtifact) -> List[str]:
        """Format the passes summary section."""
        lines = [
            " PASSES ",
            ""
        ]

        # Group passes by browser
        passes_by_browser = defaultdict(int)
        for result in run_artifact.cell_results:
            if result.status == TestStatus.PASS:
                passes_by_browser[result.browser] += 1

        for browser, count in passes_by_browser.items():
            try:
                browser_display = get_browser(browser).display_name
            except:
                browser_display = browser

            lines.append(f" {browser_display}: {count} run(s) passed")

        lines.append("")
        return lines

    def _format_environment_breakdown(self, run_artifact: RunArtifact) -> List[str]:
        """Format the per-dimension environment breakdown."""
        lines = [
            " ENVIRONMENT BREAKDOWN ",
            ""
        ]

        # Breakdown by viewport
        viewport_stats = self._calculate_dimension_stats(run_artifact.cell_results, "viewport")
        lines.append("Viewports:")
        for name, (passed, total) in viewport_stats.items():
            status_emoji = "" if passed == total else "" if passed > 0 else ""
            lines.append(f"  • {name}: {passed}/{total} runs passed {status_emoji}")

        lines.append("")

        # Breakdown by browser
        browser_stats = self._calculate_dimension_stats(run_artifact.cell_results, "browser")
        lines.append("Browsers:")
        for name, (passed, total) in browser_stats.items():
            status_emoji = "" if passed == total else "" if passed > 0 else ""
            try:
                display_name = get_browser(name).display_name
            except:
                display_name = name
            lines.append(f"  • {display_name}: {passed}/{total} runs passed {status_emoji}")

        lines.append("")

        # Breakdown by network
        network_stats = self._calculate_dimension_stats(run_artifact.cell_results, "network")
        lines.append("Network:")
        for name, (passed, total) in network_stats.items():
            status_emoji = "" if passed == total else "" if passed > 0 else ""
            lines.append(f"  • {name}: {passed}/{total} runs passed {status_emoji}")

        lines.append("")
        return lines

    def _calculate_dimension_stats(
        self,
        cell_results: List[CellResult],
        dimension: str
    ) -> Dict[str, tuple]:
        """
        Calculate pass/total stats for a dimension.

        Args:
            cell_results: List of cell results
            dimension: "viewport", "browser", or "network"

        Returns:
            Dict mapping dimension value to (passed, total) tuple
        """
        stats = defaultdict(lambda: [0, 0])  # [passed, total]

        for result in cell_results:
            if dimension == "viewport":
                key = result.viewport
            elif dimension == "browser":
                key = result.browser
            elif dimension == "network":
                key = result.network
            else:
                continue

            stats[key][1] += 1  # total
            if result.status == TestStatus.PASS:
                stats[key][0] += 1  # passed

        return {k: tuple(v) for k, v in stats.items()}

    def _format_next_steps(self, run_artifact: RunArtifact) -> List[str]:
        """Format the next steps / actionable guidance section."""
        lines = [
            " NEXT STEPS ",
            ""
        ]

        if run_artifact.failed_cells > 0:
            # Get first P0 failure for specific guidance
            p0_failures = [
                r for r in run_artifact.cell_results
                if r.failure_priority == FailurePriority.P0 and r.status == TestStatus.FAIL
            ]

            if p0_failures:
                first_failure = p0_failures[0]
                lines.append(f"→ Fix critical issue: {first_failure.failure_summary[:100]}")

            # Check for Safari-specific failures
            safari_failures = [
                r for r in run_artifact.cell_results
                if "webkit" in r.browser and r.status == TestStatus.FAIL
            ]

            if safari_failures:
                lines.append("→ Debug Safari/WebKit-specific issues")

            # Check for network-related failures
            network_failures = [
                r for r in run_artifact.cell_results
                if r.network != "normal" and r.status == TestStatus.FAIL
            ]

            if network_failures:
                lines.append("→ Optimize for slow network conditions (image compression, lazy loading)")

        else:
            lines.append("→ All tests passed! ")

        # Add re-run command
        scenario_slug = run_artifact.scenario_name.split(" - ")[0].lower()
        lines.append(f"→ Re-run this test: \"re-run {scenario_slug} test\"")

        lines.append("")
        return lines
