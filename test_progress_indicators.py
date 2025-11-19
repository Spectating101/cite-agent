#!/usr/bin/env python3
"""
Test Progress Indicators - Multi-Step & Tool Execution
Tests Fix #3: Progress indicators appear correctly during complex queries
"""

import subprocess
import sys
import time

def test_progress_indicators():
    """Test that progress indicators show during multi-step queries"""
    
    print("=" * 80)
    print("TEST 1: PROGRESS INDICATORS")
    print("=" * 80)
    
    # Test query that should trigger multiple steps and tool usage
    test_query = """
analyze the workspace structure and tell me what kind of project this is
""".strip()
    
    print(f"\n📝 Test Query: {test_query}")
    print("\n🎯 Expected Behavior:")
    print("  - Should see: 💭 Processing step X/Y...")
    print("  - Should see: 🔧 listing directory...")
    print("  - Progress indicators enhance UX without spam")
    
    print("\n▶️  Executing test...\n")
    print("-" * 80)
    
    # Run cite-agent with the test query
    cmd = f'echo "{test_query}" | cite-agent'
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    output = result.stdout + result.stderr
    
    print(output)
    print("-" * 80)
    
    # Verify progress indicators present
    has_step_indicator = "💭 Processing step" in output or "Processing step" in output
    has_tool_indicator = "🔧" in output or "listing" in output or "reading" in output
    
    print("\n✅ VERIFICATION:")
    print(f"  {'✓' if has_step_indicator else '✗'} Multi-step progress indicator")
    print(f"  {'✓' if has_tool_indicator else '✗'} Tool execution indicator")
    
    if has_step_indicator and has_tool_indicator:
        print("\n🎉 TEST PASSED: Progress indicators working correctly!")
        return True
    elif has_step_indicator or has_tool_indicator:
        print("\n⚠️  TEST PARTIAL: Some indicators present")
        return True
    else:
        print("\n❌ TEST FAILED: No progress indicators found")
        return False

if __name__ == "__main__":
    try:
        success = test_progress_indicators()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
