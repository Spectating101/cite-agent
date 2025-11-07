#!/usr/bin/env python3
"""
Direct test of response enhancement
Tests before/after quality to measure improvement
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.response_enhancer import ResponseEnhancer
from cite_agent.quality_gate import assess_response_quality


def test_enhancement():
    """Test enhancement on sample responses"""
    test_cases = [
        {
            'query': 'List Python files in this directory',
            'response': 'I found some files including main.py and utils.py',
            'context': {'tools_used': ['shell'], 'api_results': {'files': ['main.py', 'utils.py', 'test.py']}}
        },
        {
            'query': 'What is quantum computing and how does it work?',
            'response': 'Well quantum computing is basically a type of computing that uses quantum mechanics maybe with qubits',
            'context': {}
        },
        {
            'query': 'Compare Apple and Microsoft revenue growth',
            'response': 'Apple had some growth and Microsoft also had growth in recent quarters',
            'context': {'api_results': {'apple': 12, 'microsoft': 15}}
        },
    ]

    print("=" * 80)
    print("DIRECT ENHANCEMENT TESTING")
    print("=" * 80)

    total_before = 0
    total_after = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['query']}")
        print("=" * 80)

        # Assess before enhancement
        before_assessment = assess_response_quality(
            test['response'],
            test['query'],
            test['context']
        )

        print(f"\nBEFORE Enhancement:")
        print(f"Response: {test['response']}")
        print(f"Quality Score: {before_assessment.overall_score:.2f}")
        print(f"Issues: {before_assessment.issues}")

        # Enhance
        enhanced = ResponseEnhancer.enhance(
            test['response'],
            test['query'],
            test['context']
        )

        # Assess after enhancement
        after_assessment = assess_response_quality(
            enhanced,
            test['query'],
            test['context']
        )

        print(f"\nAFTER Enhancement:")
        print(f"Response: {enhanced}")
        print(f"Quality Score: {after_assessment.overall_score:.2f}")
        print(f"Issues: {after_assessment.issues}")

        improvement = after_assessment.overall_score - before_assessment.overall_score
        print(f"\n{'📈' if improvement > 0 else '📉'} Improvement: {improvement:+.2f}")

        total_before += before_assessment.overall_score
        total_after += after_assessment.overall_score

    # Overall summary
    avg_before = total_before / len(test_cases)
    avg_after = total_after / len(test_cases)
    overall_improvement = avg_after - avg_before

    print(f"\n{'='*80}")
    print("OVERALL RESULTS")
    print("=" * 80)
    print(f"Average Before: {avg_before:.2f}")
    print(f"Average After: {avg_after:.2f}")
    print(f"Overall Improvement: {overall_improvement:+.2f} ({overall_improvement/avg_before*100:+.1f}%)")

    if avg_after >= 0.75:
        print("\n✅ Enhancement successfully boosts quality to target level!")
    elif overall_improvement > 0.05:
        print("\n📈 Enhancement provides meaningful improvement")
    else:
        print("\n⚠️  Enhancement not providing significant improvement")


if __name__ == "__main__":
    test_enhancement()
