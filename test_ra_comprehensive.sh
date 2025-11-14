#!/bin/bash
# Comprehensive Research Assistant Testing Suite
# Tests real-world RA workflows, not just simple queries

echo "=================================="
echo "🧪 RESEARCH ASSISTANT COMPREHENSIVE TEST SUITE"
echo "=================================="
echo ""

# Test 1: Academic Paper Search and Analysis
echo "=== TEST 1: Academic Paper Search ==="
echo "Query: 'Find recent papers on transformer attention mechanisms'"
cite "Find recent papers on transformer attention mechanisms" 2>&1 | head -50
echo ""
echo "---"
echo ""

# Test 2: Financial Data Retrieval
echo "=== TEST 2: Financial Data Analysis ==="
echo "Query: 'What was Apple's revenue growth in the last 3 years?'"
cite "What was Apple's revenue growth in the last 3 years?" 2>&1 | head -50
echo ""
echo "---"
echo ""

# Test 3: File Operations - List and Read
echo "=== TEST 3: File Operations ==="
echo "Query: 'Show me all Python files in cite_agent directory'"
cite "Show me all Python files in cite_agent directory" 2>&1 | head -50
echo ""
echo "---"
echo ""

# Test 4: Multi-step Research Query
echo "=== TEST 4: Multi-Step Research ==="
echo "Query: 'Find papers on GPT-4 architecture and summarize the key innovations'"
cite "Find papers on GPT-4 architecture and summarize the key innovations" 2>&1 | head -80
echo ""
echo "---"
echo ""

# Test 5: Combined Research (Papers + Financial)
echo "=== TEST 5: Combined Research Query ==="
echo "Query: 'Find papers on AI chip manufacturing and compare NVIDIA vs AMD revenue'"
cite "Find papers on AI chip manufacturing and compare NVIDIA vs AMD revenue" 2>&1 | head -80
echo ""
echo "---"
echo ""

# Test 6: Data Analysis Request
echo "=== TEST 6: Data Analysis ==="
echo "Query: 'Compare Microsoft and Google profit margins'"
cite "Compare Microsoft and Google profit margins" 2>&1 | head -50
echo ""
echo "---"
echo ""

# Test 7: File Analysis
echo "=== TEST 7: Code Analysis ==="
echo "Query: 'Read the main function in cite_agent/cli.py and explain what it does'"
cite "Read the main function in cite_agent/cli.py and explain what it does" 2>&1 | head -60
echo ""
echo "---"
echo ""

# Test 8: Complex Multi-Tool Query
echo "=== TEST 8: Complex Multi-Tool Query ==="
echo "Query: 'Search for papers on RAG systems, find setup.py in the repo, and check if we have any documentation files'"
cite "Search for papers on RAG systems, find setup.py in the repo, and check if we have any documentation files" 2>&1 | head -100
echo ""
echo "=================================="
echo "✅ COMPREHENSIVE TEST SUITE COMPLETE"
echo "=================================="
