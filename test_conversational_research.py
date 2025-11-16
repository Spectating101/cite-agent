#!/usr/bin/env python3
"""
FOCUSED 3-TOPIC ROBUSTNESS TEST WITH PROPER DELAYS

Found issue: Per-minute rate limit kicks in after ~11 requests
Solution: Add 6-second delays between requests to stay under rate limit

Each topic has 4 phases = 12 requests total
With delays: 12 requests spread over 1+ minute = stays under limit
"""

import os
import sys
import asyncio
import time
import json

# Add repo to path if running standalone
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# SET UP ALL 4 CEREBRAS API KEYS
os.environ["CEREBRAS_API_KEY_1"] = "csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj"
os.environ["CEREBRAS_API_KEY_2"] = "csk-edrc3v63k43fe4hdt529ynt4h9mfd9k9wjpjj3nn5pcvm2t4"
os.environ["CEREBRAS_API_KEY_3"] = "csk-ek3cj5jv26hpnd2h65d8955pjmvxctdjknfv6pwehr82pnhr"
os.environ["CEREBRAS_API_KEY_4"] = "csk-n5h26f263vr5rxp9fpn4w8xkfvpc5v9kjdw95vfc8d3x4ce9"
os.environ["USE_LOCAL_KEYS"] = "true"
os.environ["NOCTURNAL_DEBUG"] = "0"

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

# 3 diverse topics for focused testing
RESEARCH_TOPICS = [
    {
        "name": "ESG and Stock Returns",
        "initial_query": "I want to research the relationship between ESG scores and stock returns. Can you find recent papers and tell me what the main findings are?",
        "methodology_query": "What regression model should I use to test if ESG scores predict returns? Be specific about the equation.",
        "implementation_query": "Can you write Python code to run a Fama-MacBeth regression testing if ESG predicts returns? Use pandas and statsmodels. Make sure to test for errors and include error handling.",
        "debug_query": "I got an error 'KeyError: ESG_score'. Can you help me debug this and provide the fixed code?",
    },
    {
        "name": "Machine Learning for Credit Risk",
        "initial_query": "I want to use machine learning to predict credit default. What approaches do recent papers use?",
        "methodology_query": "Should I use random forest or gradient boosting for credit default prediction? What does the literature say?",
        "implementation_query": "Write Python code using sklearn to train a random forest for credit default prediction. Include cross-validation and make sure to handle missing values.",
        "debug_query": "I'm getting 'ValueError: could not convert string to float'. Show me the fixed code with proper data preprocessing.",
    },
    {
        "name": "Volatility Clustering in Forex",
        "initial_query": "I'm researching volatility clustering in forex markets. Find papers on GARCH models for currency pairs.",
        "methodology_query": "Should I use GARCH(1,1) or EGARCH for forex volatility? What's the difference?",
        "implementation_query": "Write Python code using arch package to fit a GARCH(1,1) model to EUR/USD returns. Include model diagnostics.",
        "debug_query": "Getting 'ConvergenceWarning: Maximum Likelihood optimization failed'. Show me the fixed code with better starting values.",
    },
]

DELAY_BETWEEN_REQUESTS = 6  # seconds - to avoid per-minute rate limit

async def test_single_topic(agent, topic, topic_num, total_topics):
    """Test agent on a single research topic - full conversational cycle"""

    print("\n" + "=" * 100)
    print(f"TOPIC {topic_num}/{total_topics}: {topic['name']}")
    print("=" * 100)

    scores = {
        "literature_review": 0,
        "methodology": 0,
        "implementation": 0,
        "debugging": 0,
    }

    # Phase 1: Literature Review
    print(f"\n[PHASE 1: Literature Review]")
    print(f"Researcher: {topic['initial_query'][:80]}...")
    request1 = ChatRequest(question=topic['initial_query'], user_id="researcher")
    response1 = await agent.process_request(request1)

    print(f"Agent response length: {len(response1.response)} chars")
    print(f"Tools: {response1.tools_used}, Tokens: {response1.tokens_used}")

    if 'archive_api' in (response1.tools_used or []) and len(response1.response) > 200:
        scores["literature_review"] = 1
        print("✅ PASS: Found papers via Archive API")
    else:
        print(f"❌ FAIL: No archive ({response1.tools_used}) or too short ({len(response1.response)} chars)")

    print(f"\n⏱️  Waiting {DELAY_BETWEEN_REQUESTS}s...")
    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    # Phase 2: Methodology
    print(f"\n[PHASE 2: Methodology Design]")
    print(f"Researcher: {topic['methodology_query'][:80]}...")
    request2 = ChatRequest(question=topic['methodology_query'], user_id="researcher")
    response2 = await agent.process_request(request2)

    print(f"Agent response length: {len(response2.response)} chars")
    print(f"Tokens: {response2.tokens_used}")

    if len(response2.response) > 150:
        scores["methodology"] = 1
        print("✅ PASS: Provided methodology guidance")
    else:
        print(f"❌ FAIL: Too short ({len(response2.response)} chars)")

    print(f"\n⏱️  Waiting {DELAY_BETWEEN_REQUESTS}s...")
    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    # Phase 3: Code Implementation
    print(f"\n[PHASE 3: Code Implementation]")
    print(f"Researcher: {topic['implementation_query'][:80]}...")
    request3 = ChatRequest(question=topic['implementation_query'], user_id="researcher")
    response3 = await agent.process_request(request3)

    print(f"Agent response length: {len(response3.response)} chars")
    print(f"Tokens: {response3.tokens_used}")

    # Check for code
    has_code = any(kw in response3.response for kw in ['import ', 'def ', '```python', 'import pandas', 'import numpy'])
    has_substance = len(response3.response) > 300

    # Extract code if present
    code_blocks = []
    if '```python' in response3.response:
        parts = response3.response.split('```python')
        for part in parts[1:]:
            if '```' in part:
                code = part.split('```')[0].strip()
                code_blocks.append(code)
                print(f"\n📝 Code block found ({len(code)} chars):")
                print(code[:200] + "..." if len(code) > 200 else code)

    if has_code and has_substance:
        scores["implementation"] = 1
        print(f"✅ PASS: Generated code ({len(code_blocks)} blocks)")
    else:
        print(f"❌ FAIL: No code (has_code={has_code}, len={len(response3.response)})")

    print(f"\n⏱️  Waiting {DELAY_BETWEEN_REQUESTS}s...")
    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    # Phase 4: Debugging
    print(f"\n[PHASE 4: Debugging & Error Handling]")
    print(f"Researcher: {topic['debug_query'][:80]}...")
    request4 = ChatRequest(question=topic['debug_query'], user_id="researcher")
    response4 = await agent.process_request(request4)

    print(f"Agent response length: {len(response4.response)} chars")
    print(f"Tokens: {response4.tokens_used}")

    helpful_debug = any(kw in response4.response.lower() for kw in ['error', 'fix', 'fixed', 'issue', 'problem', 'solution', 'try'])
    has_fix = 'import ' in response4.response or 'def ' in response4.response

    if helpful_debug and len(response4.response) > 100:
        scores["debugging"] = 1
        print(f"✅ PASS: Provided debugging help (has_fix_code={has_fix})")
    else:
        print(f"❌ FAIL: Unhelpful ({helpful_debug=}, len={len(response4.response)})")

    total_score = sum(scores.values())
    print(f"\n📊 Topic Score: {total_score}/4")

    return scores


async def main():
    print("=" * 100)
    print("FOCUSED 3-TOPIC ROBUSTNESS TEST WITH RATE LIMIT HANDLING")
    print(f"Delay between requests: {DELAY_BETWEEN_REQUESTS}s")
    print("=" * 100)

    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print(f"\n✅ Agent initialized with {len(agent.api_keys)} API keys")

    all_scores = []
    start_time = time.time()

    for i, topic in enumerate(RESEARCH_TOPICS, 1):
        topic_start = time.time()
        scores = await test_single_topic(agent, topic, i, len(RESEARCH_TOPICS))
        topic_elapsed = time.time() - topic_start

        all_scores.append({"topic": topic["name"], "scores": scores, "time": topic_elapsed})

        print(f"\n⏱️  Topic completed in {topic_elapsed:.1f}s")
        print(f"   Current API key index: {agent.current_key_index}")

        # Extra delay between topics
        if i < len(RESEARCH_TOPICS):
            print(f"\n⏱️  Inter-topic delay: {DELAY_BETWEEN_REQUESTS}s...\n")
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    total_elapsed = time.time() - start_time

    # Final Summary
    print("\n" + "=" * 100)
    print("FINAL RESULTS")
    print("=" * 100)

    print(f"\n{'Topic':<40} {'Lit':>5} {'Meth':>5} {'Code':>5} {'Debug':>5} {'Total':>5} {'Time':>8}")
    print("-" * 85)

    total_lit = total_meth = total_code = total_debug = 0

    for result in all_scores:
        s = result["scores"]
        total = sum(s.values())
        total_lit += s["literature_review"]
        total_meth += s["methodology"]
        total_code += s["implementation"]
        total_debug += s["debugging"]

        lit_icon = "✅" if s["literature_review"] else "❌"
        meth_icon = "✅" if s["methodology"] else "❌"
        code_icon = "✅" if s["implementation"] else "❌"
        debug_icon = "✅" if s["debugging"] else "❌"

        print(f"{result['topic']:<40} {lit_icon:>5} {meth_icon:>5} {code_icon:>5} {debug_icon:>5} {total:>5}/4 {result['time']:>7.1f}s")

    print("-" * 85)
    print(f"{'TOTAL':<40} {total_lit:>5} {total_meth:>5} {total_code:>5} {total_debug:>5} {total_lit+total_meth+total_code+total_debug:>5}/12 {total_elapsed:>7.1f}s")

    total_possible = len(RESEARCH_TOPICS) * 4
    total_achieved = total_lit + total_meth + total_code + total_debug

    print(f"\n🎯 Overall: {total_achieved}/{total_possible} ({100*total_achieved//total_possible}%)")
    print(f"\n   Literature: {total_lit}/3 ({100*total_lit//3}%)")
    print(f"   Methodology: {total_meth}/3 ({100*total_meth//3}%)")
    print(f"   Implementation: {total_code}/3 ({100*total_code//3}%)")
    print(f"   Debugging: {total_debug}/3 ({100*total_debug//3}%)")
    print(f"\n⏱️  Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")

    if total_achieved == 12:
        print("\n🎉 PERFECT: All checks passed!")
    elif total_achieved >= 10:
        print("\n✅ EXCELLENT: Strong performance!")
    elif total_achieved >= 8:
        print("\n👍 GOOD: Solid performance")
    elif total_achieved >= 6:
        print("\n⚠️  FAIR: Some issues")
    else:
        print("\n❌ POOR: Needs work")

    results_path = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'total_score': total_achieved,
            'total_possible': total_possible,
            'success_rate': total_achieved / total_possible,
            'total_time': total_elapsed,
            'by_category': {'literature_review': total_lit, 'methodology': total_meth, 'implementation': total_code, 'debugging': total_debug},
            'by_topic': all_scores
        }, f, indent=2)

    print(f"\n💾 Saved to: {results_path}")


if __name__ == "__main__":
    asyncio.run(main())
