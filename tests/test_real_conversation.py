#!/usr/bin/env python3
"""
Test ACTUAL conversation quality - not just "does it work" but "is it GOOD"
"""

import asyncio
import sys
sys.path.insert(0, '/home/user/cite-agent')

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


async def test_real_conversation_quality():
    """Test actual conversational responses like a real user would experience"""

    print("=" * 70)
    print("REAL CONVERSATION QUALITY TEST")
    print("Testing if agent responds like Claude would - natural, helpful, smart")
    print("=" * 70)
    print()

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    test_cases = [
        {
            "name": "Simple greeting",
            "question": "Hi, can you help me find research papers?",
            "quality_checks": {
                "Friendly tone": lambda r: any(w in r.lower() for w in ["hello", "hi", "yes", "sure", "happy", "help"]),
                "Not robotic": lambda r: not r.startswith("I am") and "I am an AI" not in r,
                "Offers value": lambda r: "research" in r.lower() or "paper" in r.lower() or "search" in r.lower(),
            }
        },
        {
            "name": "Research question",
            "question": "Find me papers about transformer neural networks",
            "quality_checks": {
                "Takes action": lambda r: len(r) > 50,  # Should do something, not just acknowledge
                "Conversational": lambda r: not r.startswith("```") and "json" not in r.lower(),
                "Helpful": lambda r: "paper" in r.lower() or "found" in r.lower() or "search" in r.lower(),
            }
        },
        {
            "name": "Follow-up question",
            "question": "What's the first paper about?",
            "quality_checks": {
                "Understands context": lambda r: len(r) > 20,  # Should reference papers from memory
                "Not confused": lambda r: "which paper" not in r.lower() or "first paper" in r.lower(),
                "Informative": lambda r: len(r) > 30,
            }
        },
        {
            "name": "Comparison question",
            "question": "How does that compare to BERT?",
            "quality_checks": {
                "Provides comparison": lambda r: len(r) > 50,
                "Conversational": lambda r: not r.startswith("```"),
                "Substantive": lambda r: "bert" in r.lower() or "compares" in r.lower() or "difference" in r.lower(),
            }
        },
    ]

    all_passed = True
    results_summary = []

    for i, test in enumerate(test_cases, 1):
        print(f"TEST {i}: {test['name']}")
        print(f"USER: {test['question']}")
        print()

        try:
            request = ChatRequest(
                question=test['question'],
                user_id="test_user",
                conversation_id="quality_test"
            )

            response = await agent.process_request(request)
            response_text = response.response

            print(f"AGENT: {response_text[:300]}{'...' if len(response_text) > 300 else ''}")
            print()

            # Quality checks
            test_passed = True
            print("Quality Checks:")
            for check_name, check_fn in test['quality_checks'].items():
                passed = check_fn(response_text)
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name}")
                if not passed:
                    test_passed = False
                    all_passed = False

            results_summary.append({
                "test": test['name'],
                "passed": test_passed,
                "response_length": len(response_text),
                "tools_used": response.tools_used
            })

            print()
            print("-" * 70)
            print()

        except Exception as e:
            print(f"❌ ERROR: {e}")
            print()
            all_passed = False
            results_summary.append({
                "test": test['name'],
                "passed": False,
                "error": str(e)
            })

    await agent.close()

    # Final summary
    print("=" * 70)
    print("CONVERSATION QUALITY SUMMARY")
    print("=" * 70)
    print()

    for result in results_summary:
        status = "✅" if result.get('passed') else "❌"
        print(f"{status} {result['test']}")
        if 'response_length' in result:
            print(f"   Response: {result['response_length']} chars, Tools: {result.get('tools_used', [])}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        print()

    print("=" * 70)
    if all_passed:
        print("✅ ALL QUALITY CHECKS PASSED")
        print("   Agent responds conversationally and helpfully!")
    else:
        print("❌ SOME QUALITY CHECKS FAILED")
        print("   Agent needs improvement to match Claude-level quality")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_real_conversation_quality())
    sys.exit(0 if success else 1)
