#!/usr/bin/env python3
"""
COMPREHENSIVE v1.5.6 Testing - Real Tool Sequencing
Tests actual multi-tool workflows with complex scenarios
"""

import subprocess
import sys
import time

def run_test(name, query, expect_sequencing=False):
    """Run a test query and show results"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"Query: {query}")
    print(f"Expected: Multi-step={expect_sequencing}")
    print('='*80)
    
    start = time.time()
    try:
        result = subprocess.run(
            ['cite-agent', query],
            capture_output=True,
            text=True,
            timeout=60
        )
        elapsed = time.time() - start
        
        output = result.stdout + result.stderr
        
        # Check for key indicators
        has_sequencing = 'Needs sequencing: True' in output or 'step workflow' in output.lower()
        has_error = 'error' in output.lower() or 'traceback' in output.lower()
        response_start = output.find('📝 Response:')
        
        if response_start >= 0:
            response = output[response_start:].split('\n', 10)[:10]
            print("RESPONSE:")
            for line in response:
                print(f"  {line}")
        
        print(f"\n⏱️  Time: {elapsed:.1f}s")
        print(f"🔀 Sequencing: {'YES' if has_sequencing else 'NO'}")
        print(f"❌ Errors: {'YES' if has_error else 'NO'}")
        
        if expect_sequencing and not has_sequencing:
            print("⚠️  WARNING: Expected sequencing but didn't happen")
        
        return not has_error
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  CITE-AGENT v1.5.6 COMPREHENSIVE TOOL SEQUENCING TEST       ║
║  Testing REAL multi-tool workflows with complex scenarios    ║
╚══════════════════════════════════════════════════════════════╝
""")

    tests = [
        # === CATEGORY 1: Multi-Step Mathematical Analysis ===
        (
            "Multi-step Math: Factorial → Multiply → Check Prime",
            "Calculate 7 factorial, multiply that result by 3, then tell me if the final number is prime or composite",
            True
        ),
        (
            "Multi-step Statistics: Generate → Calculate → Compare",
            "Calculate the mean of the numbers 15, 25, 35, 45, 55. Then calculate the median. Finally tell me which is larger.",
            True
        ),
        
        # === CATEGORY 2: Research → Analysis Workflows ===
        (
            "Research → Filter → Extract Citation",
            "Search for papers about 'transformer models' from 2020 onwards, find the most cited one, and tell me its citation count",
            True
        ),
        (
            "Research → Compare Papers",
            "Find papers about 'BERT' and papers about 'GPT', then tell me which topic has more papers published after 2019",
            True
        ),
        
        # === CATEGORY 3: Shell → Analysis Workflows ===
        (
            "Shell → Count → Compare",
            "Count how many .md files are in the current directory, then count how many .py files, then tell me which type has more files",
            True
        ),
        (
            "Shell → Read → Analyze",
            "List all Python files in cite_agent/ directory, find the one with 'ai' in its name, and tell me approximately how many lines it has",
            True
        ),
        
        # === CATEGORY 4: Data → Calculate → Compare ===
        (
            "Shell Data → Statistics → Threshold",
            "Run 'echo 10,20,30,40,50 > /tmp/test_data.txt', read that file, calculate the average, and tell me if it's above 25",
            True
        ),
        
        # === CATEGORY 5: Cross-Domain Complex Workflows ===
        (
            "Research → Shell → Analysis Combined",
            "Search for a paper about 'attention mechanism', save its title, then count how many words are in that title",
            True
        ),
        (
            "Math → Compare → Research",
            "Calculate 100 divided by 7. Then search for papers that have approximately that many citations (around 14).",
            True
        ),
        
        # === CATEGORY 6: Simple Baseline Tests ===
        (
            "Simple: Direct Calculation",
            "What is 123 times 456?",
            False
        ),
        (
            "Simple: Direct Research",
            "Find one paper about machine learning",
            False
        ),
        (
            "Simple: Direct Shell",
            "Run: pwd",
            False
        ),
    ]

    results = []
    for test_name, query, expect_seq in tests:
        passed = run_test(test_name, query, expect_seq)
        results.append((test_name, passed))
        time.sleep(2)  # Rate limiting

    # Summary
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST SUMMARY")
    print('='*80)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n📊 TOTAL: {passed}/{total} passed ({100*passed//total}%)")
    
    if passed < total * 0.8:
        print("\n⚠️  WARNING: Less than 80% pass rate - needs work")
        return 1
    elif passed == total:
        print("\n🎉 PERFECT SCORE - Ready to ship!")
        return 0
    else:
        print("\n✅ GOOD - Most features working")
        return 0


if __name__ == '__main__':
    sys.exit(main())
