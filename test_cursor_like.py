#!/usr/bin/env python3
"""
Test Cursor-like natural language interaction.
Validates:
1. Natural language → shell command mapping (no "Run:" prefix needed)
2. Persistent working directory across commands
3. Data analysis inference
4. Fuzzy directory matching
"""

import sys
import os
import asyncio

sys.path.insert(0, '.')
os.environ['NOCTURNAL_DEBUG'] = '1'
os.environ['USE_LOCAL_KEYS'] = 'false'  # Won't use LLM, just heuristics

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest
from cite_agent.tool_executor import ToolExecutor


async def test_heuristic_patterns():
    """Test that natural language maps to shell commands without LLM calls."""
    print("\n" + "="*70)
    print("🧪 TEST 1: Natural Language → Shell Command Mapping")
    print("="*70)

    agent = EnhancedNocturnalAgent()
    agent._tool_executor = ToolExecutor(agent=agent)

    # Initialize shell session
    agent.shell_session = True  # Mock shell session existence
    agent.file_context['current_cwd'] = os.getcwd()

    test_cases = [
        ("what files", "ls"),
        ("where am i", "pwd"),
        ("go home", "cd ~"),
        ("show files in /tmp", "ls -la /tmp"),
        ("read setup.py", "cat setup.py"),
        ("git status", "git status"),
    ]

    passed = 0
    for query, expected_keyword in test_cases:
        request = ChatRequest(question=query, user_id="test")
        response = await agent._try_heuristic_shell_execution(request, debug_mode=True)

        if response:
            print(f"✅ '{query}' → Executed (tokens: {response.tokens_used})")
            passed += 1
        else:
            print(f"❌ '{query}' → Not mapped (would need LLM)")

    print(f"\nResult: {passed}/{len(test_cases)} patterns mapped (should be 6/6)")
    return passed == len(test_cases)


async def test_cwd_persistence():
    """Test that working directory persists across commands."""
    print("\n" + "="*70)
    print("🧪 TEST 2: Persistent Working Directory")
    print("="*70)

    agent = EnhancedNocturnalAgent()
    executor = ToolExecutor(agent=agent)

    # Initialize
    agent.shell_session = True
    initial_cwd = os.getcwd()
    agent.file_context['current_cwd'] = initial_cwd

    print(f"Initial CWD: {initial_cwd}")

    # Simulate cd command
    result = executor._execute_shell_command({"command": "cd /tmp"})
    new_cwd = agent.file_context.get('current_cwd', 'NOT SET')
    print(f"After 'cd /tmp': {new_cwd}")

    if new_cwd == '/tmp':
        print("✅ CWD updated to /tmp")

        # Now execute ls - should run in /tmp
        result2 = executor._execute_shell_command({"command": "ls"})
        if result2.get('working_directory') == '/tmp':
            print(f"✅ 'ls' executed in persistent CWD: {result2.get('working_directory')}")
            return True
        else:
            print(f"❌ 'ls' executed in wrong directory: {result2.get('working_directory')}")
            return False
    else:
        print(f"❌ CWD not updated (still {new_cwd})")
        return False


async def test_fuzzy_matching():
    """Test fuzzy directory matching (handles typos)."""
    print("\n" + "="*70)
    print("🧪 TEST 3: Fuzzy Directory Matching")
    print("="*70)

    # Create test directories
    test_dir = "/tmp/cite_agent_test"
    os.makedirs(f"{test_dir}/cm522-main", exist_ok=True)
    os.makedirs(f"{test_dir}/project-alpha", exist_ok=True)

    agent = EnhancedNocturnalAgent()
    executor = ToolExecutor(agent=agent)
    agent.shell_session = True
    agent.file_context['current_cwd'] = test_dir

    # Test: "cm522" should match "cm522-main"
    result = executor._execute_shell_command({"command": "cd cm522"})
    new_cwd = agent.file_context.get('current_cwd', '')

    if "cm522-main" in new_cwd:
        print(f"✅ 'cd cm522' fuzzy matched to: {new_cwd}")
        passed = True
    else:
        print(f"❌ 'cd cm522' did not match cm522-main (got: {new_cwd})")
        passed = False

    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

    return passed


async def test_data_analysis_patterns():
    """Test data analysis command mapping."""
    print("\n" + "="*70)
    print("🧪 TEST 4: Data Analysis Command Mapping")
    print("="*70)

    agent = EnhancedNocturnalAgent()
    agent._tool_executor = ToolExecutor(agent=agent)
    agent.shell_session = True
    agent.file_context['current_cwd'] = os.getcwd()

    test_cases = [
        "load sales.csv",
        "calculate statistics of data.csv",
        "analyze results.csv",
    ]

    passed = 0
    for query in test_cases:
        request = ChatRequest(question=query, user_id="test")
        response = await agent._try_heuristic_shell_execution(request, debug_mode=True)

        if response:
            print(f"✅ '{query}' → Mapped to Python (tokens: {response.tokens_used})")
            passed += 1
        else:
            print(f"❌ '{query}' → Not mapped")

    print(f"\nResult: {passed}/{len(test_cases)} analysis patterns mapped")
    return passed == len(test_cases)


async def main():
    print("="*70)
    print("🚀 CURSOR-LIKE AGENT INTEGRATION TESTS")
    print("="*70)

    results = []

    # Run tests
    results.append(("Natural Language Mapping", await test_heuristic_patterns()))
    results.append(("Persistent CWD", await test_cwd_persistence()))
    results.append(("Fuzzy Matching", await test_fuzzy_matching()))
    results.append(("Data Analysis", await test_data_analysis_patterns()))

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Agent has Cursor-like capabilities.")
    else:
        print("\n⚠️  Some tests failed. Review output above.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
