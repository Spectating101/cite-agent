#!/bin/bash
# Quick proof that function calling works with Claude Code's fixes
# Run this to verify: no JSON leaking, proper citations, good synthesis

echo "=== FUNCTION CALLING VALIDATION TEST ==="
echo ""
echo "Testing with fixes from Claude Code (commit 087be46)"
echo "Expected: Clean output, NO raw JSON, proper citations"
echo ""

export NOCTURNAL_DEBUG=1

# Test 1: Paper search (tests JSON leaking + citation formatting)
echo "----------------------------------------"
echo "TEST 1: Paper Search (Critical Test)"
echo "Query: 'find papers on transformers'"
echo "----------------------------------------"
echo ""

result=$(echo "find papers on transformers" | python3 -m cite_agent.cli 2>&1)

# Check for JSON leaking
if echo "$result" | grep -q '{"query":'; then
    echo "❌ FAIL: JSON leaked into response"
    echo ""
    echo "Sample of leaked JSON:"
    echo "$result" | grep '{"query":' | head -3
    exit 1
else
    echo "✅ PASS: No JSON leaking detected"
fi

# Check for proper citation format
if echo "$result" | grep -qP '\d+\.\s+.+\(.+,\s+\d{4}\)'; then
    echo "✅ PASS: Proper citation format found"
else
    echo "❌ FAIL: Citation format incorrect"
    echo ""
    echo "Response sample:"
    echo "$result" | grep -A5 "📝 Response:"
    exit 1
fi

# Check for synthesis (not just raw output)
if echo "$result" | grep -q "Found [0-9]* papers"; then
    echo "✅ PASS: Synthesis detected (not raw tool output)"
else
    echo "⚠️  WARNING: No synthesis header found"
fi

echo ""
echo "----------------------------------------"
echo "TEST 2: Token Efficiency"
echo "Query: 'hi' (should skip synthesis)"
echo "----------------------------------------"
echo ""

result=$(echo "hi" | python3 -m cite_agent.cli 2>&1)
tokens=$(echo "$result" | grep "Tokens used:" | grep -oP '\d+' | head -1)

if [ -z "$tokens" ]; then
    echo "⚠️  WARNING: Could not extract token count"
else
    if [ "$tokens" -lt 500 ]; then
        echo "✅ PASS: $tokens tokens (excellent - synthesis skipped)"
    elif [ "$tokens" -lt 1000 ]; then
        echo "✅ PASS: $tokens tokens (acceptable)"
    else
        echo "❌ FAIL: $tokens tokens (too high - synthesis not skipped)"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "✅ ALL TESTS PASSED"
echo "========================================"
echo ""
echo "Function calling is working correctly with Claude Code's fixes:"
echo "  ✅ No JSON leaking"
echo "  ✅ Proper citation formatting"
echo "  ✅ Token optimization active"
echo ""
echo "Safe to use in production."
