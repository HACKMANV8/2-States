#!/usr/bin/env python3
"""
Test the API run endpoint to verify it properly calls the TestGPT engine
"""

import requests
import json
from backend import crud
from backend.database import SessionLocal

# Get a test suite from database
db = SessionLocal()
suites = crud.get_test_suites(db, skip=0, limit=1)

if not suites:
    print("❌ No test suites found in database")
    exit(1)

suite = suites[0]
print(f"✅ Found test suite: {suite.name}")
print(f"   ID: {suite.id}")
print(f"   URL: {suite.target_url}")
print(f"   Steps: {len(suite.test_steps)}")
print()

# Test the API endpoint
print("🚀 Testing API run endpoint...")
print(f"   POST http://localhost:8000/api/tests/{suite.id}/run")
print()

response = requests.post(
    f"http://localhost:8000/api/tests/{suite.id}/run",
    json={
        "test_suite_id": suite.id,
        "browser": "chrome",
        "viewport_width": 1920,
        "viewport_height": 1080,
        "triggered_by": "manual"
    },
    headers={"Content-Type": "application/json"}
)

print(f"📊 Response Status: {response.status_code}")
print()

if response.status_code == 200:
    result = response.json()
    print("✅ API call successful!")
    print(f"   Execution ID: {result['id']}")
    print(f"   Status: {result['status']}")
    print()
    print("🔍 Check the backend terminal for:")
    print("   - 🚀 Starting API test execution for suite...")
    print("   - 📝 Test message: ...")
    print("   - 🤖 Calling TestGPT engine.process_test_request()...")
    print()
    print("💡 If you see these logs, the API is properly calling the TestGPT engine!")
else:
    print(f"❌ API call failed:")
    print(response.text)

db.close()
