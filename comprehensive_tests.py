#!/usr/bin/env python3
"""
Comprehensive test suite - all the edge cases and research functionality
"""

import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def run_comprehensive_tests():
    """Run comprehensive tests and count pass/fail"""
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = [
        # Research functionality
        ("Find papers on climate change mitigation strategies", "research_paper_search"),
        ("I have survey data with Likert scales. What tests should I use?", "statistical_guidance"),
        ("Analyze CSV file with sales data to find patterns", "data_analysis_request"),
        ("Summarize research on transformer architectures", "literature_review"),
        ("What's the difference between LSTM and GRU?", "methodology_comparison"),

        # Edge cases
        ("What are the applications of heterogeneous graph neural networks for protein interactions in yeast?", "ultra_specific_niche"),
        ("Tell me about research", "extremely_vague"),
        ("How do behavioral economics inform reinforcement learning in autonomous vehicles?", "multi_disciplinary"),
        ("Find papers that prove deep learning needs AND doesn't need large datasets", "contradictory"),
        ("¿Cuáles son los últimos avances en aprendizaje automático?", "non_english"),
        ("I need help with 統計分析 for survey data", "mixed_language"),
        ("hlep me find paper abot machien lerning", "poorly_formatted"),
        ("I have missing data in my longitudinal study with baseline measurements at T1, follow-up at T2 and T3, dropout rates of 15% at T2 and 28% at T3, and I need to decide between multiple imputation with chained equations versus inverse probability weighting, considering that missingness might be related to the outcome variable which violates MAR assumptions.", "extremely_long_query"),
        ("I have missing data. How should I handle it for my analysis?", "missing_data_handling"),
        ("My data has ID, timestamp, response codes like 'OK', 'FAIL', 'N/A'", "non_standard_format"),
        ("Can I use p<0.001 threshold for 50 simultaneous comparisons in multivariate regression?", "impossible_statistical"),
        ("I have both interview transcripts and survey data. How do I integrate them?", "mixed_methods"),

        # Multi-turn conversation
        ("I'm analyzing customer churn data", "context_1"),
        ("What features should I look at?", "context_2"),
        ("Actually, I meant retention, not churn", "context_3_correction"),

        # Stress tests
        ("What is 2+2?", "simple_math"),
    ]

    results = []
    passed = 0
    failed = 0

    print("=" * 100)
    print("COMPREHENSIVE TEST SUITE - 21 Tests")
    print("=" * 100)
    print()

    for i, (query, test_name) in enumerate(tests, 1):
        print(f"\n[{i}/21] Testing: {test_name}")
        print(f"Query: {query[:80]}...")

        try:
            request = ChatRequest(
                question=query,
                user_id=f"test_{i}",
                conversation_id=f"conv_{i}"
            )

            response = await agent.process_request(request)
            response_len = len(response.response)

            # Determine if passed (substantive response > 200 chars, not generic error)
            is_pass = (response_len > 200 and
                      "I'm having trouble" not in response.response and
                      "Could you try rephrasing" not in response.response)

            if is_pass:
                print(f"✅ PASS - {response_len} chars")
                passed += 1
            else:
                print(f"❌ FAIL - {response_len} chars: {response.response[:100]}...")
                failed += 1

            results.append({
                'test': test_name,
                'query': query,
                'passed': is_pass,
                'response_length': response_len,
                'response_preview': response.response[:200]
            })

            # Small delay to avoid overwhelming
            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ ERROR: {str(e)[:100]}")
            failed += 1
            results.append({
                'test': test_name,
                'query': query,
                'passed': False,
                'error': str(e)
            })

    # Summary
    print("\n\n" + "=" * 100)
    print("FINAL RESULTS")
    print("=" * 100)
    print(f"Total Tests: 21")
    print(f"Passed: {passed} ({passed/21*100:.1f}%)")
    print(f"Failed: {failed} ({failed/21*100:.1f}%)")
    print()

    # Show which tests passed/failed
    print("\n✅ PASSED:")
    for r in results:
        if r.get('passed'):
            print(f"  - {r['test']}: {r['response_length']} chars")

    print("\n❌ FAILED:")
    for r in results:
        if not r.get('passed'):
            print(f"  - {r['test']}")

    return passed, failed

if __name__ == "__main__":
    passed, failed = asyncio.run(run_comprehensive_tests())
