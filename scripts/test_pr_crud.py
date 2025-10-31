#!/usr/bin/env python3
"""
Test PR Test CRUD operations.

Verifies that create, read, update operations work correctly.
"""

import sys
import os
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal
from backend.pr_test_crud import (
    create_pr_test_run,
    get_pr_test_run,
    get_pr_test_runs,
    update_pr_test_run,
    get_pr_test_stats
)

def test_crud_operations():
    """Test CRUD operations."""
    print("🧪 Testing PR Test CRUD operations...\n")

    db = SessionLocal()

    try:
        # 1. CREATE
        print("1️⃣ Testing CREATE...")
        test_run_id = f"test-run-{uuid.uuid4().hex[:8]}"
        test_data = {
            "test_run_id": test_run_id,
            "pr_url": "https://github.com/test/repo/pull/1",
            "pr_number": 1,
            "pr_title": "Test PR for CRUD operations",
            "pr_author": "testuser",
            "repo_owner": "test",
            "repo_name": "repo",
            "base_branch": "main",
            "head_branch": "feature/test",
            "head_sha": "abc123",
            "pr_description": "This is a test PR",
            "files_changed_count": 3,
            "changed_files": ["file1.py", "file2.py", "file3.py"],
            "acceptance_criteria": ["Feature works", "Tests pass"],
            "linked_issues": [42, 43],
            "deployment_url": "https://test-deploy.vercel.app",
            "deployment_platform": "Vercel",
            "deployment_accessible": True,
            "deployment_response_time_ms": 250,
            "project_type": "frontend",
            "tech_stack": ["Next.js", "React", "TypeScript"],
            "framework_detected": "Next.js 14",
            "test_scenarios": [
                {"name": "Basic functionality", "priority": "critical"},
                {"name": "Mobile responsiveness", "priority": "high"}
            ],
            "scenario_count": 2,
            "status": "running",
            "scenarios_total": 2,
            "started_at": datetime.utcnow(),
            "triggered_by": "test_script",
            "triggered_by_user": "test_user"
        }

        pr_test = create_pr_test_run(db, test_data)
        print(f"   ✅ Created PR test run: {pr_test.id}")
        print(f"   📋 PR: {pr_test.repo_owner}/{pr_test.repo_name}#{pr_test.pr_number}")
        print(f"   🔍 Status: {pr_test.status}")

        # 2. READ (by ID)
        print("\n2️⃣ Testing READ (by ID)...")
        retrieved = get_pr_test_run(db, pr_test.id)
        if retrieved:
            print(f"   ✅ Retrieved PR test run: {retrieved.pr_title}")
            print(f"   📊 Scenarios: {retrieved.scenarios_total}")
            print(f"   🌐 Deployment: {retrieved.deployment_platform}")
        else:
            print("   ❌ Failed to retrieve PR test run")

        # 3. UPDATE
        print("\n3️⃣ Testing UPDATE...")
        updates = {
            "status": "passed",
            "overall_pass": True,
            "scenarios_passed": 2,
            "scenarios_failed": 0,
            "completed_at": datetime.utcnow(),
            "duration_ms": 5000,
            "test_results": {
                "overall_status": "PASS",
                "passed_count": 2,
                "total_count": 2
            }
        }
        updated = update_pr_test_run(db, pr_test.id, updates)
        if updated:
            print(f"   ✅ Updated PR test run")
            print(f"   🔍 New status: {updated.status}")
            print(f"   ✅ Pass: {updated.overall_pass}")
            print(f"   📊 Results: {updated.scenarios_passed}/{updated.scenarios_total} passed")
        else:
            print("   ❌ Failed to update PR test run")

        # 4. LIST
        print("\n4️⃣ Testing LIST...")
        all_tests = get_pr_test_runs(db, limit=10)
        print(f"   ✅ Retrieved {len(all_tests)} PR test runs")
        for test in all_tests:
            print(f"      - {test.repo_owner}/{test.repo_name}#{test.pr_number}: {test.status}")

        # 5. FILTER
        print("\n5️⃣ Testing FILTER (by repo)...")
        filtered = get_pr_test_runs(db, repo_owner="test", repo_name="repo")
        print(f"   ✅ Retrieved {len(filtered)} tests for test/repo")

        # 6. STATS
        print("\n6️⃣ Testing STATS...")
        stats = get_pr_test_stats(db, days=7)
        print(f"   ✅ Statistics for last 7 days:")
        print(f"      - Total tests: {stats['total_tests']}")
        print(f"      - Passed: {stats['passed']}")
        print(f"      - Failed: {stats['failed']}")
        print(f"      - Success rate: {stats['success_rate']:.1f}%")

        print("\n✅ All CRUD operations successful!\n")

    except Exception as e:
        print(f"\n❌ Error during CRUD test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test_crud_operations()
