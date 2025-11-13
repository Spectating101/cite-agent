#!/usr/bin/env python3
"""
Test fallback response quality - verify conversational formatting
"""

import asyncio
import sys
sys.path.insert(0, '/home/user/cite-agent')


async def test_fallback_quality():
    """Test that fallback responses are conversational, not JSON dumps"""
    from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

    print("=" * 70)
    print("FALLBACK RESPONSE QUALITY TEST")
    print("=" * 70)
    print()

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Create mock research results
    mock_research_data = {
        "results": [
            {
                "title": "Attention Is All You Need",
                "doi": "10.5555/3295222.3295349",
                "year": 2017,
                "authors": [{"name": "Vaswani"}, {"name": "Shazeer"}],
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism.",
                "citationCount": 50000
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                "doi": "10.18653/v1/N19-1423",
                "year": 2019,
                "authors": [{"name": "Devlin"}, {"name": "Chang"}, {"name": "Lee"}],
                "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations.",
                "citationCount": 40000
            }
        ]
    }

    # Test the fallback response formatter directly
    request = ChatRequest(
        question="Find papers on transformer models",
        user_id="test_user",
        conversation_id="test_conv"
    )

    fallback_response = agent._respond_with_fallback(
        request=request,
        tools_used=["archive_api"],
        api_results={"research": mock_research_data},
        failure_reason="LLM quota exhausted",
        error_message="Groq API rate limit"
    )

    print("USER QUERY:")
    print(f"  {request.question}")
    print()
    print("FALLBACK RESPONSE:")
    print("-" * 70)
    print(fallback_response.response)
    print("-" * 70)
    print()

    # Quality checks
    response_text = fallback_response.response

    print("QUALITY CHECKS:")
    print()

    checks = {
        "✓ No JSON dumps": "```json" not in response_text,
        "✓ Mentions paper titles": "Attention Is All You Need" in response_text and "BERT" in response_text,
        "✓ Shows citation counts": "50,000" in response_text or "40,000" in response_text,
        "✓ Lists authors": "Vaswani" in response_text or "Devlin" in response_text,
        "✓ Includes years": "2017" in response_text and "2019" in response_text,
        "✓ Conversational tone": "I've gathered" in response_text or "I found" in response_text or "here's what I found" in response_text,
        "✓ Not technical jargon": response_text.count("{") < 2,  # No object dumps
        "✓ Formatted nicely": "**" in response_text,  # Has markdown formatting
    }

    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("✅ FALLBACK QUALITY: EXCELLENT")
        print("   Response is conversational and user-friendly!")
    else:
        print("❌ FALLBACK QUALITY: NEEDS IMPROVEMENT")
        print("   Some quality checks failed")
    print("=" * 70)

    await agent.close()
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_fallback_quality())
    sys.exit(0 if success else 1)
