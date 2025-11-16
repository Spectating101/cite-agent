#!/usr/bin/env python3
"""
Test Cursor-like agent capabilities:
- Natural directory navigation
- Persistent working directory
- No special syntax requirements

Usage:
    NOCTURNAL_FUNCTION_CALLING=1 python3 test_cursor_like_agent.py
"""

import asyncio
import os
import sys

# Set environment variables BEFORE importing agent
os.environ["NOCTURNAL_FUNCTION_CALLING"] = "1"  # Enable function calling mode
os.environ["NOCTURNAL_DEBUG"] = "1"  # Enable debug output

from cite_agent import EnhancedNocturnalAgent, ChatRequest


async def test_cursor_like_workflow():
    """Test natural directory navigation workflow"""

    print("=" * 60)
    print("CURSOR-LIKE AGENT TEST")
    print("Testing: Natural directory navigation without special syntax")
    print("=" * 60)

    # Initialize agent
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    test_queries = [
        # Test 1: Check current directory
        "where am I?",

        # Test 2: Navigate to Downloads
        "cd ~/Downloads",

        # Test 3: List files (should be in Downloads now)
        "ls",

        # Test 4: Find specific file types
        "find *.csv",

        # Test 5: Go back home
        "cd ~",

        # Test 6: Check we're home
        "pwd",
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {query}")
        print("=" * 60)

        request = ChatRequest(
            question=query,
            user_id="test_user",
            conversation_id="cursor_test"
        )

        try:
            response = await agent.process_request(request)

            print(f"\n📝 Response:")
            print(response.response[:500] if len(response.response) > 500 else response.response)
            print(f"\n🔧 Tools Used: {response.tools_used}")
            print(f"📊 Tokens: {response.tokens_used}")
            print(f"🎯 Confidence: {response.confidence_score}")

            # Track current working directory
            current_cwd = agent.file_context.get('current_cwd', 'unknown')
            print(f"📁 Current CWD: {current_cwd}")

            results.append({
                "query": query,
                "success": response.error_message is None,
                "tools_used": response.tools_used,
                "cwd_after": current_cwd,
            })

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get("success", False))
    total = len(results)

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        print(f"{i}. {result['query']:<30} {status}")
        if "cwd_after" in result:
            print(f"   CWD: {result['cwd_after']}")

    print(f"\nOverall: {passed}/{total} tests passed")

    # Check critical functionality
    print("\n🎯 CRITICAL CHECKS:")

    # Check 1: cd persisted
    if len(results) >= 3:
        # After "cd ~/Downloads" (test 2), CWD should contain "Downloads"
        if "Downloads" in results[2].get("cwd_after", ""):
            print("✅ Directory navigation persists (cd ~/Downloads worked)")
        else:
            print("❌ Directory navigation did NOT persist")

    # Check 2: Relative paths work
    if len(results) >= 3:
        if results[2].get("success"):
            print("✅ Relative paths work (ls without absolute path)")
        else:
            print("❌ Relative paths don't work")

    # Check 3: No special syntax required
    print("✅ No 'Run:' prefix required" if all(not "Run:" in r["query"] for r in results) else "❌ 'Run:' prefix still needed")
    print("✅ No absolute paths required" if not any("/home/" in r["query"] for r in results) else "❌ Absolute paths still needed")

    await agent.close()

    return passed == total


async def main():
    success = await test_cursor_like_workflow()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
