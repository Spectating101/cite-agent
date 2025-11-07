#!/usr/bin/env python3
"""
Quick test of Phase 1 quality improvements
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest
from cite_agent.quality_gate import assess_response_quality


async def test_basic_queries():
    """Test basic queries with Phase 1 improvements"""
    agent = EnhancedNocturnalAgent()

    test_queries = [
        "Hey!",
        "Thanks!",
        "List files in current directory",
        "Where am I?",
        "What Python files are here?",
    ]

    print("=" * 80)
    print("PHASE 1 QUALITY TEST - Basic Queries")
    print("=" * 80)

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print("=" * 80)

        request = ChatRequest(question=query, user_id="test_user")

        try:
            response = await agent.process_request(request)

            # Assess quality
            assessment = assess_response_quality(
                response.response,
                query,
                {}
            )

            print(f"\n📝 RESPONSE:\n{response.response}\n")
            print(f"📊 QUALITY METRICS:")
            print(f"   Overall Score: {assessment.overall_score:.2f}")
            print(f"   Grade: {assessment.category_scores}")

            if assessment.issues:
                print(f"\n⚠️  Issues: {', '.join(assessment.issues)}")

            if assessment.strengths:
                print(f"\n✅ Strengths: {', '.join(assessment.strengths)}")

            # Check for technical errors
            bad_terms = ['error:', 'exception', 'traceback', 'tls_error', 'certificate_verify_failed']
            response_lower = response.response.lower()

            if any(term in response_lower for term in bad_terms):
                print("\n❌ FAIL: Technical error exposed!")
            else:
                print("\n✅ PASS: No technical errors exposed")

        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()

    await agent.close()


async def test_error_handling():
    """Test that errors are handled gracefully"""
    print("\n\n" + "=" * 80)
    print("PHASE 1 ERROR HANDLING TEST")
    print("=" * 80)

    from cite_agent.error_handler import GracefulErrorHandler

    # Test various error types
    test_errors = [
        (ConnectionError("Failed to connect"), "while connecting to API"),
        (TimeoutError("Request timed out"), "while fetching data"),
        (ValueError("Invalid JSON"), "while parsing response"),
        (Exception("Something went wrong"), "while processing"),
    ]

    for error, context in test_errors:
        friendly_msg = GracefulErrorHandler.handle_error(error, context)

        print(f"\n{'='*80}")
        print(f"ERROR TYPE: {type(error).__name__}")
        print(f"CONTEXT: {context}")
        print(f"FRIENDLY MESSAGE: {friendly_msg}")

        # Check that it's user-friendly
        bad_terms = ['exception', 'traceback', 'error:', 'stack']
        if any(term in friendly_msg.lower() for term in bad_terms):
            print("❌ FAIL: Technical term in message")
        else:
            print("✅ PASS: User-friendly message")


async def main():
    await test_error_handling()
    await test_basic_queries()

    print("\n\n" + "=" * 80)
    print("PHASE 1 TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
