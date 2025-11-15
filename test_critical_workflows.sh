#!/bin/bash
# CRITICAL TEST: Financial calculations on the CORRECT branch

echo "========================================"
echo "🔥 CRITICAL WORKFLOW TESTS"
echo "Testing on: claude/repo-cleanup branch"
echo "========================================"

test_financial() {
    echo ""
    echo "TEST: $1"
    echo "Query: $2"
    echo "---"
    cite "$2" 2>&1 | head -60
    echo ""
    read -p "PASS? (y/n): " result
    echo "$result"
}

# Test 1: Profit margin calculation (MY FIX)
test_financial "Profit Margin" "What is Apple's profit margin?"

# Test 2: Multi-company comparison
test_financial "Revenue Comparison" "Compare NVIDIA and AMD revenue"

# Test 3: Research synthesis
test_financial "Research Synthesis" "Compare BERT and GPT-3 architectures. What are the key differences?"

echo ""
echo "========================================"
echo "DONE - Manual verification required"
echo "========================================"
