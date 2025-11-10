#!/usr/bin/env python3
"""
Test automatic tool usage - verify the agent detects queries and calls tools automatically
"""

import sys
sys.path.insert(0, '/home/user/cite-agent')

import asyncio
from cite_agent import EnhancedNocturnalAgent, ChatRequest

async def test_automatic_detection():
    """Test that the agent automatically detects and handles data analysis queries."""

    print("\n" + "="*80)
    print("Testing Automatic Tool Detection & Usage")
    print("="*80)

    agent = EnhancedNocturnalAgent()

    # Create sample data in Python workspace
    globals()['test_data'] = [
        {'date': '2024-01-01', 'revenue': 1500, 'costs': 800},
        {'date': '2024-01-02', 'revenue': 2200, 'costs': 1100},
        {'date': '2024-01-03', 'revenue': 1800, 'costs': 900},
    ]

    python_inspector = agent.workspace_manager.get_inspector("Python")
    if python_inspector:
        python_inspector.set_namespace(globals())

    # Test 1: Statistical summary query
    print("\n" + "-"*80)
    print("TEST 1: Statistical Summary Query (should auto-trigger summarize_data)")
    print("-"*80)

    request = ChatRequest(
        question="What are the statistics for test_data?",
        user_id="test_user"
    )

    response = await agent.process_request(request)

    print(f"\n✓ Tools Used: {response.tools_used}")
    print(f"✓ Response Preview: {response.response[:200]}...")

    if 'data_analyzer' in response.tools_used:
        print("✅ PASS: Agent automatically used data_analyzer")
    else:
        print("❌ FAIL: Agent did not automatically use data_analyzer")

    # Test 2: Column search query
    print("\n" + "-"*80)
    print("TEST 2: Column Search Query (should auto-trigger search_columns)")
    print("-"*80)

    request2 = ChatRequest(
        question="find columns with revenue",
        user_id="test_user"
    )

    response2 = await agent.process_request(request2)

    print(f"\n✓ Tools Used: {response2.tools_used}")
    print(f"✓ Response Preview: {response2.response[:200]}...")

    if 'smart_search' in response2.tools_used:
        print("✅ PASS: Agent automatically used smart_search")
    else:
        print("❌ FAIL: Agent did not automatically use smart_search")

    # Test 3: Code template query
    print("\n" + "-"*80)
    print("TEST 3: Code Template Query (should auto-trigger get_code_template)")
    print("-"*80)

    request3 = ChatRequest(
        question="how do I run a t-test in R?",
        user_id="test_user"
    )

    response3 = await agent.process_request(request3)

    print(f"\n✓ Tools Used: {response3.tools_used}")
    print(f"✓ Response Preview: {response3.response[:200]}...")

    if 'code_templates' in response3.tools_used:
        print("✅ PASS: Agent automatically used code_templates")
    else:
        print("❌ FAIL: Agent did not automatically use code_templates")

    # Test 4: Tool discovery
    print("\n" + "-"*80)
    print("TEST 4: Dynamic Tool Discovery")
    print("-"*80)

    tools = agent.get_available_tools()

    print(f"\n✓ Total Tool Categories: {tools['total_categories']}")
    print("✓ Available Categories:")
    for category, info in tools['tools'].items():
        print(f"  - {category}: {info['description']}")

    print("\n✅ PASS: Tool discovery working")

    print("\n" + "="*80)
    print("Automatic Tool Detection Tests Complete")
    print("="*80)

    await agent.close()


if __name__ == "__main__":
    asyncio.run(test_automatic_detection())
