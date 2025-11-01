#!/usr/bin/env python3
"""
TestGPT API Endpoint Testing Script

Tests all API endpoints for test storage and re-run functionality.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List


class APITester:
    """Comprehensive API testing for TestGPT"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": []
        }
        self.test_data = {
            "created_suite_id": None,
            "created_config_id": None,
            "created_execution_id": None,
        }

    def add_test_result(self, name: str, status: str, details: Dict[str, Any]):
        """Add a test result"""
        self.results["tests"].append({
            "name": name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })

    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            success = response.status_code == 200

            self.add_test_result(
                "Health Check",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "response": response.json() if success else response.text
                }
            )
            return success
        except Exception as e:
            self.add_test_result(
                "Health Check",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_create_test_suite(self) -> bool:
        """Test creating a new test suite"""
        try:
            test_suite = {
                "name": "API Test Suite - Login Flow",
                "description": "Test suite created via API for testing storage",
                "prompt": "Test the login flow on the example website",
                "target_url": "https://example.com/login",
                "test_steps": [
                    {
                        "step_number": 1,
                        "action": "navigate",
                        "target": "https://example.com/login",
                        "expected_outcome": "Login page loads successfully",
                        "timeout_seconds": 10
                    },
                    {
                        "step_number": 2,
                        "action": "fill",
                        "target": "input#username",
                        "value": "testuser",
                        "expected_outcome": "Username field is filled",
                        "timeout_seconds": 5
                    },
                    {
                        "step_number": 3,
                        "action": "fill",
                        "target": "input#password",
                        "value": "testpassword",
                        "expected_outcome": "Password field is filled",
                        "timeout_seconds": 5
                    },
                    {
                        "step_number": 4,
                        "action": "click",
                        "target": "button[type='submit']",
                        "expected_outcome": "Login button is clicked",
                        "timeout_seconds": 5
                    },
                    {
                        "step_number": 5,
                        "action": "wait_for_url",
                        "target": "https://example.com/dashboard",
                        "expected_outcome": "Dashboard loads after login",
                        "timeout_seconds": 10
                    }
                ],
                "created_by": "api-tester",
                "source_type": "manual",
                "tags": ["login", "authentication", "api-test"]
            }

            response = requests.post(
                f"{self.base_url}/api/tests",
                json=test_suite,
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            if success and "id" in data:
                self.test_data["created_suite_id"] = data["id"]

            self.add_test_result(
                "Create Test Suite",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "suite_id": data.get("id") if success else None,
                    "suite_name": data.get("name") if success else None,
                    "steps_count": len(data.get("test_steps", [])) if success else 0,
                    "response": data if success else response.text
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Create Test Suite",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_list_test_suites(self) -> bool:
        """Test listing all test suites"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tests",
                params={"limit": 10},
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else []

            self.add_test_result(
                "List Test Suites",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "count": len(data) if success else 0,
                    "suites": data if success else []
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "List Test Suites",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_get_test_suite(self) -> bool:
        """Test getting a specific test suite"""
        if not self.test_data["created_suite_id"]:
            self.add_test_result(
                "Get Test Suite",
                "SKIP",
                {"reason": "No suite ID available"}
            )
            return False

        try:
            suite_id = self.test_data["created_suite_id"]
            response = requests.get(
                f"{self.base_url}/api/tests/{suite_id}",
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            self.add_test_result(
                "Get Test Suite",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "suite_id": data.get("id") if success else None,
                    "suite_name": data.get("name") if success else None,
                    "has_steps": bool(data.get("test_steps")) if success else False,
                    "steps_count": len(data.get("test_steps", [])) if success else 0
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Get Test Suite",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_create_configuration_template(self) -> bool:
        """Test creating a configuration template"""
        try:
            config = {
                "name": "Standard Desktop Config",
                "description": "Configuration for desktop testing",
                "browsers": ["chrome", "firefox"],
                "viewports": [
                    {
                        "width": 1920,
                        "height": 1080,
                        "device_name": "desktop"
                    }
                ],
                "network_modes": ["online", "fast3g"],
                "screenshot_on_failure": True,
                "video_recording": False,
                "parallel_execution": True,
                "max_workers": 4,
                "default_timeout": 30000
            }

            response = requests.post(
                f"{self.base_url}/api/configs",
                json=config,
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            if success and "id" in data:
                self.test_data["created_config_id"] = data["id"]

            self.add_test_result(
                "Create Configuration Template",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "config_id": data.get("id") if success else None,
                    "config_name": data.get("name") if success else None,
                    "browsers": data.get("browsers") if success else [],
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Create Configuration Template",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_list_configurations(self) -> bool:
        """Test listing configuration templates"""
        try:
            response = requests.get(
                f"{self.base_url}/api/configs",
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else []

            self.add_test_result(
                "List Configuration Templates",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "count": len(data) if success else 0,
                    "configs": [
                        {
                            "id": c.get("id"),
                            "name": c.get("name"),
                            "browsers": c.get("browsers")
                        }
                        for c in data
                    ] if success else []
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "List Configuration Templates",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_run_test(self) -> bool:
        """Test running a test suite (re-run functionality)"""
        if not self.test_data["created_suite_id"]:
            self.add_test_result(
                "Run Test",
                "SKIP",
                {"reason": "No suite ID available"}
            )
            return False

        try:
            suite_id = self.test_data["created_suite_id"]
            execution_request = {
                "test_suite_id": suite_id,
                "browser": "chrome",
                "viewport_width": 1920,
                "viewport_height": 1080,
                "network_mode": "online",
                "triggered_by": "manual",
                "triggered_by_user": "api-tester"
            }

            response = requests.post(
                f"{self.base_url}/api/tests/{suite_id}/run",
                json=execution_request,
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            if success and "id" in data:
                self.test_data["created_execution_id"] = data["id"]

            self.add_test_result(
                "Run Test (Re-run)",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "execution_id": data.get("id") if success else None,
                    "status": data.get("status") if success else None,
                    "test_suite_id": data.get("test_suite_id") if success else None,
                    "browser": data.get("browser") if success else None
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Run Test (Re-run)",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_get_execution(self) -> bool:
        """Test getting execution details"""
        if not self.test_data["created_execution_id"]:
            self.add_test_result(
                "Get Execution",
                "SKIP",
                {"reason": "No execution ID available"}
            )
            return False

        try:
            execution_id = self.test_data["created_execution_id"]

            # Wait a bit for execution to start
            time.sleep(2)

            response = requests.get(
                f"{self.base_url}/api/executions/{execution_id}",
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            self.add_test_result(
                "Get Execution",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "execution_id": data.get("id") if success else None,
                    "status": data.get("status") if success else None,
                    "started_at": data.get("started_at") if success else None,
                    "completed_at": data.get("completed_at") if success else None
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Get Execution",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_list_executions(self) -> bool:
        """Test listing all executions"""
        try:
            response = requests.get(
                f"{self.base_url}/api/executions",
                params={"limit": 10},
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else []

            self.add_test_result(
                "List Executions",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "count": len(data) if success else 0,
                    "executions": [
                        {
                            "id": e.get("id"),
                            "status": e.get("status"),
                            "test_suite_id": e.get("test_suite_id")
                        }
                        for e in data
                    ] if success else []
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "List Executions",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_get_execution_history(self) -> bool:
        """Test getting execution history for a test suite"""
        if not self.test_data["created_suite_id"]:
            self.add_test_result(
                "Get Execution History",
                "SKIP",
                {"reason": "No suite ID available"}
            )
            return False

        try:
            suite_id = self.test_data["created_suite_id"]
            response = requests.get(
                f"{self.base_url}/api/tests/{suite_id}/history",
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            self.add_test_result(
                "Get Execution History",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "test_suite_id": data.get("test_suite_id") if success else None,
                    "total_runs": data.get("total_runs") if success else 0,
                    "passed_runs": data.get("passed_runs") if success else 0,
                    "failed_runs": data.get("failed_runs") if success else 0,
                    "executions_count": len(data.get("executions", [])) if success else 0
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Get Execution History",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_batch_execution(self) -> bool:
        """Test batch execution of multiple tests"""
        if not self.test_data["created_suite_id"] or not self.test_data["created_config_id"]:
            self.add_test_result(
                "Batch Execution",
                "SKIP",
                {"reason": "Required IDs not available"}
            )
            return False

        try:
            batch_request = {
                "test_suite_ids": [self.test_data["created_suite_id"]],
                "config_id": self.test_data["created_config_id"],
                "triggered_by": "manual",
                "triggered_by_user": "api-tester"
            }

            response = requests.post(
                f"{self.base_url}/api/tests/batch/run",
                json=batch_request,
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            self.add_test_result(
                "Batch Execution",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "batch_id": data.get("batch_id") if success else None,
                    "total_tests": data.get("total_tests") if success else 0,
                    "execution_ids": data.get("execution_ids") if success else [],
                    "status": data.get("status") if success else None
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Batch Execution",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def test_statistics(self) -> bool:
        """Test getting overall statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/statistics",
                timeout=10
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            self.add_test_result(
                "Get Statistics",
                "PASS" if success else "FAIL",
                {
                    "status_code": response.status_code,
                    "total_test_suites": data.get("total_test_suites") if success else 0,
                    "total_executions": data.get("total_executions") if success else 0,
                    "passed_executions": data.get("passed_executions") if success else 0,
                    "failed_executions": data.get("failed_executions") if success else 0,
                    "running_executions": data.get("running_executions") if success else 0
                }
            )
            return success

        except Exception as e:
            self.add_test_result(
                "Get Statistics",
                "ERROR",
                {"error": str(e)}
            )
            return False

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("=" * 80)
        print("TestGPT API Endpoint Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print()

        # Run tests in order
        tests = [
            ("Health Check", self.test_health_check),
            ("Create Test Suite", self.test_create_test_suite),
            ("List Test Suites", self.test_list_test_suites),
            ("Get Test Suite", self.test_get_test_suite),
            ("Create Configuration", self.test_create_configuration_template),
            ("List Configurations", self.test_list_configurations),
            ("Run Test (Re-run)", self.test_run_test),
            ("Get Execution", self.test_get_execution),
            ("List Executions", self.test_list_executions),
            ("Get Execution History", self.test_get_execution_history),
            ("Batch Execution", self.test_batch_execution),
            ("Get Statistics", self.test_statistics),
        ]

        for test_name, test_func in tests:
            print(f"Running: {test_name}...", end=" ")
            result = test_func()
            status_icon = "" if result else ""
            print(f"{status_icon}")
            time.sleep(0.5)  # Small delay between tests

        return self.results

    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for t in self.results["tests"] if t["status"] == "PASS")
        failed = sum(1 for t in self.results["tests"] if t["status"] == "FAIL")
        errors = sum(1 for t in self.results["tests"] if t["status"] == "ERROR")
        skipped = sum(1 for t in self.results["tests"] if t["status"] == "SKIP")
        total = len(self.results["tests"])

        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f" Passed: {passed}")
        print(f" Failed: {failed}")
        print(f" Errors: {errors}")
        print(f"⏭  Skipped: {skipped}")
        print()

        # Print failed/error tests
        if failed > 0 or errors > 0:
            print("Failed/Error Tests:")
            for test in self.results["tests"]:
                if test["status"] in ["FAIL", "ERROR"]:
                    print(f"  - {test['name']}: {test['status']}")
                    if "error" in test["details"]:
                        print(f"    Error: {test['details']['error']}")
            print()

        # Print created resources
        if self.test_data["created_suite_id"]:
            print(f"Created Test Suite ID: {self.test_data['created_suite_id']}")
        if self.test_data["created_config_id"]:
            print(f"Created Config ID: {self.test_data['created_config_id']}")
        if self.test_data["created_execution_id"]:
            print(f"Created Execution ID: {self.test_data['created_execution_id']}")
        print()

    def save_results(self, filepath: str = None):
        """Save results to JSON file"""
        if filepath is None:
            filepath = f"/tmp/testgpt_api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f" Full results saved to: {filepath}")
        return filepath


def main():
    """Main execution"""
    import sys

    # Check if API server is running
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Testing API at: {base_url}")
    print()

    tester = APITester(base_url)

    try:
        tester.run_all_tests()
        tester.print_summary()
        tester.save_results()

        # Return exit code based on results
        failed = sum(1 for t in tester.results["tests"] if t["status"] in ["FAIL", "ERROR"])
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print("\n  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
