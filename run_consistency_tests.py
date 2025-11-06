#!/usr/bin/env python3
"""
Run comprehensive tests 3 times to measure consistency and quality
"""

import asyncio
import json
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def run_test_suite():
    """Run one complete test suite"""
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = [
        # Core research functionality
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
        ("I have missing data in my longitudinal study. How should I handle it?", "missing_data_longitudinal"),
        ("I have missing data. How should I handle it for my analysis?", "missing_data_simple"),
        ("My data has ID, timestamp, response codes like 'OK', 'FAIL', 'N/A'", "non_standard_format"),
        ("Can I use p<0.001 threshold for 50 simultaneous comparisons?", "impossible_statistical"),
        ("I have both interview transcripts and survey data. How do I integrate them?", "mixed_methods"),

        # Context tracking
        ("I'm analyzing customer churn data", "context_1"),
        ("What features should I look at?", "context_2"),
    ]

    results = []

    for query, test_name in tests:
        try:
            request = ChatRequest(
                question=query,
                user_id=f"consistency_{test_name}",
                conversation_id=f"conv_{test_name}"
            )

            response = await agent.process_request(request)
            response_len = len(response.response)
            word_count = len(response.response.split())

            # Determine if passed
            is_pass = (response_len > 100 and
                      "I'm having trouble" not in response.response and
                      "Could you try rephrasing" not in response.response)

            results.append({
                'test': test_name,
                'query': query[:80],
                'passed': is_pass,
                'chars': response_len,
                'words': word_count,
                'tools': response.tools_used if response.tools_used else []
            })

            await asyncio.sleep(2)

        except Exception as e:
            results.append({
                'test': test_name,
                'query': query[:80],
                'passed': False,
                'error': str(e)[:100]
            })

    return results

async def run_multiple_iterations(num_runs=3):
    """Run test suite multiple times and analyze consistency"""
    all_runs = []

    print("=" * 100)
    print(f"RUNNING {num_runs} COMPREHENSIVE TEST ITERATIONS")
    print("=" * 100)
    print()

    for run_num in range(1, num_runs + 1):
        print(f"\n{'='*50}")
        print(f"RUN #{run_num}/{num_runs}")
        print(f"{'='*50}\n")

        run_results = await run_test_suite()
        all_runs.append(run_results)

        # Print summary for this run
        passed = sum(1 for r in run_results if r.get('passed'))
        total = len(run_results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n✓ Run #{run_num} Complete: {passed}/{total} passed ({pass_rate:.1f}%)")

        # Show which tests passed
        print(f"\n✅ PASSED ({passed}):")
        for r in run_results:
            if r.get('passed'):
                word_count = r.get('words', 0)
                status = "✓ Concise" if word_count <= 200 else f"⚠ Verbose ({word_count}w)"
                print(f"  - {r['test']}: {word_count}w {status}")

        print(f"\n❌ FAILED ({total - passed}):")
        for r in run_results:
            if not r.get('passed'):
                print(f"  - {r['test']}")

    # Analyze consistency across runs
    print("\n\n" + "=" * 100)
    print("CONSISTENCY ANALYSIS")
    print("=" * 100)

    # Calculate pass rate for each run
    pass_rates = []
    for i, run in enumerate(all_runs, 1):
        passed = sum(1 for r in run if r.get('passed'))
        total = len(run)
        rate = (passed / total * 100) if total > 0 else 0
        pass_rates.append(rate)
        print(f"Run {i}: {passed}/{total} = {rate:.1f}%")

    # Calculate variance
    avg_pass_rate = sum(pass_rates) / len(pass_rates)
    variance = max(pass_rates) - min(pass_rates)

    print(f"\nAverage Pass Rate: {avg_pass_rate:.1f}%")
    print(f"Variance: {variance:.1f}% ({' PERFECT CONSISTENCY' if variance == 0 else 'some variance'})")

    # Per-test consistency
    print("\n\nPER-TEST CONSISTENCY:")
    test_names = [r['test'] for r in all_runs[0]]

    for test_name in test_names:
        results_for_test = [any(r['test'] == test_name and r.get('passed') for r in run) for run in all_runs]
        passes = sum(results_for_test)
        consistency = (passes / num_runs * 100)

        if consistency == 100:
            print(f"✅ {test_name}: ALWAYS passes ({passes}/{num_runs})")
        elif consistency == 0:
            print(f"❌ {test_name}: ALWAYS fails ({passes}/{num_runs})")
        else:
            print(f"⚠️  {test_name}: INCONSISTENT ({passes}/{num_runs} = {consistency:.0f}%)")

    # Word count analysis
    print("\n\nRESPONSE LENGTH ANALYSIS:")
    for run_num, run in enumerate(all_runs, 1):
        avg_words = sum(r.get('words', 0) for r in run if r.get('passed')) / max(sum(1 for r in run if r.get('passed')), 1)
        print(f"Run {run_num} avg: {avg_words:.0f} words")

        concise_count = sum(1 for r in run if r.get('passed') and r.get('words', 0) <= 200)
        verbose_count = sum(1 for r in run if r.get('passed') and r.get('words', 0) > 200)
        print(f"  Concise (≤200w): {concise_count}, Verbose (>200w): {verbose_count}")

    return all_runs, avg_pass_rate, variance

if __name__ == "__main__":
    runs, avg_pass_rate, variance = asyncio.run(run_multiple_iterations(3))
