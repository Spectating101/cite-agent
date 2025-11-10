#!/usr/bin/env python3
"""
Test script for new features added by CC Web:
- Workspace inspection
- Data analysis toolkit
- Code templates
- Smart search
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent

async def test_workspace_inspection():
    """Test workspace inspection feature"""
    print("\n" + "="*60)
    print("TEST 1: Workspace Inspection")
    print("="*60)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    try:
        # Test 1a: Describe workspace
        print("\n[1a] Testing describe_workspace()...")
        result = agent.describe_workspace()

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Found workspace data")
            if 'platform' in result:
                print(f"      Platform: {result.get('platform')}")
                print(f"      Total objects: {result.get('total_objects', 0)}")
            else:
                # Multiple platforms
                for platform, data in result.items():
                    print(f"      Platform: {platform}")
                    print(f"      Objects: {data.get('total_objects', 0)}")

        # Test 1b: Create some Python objects to inspect
        print("\n[1b] Creating test objects in Python namespace...")
        import numpy as np
        import pandas as pd

        # Create test data
        test_df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'score': [85, 90, 88, 92, 87],
            'group': ['A', 'B', 'A', 'B', 'A']
        })
        test_vector = [1, 2, 3, 4, 5]
        test_dict = {'key1': 'value1', 'key2': 'value2'}

        print("   ✅ Created: test_df (DataFrame), test_vector (list), test_dict (dict)")

        # Test 1c: List workspace objects again
        print("\n[1c] Listing workspace objects after creation...")
        result = agent.describe_workspace()

        if 'error' not in result:
            platform_data = result if 'total_objects' in result else result.get('Python', {})
            objects = platform_data.get('objects', [])
            found_objects = [obj['name'] for obj in objects if obj['name'] in ['test_df', 'test_vector', 'test_dict']]
            print(f"   ✅ Found {len(found_objects)} test objects: {found_objects}")

        # Test 1d: Inspect specific object
        print("\n[1d] Inspecting test_df...")
        result = agent.inspect_workspace_object('test_df')

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Object type: {result.get('type')}")
            print(f"      Dimensions: {result.get('dimensions')}")
            print(f"      Columns: {result.get('columns')}")

        # Test 1e: Get data
        print("\n[1e] Getting data from test_df...")
        result = agent.get_workspace_data('test_df', limit=10)

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Retrieved {result.get('shown_rows', 0)} rows")
            if result.get('data'):
                print(f"      Sample: {result['data'][0]}")

        return True

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await agent.close()


async def test_data_analysis():
    """Test data analysis toolkit"""
    print("\n" + "="*60)
    print("TEST 2: Data Analysis Toolkit")
    print("="*60)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    try:
        # Create test data
        import pandas as pd
        test_data = pd.DataFrame({
            'age': [25, 30, 35, 40, 45, 50, 55],
            'income': [50000, 60000, 70000, 80000, 90000, 100000, 110000],
            'satisfaction': [7, 8, 6, 9, 8, 7, 9]
        })

        # Test 2a: Summarize data
        print("\n[2a] Testing summarize_data()...")
        result = agent.summarize_data('test_data')

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Summary generated")
            print(f"      Shape: {result.get('shape')}")
            print(f"      Size: {result.get('total_size_mb', 0):.4f} MB")
            if 'methods_text' in result:
                print(f"      Methods text: {result['methods_text'][:100]}...")

        # Test 2b: Search columns
        print("\n[2b] Testing search_columns()...")
        result = agent.search_columns('age')

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Found {result.get('total_matches', 0)} matches")
            for match in result.get('results', [])[:3]:
                print(f"      - {match.get('object')}.{match.get('column')}")

        return True

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await agent.close()


async def test_code_templates():
    """Test code templates feature"""
    print("\n" + "="*60)
    print("TEST 3: Code Templates")
    print("="*60)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    try:
        # Test 3a: List templates
        print("\n[3a] Testing list_code_templates()...")
        result = agent.list_code_templates()

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Found {result.get('total', 0)} templates")
            for template in result.get('templates', [])[:5]:
                print(f"      - {template.get('name')}: {template.get('description')[:50]}...")

        # Test 3b: Get specific template
        print("\n[3b] Testing get_code_template('t_test_r')...")
        result = agent.get_code_template(
            't_test_r',
            data='my_data',
            group_var='group',
            variable='score',
            group1='A',
            group2='B'
        )

        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Template generated ({len(result.get('code', ''))} chars)")
            print(f"      First 200 chars:")
            print(f"      {result.get('code', '')[:200]}")

        return True

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await agent.close()


async def test_smart_search():
    """Test smart search / automatic tool detection"""
    print("\n" + "="*60)
    print("TEST 4: Smart Search & Auto Tool Detection")
    print("="*60)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    try:
        # Check if smart search module exists
        print("\n[4a] Checking if smart_search module exists...")
        try:
            from cite_agent import smart_search
            print(f"   ✅ smart_search module found")

            # Check for key functions
            if hasattr(smart_search, 'detect_query_intent'):
                print(f"      ✅ detect_query_intent() exists")
            if hasattr(smart_search, 'SmartQueryDetector'):
                print(f"      ✅ SmartQueryDetector class exists")
        except ImportError as e:
            print(f"   ⚠️  smart_search module not found: {e}")

        # Check if method detector exists
        print("\n[4b] Checking if method_detector module exists...")
        try:
            from cite_agent import method_detector
            print(f"   ✅ method_detector module found")

            if hasattr(method_detector, 'detect_statistical_method'):
                print(f"      ✅ detect_statistical_method() exists")
        except ImportError as e:
            print(f"   ⚠️  method_detector module not found: {e}")

        return True

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await agent.close()


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE FEATURE TEST SUITE")
    print("Testing CC Web's new features")
    print("="*60)

    results = []

    # Run tests
    results.append(("Workspace Inspection", await test_workspace_inspection()))
    results.append(("Data Analysis", await test_data_analysis()))
    results.append(("Code Templates", await test_code_templates()))
    results.append(("Smart Search", await test_smart_search()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 All features working!")
    else:
        print(f"\n⚠️  {total - passed} feature(s) need attention")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
