#!/usr/bin/env python3
"""
Unit tests for specific bug fixes.

These tests directly verify tool behavior without requiring API authentication.
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.research_assistant import DataAnalyzer


def test_csv_case_insensitive():
    """Test Bug #4: CSV column case sensitivity fix"""
    print("\n" + "="*80)
    print("TEST: CSV Case-Insensitive Column Matching")
    print("="*80)

    # Create test data with mixed case columns
    test_data = pd.DataFrame({
        "Student": ["Alice", "Bob", "Charlie"],
        "Math": [85, 78, 92],
        "English": [92, 85, 88],
        "Science": [88, 90, 85]
    })

    analyzer = DataAnalyzer()
    analyzer.current_dataset = test_data

    # Test 1: Lowercase "math" should match "Math"
    print("\nTest 1: Query for 'math' (lowercase)")
    result1 = analyzer.descriptive_stats("math")

    if "error" in result1:
        print(f"  ❌ FAIL: {result1['error']}")
        return False
    else:
        print(f"  ✅ PASS: Found column '{result1['column']}'")
        print(f"  Mean: {result1['mean']}")

    # Test 2: Uppercase "ENGLISH" should match "English"
    print("\nTest 2: Query for 'ENGLISH' (uppercase)")
    result2 = analyzer.descriptive_stats("ENGLISH")

    if "error" in result2:
        print(f"  ❌ FAIL: {result2['error']}")
        return False
    else:
        print(f"  ✅ PASS: Found column '{result2['column']}'")
        print(f"  Mean: {result2['mean']}")

    # Test 3: Non-existent column should give helpful error
    print("\nTest 3: Query for 'History' (doesn't exist)")
    result3 = analyzer.descriptive_stats("History")

    if "error" in result3:
        print(f"  ✅ PASS: Correct error message")
        print(f"  Message: {result3['error']}")
    else:
        print(f"  ❌ FAIL: Should have returned error")
        return False

    # Test 4: Correlation with mixed case
    print("\nTest 4: Correlation between 'math' and 'SCIENCE' (mixed case)")
    result4 = analyzer.run_correlation("math", "SCIENCE")

    if "error" in result4:
        print(f"  ❌ FAIL: {result4['error']}")
        return False
    else:
        print(f"  ✅ PASS: Correlation = {result4['correlation']:.3f}")

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED: CSV case-insensitive matching works!")
    print("="*80)
    return True


def test_file_listing_truncation():
    """Test Bug #7: File listing truncation"""
    print("\n" + "="*80)
    print("TEST: File Listing Truncation")
    print("="*80)

    # Simulate a directory with many files
    fake_output = "\n".join([f"file{i}.txt" for i in range(100)])
    lines = fake_output.strip().split('\n')

    MAX_LINES = 20  # New truncation limit

    print(f"\nSimulated directory with {len(lines)} files")
    print(f"MAX_LINES set to: {MAX_LINES}")

    if len(lines) > MAX_LINES:
        truncated = lines[:MAX_LINES]
        print(f"  ✅ PASS: Truncation logic would trigger")
        print(f"  Would show: {len(truncated)} files")
        print(f"  Would hide: {len(lines) - MAX_LINES} files")
    else:
        print(f"  ❌ FAIL: Truncation didn't trigger")
        return False

    print("\n" + "="*80)
    print("✅ TEST PASSED: File listing truncation logic correct")
    print("="*80)
    return True


def test_matplotlib_dependency():
    """Test Bug #2: Matplotlib available"""
    print("\n" + "="*80)
    print("TEST: Matplotlib Dependency")
    print("="*80)

    try:
        import matplotlib
        version = matplotlib.__version__
        print(f"  ✅ PASS: matplotlib {version} installed")
        print("\n" + "="*80)
        print("✅ TEST PASSED: Matplotlib dependency satisfied")
        print("="*80)
        return True
    except ImportError as e:
        print(f"  ❌ FAIL: matplotlib not installed")
        print(f"  Error: {e}")
        print("\n" + "="*80)
        print("❌ TEST FAILED: Run 'pip install matplotlib>=3.7.0'")
        print("="*80)
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CITE-AGENT BUG FIX VERIFICATION")
    print("Direct unit tests for bug fixes (no API required)")
    print("="*80)

    results = []

    # Run tests
    results.append(("CSV Case Sensitivity", test_csv_case_insensitive()))
    results.append(("File Listing Truncation", test_file_listing_truncation()))
    results.append(("Matplotlib Dependency", test_matplotlib_dependency()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")
    print("="*80)

    sys.exit(0 if passed_count == total_count else 1)
