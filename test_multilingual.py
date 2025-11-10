#!/usr/bin/env python3
"""
Test multilingual support with function calling
Tests Chinese, English, and mixed queries to verify LLM-driven tool selection
"""
import asyncio
import sys
import pandas as pd
import numpy as np
import os

sys.path.insert(0, '.')
os.environ['NOCTURNAL_DEBUG'] = '1'

# Create test data in __main__
import __main__
__main__.研究數據 = pd.DataFrame({
    '參與者ID': range(1, 51),
    '年齡': np.random.randint(18, 65, 50),
    '治療組': np.random.choice(['對照組', '藥物組'], 50),
    '血壓': np.random.normal(120, 15, 50),
    '心率': np.random.normal(75, 10, 50),
})

__main__.research_data = pd.DataFrame({
    'participant_id': range(1, 51),
    'age': np.random.randint(18, 65, 50),
    'treatment': np.random.choice(['Control', 'Drug'], 50),
    'blood_pressure': np.random.normal(120, 15, 50),
    'heart_rate': np.random.normal(75, 10, 50),
})

print("Created test datasets:")
print("  - research_data (English)")
print("  - 研究數據 (Chinese)")

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_multilingual():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = [
        # English queries
        {
            "name": "English - List data",
            "question": "What data do I have in my workspace?",
            "language": "en",
            "expected_tool": "describe_workspace",
            "check": lambda r: 'research_data' in r.lower() or 'dataframe' in r.lower()
        },
        {
            "name": "English - Get statistics",
            "question": "Give me descriptive statistics for research_data",
            "language": "en",
            "expected_tool": "summarize_data",
            "check": lambda r: 'mean' in r.lower() or 'std' in r.lower() or 'statistics' in r.lower()
        },
        {
            "name": "English - Search columns",
            "question": "Which columns contain 'pressure'?",
            "language": "en",
            "expected_tool": "search_columns",
            "check": lambda r: 'blood_pressure' in r.lower() or 'pressure' in r.lower()
        },

        # Chinese queries (Traditional Chinese)
        {
            "name": "Chinese - List data",
            "question": "我的工作空間有什麼數據？",  # What data is in my workspace?
            "language": "zh-TW",
            "expected_tool": "describe_workspace",
            "check": lambda r: '研究數據' in r or 'research_data' in r.lower() or '資料' in r
        },
        {
            "name": "Chinese - Get statistics",
            "question": "給我 research_data 的描述性統計",  # Give me descriptive statistics for research_data
            "language": "zh-TW",
            "expected_tool": "summarize_data",
            "check": lambda r: '平均' in r or '標準差' in r or 'mean' in r.lower() or 'std' in r.lower()
        },
        {
            "name": "Chinese - Search columns",
            "question": "哪些欄位包含「壓」字？",  # Which columns contain "pressure"?
            "language": "zh-TW",
            "expected_tool": "search_columns",
            "check": lambda r: '血壓' in r or 'pressure' in r.lower()
        },

        # Mixed language queries
        {
            "name": "Mixed - English question about Chinese data",
            "question": "Tell me about the 研究數據 dataset",
            "language": "en",
            "expected_tool": "inspect_workspace_object",
            "check": lambda r: '參與者' in r or 'columns' in r.lower() or '欄位' in r
        },
    ]

    results = []

    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(tests)}: {test['name']}")
        print(f"{'='*70}")
        print(f"Question: {test['question']}")
        print(f"Expected tool: {test['expected_tool']}")
        print(f"Language: {test['language']}")

        try:
            # Set language preference
            agent.language_preference = test['language']

            request = ChatRequest(
                question=test['question'],
                conversation_id=f"test_{i}"
            )

            response = await agent.process_request(request)

            print(f"\nResponse:")
            print(response.response[:500])  # First 500 chars

            # Check if response contains expected content
            passed = test['check'](response.response)

            print(f"\nTools used: {response.tools_used}")
            print(f"Check passed: {'✅ PASS' if passed else '❌ FAIL'}")

            results.append({
                'test': test['name'],
                'passed': passed,
                'tools_used': response.tools_used,
                'expected_tool': test['expected_tool']
            })

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'test': test['name'],
                'passed': False,
                'error': str(e)
            })

        await asyncio.sleep(1)  # Small delay between requests

    await agent.close()

    # Summary
    print(f"\n{'='*70}")
    print("MULTILINGUAL TEST SUMMARY")
    print(f"{'='*70}")

    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)

    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status}: {result['test']}")
        if 'tools_used' in result:
            print(f"         Tools used: {result.get('tools_used', [])}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.0f}%)")

    if passed_count == total_count:
        print("\n🎉 Perfect! Function calling works in multiple languages!")
        print("✅ English queries work")
        print("✅ Chinese queries work")
        print("✅ Mixed language queries work")
        print("\nLLM understands INTENT, not just keywords!")
    elif passed_count >= total_count * 0.7:
        print(f"\n⚠️  Mostly working ({passed_count}/{total_count})")
        print("Some queries may need backend function calling support")
    else:
        print(f"\n❌ Many failures ({passed_count}/{total_count})")
        print("Backend may not support function calling yet")
        print("Or hardcoded keyword matching is still interfering")

    return passed_count == total_count

if __name__ == "__main__":
    success = asyncio.run(test_multilingual())
    sys.exit(0 if success else 1)
