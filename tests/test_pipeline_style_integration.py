#!/usr/bin/env python3
"""
Pipeline Style Integration Test

Tests if the complete response pipeline produces pleasant, stylish responses
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.response_pipeline import ResponsePipeline


async def test_pipeline_style():
    """Test if pipeline produces pleasant, stylish responses"""

    test_cases = [
        {
            'name': 'Simple greeting',
            'raw_response': 'Hello. How can I assist you today?',
            'query': 'Hey!',
            'response_type': 'greeting',
            'style_checks': {
                'warm_greeting': ['hi', 'ready to help', 'what can i'],
                'no_robotic': ['how can i assist', 'how may i help'],
                'personality': True,
            }
        },
        {
            'name': 'File listing',
            'raw_response': 'I have analyzed the directory and located the following files: main.py, utils.py, test.py',
            'query': 'List Python files',
            'response_type': 'file_list',
            'style_checks': {
                'natural_language': ["i've", 'found', 'i see'],
                'elegant_formatting': ['•', '\n\n'],
                'anticipatory': ['want me to', 'should i', 'let me know'],
            }
        },
        {
            'name': 'Code explanation',
            'raw_response': 'This code defines a function that processes data.',
            'query': 'What does this code do?',
            'response_type': 'code',
            'style_checks': {
                'anticipatory': ['want me to', 'walk through', 'explore'],
                'helpful': True,
            }
        },
        {
            'name': 'Thank you response',
            'raw_response': 'You are welcome.',
            'query': 'Thanks!',
            'response_type': 'acknowledgment',
            'style_checks': {
                'warm': ['happy to help', 'glad to', 'let me know'],
                'no_formal': ['you are welcome'],
            }
        },
    ]

    print("=" * 80)
    print("PIPELINE STYLE INTEGRATION TEST")
    print("Testing if full pipeline produces pleasant, stylish responses")
    print("=" * 80)

    passed = 0
    failed = 0
    total_style_score = 0

    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"TEST: {test['name']}")
        print("=" * 80)

        # Process through pipeline
        result = await ResponsePipeline.process(
            test['raw_response'],
            test['query'],
            {},
            test['response_type']
        )

        print(f"\n❌ BEFORE:")
        print(f"   {test['raw_response']}")

        print(f"\n✅ AFTER PIPELINE:")
        print(f"   {result.final_response}")

        print(f"\n📊 QUALITY METRICS:")
        print(f"   Quality Score: {result.quality_score:.2f}")
        print(f"   Improvements: {', '.join(result.improvements_applied)}")

        # Check style
        response_lower = result.final_response.lower()
        style_score = 0
        max_checks = 0

        print(f"\n🎨 STYLE CHECKS:")

        for check_name, check_criteria in test['style_checks'].items():
            if isinstance(check_criteria, list):
                # Check if phrases are present or absent based on check name
                found = any(phrase in response_lower for phrase in check_criteria)
                max_checks += 1

                # Negative checks (no_*) should verify phrases are ABSENT
                if check_name.startswith('no_'):
                    if not found:
                        style_score += 1
                        print(f"   ✅ {check_name}: Not present (good)")
                    else:
                        print(f"   ❌ {check_name}: Still present (bad)")
                else:
                    # Positive checks should verify phrases are PRESENT
                    if found:
                        style_score += 1
                        print(f"   ✅ {check_name}: Found")
                    else:
                        print(f"   ❌ {check_name}: Missing")

            elif isinstance(check_criteria, bool):
                # Just check that response is not empty and has personality
                if len(result.final_response) > 20:
                    style_score += 1
                    max_checks += 1
                    print(f"   ✅ {check_name}: Present")
                else:
                    max_checks += 1
                    print(f"   ❌ {check_name}: Missing")

        # Calculate percentage
        style_percentage = (style_score / max_checks * 100) if max_checks > 0 else 0
        total_style_score += style_percentage

        print(f"\n   Style Score: {style_score}/{max_checks} ({style_percentage:.1f}%)")

        if style_percentage >= 60:  # 60% threshold
            print(f"   ✅ PASS - Response is pleasant and stylish")
            passed += 1
        else:
            print(f"   ❌ FAIL - Response needs more style")
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)

    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    avg_style_score = total_style_score / total if total > 0 else 0

    print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({(100-success_rate):.1f}%)")
    print(f"📊 Average Style Score: {avg_style_score:.1f}%")

    if success_rate >= 75 and avg_style_score >= 60:
        print("\n✅ PIPELINE PRODUCES PLEASANT, STYLISH RESPONSES!")
        return True
    else:
        print("\n❌ Pipeline needs more style work")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_pipeline_style())
    sys.exit(0 if result else 1)
