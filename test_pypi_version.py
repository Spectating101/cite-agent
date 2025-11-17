#!/usr/bin/env python3
"""
Test cite-agent v1.4.5 installed from PyPI (NOT local source).

This test validates the ACTUAL PRODUCTION package.
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# CRITICAL: Do NOT use local source - use pip-installed package
# Remove current directory from path to ensure we use PyPI version
if '.' in sys.path:
    sys.path.remove('.')
if os.getcwd() in sys.path:
    sys.path.remove(os.getcwd())

# Enable function calling mode
os.environ["NOCTURNAL_FUNCTION_CALLING"] = "1"
os.environ["NOCTURNAL_DEBUG"] = "0"

# Import from pip-installed package
from cite_agent import EnhancedNocturnalAgent, ChatRequest, __version__


async def run_pypi_tests():
    """Run tests using PyPI-installed cite-agent."""

    print("=" * 70)
    print("CITE-AGENT PyPI VERSION TEST")
    print(f"Package version: {__version__}")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 70)

    if __version__ != "1.4.5":
        print(f"❌ ERROR: Expected version 1.4.5, got {__version__}")
        print("   Please run: pip install --upgrade cite-agent==1.4.5")
        return

    print(f"✅ Using cite-agent {__version__} from PyPI")

    # Initialize agent
    print("\n🚀 Initializing agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    print(f"✅ Agent initialized")
    print(f"   LLM Provider: {getattr(agent, 'llm_provider', 'unknown')}")

    # Test cases - same as before
    test_cases = [
        {
            "name": "File Listing",
            "query": "what files are here?",
            "expected_tool": "list_directory"
        },
        {
            "name": "Conversational",
            "query": "thanks",
            "expected_tool": "chat"
        },
        {
            "name": "Load CSV",
            "query": "load data/test_stats.csv",
            "expected_tool": "load_dataset"
        },
        {
            "name": "Statistics Query",
            "query": "what's the mean spread?",
            "expected_tool": "analyze_data"
        },
        {
            "name": "Paper Search",
            "query": "find papers on BERT transformers",
            "expected_tool": "search_papers"
        },
    ]

    results = []
    total_tokens = 0

    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)

    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test['name']} ---")
        print(f"Query: {test['query']}")

        try:
            response = await agent.process_request(ChatRequest(
                question=test['query'],
                user_id="pypi_test",
                conversation_id="pypi_session"
            ))

            tools = response.tools_used
            tokens = response.tokens_used
            total_tokens += tokens

            # Check if expected tool was called
            tool_match = test['expected_tool'] in tools
            status = "✅" if tool_match else "⚠️"

            print(f"Tools: {tools}")
            print(f"Tokens: {tokens}")
            print(f"{status} Expected '{test['expected_tool']}': {'PASS' if tool_match else 'FAIL'}")

            # Show response preview
            resp_preview = response.response[:200] + "..." if len(response.response) > 200 else response.response
            print(f"Response: {resp_preview}")

            results.append({
                "test": test['name'],
                "query": test['query'],
                "expected": test['expected_tool'],
                "actual": tools,
                "tokens": tokens,
                "pass": tool_match
            })

            await asyncio.sleep(1)  # Rate limit

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "test": test['name'],
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results if r.get('pass', False))
    failed = len(results) - passed

    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Cost: ${total_tokens * 0.60 / 1_000_000:.4f} ({total_tokens * 0.60 / 1_000_000 * 100:.2f} cents)")

    if passed == len(test_cases):
        print("\n🎉 ALL TESTS PASS! PyPI version is production-ready!")
    else:
        print(f"\n⚠️ {failed} test(s) need attention")

    # Save results
    with open("pypi_test_results.json", "w") as f:
        json.dump({
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
            "total_tokens": total_tokens,
            "cost_usd": total_tokens * 0.60 / 1_000_000,
            "results": results
        }, f, indent=2)
    print(f"\n✅ Results saved to pypi_test_results.json")

    await agent.close()
    print("✅ Agent closed")


if __name__ == "__main__":
    print("Testing cite-agent from PyPI (not local source)...")
    asyncio.run(run_pypi_tests())
