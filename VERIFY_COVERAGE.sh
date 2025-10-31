#!/bin/bash
# Verification script for TestGPT Coverage System
# Tests all functionality to ensure system is working

echo "========================================================================"
echo "TestGPT Coverage System - Verification Script"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Test 1: Check dependencies (only required ones)
echo "📦 Test 1: Checking required dependencies..."
python3 -c "import sqlalchemy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Required dependencies installed${NC}"
    # Check optional astor (only needed for Python < 3.9)
    python3 -c "import astor" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   astor: installed"
    else
        echo "   astor: not installed (optional - Python 3.9+ has ast.unparse built-in)"
    fi
else
    echo -e "${RED}❌ Missing required dependencies${NC}"
    echo "   Run: pip install -r coverage_requirements.txt"
    FAILED=1
fi
echo ""

# Test 2: Initialize database
echo "🗄️  Test 2: Database initialization..."
python3 coverage/cli.py init > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
    FAILED=1
fi
echo ""

# Test 3: MCDC Analysis
echo "🔍 Test 3: MCDC analysis..."
python3 coverage/cli.py analyze-mcdc examples/sample_mcdc.py > /tmp/mcdc_output.txt 2>&1
if grep -q "MCDC Achievable: ✅" /tmp/mcdc_output.txt; then
    echo -e "${GREEN}✅ MCDC analysis working${NC}"
    DECISIONS=$(grep -c "Decision [0-9]:" /tmp/mcdc_output.txt)
    echo "   Found $DECISIONS boolean decisions"
else
    echo -e "${RED}❌ MCDC analysis failed${NC}"
    FAILED=1
fi
echo ""

# Test 4: End-to-end test
echo "🧪 Test 4: End-to-end system test..."
python3 scripts/test_coverage_system.py > /tmp/e2e_output.txt 2>&1
if grep -q "ALL TESTS PASSED" /tmp/e2e_output.txt; then
    echo -e "${GREEN}✅ End-to-end test passed${NC}"
    echo "   All components functional"
else
    echo -e "${RED}❌ End-to-end test failed${NC}"
    echo "   Check /tmp/e2e_output.txt for details"
    FAILED=1
fi
echo ""

# Test 5: Database operations
echo "💾 Test 5: Database operations..."
python3 coverage/cli.py list > /tmp/db_output.txt 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database queries working${NC}"
    RUNS=$(grep -c "cov-\|test-run" /tmp/db_output.txt)
    echo "   Found $RUNS coverage runs"
else
    echo -e "${RED}❌ Database queries failed${NC}"
    FAILED=1
fi
echo ""

# Summary
echo "========================================================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL VERIFICATION TESTS PASSED${NC}"
    echo ""
    echo "The TestGPT Coverage System is fully functional!"
    echo ""
    echo "Next steps:"
    echo "  • Run: python scripts/test_coverage_system.py"
    echo "  • Run: python coverage/cli.py analyze-mcdc examples/sample_mcdc.py"
    echo "  • See: COVERAGE_EXECUTION_GUIDE.md for more details"
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please check the error messages above and:"
    echo "  1. Install dependencies: pip install -r coverage_requirements.txt"
    echo "  2. Re-run this script: ./VERIFY_COVERAGE.sh"
    echo "  3. Check logs in /tmp/*_output.txt"
fi
echo "========================================================================"

exit $FAILED
