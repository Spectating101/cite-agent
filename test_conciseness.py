#!/usr/bin/env python3
"""
Test if conciseness improvements are working
Compare response lengths before and after
"""

import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_conciseness():
    """Test if responses are now concise"""
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = [
        ("What's the difference between LSTM and GRU?", "Expected: ~100 words, with offer to expand"),
        ("I have survey data with Likert scales. What tests?", "Expected: ~50 words, direct answer"),
        ("Summarize research on transformers", "Expected: ~100 words summary + offer details"),
        ("How do I handle missing data?", "Expected: ~50 words + ask for context"),
    ]

    print("=" * 100)
    print("CONCISENESS TEST - After Adding 50-200 Word Limit")
    print("=" * 100)
    print()

    for query, expected in tests:
        print(f"\nQuery: {query}")
        print(f"Expected: {expected}")

        request = ChatRequest(
            question=query,
            user_id="concise_test",
            conversation_id="concise_conv"
        )

        response = await agent.process_request(request)

        word_count = len(response.response.split())
        char_count = len(response.response)

        print(f"✓ Word count: {word_count} words ({char_count} chars)")

        if word_count <= 200:
            print(f"✅ GOOD - Concise response")
        elif word_count <= 400:
            print(f"⚠️  OK - Slightly verbose but acceptable")
        else:
            print(f"❌ FAIL - Too verbose ({word_count} words)")

        print(f"Response: {response.response[:300]}...")
        print()

        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_conciseness())
