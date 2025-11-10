#!/usr/bin/env python3
"""
Test agent intelligence WITH proper environment setup
"""
import os
import sys
from pathlib import Path

# Load .env.local FIRST
from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env.local'
if env_file.exists():
    load_dotenv(env_file, override=True)
    print(f"✅ Loaded {env_file}")
    print(f"   USE_LOCAL_KEYS={os.getenv('USE_LOCAL_KEYS')}")
    print(f"   CEREBRAS_API_KEY_1={os.getenv('CEREBRAS_API_KEY_1', 'NOT SET')[:20]}...")
    print(f"   CEREBRAS_API_KEY_2={os.getenv('CEREBRAS_API_KEY_2', 'NOT SET')[:20]}...")
else:
    print(f"❌ {env_file} not found")
    sys.exit(1)

# Now run the test
import asyncio
import pandas as pd
import numpy as np
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

# Create test data in __main__
import __main__
__main__.research_data = pd.DataFrame({
    'participant_id': range(1, 51),
    'age': np.random.randint(18, 65, 50),
    'score': np.random.normal(100, 15, 50),
    'condition': np.random.choice(['control', 'treatment'], 50)
})

async def test_intelligence():
    """Test if agent automatically uses features"""
    print("\n" + "="*70)
    print("AGENT INTELLIGENCE TEST - With Cerebras Keys Loaded")
    print("="*70)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print(f"\n🔍 Agent status:")
    print(f"   Client initialized: {agent.client is not None}")
    print(f"   API keys loaded: {len(agent.api_keys) if hasattr(agent, 'api_keys') else 0}")
    print(f"   Provider: {getattr(agent, 'llm_provider', 'unknown')}")

    tests = [
        {
            'name': 'Workspace listing',
            'query': 'What data do I have in my workspace?',
            'expected_tool': 'workspace_inspection',
            'check': lambda r: 'research_data' in r.response.lower()
        },
        {
            'name': 'Object inspection',
            'query': 'Tell me about the research_data dataset',
            'expected_tool': 'object_inspection',
            'check': lambda r: 'participant_id' in r.response.lower() or 'age' in r.response.lower()
        },
        {
            'name': 'Statistical summary',
            'query': 'Give me statistics for research_data',
            'expected_tool': 'data_summary',
            'check': lambda r: 'mean' in r.response.lower() or 'std' in r.response.lower()
        }
    ]

    results = []

    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"Query: {test['query']}")

        try:
            request = ChatRequest(question=test['query'], user_id='test')
            response = await agent.process_request(request)

            print(f"\nAgent response:")
            print(response.response[:200])
            print(f"\nTools used: {response.tools_used}")

            passed = test['check'](response) if response.tools_used else False

            results.append({
                'test': test['name'],
                'passed': passed,
                'tools_used': response.tools_used
            })

            print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: {test['name']}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                'test': test['name'],
                'passed': False,
                'error': str(e)
            })

    await agent.close()

    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        print(f"{status}: {r['test']}")

    print(f"\nAgent Intelligence: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n✅ Agent successfully uses features automatically!")
        return True
    else:
        print("\n❌ Agent doesn't automatically use all features")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_intelligence())
    sys.exit(0 if success else 1)
