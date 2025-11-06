#!/usr/bin/env python3
"""Test if missing data false clarification is fixed"""

import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_missing_data():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    queries = [
        "I have missing data. How should I handle it for my analysis?",
        "My study has missing data at follow-up. What should I do?",
        "How do I handle missing values in my dataset?",
    ]

    print("=" * 100)
    print("TESTING MISSING DATA QUERIES - Should NOT get false clarification")
    print("=" * 100)
    print()

    for query in queries:
        print(f"Query: {query}")

        request = ChatRequest(
            question=query,
            user_id="missing_test",
            conversation_id="missing_conv"
        )

        response = await agent.process_request(request)

        is_clarification = 'clarification' in response.tools_used if response.tools_used else False
        asks_what_kind = "what kind of analysis" in response.response.lower()

        if is_clarification or asks_what_kind:
            print(f"❌ FAIL - False clarification triggered")
            print(f"   Tools: {response.tools_used}")
            print(f"   Response: {response.response[:200]}")
        else:
            print(f"✅ PASS - Direct answer ({len(response.response.split())} words)")
            print(f"   Response: {response.response[:200]}...")

        print()
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_missing_data())
