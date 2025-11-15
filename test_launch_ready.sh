#!/bin/bash
# LAUNCH-READY TEST SUITE
# Natural language queries covering all critical use cases
# No fucking around with edge cases - test what professors actually need

echo "================================================"
echo "🚀 LAUNCH-READY TEST SUITE"
echo "================================================"
echo "Testing realistic professor workflows"
echo ""

PASS=0
FAIL=0
TOTAL=0

test_query() {
    local num=$1
    local category=$2
    local query=$3
    local expected=$4

    TOTAL=$((TOTAL + 1))

    echo ""
    echo "════════════════════════════════════════════════"
    echo "TEST $num: $category"
    echo "════════════════════════════════════════════════"
    echo "Query: \"$query\""
    echo "Expected: $expected"
    echo "────────────────────────────────────────────────"

    response=$(cite "$query" 2>&1)
    echo "$response"

    # Manual verification prompt
    echo ""
    echo "────────────────────────────────────────────────"
    read -p "Did this PASS? (y/n): " result

    if [[ "$result" == "y" || "$result" == "Y" ]]; then
        echo "✅ PASS"
        PASS=$((PASS + 1))
    else
        echo "❌ FAIL"
        FAIL=$((FAIL + 1))
    fi

    sleep 2
}

# ============================================================================
# CATEGORY 1: FINANCIAL ANALYSIS (Core Professor Use Case)
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  CATEGORY 1: FINANCIAL ANALYSIS                ║"
echo "╚════════════════════════════════════════════════╝"

test_query "1.1" "Single company revenue" \
    "What is NVIDIA's revenue for the most recent quarter?" \
    "Shows revenue amount with date and SEC source"

test_query "1.2" "Profit margin calculation" \
    "What is Apple's profit margin?" \
    "Shows percentage WITH formula and calculation steps"

test_query "1.3" "Multi-company comparison" \
    "Compare the revenue of NVIDIA and AMD" \
    "Shows both revenues, difference, and ratio"

test_query "1.4" "Margin comparison" \
    "Compare Microsoft and Google profit margins" \
    "Shows both margins with formulas, declares winner"

test_query "1.5" "Growth analysis" \
    "What is Amazon's revenue and profit margin?" \
    "Shows revenue AND calculated margin (not just raw data)"

# ============================================================================
# CATEGORY 2: LITERATURE SEARCH (Core Professor Use Case)
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  CATEGORY 2: LITERATURE SEARCH                 ║"
echo "╚════════════════════════════════════════════════╝"

test_query "2.1" "Basic paper search" \
    "Find papers on vision transformers" \
    "Shows real papers with authors, venue, year"

test_query "2.2" "Comparative analysis" \
    "Compare BERT and GPT-3 architectures. What are the key differences?" \
    "Lists 3+ architectural differences clearly"

test_query "2.3" "Research synthesis" \
    "Based on recent papers, what are the main challenges in scaling vision transformers?" \
    "Synthesizes challenges from multiple sources"

test_query "2.4" "Specific topic search" \
    "Find papers on attention mechanisms in transformers" \
    "Shows relevant papers, not off-topic results"

test_query "2.5" "Author search" \
    "Find recent papers by Yoshua Bengio" \
    "Shows papers by that author OR says none found (no hallucination)"

# ============================================================================
# CATEGORY 3: MULTI-STEP REASONING (Advanced Use Case)
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  CATEGORY 3: MULTI-STEP REASONING              ║"
echo "╚════════════════════════════════════════════════╝"

test_query "3.1" "Find + analyze" \
    "Find papers on transformers and tell me which one has the most citations" \
    "Shows papers AND identifies most cited (or tries web search)"

test_query "3.2" "Research + finance combo" \
    "Find papers on AI chip manufacturing and compare NVIDIA vs AMD revenue" \
    "Attempts both research AND financial data"

test_query "3.3" "Synthesis request" \
    "Find 3 papers on neural architecture search and summarize their main contributions" \
    "Shows 3 papers with summaries OR gracefully says none found"

# ============================================================================
# CATEGORY 4: FILE OPERATIONS (Utility Use Case)
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  CATEGORY 4: FILE OPERATIONS                   ║"
echo "╚════════════════════════════════════════════════╝"

test_query "4.1" "List Python files" \
    "Show me all Python files in cite_agent directory" \
    "Lists .py files in cite_agent/"

test_query "4.2" "Read specific function" \
    "Read the main function in cite_agent/cli.py and explain what it does" \
    "Shows function code AND explains purpose"

test_query "4.3" "File content" \
    "What's in the README.md file?" \
    "Shows README content or summary"

# ============================================================================
# CATEGORY 5: CONVERSATIONAL (User Experience)
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  CATEGORY 5: CONVERSATIONAL                    ║"
echo "╚════════════════════════════════════════════════╝"

test_query "5.1" "Simple greeting" \
    "hi" \
    "Friendly response, low tokens (~1000-1500)"

test_query "5.2" "Capabilities question" \
    "what can you help me with?" \
    "Lists capabilities (research, finance, files)"

test_query "5.3" "Clarification handling" \
    "Compare them" \
    "Asks for clarification (who to compare?)"

# ============================================================================
# RESULTS SUMMARY
# ============================================================================

echo ""
echo "════════════════════════════════════════════════"
echo "📊 FINAL RESULTS"
echo "════════════════════════════════════════════════"
echo "Total Tests:  $TOTAL"
echo "Passed:       $PASS"
echo "Failed:       $FAIL"
echo "Pass Rate:    $(awk "BEGIN {printf \"%.1f\", ($PASS/$TOTAL)*100}")%"
echo "════════════════════════════════════════════════"

if (( $(awk "BEGIN {print ($PASS/$TOTAL*100 >= 90)}") )); then
    echo "✅ LAUNCH READY (≥90% pass rate)"
elif (( $(awk "BEGIN {print ($PASS/$TOTAL*100 >= 80)}") )); then
    echo "⚠️  BORDERLINE (80-90% pass rate) - Review failures"
else
    echo "❌ NOT READY (<80% pass rate) - Fix critical issues"
fi

echo ""
echo "Detailed results saved to test_launch_results.log"
