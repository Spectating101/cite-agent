#!/usr/bin/env python3
"""
Debug test to see what responses look like
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


async def test_response_style():
    """Test what actual responses look like"""
    agent = EnhancedNocturnalAgent()

    queries = [
        "Hey!",
        "List Python files",
        "Thanks!",
    ]

    for query in queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print("=" * 80)

        try:
            request = ChatRequest(question=query, user_id="debug_test")
            response = await agent.process_request(request)

            print(f"\nRESPONSE:")
            print(response.response)
            print(f"\nRESPONSE LENGTH: {len(response.response)} chars")

            # Check for style markers
            response_lower = response.response.lower()
            has_warmth = any(w in response_lower for w in ['happy', 'glad', 'hi there'])
            has_anticipatory = any(a in response_lower for a in ['want me to', 'let me know', 'should i'])
            has_natural = any(n in response_lower for n in ["i found", "i've", "here's"])

            print(f"\nSTYLE MARKERS:")
            print(f"  Warmth: {has_warmth}")
            print(f"  Anticipatory: {has_anticipatory}")
            print(f"  Natural: {has_natural}")

        except Exception as e:
            print(f"\nERROR: {e}")

    await agent.close()


if __name__ == "__main__":
    asyncio.run(test_response_style())
