#!/usr/bin/env python3
"""
Test selective routing: Research → FC, Financial → Traditional
"""

import asyncio
import os

os.environ['NOCTURNAL_DEBUG'] = '1'
os.environ['USE_LOCAL_KEYS'] = 'true'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


async def test_routing():
    print("="*100)
    print("TESTING SELECTIVE ROUTING")
    print("="*100)

    print("\n" + "="*100)
    print("TEST 1: RESEARCH QUERY (Should use Function Calling)")
    print("="*100)

    agent1 = EnhancedNocturnalAgent()
    request1 = ChatRequest(question="Find papers on vision transformers")

    try:
        print("\nExecuting research query...")
        response1 = await agent1.process_request(request1)

        print(f"\n✅ RESEARCH QUERY RESULT:")
        print(f"  Response length: {len(response1.response)} chars")
        print(f"  Tokens: {response1.tokens_used}")
        print(f"  Tools: {response1.tools_used}")
        print(f"\n  Response preview:\n{response1.response[:500]}...")

    except Exception as e:
        print(f"\n❌ RESEARCH QUERY FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*100)
    print("TEST 2: FINANCIAL QUERY (Should use Traditional)")
    print("="*100)

    agent2 = EnhancedNocturnalAgent()
    request2 = ChatRequest(question="What is Apple's profit margin?")

    try:
        print("\nExecuting financial query...")
        response2 = await agent2.process_request(request2)

        print(f"\n✅ FINANCIAL QUERY RESULT:")
        print(f"  Response length: {len(response2.response)} chars")
        print(f"  Tokens: {response2.tokens_used}")
        print(f"  Tools: {response2.tools_used}")
        print(f"\n  Response preview:\n{response2.response[:500]}...")

    except Exception as e:
        print(f"\n❌ FINANCIAL QUERY FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*100)
    print("TEST 3: SIMPLE FILE QUERY (Should use Function Calling)")
    print("="*100)

    agent3 = EnhancedNocturnalAgent()
    request3 = ChatRequest(question="list files in the cite_agent directory")

    try:
        print("\nExecuting file query...")
        response3 = await agent3.process_request(request3)

        print(f"\n✅ FILE QUERY RESULT:")
        print(f"  Response length: {len(response3.response)} chars")
        print(f"  Tokens: {response3.tokens_used}")
        print(f"  Tools: {response3.tools_used}")
        print(f"\n  Response preview:\n{response3.response[:300]}...")

    except Exception as e:
        print(f"\n❌ FILE QUERY FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*100)
    print("SELECTIVE ROUTING TEST COMPLETE")
    print("="*100)


if __name__ == "__main__":
    asyncio.run(test_routing())
