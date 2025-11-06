#!/usr/bin/env python3
"""
Show ACTUAL test interactions - real questions and real responses
"""

import asyncio
import sys
import os
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def show_real_interactions():
    """Run actual test queries and show exact responses"""
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("=" * 100)
    print("ACTUAL TEST INTERACTIONS - Real Questions & Real Responses")
    print("=" * 100)

    # Test 1: Research paper search
    print("\n" + "=" * 100)
    print("TEST 1: Research Paper Search")
    print("=" * 100)
    q1 = "Find papers on machine learning interpretability from the last 2 years"
    print(f"\nQUESTION: {q1}")
    print("\nAGENT RESPONSE:")
    print("-" * 100)

    r1 = await agent.process_request(ChatRequest(
        question=q1,
        user_id="test_1",
        conversation_id="conv_1"
    ))
    print(r1.response)
    print("-" * 100)
    print(f"Length: {len(r1.response)} chars | Tools used: {r1.tools_used}")

    await asyncio.sleep(3)  # Rate limit

    # Test 2: Statistical analysis
    print("\n\n" + "=" * 100)
    print("TEST 2: Statistical Analysis Guidance")
    print("=" * 100)
    q2 = "I have survey data with 5-point Likert scales. What statistical tests should I use?"
    print(f"\nQUESTION: {q2}")
    print("\nAGENT RESPONSE:")
    print("-" * 100)

    r2 = await agent.process_request(ChatRequest(
        question=q2,
        user_id="test_2",
        conversation_id="conv_2"
    ))
    print(r2.response)
    print("-" * 100)
    print(f"Length: {len(r2.response)} chars | Tools used: {r2.tools_used}")

    await asyncio.sleep(3)

    # Test 3: Data analysis recommendation
    print("\n\n" + "=" * 100)
    print("TEST 3: Data Analysis Recommendations")
    print("=" * 100)
    q3 = "I have a CSV file with customer purchase data. How should I analyze it to find patterns?"
    print(f"\nQUESTION: {q3}")
    print("\nAGENT RESPONSE:")
    print("-" * 100)

    r3 = await agent.process_request(ChatRequest(
        question=q3,
        user_id="test_3",
        conversation_id="conv_3"
    ))
    print(r3.response)
    print("-" * 100)
    print(f"Length: {len(r3.response)} chars | Tools used: {r3.tools_used}")

    await asyncio.sleep(3)

    # Test 4: Literature review
    print("\n\n" + "=" * 100)
    print("TEST 4: Literature Review Synthesis")
    print("=" * 100)
    q4 = "Summarize the current research on deep learning for medical image analysis"
    print(f"\nQUESTION: {q4}")
    print("\nAGENT RESPONSE:")
    print("-" * 100)

    r4 = await agent.process_request(ChatRequest(
        question=q4,
        user_id="test_4",
        conversation_id="conv_4"
    ))
    print(r4.response)
    print("-" * 100)
    print(f"Length: {len(r4.response)} chars | Tools used: {r4.tools_used}")

    await asyncio.sleep(3)

    # Test 5: Specific methodology question
    print("\n\n" + "=" * 100)
    print("TEST 5: Specific Methodology Question")
    print("=" * 100)
    q5 = "What's the difference between random forest and gradient boosting for classification?"
    print(f"\nQUESTION: {q5}")
    print("\nAGENT RESPONSE:")
    print("-" * 100)

    r5 = await agent.process_request(ChatRequest(
        question=q5,
        user_id="test_5",
        conversation_id="conv_5"
    ))
    print(r5.response)
    print("-" * 100)
    print(f"Length: {len(r5.response)} chars | Tools used: {r5.tools_used}")

    await asyncio.sleep(3)

    # Test 6: Research gap identification
    print("\n\n" + "=" * 100)
    print("TEST 6: Research Gap Identification")
    print("=" * 100)
    q6 = "What are the current limitations in natural language processing for low-resource languages?"
    print(f"\nQUESTION: {q6}")
    print("\nAGENT RESPONSE:")
    print("-" * 100)

    r6 = await agent.process_request(ChatRequest(
        question=q6,
        user_id="test_6",
        conversation_id="conv_6"
    ))
    print(r6.response)
    print("-" * 100)
    print(f"Length: {len(r6.response)} chars | Tools used: {r6.tools_used}")

    print("\n\n" + "=" * 100)
    print("SUMMARY OF ACTUAL INTERACTIONS")
    print("=" * 100)
    print(f"Test 1 (Paper Search): {len(r1.response)} chars")
    print(f"Test 2 (Statistical): {len(r2.response)} chars")
    print(f"Test 3 (Data Analysis): {len(r3.response)} chars")
    print(f"Test 4 (Literature Review): {len(r4.response)} chars")
    print(f"Test 5 (Methodology): {len(r5.response)} chars")
    print(f"Test 6 (Research Gaps): {len(r6.response)} chars")

if __name__ == "__main__":
    asyncio.run(show_real_interactions())
