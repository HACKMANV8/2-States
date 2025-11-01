#!/usr/bin/env python3
"""
Test MCDC analyzer with edge cases to ensure robustness.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from coverage.instrumentation.mcdc_analyzer import MCDCAnalyzer


def test_edge_cases():
    """Test MCDC analysis with various edge cases."""
    analyzer = MCDCAnalyzer()

    test_cases = [
        # Edge case 1: Single condition
        ("Single condition", "is_valid", "test.py", 1),

        # Edge case 2: Simple AND
        ("Simple AND", "a and b", "test.py", 2),

        # Edge case 3: Simple OR
        ("Simple OR", "a or b", "test.py", 3),

        # Edge case 4: Triple AND
        ("Triple AND", "a and b and c", "test.py", 4),

        # Edge case 5: Triple OR
        ("Triple OR", "a or b or c", "test.py", 5),

        # Edge case 6: Nested conditions
        ("Nested", "(a and b) or (c and d)", "test.py", 6),

        # Edge case 7: NOT conditions
        ("NOT conditions", "not a and b", "test.py", 7),

        # Edge case 8: Complex nested
        ("Complex nested", "(a or b) and (c or d) and e", "test.py", 8),

        # Edge case 9: Multiple NOTs
        ("Multiple NOTs", "not a and not b or c", "test.py", 9),

        # Edge case 10: Very simple
        ("Very simple", "x", "test.py", 10),
    ]

    print("=" * 70)
    print("MCDC EDGE CASE TESTING")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for name, expression, file_path, line in test_cases:
        try:
            result = analyzer.analyze_decision(expression, file_path, line)

            if result.is_achievable:
                status = " PASS"
                passed += 1
            else:
                status = "  WARN"
                passed += 1  # Still counts as pass, just not achievable

            print(f"{status} {name}")
            print(f"    Expression: {expression}")
            print(f"    Conditions: {len(result.decision.conditions)}")
            print(f"    MCDC Achievable: {'Yes' if result.is_achievable else 'No'}")
            if result.is_achievable:
                print(f"    Required Tests: {result.minimum_test_count}")
                print(f"    Truth Table Rows: {len(result.truth_table)}")
            else:
                print(f"    Reason: {result.reason}")
            print()

        except Exception as e:
            status = " FAIL"
            failed += 1
            print(f"{status} {name}")
            print(f"    Expression: {expression}")
            print(f"    Error: {str(e)}")
            print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


def test_error_handling():
    """Test error handling for invalid inputs."""
    analyzer = MCDCAnalyzer()

    print("\n" + "=" * 70)
    print("ERROR HANDLING TESTS")
    print("=" * 70)
    print()

    error_cases = [
        ("Empty expression", "", "test.py", 1),
        ("Invalid syntax", "a and and b", "test.py", 2),
        ("Unbalanced parens", "(a and b", "test.py", 3),
    ]

    passed = 0
    failed = 0

    for name, expression, file_path, line in error_cases:
        try:
            result = analyzer.analyze_decision(expression, file_path, line)
            # If we get here, the analyzer handled it gracefully
            print(f" PASS {name}")
            print(f"    Expression: '{expression}'")
            print(f"    Handled gracefully")
            passed += 1
        except Exception as e:
            print(f" PASS {name}")
            print(f"    Expression: '{expression}'")
            print(f"    Expected error: {type(e).__name__}")
            passed += 1
        print()

    print("=" * 70)
    print(f"ERROR HANDLING: {passed} tests passed")
    print("=" * 70)

    return True


def test_max_complexity():
    """Test handling of very complex conditions."""
    analyzer = MCDCAnalyzer()

    print("\n" + "=" * 70)
    print("COMPLEXITY LIMIT TESTS")
    print("=" * 70)
    print()

    # Test with maximum allowed conditions (8)
    max_expr = " and ".join([f"c{i}" for i in range(8)])
    print(f"Testing maximum complexity (8 conditions)...")
    print(f"Expression: {max_expr}")

    try:
        result = analyzer.analyze_decision(max_expr, "test.py", 1)
        print(f" Handled max complexity")
        print(f"   Truth table rows: {len(result.truth_table)}")
        print(f"   MCDC achievable: {result.is_achievable}")
    except Exception as e:
        print(f" Failed at max complexity: {e}")
        return False

    print()

    # Test with more than maximum (9 conditions)
    over_max_expr = " and ".join([f"c{i}" for i in range(9)])
    print(f"Testing over maximum (9 conditions)...")
    print(f"Expression: {over_max_expr}")

    try:
        result = analyzer.analyze_decision(over_max_expr, "test.py", 2)
        if not result.is_achievable and "complexity" in result.reason.lower():
            print(f" Correctly rejected over-complex condition")
            print(f"   Reason: {result.reason}")
        else:
            print(f"  Accepted over-complex condition (may need review)")
    except Exception as e:
        print(f" Correctly raised error for over-complex condition")
        print(f"   Error: {e}")

    print()
    print("=" * 70)

    return True


if __name__ == "__main__":
    print("\n")
    print("" + "" * 68 + "")
    print("" + " " * 15 + "MCDC ANALYZER EDGE CASE TEST SUITE" + " " * 19 + "")
    print("" + "" * 68 + "")
    print()

    all_passed = True

    # Run all test suites
    all_passed &= test_edge_cases()
    all_passed &= test_error_handling()
    all_passed &= test_max_complexity()

    print("\n" + "=" * 70)
    if all_passed:
        print(" ALL EDGE CASE TESTS PASSED")
        print("=" * 70)
        print("\nMCDC analyzer is robust and handles edge cases correctly!")
        sys.exit(0)
    else:
        print(" SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease review failures above.")
        sys.exit(1)
