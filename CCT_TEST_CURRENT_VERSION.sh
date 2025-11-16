#!/bin/bash
################################################################################
# CCT TEST SCRIPT - CURRENT WORKING VERSION
#
# This tests commit 600ad3d which has traditional mode working perfectly
#
# SETUP INSTRUCTIONS FOR CCT:
# 1. git pull origin claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
# 2. git checkout 600ad3d  # Make sure you're on the right commit
# 3. chmod +x CCT_TEST_CURRENT_VERSION.sh
# 4. ./CCT_TEST_CURRENT_VERSION.sh
#
################################################################################

echo "════════════════════════════════════════════════════════════════════════════════"
echo "CCT TEST - CURRENT WORKING VERSION (commit 600ad3d)"
echo "════════════════════════════════════════════════════════════════════════════════"

# Check we're on the right commit
CURRENT_COMMIT=$(git rev-parse --short HEAD)
if [ "$CURRENT_COMMIT" != "600ad3d" ]; then
    echo "⚠️  WARNING: You're on commit $CURRENT_COMMIT, not 600ad3d"
    echo "   Run: git checkout 600ad3d"
    echo ""
fi

# Check git status
echo ""
echo "📋 Git Status:"
git status --short
echo ""

# Set environment variables
export CEREBRAS_API_KEY_1='csk-edrc3v63k43fe4hdt529ynt4h9mfd9k9wjpjj3nn5pcvm2t4'
export CEREBRAS_API_KEY_2='csk-ek3cj5jv26hpnd2h65d8955pjmvxctdjknfv6pwehr82pnhr'
export CEREBRAS_API_KEY_3='csk-n5h26f263vr5rxp9fpn4w8xkfvpc5v9kjdw95vfc8d3x4ce9'
export USE_LOCAL_KEYS='true'
export NOCTURNAL_DEBUG='0'

echo "✅ Environment configured:"
echo "   - CEREBRAS_API_KEY_1: ${CEREBRAS_API_KEY_1:0:25}..."
echo "   - USE_LOCAL_KEYS: $USE_LOCAL_KEYS"
echo ""

# Run tests
timeout 180 python3 << 'PYEOF'
import asyncio
import os
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def run_tests():
    print("═" * 80)
    print("RUNNING 3 TESTS")
    print("═" * 80)

    agent = EnhancedNocturnalAgent()

    tests = [
        {
            "name": "Research Query",
            "question": "Find papers on vision transformers",
            "expected": "Should find papers about Vision Transformer (ViT) architecture"
        },
        {
            "name": "Financial Query",
            "question": "What is Apple's profit margin?",
            "expected": "Should calculate ~24.9% profit margin from SEC data"
        },
        {
            "name": "Generic Query",
            "question": "What is 2+2?",
            "expected": "Should answer: 4"
        }
    ]

    results = []

    for i, test in enumerate(tests, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}/3: {test['name']}")
        print(f"Question: {test['question']}")
        print(f"Expected: {test['expected']}")
        print(f"{'─' * 80}")

        try:
            request = ChatRequest(question=test['question'])
            response = await agent.process_request(request)

            # Show results
            print(f"\n✅ SUCCESS")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Tools: {response.tools_used}")
            print(f"\n📄 Response (first 300 chars):")
            print(f"   {response.response[:300]}...")

            # Validate response quality
            is_valid = False
            if i == 1:  # Research
                is_valid = response.tokens_used > 1000 and "transform" in response.response.lower()
            elif i == 2:  # Financial
                is_valid = "24" in response.response or "profit" in response.response.lower()
            elif i == 3:  # Generic
                is_valid = "4" in response.response

            results.append({
                "test": test['name'],
                "passed": is_valid,
                "tokens": response.tokens_used
            })

            print(f"\n{'✅ PASS' if is_valid else '❌ FAIL'} - Response quality check")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                "test": test['name'],
                "passed": False,
                "tokens": 0
            })

        # Small delay between tests
        await asyncio.sleep(1)

    # Summary
    print(f"\n{'═' * 80}")
    print("TEST SUMMARY")
    print(f"{'═' * 80}")

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        print(f"{status} - {r['test']} ({r['tokens']} tokens)")

    print(f"\n📊 OVERALL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The agent is working correctly.")
    elif passed >= total * 0.66:
        print("\n⚠️  Most tests passed. Check failed tests above.")
    else:
        print("\n❌ TESTS FAILING. This version may have issues.")

    print(f"{'═' * 80}")

asyncio.run(run_tests())
PYEOF

TEST_EXIT=$?

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
if [ $TEST_EXIT -eq 0 ]; then
    echo "✅ Test script completed successfully"
else
    echo "❌ Test script failed with exit code: $TEST_EXIT"
fi
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 NEXT STEPS FOR CCT:"
echo "   1. Review the test results above"
echo "   2. If tests pass: This version (600ad3d) is working correctly"
echo "   3. If tests fail: Check environment variables and git commit"
echo "   4. Report findings back to user"
echo "════════════════════════════════════════════════════════════════════════════════"

exit $TEST_EXIT
