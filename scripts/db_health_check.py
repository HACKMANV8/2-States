#!/usr/bin/env python3
"""
Database Health Check Script for TestGPT
Validates test storage and re-run functionality across all tables.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from database import (
    TestSuite, ConfigurationTemplate, TestExecution, ExecutionStep,
    PRTestRun, PRTestMetrics, DB_PATH, engine, SessionLocal
)


class DatabaseHealthChecker:
    """Comprehensive database health checker for TestGPT"""

    def __init__(self):
        self.db = SessionLocal()
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_path": DB_PATH,
            "checks": []
        }

    def add_check(self, name: str, status: str, details: dict):
        """Add a check result"""
        self.results["checks"].append({
            "name": name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    def check_database_exists(self):
        """Verify database file exists"""
        exists = os.path.exists(DB_PATH)
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024) if exists else 0

        self.add_check(
            "Database File Exists",
            "PASS" if exists else "FAIL",
            {
                "path": DB_PATH,
                "exists": exists,
                "size_mb": round(size_mb, 2)
            }
        )
        return exists

    def check_tables_exist(self):
        """Verify all required tables exist"""
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = [
            "test_suites",
            "configuration_templates",
            "test_executions_v2",
            "execution_steps",
            "pr_test_runs",
            "pr_test_metrics"
        ]

        missing_tables = [t for t in required_tables if t not in tables]

        self.add_check(
            "Required Tables Exist",
            "PASS" if not missing_tables else "FAIL",
            {
                "found_tables": tables,
                "missing_tables": missing_tables,
                "total_tables": len(tables)
            }
        )

        return not missing_tables

    def check_test_suites_storage(self):
        """Verify test_suites table has valid entries"""
        try:
            suites = self.db.query(TestSuite).all()

            # Check for test steps in JSON format
            suites_with_steps = [s for s in suites if s.test_steps]
            suites_with_invalid_json = []

            for suite in suites_with_steps:
                if not isinstance(suite.test_steps, (list, dict)):
                    suites_with_invalid_json.append(suite.id)

            # Group by source type
            by_source = {}
            for suite in suites:
                source = suite.source_type or "unknown"
                by_source[source] = by_source.get(source, 0) + 1

            self.add_check(
                "Test Suites Storage",
                "PASS" if suites and not suites_with_invalid_json else ("WARN" if not suites else "FAIL"),
                {
                    "total_suites": len(suites),
                    "suites_with_steps": len(suites_with_steps),
                    "invalid_json_count": len(suites_with_invalid_json),
                    "by_source_type": by_source,
                    "recent_suites": [
                        {
                            "id": s.id,
                            "name": s.name,
                            "created_at": s.created_at.isoformat() if s.created_at else None,
                            "source_type": s.source_type,
                            "has_steps": bool(s.test_steps)
                        }
                        for s in suites[-5:]  # Last 5 suites
                    ]
                }
            )

            return len(suites) > 0

        except Exception as e:
            self.add_check(
                "Test Suites Storage",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def check_test_executions(self):
        """Verify test_executions table and execution history"""
        try:
            executions = self.db.query(TestExecution).all()

            # Analyze execution statuses
            by_status = {}
            for exec in executions:
                status = exec.status or "unknown"
                by_status[status] = by_status.get(status, 0) + 1

            # Check test suite linkage
            linked_executions = [e for e in executions if e.test_suite_id]

            # Calculate execution times
            avg_exec_time = None
            if executions:
                times = [e.execution_time_ms for e in executions if e.execution_time_ms]
                if times:
                    avg_exec_time = sum(times) / len(times)

            # Check for executions per test
            execution_counts = {}
            for exec in executions:
                if exec.test_suite_id:
                    execution_counts[exec.test_suite_id] = execution_counts.get(exec.test_suite_id, 0) + 1

            most_run_test = None
            if execution_counts:
                most_run_id = max(execution_counts, key=execution_counts.get)
                most_run_test = {
                    "test_suite_id": most_run_id,
                    "execution_count": execution_counts[most_run_id]
                }

            self.add_check(
                "Test Executions History",
                "PASS" if executions else "WARN",
                {
                    "total_executions": len(executions),
                    "linked_to_suite": len(linked_executions),
                    "by_status": by_status,
                    "avg_execution_time_ms": round(avg_exec_time, 2) if avg_exec_time else None,
                    "most_run_test": most_run_test,
                    "recent_executions": [
                        {
                            "id": e.id,
                            "test_suite_id": e.test_suite_id,
                            "status": e.status,
                            "created_at": e.created_at.isoformat() if e.created_at else None,
                            "execution_time_ms": e.execution_time_ms
                        }
                        for e in executions[-5:]  # Last 5 executions
                    ]
                }
            )

            return True

        except Exception as e:
            self.add_check(
                "Test Executions History",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def check_configuration_templates(self):
        """Verify configuration templates are properly stored"""
        try:
            configs = self.db.query(ConfigurationTemplate).all()

            # Check for valid JSON configurations
            configs_with_browsers = [c for c in configs if c.browsers]
            configs_with_viewports = [c for c in configs if c.viewports]
            configs_with_networks = [c for c in configs if c.network_modes]

            self.add_check(
                "Configuration Templates",
                "PASS" if configs else "WARN",
                {
                    "total_configs": len(configs),
                    "with_browsers": len(configs_with_browsers),
                    "with_viewports": len(configs_with_viewports),
                    "with_networks": len(configs_with_networks),
                    "configs": [
                        {
                            "id": c.id,
                            "name": c.name,
                            "browsers": c.browsers if c.browsers else [],
                            "parallel_execution": c.parallel_execution
                        }
                        for c in configs
                    ]
                }
            )

            return True

        except Exception as e:
            self.add_check(
                "Configuration Templates",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def check_execution_steps(self):
        """Verify execution steps are being stored"""
        try:
            steps = self.db.query(ExecutionStep).all()

            # Group by execution
            by_execution = {}
            for step in steps:
                by_execution[step.execution_id] = by_execution.get(step.execution_id, 0) + 1

            # Check pass rate
            passed_steps = [s for s in steps if s.passed]
            pass_rate = (len(passed_steps) / len(steps) * 100) if steps else 0

            self.add_check(
                "Execution Steps Storage",
                "PASS" if steps else "WARN",
                {
                    "total_steps": len(steps),
                    "unique_executions": len(by_execution),
                    "passed_steps": len(passed_steps),
                    "pass_rate_percent": round(pass_rate, 2),
                    "recent_steps": [
                        {
                            "id": s.id,
                            "execution_id": s.execution_id,
                            "step_number": s.step_number,
                            "action": s.action,
                            "passed": s.passed
                        }
                        for s in steps[-10:]  # Last 10 steps
                    ]
                }
            )

            return True

        except Exception as e:
            self.add_check(
                "Execution Steps Storage",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def check_pr_test_runs(self):
        """Verify PR test runs are being stored"""
        try:
            pr_runs = self.db.query(PRTestRun).all()

            # Analyze PR runs
            by_status = {}
            for run in pr_runs:
                status = run.status or "unknown"
                by_status[status] = by_status.get(status, 0) + 1

            # Check Slack/GitHub integration
            with_slack = [r for r in pr_runs if r.slack_message_posted]
            with_github_comment = [r for r in pr_runs if r.github_comment_posted]

            self.add_check(
                "PR Test Runs",
                "PASS" if pr_runs else "WARN",
                {
                    "total_pr_runs": len(pr_runs),
                    "by_status": by_status,
                    "with_slack_notification": len(with_slack),
                    "with_github_comment": len(with_github_comment),
                    "recent_runs": [
                        {
                            "id": r.id,
                            "pr_number": r.pr_number,
                            "status": r.status,
                            "overall_pass": r.overall_pass,
                            "created_at": r.created_at.isoformat() if r.created_at else None
                        }
                        for r in pr_runs[-5:]  # Last 5 PR runs
                    ]
                }
            )

            return True

        except Exception as e:
            self.add_check(
                "PR Test Runs",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def check_data_integrity(self):
        """Check for orphaned records and data integrity issues"""
        try:
            # Check for orphaned executions (executions without test suites)
            orphaned_executions = self.db.query(TestExecution).filter(
                TestExecution.test_suite_id.isnot(None)
            ).all()

            orphaned_count = 0
            for exec in orphaned_executions:
                suite = self.db.query(TestSuite).filter(TestSuite.id == exec.test_suite_id).first()
                if not suite:
                    orphaned_count += 1

            # Check for orphaned execution steps
            orphaned_steps = self.db.query(ExecutionStep).all()
            orphaned_steps_count = 0
            for step in orphaned_steps:
                execution = self.db.query(TestExecution).filter(TestExecution.id == step.execution_id).first()
                if not execution:
                    orphaned_steps_count += 1

            self.add_check(
                "Data Integrity",
                "PASS" if orphaned_count == 0 and orphaned_steps_count == 0 else "WARN",
                {
                    "orphaned_executions": orphaned_count,
                    "orphaned_execution_steps": orphaned_steps_count,
                    "integrity_issues": orphaned_count + orphaned_steps_count
                }
            )

            return orphaned_count == 0 and orphaned_steps_count == 0

        except Exception as e:
            self.add_check(
                "Data Integrity",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def check_recent_activity(self):
        """Check for recent test activity"""
        try:
            # Check for tests run in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)

            recent_suites = self.db.query(TestSuite).filter(
                TestSuite.created_at >= yesterday
            ).count()

            recent_executions = self.db.query(TestExecution).filter(
                TestExecution.created_at >= yesterday
            ).count()

            recent_pr_runs = self.db.query(PRTestRun).filter(
                PRTestRun.created_at >= yesterday
            ).count()

            self.add_check(
                "Recent Activity (24h)",
                "PASS" if recent_executions > 0 else "INFO",
                {
                    "new_test_suites": recent_suites,
                    "test_executions": recent_executions,
                    "pr_test_runs": recent_pr_runs,
                    "total_activity": recent_suites + recent_executions + recent_pr_runs
                }
            )

            return True

        except Exception as e:
            self.add_check(
                "Recent Activity",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def generate_summary(self):
        """Generate overall summary"""
        pass_count = sum(1 for c in self.results["checks"] if c["status"] == "PASS")
        warn_count = sum(1 for c in self.results["checks"] if c["status"] == "WARN")
        fail_count = sum(1 for c in self.results["checks"] if c["status"] == "FAIL")
        error_count = sum(1 for c in self.results["checks"] if c["status"] == "ERROR")
        total_checks = len(self.results["checks"])

        self.results["summary"] = {
            "total_checks": total_checks,
            "passed": pass_count,
            "warnings": warn_count,
            "failed": fail_count,
            "errors": error_count,
            "overall_status": "HEALTHY" if fail_count == 0 and error_count == 0 else "ISSUES_FOUND"
        }

    def run_all_checks(self):
        """Run all health checks"""
        print("=" * 80)
        print("TestGPT Database Health Check")
        print("=" * 80)
        print()

        # Run all checks
        self.check_database_exists()
        self.check_tables_exist()
        self.check_test_suites_storage()
        self.check_test_executions()
        self.check_configuration_templates()
        self.check_execution_steps()
        self.check_pr_test_runs()
        self.check_data_integrity()
        self.check_recent_activity()

        # Generate summary
        self.generate_summary()

        # Close database connection
        self.db.close()

        return self.results

    def print_results(self):
        """Print formatted results to console"""
        summary = self.results["summary"]

        print("\n" + "=" * 80)
        print("OVERALL STATUS: " + summary["overall_status"])
        print("=" * 80)
        print(f"Total Checks: {summary['total_checks']}")
        print(f" Passed: {summary['passed']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f" Failed: {summary['failed']}")
        print(f" Errors: {summary['errors']}")
        print()

        # Print individual check results
        for check in self.results["checks"]:
            status_icon = {
                "PASS": "",
                "WARN": "",
                "FAIL": "",
                "ERROR": "",
                "INFO": "ℹ"
            }.get(check["status"], "?")

            print(f"{status_icon} {check['name']}: {check['status']}")

            # Print key details
            if check["status"] in ["FAIL", "ERROR"]:
                for key, value in check["details"].items():
                    if key == "error":
                        print(f"   Error: {value}")
                    elif key == "missing_tables":
                        print(f"   Missing: {value}")
            else:
                # Print summary info for passing checks
                if "total_suites" in check["details"]:
                    print(f"   Total Suites: {check['details']['total_suites']}")
                if "total_executions" in check["details"]:
                    print(f"   Total Executions: {check['details']['total_executions']}")
                if "by_status" in check["details"]:
                    print(f"   By Status: {check['details']['by_status']}")

            print()

    def save_to_file(self, filepath: str = None):
        """Save results to JSON file"""
        if filepath is None:
            filepath = f"/tmp/testgpt_health_check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f" Full results saved to: {filepath}")
        return filepath


def main():
    """Main execution"""
    checker = DatabaseHealthChecker()
    results = checker.run_all_checks()
    checker.print_results()
    checker.save_to_file()

    # Exit with appropriate code
    if results["summary"]["overall_status"] == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
