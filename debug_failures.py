#!/usr/bin/env python3
"""
Debug the 9 failing tests to understand root cause
"""

import asyncio
import sys
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def debug_failures():
    """Test the failing queries with debug output"""
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    failing_tests = [
        "Summarize research on transformer architectures",
        "What's the difference between LSTM and GRU?",
        "What are the applications of heterogeneous graph neural networks for protein interactions in yeast?",
        "Tell me about research",
        "How do behavioral economics inform reinforcement learning in autonomous vehicles?",
        "Find papers that prove deep learning needs AND doesn't need large datasets",
        "hlep me find paper abot machien lerning",
        "I have missing data. How should I handle it for my analysis?",
    ]

    print("=" * 100)
    print("DEBUGGING FAILING TESTS")
    print("=" * 100)
    print()

    for i, query in enumerate(failing_tests, 1):
        print(f"\n[{i}/{len(failing_tests)}] Testing: {query[:80]}...")

        try:
            request = ChatRequest(
                question=query,
                user_id=f"debug_{i}",
                conversation_id=f"debug_conv_{i}"
            )

            response = await agent.process_request(request)

            print(f"Response length: {len(response.response)} chars")
            print(f"Tools used: {response.tools_used}")
            print(f"Error message: {response.error_message if hasattr(response, 'error_message') else 'None'}")
            print(f"Response preview: {response.response[:200]}...")

            await asyncio.sleep(2)

        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_failures())
