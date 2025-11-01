"""
Test script for TestGPT Backend API.

Tests all major endpoints to verify functionality.
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint"""
    print("\n Testing health check...")
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print(" Health check passed")


def test_create_config():
    """Test creating a configuration template"""
    print("\n  Testing configuration template creation...")
    config_data = {
        "name": "Test Config",
        "description": "Configuration for testing",
        "browsers": ["chrome", "firefox"],
        "viewports": [
            {"width": 1920, "height": 1080, "device_name": "desktop"}
        ],
        "network_modes": ["online"],
        "screenshot_on_failure": True,
        "video_recording": False,
        "parallel_execution": True,
        "max_workers": 2,
        "default_timeout": 30000,
    }

    response = requests.post(
        f"{API_BASE_URL}/api/configs",
        json=config_data,
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    config = response.json()
    assert config["name"] == "Test Config"
    print(f" Created config: {config['id']}")
    return config["id"]


def test_list_configs():
    """Test listing configuration templates"""
    print("\n Testing configuration list...")
    response = requests.get(f"{API_BASE_URL}/api/configs")
    assert response.status_code == 200
    configs = response.json()
    assert isinstance(configs, list)
    print(f" Found {len(configs)} configurations")
    return configs


def test_create_test_suite():
    """Test creating a test suite"""
    print("\n Testing test suite creation...")
    test_data = {
        "name": "Homepage Test",
        "description": "Test the homepage functionality",
        "prompt": "Test if homepage loads and has correct title",
        "target_url": "https://example.com",
        "test_steps": [
            {
                "step_number": 1,
                "action": "navigate",
                "target": "https://example.com",
                "expected_outcome": "Page loads successfully",
                "timeout_seconds": 10
            },
            {
                "step_number": 2,
                "action": "assert_visible",
                "target": "h1",
                "expected_outcome": "Heading is visible",
                "timeout_seconds": 5
            }
        ],
        "tags": ["homepage", "smoke"],
        "source_type": "manual",
        "created_by": "test_script"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/tests",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    suite = response.json()
    assert suite["name"] == "Homepage Test"
    assert len(suite["test_steps"]) == 2
    print(f" Created test suite: {suite['id']}")
    return suite["id"]


def test_list_test_suites():
    """Test listing test suites"""
    print("\n Testing test suite list...")
    response = requests.get(f"{API_BASE_URL}/api/tests")
    assert response.status_code == 200
    suites = response.json()
    assert isinstance(suites, list)
    print(f" Found {len(suites)} test suites")
    return suites


def test_get_test_suite(suite_id):
    """Test getting a specific test suite"""
    print(f"\n Testing get test suite {suite_id}...")
    response = requests.get(f"{API_BASE_URL}/api/tests/{suite_id}")
    assert response.status_code == 200
    suite = response.json()
    assert suite["id"] == suite_id
    print(f" Retrieved test suite: {suite['name']}")
    return suite


def test_update_test_suite(suite_id):
    """Test updating a test suite"""
    print(f"\n  Testing update test suite {suite_id}...")
    update_data = {
        "description": "Updated description",
        "tags": ["homepage", "smoke", "updated"]
    }

    response = requests.put(
        f"{API_BASE_URL}/api/tests/{suite_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    suite = response.json()
    assert suite["description"] == "Updated description"
    assert "updated" in suite["tags"]
    print(f" Updated test suite")


def test_run_test(suite_id, config_id):
    """Test running a test (creates pending execution)"""
    print(f"\n  Testing run test {suite_id}...")
    run_data = {
        "test_suite_id": suite_id,
        "config_id": config_id,
        "browser": "chrome",
        "viewport_width": 1920,
        "viewport_height": 1080,
        "network_mode": "online",
        "triggered_by": "manual",
        "triggered_by_user": "test_script"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/tests/{suite_id}/run",
        json=run_data,
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    execution = response.json()
    assert execution["status"] == "pending"
    assert execution["test_suite_id"] == suite_id
    print(f" Created execution: {execution['id']} (status: {execution['status']})")
    return execution["id"]


def test_list_executions():
    """Test listing executions"""
    print("\n Testing execution list...")
    response = requests.get(f"{API_BASE_URL}/api/executions")
    assert response.status_code == 200
    executions = response.json()
    assert isinstance(executions, list)
    print(f" Found {len(executions)} executions")
    return executions


def test_get_execution(execution_id):
    """Test getting execution details"""
    print(f"\n Testing get execution {execution_id}...")
    response = requests.get(f"{API_BASE_URL}/api/executions/{execution_id}")
    assert response.status_code == 200
    execution = response.json()
    assert execution["id"] == execution_id
    print(f" Retrieved execution: {execution['status']}")


def test_get_history(suite_id):
    """Test getting execution history"""
    print(f"\n Testing execution history for {suite_id}...")
    response = requests.get(f"{API_BASE_URL}/api/tests/{suite_id}/history")
    assert response.status_code == 200
    history = response.json()
    assert history["test_suite_id"] == suite_id
    assert "executions" in history
    print(f" Retrieved history: {history['total_runs']} runs")


def test_statistics():
    """Test getting statistics"""
    print("\n Testing statistics...")
    response = requests.get(f"{API_BASE_URL}/api/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert "total_test_suites" in stats
    assert "total_executions" in stats
    print(f" Statistics: {stats['total_test_suites']} suites, {stats['total_executions']} executions")


def test_batch_run(suite_ids, config_id):
    """Test batch test execution"""
    print(f"\n Testing batch run...")
    batch_data = {
        "test_suite_ids": suite_ids,
        "config_id": config_id,
        "triggered_by": "manual",
        "triggered_by_user": "test_script"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/tests/batch/run",
        json=batch_data,
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    batch = response.json()
    assert batch["total_tests"] == len(suite_ids)
    print(f" Batch created: {batch['total_tests']} tests queued")


def test_delete_test_suite(suite_id):
    """Test deleting a test suite"""
    print(f"\n  Testing delete test suite {suite_id}...")
    response = requests.delete(f"{API_BASE_URL}/api/tests/{suite_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "deleted"
    print(f" Deleted test suite")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TestGPT Backend API Tests")
    print("=" * 60)

    try:
        # Test health
        test_health()

        # Test configurations
        config_id = test_create_config()
        configs = test_list_configs()

        # Test suites
        suite_id_1 = test_create_test_suite()
        suite_id_2 = test_create_test_suite()  # Create second suite
        suites = test_list_test_suites()
        test_get_test_suite(suite_id_1)
        test_update_test_suite(suite_id_1)

        # Test executions
        execution_id = test_run_test(suite_id_1, config_id)
        test_list_executions()
        test_get_execution(execution_id)
        test_get_history(suite_id_1)

        # Test statistics
        test_statistics()

        # Test batch run
        test_batch_run([suite_id_1, suite_id_2], config_id)

        # Cleanup
        test_delete_test_suite(suite_id_1)
        test_delete_test_suite(suite_id_2)

        print("\n" + "=" * 60)
        print(" ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n Test failed: {str(e)}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n Cannot connect to API server at http://localhost:8000")
        print("   Make sure the backend server is running:")
        print("   python backend/api/main.py")
        return False
    except Exception as e:
        print(f"\n Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
