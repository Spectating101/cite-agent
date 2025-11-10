#!/usr/bin/env python3
"""
Consistency Test: Run features multiple times to verify reliability
Tests each feature 5 times to ensure consistent results
"""

import asyncio
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, '.')

# Create test data in __main__
import __main__
__main__.consistency_test_data = pd.DataFrame({
    'id': range(1, 21),
    'value': np.random.randint(10, 100, 20),
    'category': np.random.choice(['A', 'B', 'C'], 20),
})

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent

async def run_consistency_tests():
    """Run each feature multiple times"""

    print("="*70)
    print("CONSISTENCY TEST SUITE - 5 Runs Per Feature")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)

    results = {
        'workspace_inspection': [],
        'object_inspection': [],
        'data_preview': [],
        'statistical_summary': [],
        'column_search': [],
        'code_templates': [],
    }

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Test 1: Workspace Inspection (5 times)
    print("\n" + "="*70)
    print("TEST 1: Workspace Inspection Consistency (5 runs)")
    print("="*70)

    for i in range(5):
        try:
            result = agent.describe_workspace()
            success = 'Python' in result and result['Python'].get('total_objects', 0) > 0
            obj_count = result.get('Python', {}).get('total_objects', 0)

            results['workspace_inspection'].append({
                'run': i+1,
                'success': success,
                'object_count': obj_count,
                'error': None
            })

            status = "✅" if success else "❌"
            print(f"  Run {i+1}: {status} Found {obj_count} objects")

        except Exception as e:
            results['workspace_inspection'].append({
                'run': i+1,
                'success': False,
                'object_count': 0,
                'error': str(e)
            })
            print(f"  Run {i+1}: ❌ Error: {e}")

        await asyncio.sleep(0.1)  # Small delay

    # Test 2: Object Inspection (5 times)
    print("\n" + "="*70)
    print("TEST 2: Object Inspection Consistency (5 runs)")
    print("="*70)

    for i in range(5):
        try:
            result = agent.inspect_workspace_object('consistency_test_data')
            success = 'error' not in result and result.get('type') == 'DataFrame'
            dimensions = result.get('dimensions', [])

            results['object_inspection'].append({
                'run': i+1,
                'success': success,
                'dimensions': dimensions,
                'columns': len(result.get('columns', [])),
                'error': result.get('error')
            })

            status = "✅" if success else "❌"
            print(f"  Run {i+1}: {status} Dimensions: {dimensions}, Columns: {len(result.get('columns', []))}")

        except Exception as e:
            results['object_inspection'].append({
                'run': i+1,
                'success': False,
                'error': str(e)
            })
            print(f"  Run {i+1}: ❌ Error: {e}")

        await asyncio.sleep(0.1)

    # Test 3: Data Preview (5 times)
    print("\n" + "="*70)
    print("TEST 3: Data Preview Consistency (5 runs)")
    print("="*70)

    for i in range(5):
        try:
            result = agent.get_workspace_data('consistency_test_data', limit=5)
            success = 'error' not in result and len(result.get('data', [])) > 0
            row_count = result.get('shown_rows', 0)

            results['data_preview'].append({
                'run': i+1,
                'success': success,
                'rows_shown': row_count,
                'total_rows': result.get('total_rows', 0),
                'error': result.get('error')
            })

            status = "✅" if success else "❌"
            print(f"  Run {i+1}: {status} Showed {row_count} of {result.get('total_rows', 0)} rows")

        except Exception as e:
            results['data_preview'].append({
                'run': i+1,
                'success': False,
                'error': str(e)
            })
            print(f"  Run {i+1}: ❌ Error: {e}")

        await asyncio.sleep(0.1)

    # Test 4: Statistical Summary (5 times)
    print("\n" + "="*70)
    print("TEST 4: Statistical Summary Consistency (5 runs)")
    print("="*70)

    for i in range(5):
        try:
            result = agent.summarize_data('consistency_test_data')
            success = 'error' not in result and 'methods_text' in result
            methods_len = len(result.get('methods_text', ''))
            has_shape = 'shape' in result

            results['statistical_summary'].append({
                'run': i+1,
                'success': success,
                'methods_length': methods_len,
                'has_shape': has_shape,
                'shape': result.get('shape', None),
                'error': result.get('error')
            })

            status = "✅" if success else "❌"
            print(f"  Run {i+1}: {status} Methods text: {methods_len} chars, Shape: {result.get('shape', 'N/A')}")

        except Exception as e:
            results['statistical_summary'].append({
                'run': i+1,
                'success': False,
                'error': str(e)
            })
            print(f"  Run {i+1}: ❌ Error: {e}")

        await asyncio.sleep(0.1)

    # Test 5: Column Search (5 times)
    print("\n" + "="*70)
    print("TEST 5: Column Search Consistency (5 runs)")
    print("="*70)

    for i in range(5):
        try:
            result = agent.search_columns('value')
            success = 'error' not in result
            matches = result.get('total_matches', 0)

            results['column_search'].append({
                'run': i+1,
                'success': success,
                'matches': matches,
                'error': result.get('error')
            })

            status = "✅" if success else "❌"
            print(f"  Run {i+1}: {status} Found {matches} matches")

        except Exception as e:
            results['column_search'].append({
                'run': i+1,
                'success': False,
                'error': str(e)
            })
            print(f"  Run {i+1}: ❌ Error: {e}")

        await asyncio.sleep(0.1)

    # Test 6: Code Templates (5 times)
    print("\n" + "="*70)
    print("TEST 6: Code Template Consistency (5 runs)")
    print("="*70)

    for i in range(5):
        try:
            result = agent.get_code_template(
                'ttest_independent_r',
                data='my_data',
                variable='score',
                group_var='group',
                group1='A',
                group2='B'
            )
            success = 'error' not in result and 'code' in result
            code_len = len(result.get('code', ''))
            has_citations = 'citations' in result and len(result.get('citations', [])) > 0

            results['code_templates'].append({
                'run': i+1,
                'success': success,
                'code_length': code_len,
                'has_citations': has_citations,
                'citation_count': len(result.get('citations', [])),
                'error': result.get('error')
            })

            status = "✅" if success else "❌"
            print(f"  Run {i+1}: {status} Code: {code_len} chars, Citations: {len(result.get('citations', []))}")

        except Exception as e:
            results['code_templates'].append({
                'run': i+1,
                'success': False,
                'error': str(e)
            })
            print(f"  Run {i+1}: ❌ Error: {e}")

        await asyncio.sleep(0.1)

    await agent.close()

    # Analyze consistency
    print("\n" + "="*70)
    print("CONSISTENCY ANALYSIS")
    print("="*70)

    summary = {}
    for feature, runs in results.items():
        successes = sum(1 for r in runs if r['success'])
        success_rate = (successes / len(runs)) * 100

        summary[feature] = {
            'total_runs': len(runs),
            'successes': successes,
            'failures': len(runs) - successes,
            'success_rate': success_rate
        }

        status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 80 else "❌"
        print(f"\n{status_icon} {feature.replace('_', ' ').title()}:")
        print(f"   Success: {successes}/{len(runs)} runs ({success_rate:.0f}%)")

        # Check for variance in results
        if feature == 'workspace_inspection' and successes > 0:
            obj_counts = [r['object_count'] for r in runs if r['success']]
            if len(set(obj_counts)) > 1:
                print(f"   ⚠️  Object count variance: {set(obj_counts)}")
            else:
                print(f"   ✅ Consistent object count: {obj_counts[0]}")

        if feature == 'object_inspection' and successes > 0:
            dims = [tuple(r['dimensions']) for r in runs if r['success']]
            if len(set(dims)) > 1:
                print(f"   ⚠️  Dimension variance: {set(dims)}")
            else:
                print(f"   ✅ Consistent dimensions: {dims[0]}")

        if feature == 'statistical_summary' and successes > 0:
            shapes = [tuple(r['shape']) if r['shape'] else None for r in runs if r['success']]
            if len(set(shapes)) > 1:
                print(f"   ⚠️  Shape variance: {set(shapes)}")
            else:
                print(f"   ✅ Consistent shape: {shapes[0]}")

        if feature == 'column_search' and successes > 0:
            match_counts = [r['matches'] for r in runs if r['success']]
            if len(set(match_counts)) > 1:
                print(f"   ⚠️  Match count variance: {set(match_counts)}")
            else:
                print(f"   ✅ Consistent matches: {match_counts[0]}")

        if feature == 'code_templates' and successes > 0:
            code_lens = [r['code_length'] for r in runs if r['success']]
            if len(set(code_lens)) > 1:
                print(f"   ⚠️  Code length variance: {set(code_lens)}")
            else:
                print(f"   ✅ Consistent code: {code_lens[0]} chars")

    # Overall verdict
    print("\n" + "="*70)
    print("OVERALL VERDICT")
    print("="*70)

    total_success_rate = sum(s['success_rate'] for s in summary.values()) / len(summary)

    print(f"\nAverage success rate: {total_success_rate:.1f}%")

    if total_success_rate == 100:
        print("✅ EXCELLENT: All features 100% consistent across 5 runs")
        verdict = "PRODUCTION READY"
    elif total_success_rate >= 95:
        print("✅ VERY GOOD: Features highly consistent (95%+)")
        verdict = "PRODUCTION READY"
    elif total_success_rate >= 80:
        print("⚠️  ACCEPTABLE: Features mostly consistent (80%+)")
        verdict = "NEEDS MONITORING"
    else:
        print("❌ POOR: Features inconsistent (<80%)")
        verdict = "NOT PRODUCTION READY"

    print(f"\nVerdict: {verdict}")
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")

    return total_success_rate >= 95

if __name__ == "__main__":
    success = asyncio.run(run_consistency_tests())
    sys.exit(0 if success else 1)
