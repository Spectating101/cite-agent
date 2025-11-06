#!/usr/bin/env python3
"""Test if clarification improvements work"""

import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_clarifications():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = [
        ("Tell me about the company", "Should ask: 'What kind of company?' or 'Which company?'"),
        ("Help me with my project", "Should ask: 'What kind of project?' with bullets"),
        ("I need help with data processing", "Should clarify what kind of data"),
    ]

    print("=" * 80)
    print("TESTING CLARIFICATION RESPONSES")
    print("=" * 80)

    for i, (query, expected) in enumerate(tests, 1):
        print(f"\n[Test {i}]")
        print(f"Query: {query}")
        print(f"Expected: {expected}")

        req = ChatRequest(
            question=query,
            user_id="test_clarif",
            conversation_id=f"clarif_{i}"
        )
        resp = await agent.process_request(req)
        print(f"Response: {resp.response}")

        # Check for good indicators
        has_what_kind = any(phrase in resp.response.lower() for phrase in [
            'what kind', 'which', 'tell me more', 'what type', 'what are you'
        ])
        has_bullets = '•' in resp.response or '-' in resp.response

        print(f"Has clarification phrases: {has_what_kind}")
        print(f"Has bullet points: {has_bullets}")

        if has_what_kind and has_bullets:
            print("✅ PASS")
        elif has_what_kind:
            print("⚠️  PASS (but no bullets)")
        else:
            print("❌ FAIL")

    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_clarifications())
