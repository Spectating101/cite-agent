#!/bin/bash
# Comprehensive Professor Test Suite for Cite-Agent
# Tests realistic research assistant use cases

export NOCTURNAL_DEBUG=1

echo "==============================================="
echo "CITE-AGENT COMPREHENSIVE PROFESSOR TEST SUITE"
echo "==============================================="
echo ""

# Function to run test and capture results
run_test() {
    local test_num=$1
    local test_name=$2
    local query=$3

    echo "────────────────────────────────────────────────"
    echo "TEST $test_num: $test_name"
    echo "Query: $query"
    echo "────────────────────────────────────────────────"

    echo "$query" | python3 -m cite_agent.cli 2>&1 | tee "test_${test_num}_output.txt"

    # Extract token count
    tokens=$(grep "📊 Tokens used:" "test_${test_num}_output.txt" | tail -1 | awk '{print $4}')
    echo ""
    echo "✓ Test $test_num complete. Tokens: $tokens"
    echo ""
    sleep 2
}

# CATEGORY 1: BASIC FUNCTIONALITY (Foundation)
echo "═══════════════════════════════════════════════"
echo "CATEGORY 1: BASIC FUNCTIONALITY"
echo "═══════════════════════════════════════════════"

run_test "1.1" "Simple greeting" "hi"

run_test "1.2" "Agent capabilities" "what can you help me with?"

run_test "1.3" "Simple factual query" "What is a transformer in deep learning?"

# CATEGORY 2: LITERATURE SEARCH & ANALYSIS
echo "═══════════════════════════════════════════════"
echo "CATEGORY 2: LITERATURE SEARCH & ANALYSIS"
echo "═══════════════════════════════════════════════"

run_test "2.1" "Basic paper search" "Find papers on vision transformers"

run_test "2.2" "Comparative analysis" "Compare BERT and GPT-3 architectures. What are the key differences?"

run_test "2.3" "Recent research query" "Find the most cited papers on diffusion models from 2023-2024"

run_test "2.4" "Synthesis request" "Find 3 papers on neural architecture search and summarize their main contributions"

# CATEGORY 3: FINANCIAL ANALYSIS
echo "═══════════════════════════════════════════════"
echo "CATEGORY 3: FINANCIAL ANALYSIS"
echo "═══════════════════════════════════════════════"

run_test "3.1" "Single company query" "What is NVIDIA's revenue for the most recent quarter?"

run_test "3.2" "Multi-company comparison" "Compare the revenue of NVIDIA and AMD"

run_test "3.3" "Multi-metric analysis" "Show me Apple's revenue, profit, and market cap"

# CATEGORY 4: DATA & FILE OPERATIONS
echo "═══════════════════════════════════════════════"
echo "CATEGORY 4: DATA & FILE OPERATIONS"
echo "═══════════════════════════════════════════════"

run_test "4.1" "Directory exploration" "What files are in the data folder?"

run_test "4.2" "File content query" "What's in the company_tickers.json file in the data folder?"

run_test "4.3" "Script understanding" "What does the build_distribution.py script in scripts/ do?"

# CATEGORY 5: SYNTHESIS & REASONING
echo "═══════════════════════════════════════════════"
echo "CATEGORY 5: SYNTHESIS & REASONING"
echo "═══════════════════════════════════════════════"

run_test "5.1" "Multi-step reasoning" "Find papers on transformers and tell me which one has the most citations"

run_test "5.2" "Contextual synthesis" "Based on recent papers, what are the main challenges in scaling vision transformers?"

run_test "5.3" "Complex comparison" "Compare the research approaches of BERT, ViT, and Swin Transformer. What paradigm shift does each represent?"

echo ""
echo "═══════════════════════════════════════════════"
echo "TEST SUITE COMPLETE"
echo "═══════════════════════════════════════════════"
echo ""
echo "Output files generated: test_*_output.txt"
echo ""
echo "Summary will be generated next..."
