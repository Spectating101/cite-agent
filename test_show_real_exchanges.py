#!/usr/bin/env python3
"""
Show real agent exchanges so we can judge quality ourselves
No automated scoring - just see what it says
"""

import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def show_exchange(agent, query, conv_id, description):
    """Show one exchange"""
    print("\n" + "="*80)
    print(f"TEST: {description}")
    print("="*80)
    print(f"👤 USER: {query}")
    print()

    req = ChatRequest(
        question=query,
        user_id="demo_user",
        conversation_id=conv_id
    )

    resp = await agent.process_request(req)

    print(f"🤖 AGENT:\n{resp.response}")

    if resp.error_message:
        print(f"\n⚠️  ERROR: {resp.error_message}")

    print("\n" + "-"*80)
    return resp

async def main():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("\n" + "="*80)
    print("REAL AGENT EXCHANGES - Judge for yourself")
    print("="*80)

    # Test 1: Simple greeting
    await show_exchange(
        agent,
        "Hey, how's it going?",
        "demo_1",
        "Simple Greeting (should be warm and natural)"
    )

    # Test 2: Ambiguous query (should clarify nicely)
    await show_exchange(
        agent,
        "Tell me about the company",
        "demo_2",
        "Ambiguous Query (should ask for clarification with bullets)"
    )

    # Test 3: Clear query about files
    await show_exchange(
        agent,
        "What Python files are in this directory?",
        "demo_3",
        "Clear File Query (should list Python files)"
    )

    # Test 4: Follow-up with pronoun
    resp1 = await show_exchange(
        agent,
        "What test files are in this project?",
        "demo_4",
        "Initial Query - Find test files"
    )

    await show_exchange(
        agent,
        "How many did you find?",
        "demo_4",  # Same conversation
        "Follow-up with Pronoun (should remember context)"
    )

    # Test 5: Research query
    await show_exchange(
        agent,
        "What are the latest papers on transformer models?",
        "demo_5",
        "Research Query (should search or explain capabilities)"
    )

    # Test 6: Multi-part question
    await show_exchange(
        agent,
        "Can you find Python files, check which ones have 'test' in the name, and tell me how many there are?",
        "demo_6",
        "Multi-part Question (should address all parts)"
    )

    # Test 7: Vague request
    await show_exchange(
        agent,
        "Help me with my project",
        "demo_7",
        "Vague Request (should clarify what kind of help)"
    )

    # Test 8: Correction
    resp1 = await show_exchange(
        agent,
        "I'm working on a Python project",
        "demo_8",
        "Initial statement about Python"
    )

    await show_exchange(
        agent,
        "Actually, it's a JavaScript project, not Python",
        "demo_8",  # Same conversation
        "Correction (should acknowledge the correction)"
    )

    await agent.cleanup()

    print("\n" + "="*80)
    print("DONE - Now you can judge:")
    print("  1. Are responses natural and helpful?")
    print("  2. Does it clarify ambiguity well?")
    print("  3. Does it remember context?")
    print("  4. Is formatting good (bullets, structure)?")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
