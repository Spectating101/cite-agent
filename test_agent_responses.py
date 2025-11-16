#!/usr/bin/env python3
"""
Test script to evaluate agent response quality.
Tests the recent changes: fuzzy directory matching, persistent CWD, data analysis.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cite_agent import EnhancedNocturnalAgent, ChatRequest

# Enable function calling mode
os.environ["NOCTURNAL_FUNCTION_CALLING"] = "1"
os.environ["NOCTURNAL_DEBUG"] = "1"


async def test_agent():
    agent = EnhancedNocturnalAgent()

    print("=" * 60)
    print("CITE-AGENT RESPONSE QUALITY TESTS")
    print("=" * 60)

    # Initialize shell session manually (without full API auth)
    import subprocess
    agent.shell_session = subprocess.Popen(
        ['bash'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=os.path.expanduser("~/Downloads")
    )

    from cite_agent.tool_executor import ToolExecutor

    executor = ToolExecutor(agent)
    executor.debug_mode = True

    # Initialize file context
    agent.file_context = {
        'last_file': None,
        'last_directory': None,
        'recent_files': [],
        'recent_dirs': [],
        'current_cwd': os.path.expanduser("~/Downloads"),
    }

    print("\n" + "=" * 60)
    print("TEST 1: FUZZY DIRECTORY MATCHING")
    print("=" * 60)
    print("Input: cd cm 522")
    print("Expected: Should match 'cm522-main' directory")
    print()

    result = await executor.execute_tool("execute_shell_command", {"command": "cd cm 522"})
    print(f"Result: {result}")
    print(f"Current CWD after: {agent.file_context.get('current_cwd')}")

    if "cm522-main" in str(agent.file_context.get('current_cwd', '')):
        print("✅ PASS: Fuzzy matching worked!")
    else:
        print("❌ FAIL: Did not match cm522-main")

    print("\n" + "=" * 60)
    print("TEST 2: PERSISTENT CWD - RELATIVE PATH")
    print("=" * 60)
    print("Input: ls *.csv (should use current cwd from test 1)")
    print()

    result = await executor.execute_tool("list_directory", {"path": "."})
    print(f"Result (first 500 chars): {str(result)[:500]}")

    if "csv" in str(result).lower():
        print("✅ PASS: Found CSV files in cm522-main!")
    else:
        print("⚠️  Check: No CSV files found in listing")

    print("\n" + "=" * 60)
    print("TEST 3: DATA ANALYSIS - LOAD CSV WITH STATS")
    print("=" * 60)
    print("Input: Load ivol_summary_results.csv")
    print("Expected: Should show actual computed statistics")
    print()

    # Reset to cm522-main if needed
    agent.file_context['current_cwd'] = os.path.expanduser("~/Downloads/cm522-main")

    result = await executor.execute_tool("load_dataset", {"filepath": "ivol_summary_results.csv"})
    print(f"Result: {result}")

    if "column_statistics" in result or "mean" in str(result):
        print("✅ PASS: Statistics computed!")
    else:
        print("⚠️  Check: Statistics may not be computed")

    print("\n" + "=" * 60)
    print("TEST 4: ANOTHER FUZZY MATCH")
    print("=" * 60)
    agent.file_context['current_cwd'] = os.path.expanduser("~/Downloads")
    print("Input: cd code slides ivol")
    print("Expected: Should match 'Code and Slides IVOL' directory")
    print()

    result = await executor.execute_tool("execute_shell_command", {"command": "cd code slides ivol"})
    print(f"Result: {result}")
    print(f"Current CWD after: {agent.file_context.get('current_cwd')}")

    if "Code and Slides IVOL" in str(agent.file_context.get('current_cwd', '')):
        print("✅ PASS: Fuzzy matching with spaces worked!")
    else:
        print("❌ FAIL: Did not match 'Code and Slides IVOL'")

    print("\n" + "=" * 60)
    print("TEST 5: BACK NAVIGATION")
    print("=" * 60)
    print("Input: cd ..")
    print()

    result = await executor.execute_tool("execute_shell_command", {"command": "cd .."})
    print(f"Result: {result}")
    print(f"Current CWD after: {agent.file_context.get('current_cwd')}")

    if agent.file_context.get('current_cwd', '').endswith("/Downloads"):
        print("✅ PASS: Back navigation works!")
    else:
        print("⚠️  Check current directory")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("These tests verify:")
    print("1. Fuzzy directory matching handles typos/spacing")
    print("2. Persistent CWD allows natural file navigation")
    print("3. Data loading computes actual statistics")
    print("4. Shell commands maintain state across calls")
    print()
    print("For full integration tests with LLM synthesis,")
    print("run: python3 -m cite_agent (requires API auth)")


if __name__ == "__main__":
    asyncio.run(test_agent())
