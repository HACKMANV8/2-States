"""
Persistence layer for PR test runs.

Handles saving and loading PR test data to/from database.
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from backend.database import SessionLocal, PRTestRun
from backend.pr_test_crud import create_pr_test_run, update_pr_test_run, get_pr_test_run


class PRTestPersistence:
    """Handles persistence of PR test runs."""

    def __init__(self):
        """Initialize persistence layer."""
        self.db = None

    def _get_db(self):
        """Get database session."""
        if not self.db:
            self.db = SessionLocal()
        return self.db

    def _close_db(self):
        """Close database session."""
        if self.db:
            self.db.close()
            self.db = None

    def save_pr_test_start(self, pr_test_data: Dict[str, Any]) -> Optional[str]:
        """
        Save PR test run at start of execution.

        Args:
            pr_test_data: PR test data dictionary

        Returns:
            Test run ID if successful, None otherwise
        """
        try:
            db = self._get_db()

            # Extract data from pr_context and other sources
            pr_context = pr_test_data.get("pr_context", {})
            pr_info = pr_context.get("pr_info", {})
            pr_metadata = pr_context.get("metadata", {})
            deployment_info = pr_test_data.get("deployment_info", {})
            codebase_analysis = pr_test_data.get("codebase_analysis", {})
            test_context = pr_test_data.get("test_context", {})

            # Build database record
            db_data = {
                "test_run_id": pr_test_data.get("test_run_id"),
                "pr_url": pr_test_data.get("pr_url"),
                "pr_number": int(pr_info.get("pr_number", 0)),
                "pr_title": pr_metadata.get("title", "Unknown"),
                "pr_author": pr_metadata.get("author"),
                "repo_owner": pr_info.get("owner", ""),
                "repo_name": pr_info.get("repo", ""),
                "base_branch": pr_metadata.get("base_branch"),
                "head_branch": pr_metadata.get("head_branch"),
                "head_sha": pr_metadata.get("head_sha"),
                "pr_description": pr_metadata.get("description"),
                "files_changed_count": len(pr_context.get("files", [])),
                "changed_files": [f["filename"] for f in pr_context.get("files", [])],
                "acceptance_criteria": test_context.get("acceptance_criteria", []),
                "linked_issues": [i.get("number") for i in pr_context.get("linked_issues", [])],
                "deployment_url": deployment_info.get("deployment_url"),
                "deployment_platform": deployment_info.get("platform"),
                "deployment_accessible": deployment_info.get("accessible"),
                "deployment_response_time_ms": deployment_info.get("validation", {}).get("response_time_ms"),
                "project_type": codebase_analysis.get("project_type"),
                "tech_stack": codebase_analysis.get("tech_stack", []),
                "framework_detected": codebase_analysis.get("framework_detected"),
                "test_scenarios": test_context.get("test_scenarios", []),
                "scenario_count": len(test_context.get("test_scenarios", [])),
                "status": "running",
                "scenarios_total": len(test_context.get("test_scenarios", [])),
                "started_at": datetime.utcnow(),
                "triggered_by": pr_test_data.get("triggered_by", "slack"),
                "triggered_by_user": pr_test_data.get("triggered_by_user"),
                "custom_instructions": pr_test_data.get("custom_instructions"),
            }

            pr_test = create_pr_test_run(db, db_data)

            print(f"    Saved PR test run to database: {pr_test.id}")

            return pr_test.id

        except Exception as e:
            print(f"     Failed to save PR test start: {e}")
            return None
        finally:
            self._close_db()

    def update_pr_test_results(self, test_run_id: str, test_results: Dict[str, Any]) -> bool:
        """
        Update PR test run with execution results.

        Args:
            test_run_id: Test run ID
            test_results: Test results dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._get_db()

            # Parse completed_at if it's a string
            completed_at_value = test_results.get("completed_at")
            if completed_at_value:
                if isinstance(completed_at_value, str):
                    from dateutil import parser
                    completed_at_value = parser.parse(completed_at_value)
            else:
                completed_at_value = datetime.utcnow()

            updates = {
                "status": "passed" if test_results.get("overall_status") == "PASS" else "failed",
                "overall_pass": test_results.get("overall_status") == "PASS",
                "scenarios_passed": test_results.get("passed_count", 0),
                "scenarios_failed": test_results.get("total_count", 0) - test_results.get("passed_count", 0),
                "test_results": test_results,
                "failures": test_results.get("failures", []),
                "console_errors": test_results.get("console_errors", []),
                "screenshots": test_results.get("screenshots", []),
                "agent_response": test_results.get("agent_response"),
                "completed_at": completed_at_value,
                "duration_ms": test_results.get("duration_ms"),
            }

            updated = update_pr_test_run(db, test_run_id, updates)

            if updated:
                print(f"    Updated PR test results: {test_run_id}")
                return True
            else:
                print(f"     Failed to update PR test (not found): {test_run_id}")
                return False

        except Exception as e:
            print(f"     Failed to update PR test results: {e}")
            return False
        finally:
            self._close_db()

    def update_github_comment_info(self, test_run_id: str, comment_result: Dict[str, Any]) -> bool:
        """
        Update PR test with GitHub comment information.

        Args:
            test_run_id: Test run ID
            comment_result: GitHub comment result

        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._get_db()

            updates = {
                "github_comment_posted": comment_result.get("success", False),
                "github_comment_url": comment_result.get("comment_url"),
                "github_comment_id": comment_result.get("comment_id"),
            }

            updated = update_pr_test_run(db, test_run_id, updates)

            return updated is not None

        except Exception as e:
            print(f"     Failed to update GitHub comment info: {e}")
            return False
        finally:
            self._close_db()

    def get_pr_test(self, test_run_id: str) -> Optional[PRTestRun]:
        """
        Get PR test run by ID.

        Args:
            test_run_id: Test run ID

        Returns:
            PRTestRun object or None
        """
        try:
            db = self._get_db()
            return get_pr_test_run(db, test_run_id)

        except Exception as e:
            print(f"     Failed to get PR test: {e}")
            return None
        finally:
            self._close_db()
