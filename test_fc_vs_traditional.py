#!/usr/bin/env python3
"""
Compare Function Calling vs Traditional Mode
Test hypothesis: FC good for research, bad for financial
"""

import asyncio
import os
import sys

os.environ['NOCTURNAL_DEBUG'] = '1'
os.environ['USE_LOCAL_KEYS'] = 'true'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


async def test_with_mode(query: str, use_function_calling: bool, description: str):
    """Test a query with specified mode"""
    mode_name = "FUNCTION CALLING" if use_function_calling else "TRADITIONAL"

    print(f"\n{'='*100}")
    print(f"MODE: {mode_name}")
    print(f"TEST: {description}")
    print(f"Query: '{query}'")
    print(f"{'='*100}\n")

    agent = EnhancedNocturnalAgent()

    # HACK: Force the mode by manipulating self.client
    # If use_function_calling=True, ensure client is set
    # If use_function_calling=False, ensure client is None

    # For now, let's just test what we can test and show the actual output
    request = ChatRequest(question=query)

    try:
        response = await agent.process_request(request)

        print(f"📊 RESULTS:")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Tools: {response.tools_used}")
        print(f"\n💬 RESPONSE:")
        print(f"{response.response}")
        print(f"\n{'='*100}\n")

        return {
            'tokens': response.tokens_used,
            'tools': response.tools_used,
            'response': response.response,
            'response_length': len(response.response)
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    print("🧪 FUNCTION CALLING vs TRADITIONAL MODE COMPARISON")
    print("="*100)
    print("Testing hypothesis: FC good for research, traditional good for financial")
    print("="*100)

    # Note: Currently function calling is disabled in the code
    # This test will show what traditional mode produces
    # Then we can manually enable FC and re-run

    print("\n\n🔬 CURRENT MODE (Function Calling DISABLED)")
    print("This shows what traditional mode produces\n")

    # Test 1: Research query
    r1 = await test_with_mode(
        "Find papers on vision transformers",
        use_function_calling=False,
        description="Research Query"
    )

    # Test 2: Financial query
    r2 = await test_with_mode(
        "What is Apple's profit margin?",
        use_function_calling=False,
        description="Financial Query"
    )

    # Test 3: Comparative research
    r3 = await test_with_mode(
        "Compare BERT and GPT-3 approaches",
        use_function_calling=False,
        description="Comparative Research"
    )

    print("\n" + "="*100)
    print("📋 INSTRUCTIONS FOR NEXT STEP:")
    print("="*100)
    print("1. Review the responses above - are they helpful?")
    print("2. To test FUNCTION CALLING mode, edit enhanced_ai_agent.py:")
    print("   Line ~4159: Uncomment 'if self.client is not None:'")
    print("   Line ~4160: Uncomment 'return await self.process_request_with_function_calling(request)'")
    print("3. Re-run this script to compare")
    print("4. Judge based on RESPONSE QUALITY, not keywords")
    print("="*100)


if __name__ == "__main__":
    asyncio.run(main())
