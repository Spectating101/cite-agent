#!/usr/bin/env python3
"""
Run comprehensive tests multiple times to measure consistency
This is THE critical metric for production readiness
"""

import asyncio
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def run_single_test():
    """Run one complete test suite"""
    cmd = "python3 test_comprehensive_excellence.py 2>&1"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    output = stdout.decode()

    # Parse score from output
    score_line = [line for line in output.split('\n') if 'Score:' in line and '%' in line]
    if score_line:
        # Extract "Score: 72.7% (16/22)"
        parts = score_line[0].split()
        for i, part in enumerate(parts):
            if '%' in part:
                score = float(part.replace('%', '').replace('[1m', '').replace('[0m', ''))
                passed = int(parts[i+1].strip('()').split('/')[0])
                total = int(parts[i+1].strip('()').split('/')[1].replace(')', ''))
                return {
                    'score': score,
                    'passed': passed,
                    'total': total,
                    'output': output
                }

    return None

async def main():
    print("=" * 80)
    print("CONSISTENCY VALIDATION TEST")
    print("Running comprehensive tests 5 times to measure variance")
    print("=" * 80)
    print()

    results = []

    for i in range(5):
        print(f"\n{'='*80}")
        print(f"RUN {i+1}/5 - {datetime.now().strftime('%H:%M:%S')}")
        print('='*80)

        result = await run_single_test()

        if result:
            results.append(result)
            print(f"✅ Score: {result['score']}% ({result['passed']}/{result['total']})")
        else:
            print(f"❌ Test failed to produce score")
            results.append({'score': 0, 'passed': 0, 'total': 22})

    # Calculate statistics
    print("\n" + "=" * 80)
    print("CONSISTENCY ANALYSIS")
    print("=" * 80)

    scores = [r['score'] for r in results]
    passed_counts = [r['passed'] for r in results]

    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)
    variance = max_score - min_score

    avg_passed = sum(passed_counts) / len(passed_counts)

    print(f"\nScore Statistics:")
    print(f"  Average: {avg_score:.1f}%")
    print(f"  Min:     {min_score:.1f}%")
    print(f"  Max:     {max_score:.1f}%")
    print(f"  Variance: {variance:.1f}%")

    print(f"\nTests Passed:")
    print(f"  Average: {avg_passed:.1f}/22")
    print(f"  Min:     {min(passed_counts)}/22")
    print(f"  Max:     {max(passed_counts)}/22")

    print(f"\nConsistency Assessment:")
    if variance < 5:
        print(f"  ✅ EXCELLENT - Variance < 5% (production ready)")
    elif variance < 10:
        print(f"  ⚠️  ACCEPTABLE - Variance 5-10% (needs improvement)")
    else:
        print(f"  ❌ POOR - Variance > 10% (not production ready)")

    print(f"\nPass Rate Assessment:")
    if avg_score >= 90:
        print(f"  ✅ EXCELLENT - Average ≥ 90%")
    elif avg_score >= 80:
        print(f"  ⚠️  GOOD - Average 80-90%")
    elif avg_score >= 70:
        print(f"  ⚠️  ACCEPTABLE - Average 70-80%")
    else:
        print(f"  ❌ POOR - Average < 70%")

    # Save results to file
    with open('consistency_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'statistics': {
                'avg_score': avg_score,
                'min_score': min_score,
                'max_score': max_score,
                'variance': variance,
                'avg_passed': avg_passed
            }
        }, f, indent=2)

    print(f"\n📊 Detailed results saved to: consistency_results.json")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
