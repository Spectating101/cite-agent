#!/usr/bin/env python3
"""
Diagnostic test for pronoun resolution failures
"""

import asyncio
import sys
import logging
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

async def test_pronoun_resolution():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("=" * 80)
    print("TESTING PRONOUN RESOLUTION")
    print("=" * 80)

    # Test Case 1: "How many did you find?"
    print("\n[Test 1] File count follow-up")
    req1 = ChatRequest(
        question="What Python files are in this directory?",
        user_id="test_user",
        conversation_id="test_conv_1"
    )
    resp1 = await agent.process_request(req1)
    print(f"Q: {req1.question}")
    print(f"A: {resp1.response[:200]}...")

    req2 = ChatRequest(
        question="How many did you find?",
        user_id="test_user",
        conversation_id="test_conv_1"
    )
    resp2 = await agent.process_request(req2)
    print(f"\nQ: {req2.question}")
    print(f"A: {resp2.response}")
    if resp2.error_message:
        print(f"ERROR: {resp2.error_message}")

    # Test Case 2: "What does it do?"
    print("\n" + "=" * 80)
    print("\n[Test 2] Pronoun 'it' resolution")
    req3 = ChatRequest(
        question="Show me the main Python file in cite_agent directory",
        user_id="test_user",
        conversation_id="test_conv_2"
    )
    resp3 = await agent.process_request(req3)
    print(f"Q: {req3.question}")
    print(f"A: {resp3.response[:200]}...")

    req4 = ChatRequest(
        question="What does it do?",
        user_id="test_user",
        conversation_id="test_conv_2"
    )
    resp4 = await agent.process_request(req4)
    print(f"\nQ: {req4.question}")
    print(f"A: {resp4.response}")
    if resp4.error_message:
        print(f"ERROR: {resp4.error_message}")

    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_pronoun_resolution())
