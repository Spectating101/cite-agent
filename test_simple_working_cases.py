#!/usr/bin/env python3
"""
Test only the cases that should work without external APIs
Show what the agent CAN do when not blocked by API failures
"""

import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_simple_cases():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("="*80)
    print("TESTING SIMPLE CASES (No external API needed)")
    print("="*80)

    # Test 1: Greeting (should work - uses lightweight model or fallback)
    print("\n" + "="*80)
    print("TEST 1: Greeting")
    print("="*80)
    print("👤 USER: Hey!")
    req = ChatRequest(question="Hey!", user_id="test", conversation_id="test1")
    resp = await agent.process_request(req)
    print(f"🤖 AGENT: {resp.response}")
    print(f"✅ Quality: {'Good' if len(resp.response) < 200 and ('hi' in resp.response.lower() or 'hey' in resp.response.lower()) else 'Needs work'}")

    # Test 2: Thanks
    print("\n" + "="*80)
    print("TEST 2: Thanks")
    print("="*80)
    print("👤 USER: Thanks!")
    req = ChatRequest(question="Thanks!", user_id="test", conversation_id="test2")
    resp = await agent.process_request(req)
    print(f"🤖 AGENT: {resp.response}")
    print(f"✅ Quality: {'Good' if len(resp.response) < 200 and ('happy' in resp.response.lower() or 'welcome' in resp.response.lower()) else 'Needs work'}")

    # Test 3: List files (should work - uses shell, no LLM)
    print("\n" + "="*80)
    print("TEST 3: List Files")
    print("="*80)
    print("👤 USER: List the files here")
    req = ChatRequest(question="List the files here", user_id="test", conversation_id="test3")
    resp = await agent.process_request(req)
    print(f"🤖 AGENT: {resp.response[:500]}...")
    has_files = any(name in resp.response for name in ['START_HERE', 'setup.py', 'cite_agent'])
    print(f"✅ Quality: {'Good - shows actual files' if has_files else 'Bad - no files shown'}")

    # Test 4: Out of scope
    print("\n" + "="*80)
    print("TEST 4: Out of Scope Request")
    print("="*80)
    print("👤 USER: Make me a sandwich")
    req = ChatRequest(question="Make me a sandwich", user_id="test", conversation_id="test4")
    resp = await agent.process_request(req)
    print(f"🤖 AGENT: {resp.response}")
    good_response = any(word in resp.response.lower() for word in ['focus', 'help with', 'financial', 'research', 'codebase'])
    print(f"✅ Quality: {'Good - politely declines' if good_response else 'Needs work'}")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("These 4 tests show what the agent CAN do when APIs work.")
    print("The API failures we saw earlier are the main blocker.")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simple_cases())
