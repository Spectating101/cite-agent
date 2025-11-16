#!/usr/bin/env python3
"""
Test natural language → shell heuristics (0-token execution).
Tests the _try_heuristic_shell_execution method.
"""

import asyncio
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["NOCTURNAL_FUNCTION_CALLING"] = "1"
os.environ["NOCTURNAL_DEBUG"] = "1"

from cite_agent import EnhancedNocturnalAgent, ChatRequest


async def test_heuristics():
    agent = EnhancedNocturnalAgent()

    print("=" * 60)
    print("NATURAL LANGUAGE → SHELL HEURISTICS (0-TOKEN TESTS)")
    print("=" * 60)

    # Initialize shell session manually
    agent.shell_session = subprocess.Popen(
        ['bash'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=os.path.expanduser("~/Downloads")
    )

    # Initialize file context
    agent.file_context = {
        'last_file': None,
        'last_directory': None,
        'recent_files': [],
        'recent_dirs': [],
        'current_cwd': os.path.expanduser("~/Downloads"),
    }

    # Initialize tool executor
    from cite_agent.tool_executor import ToolExecutor
    agent._tool_executor = ToolExecutor(agent)
    agent._tool_executor.debug_mode = True

    test_cases = [
        # (input, expected_pattern, should_match)
        ("what files", "ls", True),
        ("what's here", "ls", True),
        ("show files", "ls", True),
        ("list directory", "ls", True),
        ("where am i", "pwd", True),
        ("go to downloads", "cd", True),
        ("go home", "cd", True),
        ("go back", "cd ..", True),
        ("read setup.py", "cat", True),
        ("show me the readme", "cat", True),
        # These should NOT match heuristics (need LLM)
        ("explain the code structure", None, False),
        ("what does this function do", None, False),
    ]

    passed = 0
    failed = 0

    for query, expected_pattern, should_match in test_cases:
        print(f"\nTest: '{query}'")
        print(f"  Expected: {'Match → ' + expected_pattern if should_match else 'No match (LLM fallback)'}")

        request = ChatRequest(question=query, user_id="test")

        # Call the heuristic method directly
        result = await agent._try_heuristic_shell_execution(request, debug_mode=True)

        if should_match:
            if result is not None:
                print(f"  Result: ✅ MATCHED - tokens={result.tokens_used}")
                if result.tokens_used == 0:
                    print(f"  ✅ Zero tokens used!")
                    passed += 1
                else:
                    print(f"  ⚠️  Used {result.tokens_used} tokens (expected 0)")
                    failed += 1
                # Show first 100 chars of response
                print(f"  Response: {result.response[:100]}...")
            else:
                print(f"  Result: ❌ FAIL - No match (expected to match '{expected_pattern}')")
                failed += 1
        else:
            if result is None:
                print(f"  Result: ✅ Correctly returned None (LLM fallback)")
                passed += 1
            else:
                print(f"  Result: ⚠️  Unexpected match (expected LLM fallback)")
                print(f"  Response: {result.response[:100]}...")
                failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)

    # Cleanup
    if agent.shell_session:
        agent.shell_session.terminate()

    return passed, failed


if __name__ == "__main__":
    passed, failed = asyncio.run(test_heuristics())
    sys.exit(0 if failed == 0 else 1)
