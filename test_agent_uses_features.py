#!/usr/bin/env python3
"""
Test if the agent ACTUALLY USES the new features intelligently
Not just if the features exist, but if the agent knows to call them
"""

import asyncio
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, '.')

# Create test data in __main__ namespace
import __main__
__main__.research_data = pd.DataFrame({
    'participant_id': range(1, 51),
    'age': np.random.randint(18, 65, 50),
    'treatment': np.random.choice(['Control', 'Drug'], 50),
    'blood_pressure': np.random.normal(120, 15, 50),
    'heart_rate': np.random.normal(75, 10, 50),
})

print("Created test dataset 'research_data' with 50 participants")

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_agent_intelligence():
    """Test if agent actually uses new features"""

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    tests = []

    # Test 1: Does agent recognize workspace query?
    print("\n" + "="*70)
    print("TEST 1: Does agent list workspace when asked?")
    print("="*70)

    request = ChatRequest(
        question="What data do I have in my workspace?",
        conversation_id="test_conv"
    )

    try:
        response = await agent.process_request(request)
        print(f"\nAgent response:\n{response.response}\n")

        # Check if response mentions the dataframe
        mentions_data = 'research_data' in response.response.lower() or 'dataframe' in response.response.lower()
        tools_used = response.metadata.get('tools_used', []) if hasattr(response, 'metadata') else []

        print(f"Tools used: {tools_used}")
        print(f"Mentions data: {mentions_data}")
        tests.append(("Workspace listing", mentions_data or 'workspace' in str(tools_used)))

    except Exception as e:
        print(f"ERROR: {e}")
        tests.append(("Workspace listing", False))

    # Test 2: Does agent inspect objects when asked about them?
    print("\n" + "="*70)
    print("TEST 2: Does agent inspect when asked about specific data?")
    print("="*70)

    request = ChatRequest(
        question="Tell me about the research_data dataset - what columns does it have?",
        conversation_id="test_conv"
    )

    try:
        response = await agent.process_request(request)
        print(f"\nAgent response:\n{response.response}\n")

        # Check if it mentions actual column names
        mentions_columns = any(col in response.response for col in ['participant_id', 'age', 'treatment', 'blood_pressure', 'heart_rate'])
        tools_used = response.metadata.get('tools_used', []) if hasattr(response, 'metadata') else []

        print(f"Tools used: {tools_used}")
        print(f"Mentions actual columns: {mentions_columns}")
        tests.append(("Object inspection", mentions_columns))

    except Exception as e:
        print(f"ERROR: {e}")
        tests.append(("Object inspection", False))

    # Test 3: Does agent provide statistical summary when asked?
    print("\n" + "="*70)
    print("TEST 3: Does agent summarize data when asked for statistics?")
    print("="*70)

    request = ChatRequest(
        question="Give me descriptive statistics for the research_data",
        conversation_id="test_conv"
    )

    try:
        response = await agent.process_request(request)
        print(f"\nAgent response:\n{response.response}\n")

        # Check if it provides actual statistics
        has_stats = any(word in response.response.lower() for word in ['mean', 'std', 'standard deviation', 'm=', 'sd='])
        tools_used = response.metadata.get('tools_used', []) if hasattr(response, 'metadata') else []

        print(f"Tools used: {tools_used}")
        print(f"Has statistics: {has_stats}")
        tests.append(("Statistical summary", has_stats))

    except Exception as e:
        print(f"ERROR: {e}")
        tests.append(("Statistical summary", False))

    # Test 4: Does agent suggest code templates?
    print("\n" + "="*70)
    print("TEST 4: Does agent provide code when asked for analysis?")
    print("="*70)

    request = ChatRequest(
        question="I want to compare blood_pressure between Control and Drug groups. Give me R code for a t-test.",
        conversation_id="test_conv"
    )

    try:
        response = await agent.process_request(request)
        print(f"\nAgent response:\n{response.response}\n")

        # Check if it provides code
        has_code = 't.test' in response.response or 'shapiro.test' in response.response or '```' in response.response
        tools_used = response.metadata.get('tools_used', []) if hasattr(response, 'metadata') else []

        print(f"Tools used: {tools_used}")
        print(f"Has R code: {has_code}")
        tests.append(("Code templates", has_code))

    except Exception as e:
        print(f"ERROR: {e}")
        tests.append(("Code templates", False))

    # Test 5: Does agent search columns?
    print("\n" + "="*70)
    print("TEST 5: Does agent find columns when asked?")
    print("="*70)

    request = ChatRequest(
        question="Which columns in my data contain 'pressure'?",
        conversation_id="test_conv"
    )

    try:
        response = await agent.process_request(request)
        print(f"\nAgent response:\n{response.response}\n")

        # Check if it mentions blood_pressure
        mentions_bp = 'blood_pressure' in response.response.lower()
        tools_used = response.metadata.get('tools_used', []) if hasattr(response, 'metadata') else []

        print(f"Tools used: {tools_used}")
        print(f"Found column: {mentions_bp}")
        tests.append(("Column search", mentions_bp))

    except Exception as e:
        print(f"ERROR: {e}")
        tests.append(("Column search", False))

    await agent.close()

    # Summary
    print("\n" + "="*70)
    print("INTELLIGENCE TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nAgent Intelligence: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed >= 4:
        print("\n🎉 Agent intelligently uses new features!")
    elif passed >= 2:
        print("\n⚠️  Agent partially uses features - may need prompt engineering")
    else:
        print("\n❌ Agent doesn't automatically use features - integration issue")

    return passed >= 4

if __name__ == "__main__":
    success = asyncio.run(test_agent_intelligence())
    sys.exit(0 if success else 1)
