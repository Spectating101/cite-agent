#!/usr/bin/env python3
"""
REAL QUALITY TEST - Human judgment, not keyword matching

Test both modes and show FULL responses for manual evaluation
"""

import asyncio
import os
import sys

# Set ALL Cerebras API keys for rotation
os.environ['CEREBRAS_API_KEY_1'] = 'csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj'
os.environ['CEREBRAS_API_KEY_2'] = 'csk-edrc3v63k43fe4hdt529ynt4h9mfd9k9wjpjj3nn5pcvm2t4'
os.environ['CEREBRAS_API_KEY_3'] = 'csk-ek3cj5jv26hpnd2h65d8955pjmvxctdjknfv6pwehr82pnhr'
os.environ['CEREBRAS_API_KEY_4'] = 'csk-n5h26f263vr5rxp9fpn4w8xkfvpc5v9kjdw95vfc8d3x4ce9'
os.environ['NOCTURNAL_DEBUG'] = '1'
os.environ['USE_LOCAL_KEYS'] = 'true'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


async def test_query(query: str, force_mode: str = None):
    """
    Test a query and show FULL response
    force_mode: 'fc' for function calling, 'traditional' for traditional
    """
    agent = EnhancedNocturnalAgent()

    # Temporarily modify routing for testing
    original_question = query
    if force_mode == 'traditional':
        # Add financial keyword to force traditional mode
        query_modified = query + " (financial)"
    else:
        query_modified = query

    request = ChatRequest(question=query_modified)

    try:
        response = await agent.process_request(request)
        return response
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    print("="*100)
    print("REAL QUALITY TEST - MANUAL EVALUATION")
    print("="*100)
    print("\nNo keyword matching. No automated pass/fail.")
    print("Just showing FULL responses for human judgment.\n")

    test_queries = [
        "Find papers on vision transformers",
        "What is Apple's profit margin?",
        "Compare BERT and GPT-3 approaches"
    ]

    for query in test_queries:
        print("\n" + "="*100)
        print(f"QUERY: {query}")
        print("="*100)

        # Test with Function Calling mode (research query triggers it)
        if 'paper' in query.lower() or 'compare' in query.lower():
            print("\n--- TESTING WITH FUNCTION CALLING MODE ---\n")
            fc_response = await test_query(query)

            if fc_response:
                print(f"\n📊 METADATA:")
                print(f"  Tokens: {fc_response.tokens_used}")
                print(f"  Tools: {fc_response.tools_used}")

                print(f"\n💬 FULL RESPONSE (Function Calling):")
                print(fc_response.response)
                print(f"\n{'='*100}")

        # Test with Traditional mode (financial query triggers it)
        else:
            print("\n--- TESTING WITH TRADITIONAL MODE ---\n")
            trad_response = await test_query(query, force_mode='traditional')

            if trad_response:
                print(f"\n📊 METADATA:")
                print(f"  Tokens: {trad_response.tokens_used}")
                print(f"  Tools: {trad_response.tools_used}")

                print(f"\n💬 FULL RESPONSE (Traditional):")
                print(trad_response.response)
                print(f"\n{'='*100}")

        print("\n⏸️  Pausing 2 seconds between queries to avoid rate limits...\n")
        await asyncio.sleep(2)

    print("\n" + "="*100)
    print("EVALUATION INSTRUCTIONS:")
    print("="*100)
    print("For each response above, judge:")
    print("1. Does it actually answer the question?")
    print("2. Is the information accurate and useful?")
    print("3. Is it well-formatted and easy to read?")
    print("4. Would you be satisfied with this answer?")
    print("\nIgnore keywords - focus on QUALITY and HELPFULNESS.")
    print("="*100)


if __name__ == "__main__":
    asyncio.run(main())
