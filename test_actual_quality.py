#!/usr/bin/env python3
"""
Test ACTUAL response quality - not keyword matching
Human judgment required on outputs
"""

import asyncio
import os
import sys

os.environ['NOCTURNAL_DEBUG'] = '1'
os.environ['USE_LOCAL_KEYS'] = 'true'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_query(query: str, description: str):
    """Run a query and print the FULL response for human evaluation"""
    print(f"\n{'='*80}")
    print(f"TEST: {description}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")

    agent = EnhancedNocturnalAgent()
    request = ChatRequest(question=query)

    try:
        response = await agent.process_request(request)

        print(f"\n📊 METADATA:")
        print(f"Tokens used: {response.tokens_used}")
        print(f"Tools used: {response.tools_used}")

        print(f"\n💬 FULL RESPONSE:")
        print(response.response)

        print(f"\n" + "="*80)
        return response

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    print("🧪 ACTUAL QUALITY TEST - Human Evaluation Required")
    print("This test shows FULL responses for manual quality assessment")
    print("")

    # Test 1: Research query
    await test_query(
        "Find papers on vision transformers",
        "Research Query - Should show papers with citations"
    )

    # Test 2: Financial query
    await test_query(
        "What is Apple's profit margin?",
        "Financial Query - Should calculate margin cleanly"
    )

    # Test 3: Comparative research
    await test_query(
        "Compare BERT and GPT-3 approaches",
        "Comparative Research - Should synthesize differences"
    )

    print("\n" + "="*80)
    print("EVALUATE THE RESPONSES ABOVE:")
    print("1. Are research responses helpful and well-cited?")
    print("2. Are financial responses clean with correct calculations?")
    print("3. Is synthesis intelligent or just listing?")
    print("4. Any JSON leaking or formatting issues?")
    print("5. Token usage reasonable for complexity?")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
