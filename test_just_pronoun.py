#!/usr/bin/env python3
"""Test just the pronoun resolution tests from comprehensive suite"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Run test 5 times to check for flakiness
    for i in range(5):
        print(f"\n{'='*80}")
        print(f"RUN {i+1}/5")
        print('='*80)

        conv_id = f"conv_pronoun_{i}"

        # Turn 1
        req1 = ChatRequest(
            question="What Python files are in this directory?",
            user_id="test_pronoun",
            conversation_id=conv_id
        )
        resp1 = await agent.process_request(req1)
        print(f"Q1: {req1.question}")
        print(f"A1: {resp1.response[:100]}...")

        # Turn 2 - pronoun follow up
        req2 = ChatRequest(
            question="How many did you find?",
            user_id="test_pronoun",
            conversation_id=conv_id
        )
        resp2 = await agent.process_request(req2)
        print(f"\nQ2: {req2.question}")
        print(f"A2: {resp2.response}")

        # Check if it's the generic error
        if "I'm having trouble processing that" in resp2.response:
            print("❌ FAIL: Generic error response")
            if resp2.error_message:
                print(f"   Error: {resp2.error_message}")
        else:
            print("✅ PASS: Resolved pronoun")

    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test())
