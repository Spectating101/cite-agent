#!/usr/bin/env python3
"""
Test multilingual support with proper environment setup
"""
import os
import sys
from pathlib import Path

# Load .env.local FIRST
from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env.local'
load_dotenv(env_file, override=True)

import asyncio
import pandas as pd
import numpy as np
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

# Create test data
import __main__
__main__.research_data = pd.DataFrame({
    'participant_id': range(1, 31),
    'age': np.random.randint(20, 60, 30),
    'score': np.random.normal(75, 10, 30)
})

async def test_multilingual():
    """Test if agent works in multiple languages"""
    print("\n" + "="*70)
    print("MULTILINGUAL SUPPORT TEST")
    print("="*70)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = [
        {
            'language': 'English',
            'query': 'What data do I have?',
            'expected': 'research_data'
        },
        {
            'language': 'Chinese (Traditional)',
            'query': '我有什麼數據？',
            'expected': 'research_data'
        },
        {
            'language': 'Chinese (Simplified)',
            'query': '我有什么数据？',
            'expected': 'research_data'
        },
        {
            'language': 'Spanish',
            'query': '¿Qué datos tengo?',
            'expected': 'research_data'
        }
    ]

    results = []

    for test in tests:
        print(f"\n{'='*70}")
        print(f"Testing: {test['language']}")
        print(f"{'='*70}")
        print(f"Query: {test['query']}")

        try:
            request = ChatRequest(question=test['query'], user_id='test')
            response = await agent.process_request(request)

            print(f"\nResponse:")
            print(response.response[:300])
            print(f"\nTools used: {response.tools_used}")

            passed = test['expected'].lower() in response.response.lower()
            results.append({
                'language': test['language'],
                'passed': passed
            })

            print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                'language': test['language'],
                'passed': False
            })

    await agent.close()

    # Summary
    print(f"\n{'='*70}")
    print("MULTILINGUAL TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        print(f"{status}: {r['language']}")

    print(f"\nMultilingual Support: {passed}/{total} languages working ({passed/total*100:.0f}%)")

    if passed >= total * 0.75:  # 75% pass rate
        print("\n✅ Multilingual support working!")
        return True
    else:
        print("\n❌ Multilingual support needs improvement")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multilingual())
    sys.exit(0 if success else 1)
