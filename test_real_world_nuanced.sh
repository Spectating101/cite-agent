#!/bin/bash
# Real-World Nuanced Testing - Interactive cite-agent test with all edge cases

cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent
rm -f ~/.nocturnal_archive/session.json

export $(cat .env.local | grep -v '^#' | xargs)
export NOCTURNAL_FUNCTION_CALLING=1
export NOCTURNAL_DEBUG=1

echo "======================================================================"
echo "REAL-WORLD NUANCED TESTING - cite-agent v1.4.13"
echo "Testing: Backend busy, empty answers, full toolset, edge cases"
echo "======================================================================"
echo ""

# Test 1: File reading with proper syntax
echo "TEST 1: File Operations"
echo "Query: show me README.md"
echo "show me README.md" | timeout 30 cite-agent 2>&1 | grep -E "Agent:|README|error" | head -5
echo ""

# Test 2: Multi-step with progress indicators
echo "TEST 2: Multi-step query with progress"
echo "Query: list python files then read setup.py"
echo "list python files in cite_agent folder" | timeout 30 cite-agent 2>&1 | grep -E "💭|🔧|Processing|\.py" | head -10
echo ""

# Test 3: Data analysis (if CSV exists)
echo "TEST 3: Data loading"
echo "Query: load sample_data.csv"
echo "load sample_data.csv" | timeout 30 cite-agent 2>&1 | grep -E "Agent:|data|error|csv" | head -5
echo ""

# Test 4: Error handling - non-existent file
echo "TEST 4: Error handling (non-existent file)"
echo "Query: show me nonexistent_file_xyz.txt"
echo "show me nonexistent_file_xyz.txt" | timeout 20 cite-agent 2>&1 | grep -E "Agent:|error|not found|does not exist" | head -3
echo ""

# Test 5: Empty query
echo "TEST 5: Empty query handling"
echo "" | timeout 15 cite-agent 2>&1 | grep -E "Agent:|error|Goodbye" | head -2
echo ""

# Test 6: Shell command
echo "TEST 6: Shell command execution"
echo "Query: what files are here?"
echo "what files are here?" | timeout 25 cite-agent 2>&1 | grep -E "README|setup.py|cite_agent" | head -5
echo ""

# Test 7: Web search
echo "TEST 7: Web search capability"
echo "Query: search web for Python 3.13 features"
echo "search web for Python 3.13 features" | timeout 30 cite-agent 2>&1 | grep -E "Agent:|search|result|http" | head -5
echo ""

echo "======================================================================"
echo "TESTING COMPLETE - Check output above for results"
echo "======================================================================"
