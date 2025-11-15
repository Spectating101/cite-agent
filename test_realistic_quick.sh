#!/bin/bash
# Quick realistic test - the queries professors ACTUALLY use

echo "=================================="
echo "🎓 REALISTIC PROFESSOR QUERIES"
echo "=================================="

test_query() {
    local num=$1
    local name=$2
    local query=$3
    
    echo ""
    echo "=== TEST $num: $name ==="
    echo "Query: '$query'"
    echo "---"
    
    cite "$query" 2>&1 | head -80
    
    echo ""
    echo "✓ Test $num complete"
    sleep 3
}

# CATEGORY 1: Literature Search (Most Critical)
echo ""
echo "📚 LITERATURE SEARCH"
test_query "1" "Basic paper search" "Find papers on vision transformers"

test_query "2" "Comparative analysis" "Compare BERT and GPT-3 architectures. What are the key differences?"

test_query "3" "Synthesis request" "Find 3 papers on neural architecture search and summarize their main contributions"

# CATEGORY 2: Financial Analysis
echo ""
echo "💰 FINANCIAL ANALYSIS"
test_query "4" "Single company" "What is NVIDIA's revenue for the most recent quarter?"

test_query "5" "Multi-company comparison" "Compare the revenue of NVIDIA and AMD"

test_query "6" "Profit calculation" "What is Apple's profit margin?"

# CATEGORY 3: Multi-step Reasoning
echo ""
echo "🧠 MULTI-STEP REASONING"
test_query "7" "Find + analyze" "Find papers on transformers and tell me which one has the most citations"

test_query "8" "Research synthesis" "Based on recent papers, what are the main challenges in scaling vision transformers?"

echo ""
echo "=================================="
echo "✅ QUICK REALISTIC TEST COMPLETE"
echo "=================================="
