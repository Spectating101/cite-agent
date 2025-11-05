#!/usr/bin/env python3
"""
Test current agent behavior - verify bugs before fixing
Tests directory navigation and location queries
"""

import asyncio
import sys
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_agent_behavior():
    """Test various queries to identify current issues"""

    print("=" * 70)
    print("🧪 TESTING CURRENT AGENT BEHAVIOR")
    print("=" * 70)
    print()

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Test cases that should reveal bugs
    test_cases = [
        {
            "name": "Simple location query (should work)",
            "query": "where am I?",
            "expected": "Should return current directory (pwd)",
            "bug": None
        },
        {
            "name": "Location query - 'pwd' command",
            "query": "pwd",
            "expected": "Should return current directory",
            "bug": None
        },
        {
            "name": "BUG: File listing with 'current directory'",
            "query": "list files in current directory",
            "expected": "Should run 'ls' and show files",
            "bug": "Currently returns pwd instead (wrong!)"
        },
        {
            "name": "BUG: Show Python files",
            "query": "show me Python files in current directory",
            "expected": "Should run 'find . -name \"*.py\"' or 'ls *.py'",
            "bug": "May return pwd or require auth (wrong!)"
        },
        {
            "name": "File search",
            "query": "find files named test",
            "expected": "Should run 'find' command",
            "bug": "May require backend auth (unnecessary)"
        },
        {
            "name": "Navigate directory",
            "query": "cd cite_agent",
            "expected": "Should change directory",
            "bug": None
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_cases)}: {test['name']}")
        print(f"{'='*70}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected: {test['expected']}")
        if test['bug']:
            print(f"⚠️  Known Bug: {test['bug']}")
        print()

        try:
            request = ChatRequest(
                question=test['query'],
                user_id="test_user",
                conversation_id="test_conversation"
            )

            # Check if query triggers _is_location_query (the buggy function)
            is_location = agent._is_location_query(test['query'])
            print(f"🔍 _is_location_query() returns: {is_location}")

            # Check query classification
            from cite_agent.adaptive_providers import QueryType
            query_type = agent._classify_query_type(test['query'])
            print(f"🏷️  _classify_query_type() returns: {query_type.value}")

            print()
            print("Waiting for response...")
            response = await agent.process_request(request)

            print(f"✅ Response received:")
            print(f"   {response.response[:200]}")
            if len(response.response) > 200:
                print(f"   ... (truncated)")
            print(f"   Tools used: {response.tools_used}")

            results.append({
                "test": test['name'],
                "query": test['query'],
                "is_location": is_location,
                "query_type": query_type.value,
                "response": response.response[:100],
                "tools": response.tools_used,
                "error": response.error_message
            })

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "test": test['name'],
                "query": test['query'],
                "error": str(e)
            })

        print()
        await asyncio.sleep(1)  # Brief pause between tests

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['test']}")
        print(f"   Query: \"{result['query']}\"")
        if 'is_location' in result:
            print(f"   Location query: {result['is_location']}")
            print(f"   Query type: {result['query_type']}")
        if 'response' in result:
            print(f"   Response: {result['response']}")
        if result.get('error'):
            print(f"   ❌ Error: {result['error']}")

    print("\n" + "=" * 70)
    print("🎯 KEY FINDINGS")
    print("=" * 70)

    # Analyze results for bugs
    bugs_found = []

    # Check if "list files in current directory" triggers location query (BUG)
    test3 = results[2] if len(results) > 2 else None
    if test3 and test3.get('is_location'):
        bugs_found.append("🐛 BUG CONFIRMED: 'list files in current directory' triggers _is_location_query() (should be False)")

    # Check if file operations require auth (BUG)
    for result in results:
        if result.get('error') and 'authentication' in result['error'].lower():
            bugs_found.append(f"🐛 BUG CONFIRMED: '{result['query']}' requires auth (should be local-only)")

    if bugs_found:
        print("\n❌ Bugs Found:")
        for bug in bugs_found:
            print(f"   {bug}")
    else:
        print("\n✅ No bugs detected in these tests!")

    print("\n" + "=" * 70)
    print("✅ Testing complete!")
    print("=" * 70)
    print()

if __name__ == "__main__":
    try:
        asyncio.run(test_agent_behavior())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
