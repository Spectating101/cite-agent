#!/bin/bash
# Comprehensive Multi-Turn Testing Script
# This simulates a real user session with cite-agent

cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent
rm -f ~/.nocturnal_archive/session.json

export $(cat .env.local | grep -v '^#' | xargs)
export NOCTURNAL_FUNCTION_CALLING=1

echo "================================================================================"
echo "COMPREHENSIVE MULTI-TURN TESTING SESSION"
echo "Testing: Every feature, every edge case, real user flow"
echo "================================================================================"
echo ""

# Create input file for multi-turn conversation
cat > /tmp/cite_agent_test_input.txt << 'TESTINPUT'
show me README.md
quit
TESTINPUT

echo "🔬 TEST 1: Basic File Reading"
echo "Query: show me README.md"
echo "Expected: README content displayed, no verbose preamble"
echo ""
cat /tmp/cite_agent_test_input.txt | cite-agent 2>&1 | grep -A 30 "Agent:" | head -35
echo ""
echo "Result: $(cat /tmp/cite_agent_test_input.txt | cite-agent 2>&1 | grep -q 'Cite-Agent' && echo '✅ PASS' || echo '❌ FAIL')"
echo ""
echo "================================================================================"

# Test 2: Multi-turn with pronoun resolution
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input2.txt << 'TESTINPUT'
show me setup.py
explain what you just showed me
quit
TESTINPUT

echo "🔬 TEST 2: Multi-turn Context (Pronoun Resolution)"
echo "Turn 1: show me setup.py"
echo "Turn 2: explain what you just showed me"
echo "Expected: Should remember setup.py and explain it"
echo ""
cat /tmp/cite_agent_test_input2.txt | cite-agent 2>&1 | grep -E "Agent:|setup|explain" | head -20
echo ""
echo "================================================================================"

# Test 3: List then read (chained operations)
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input3.txt << 'TESTINPUT'
list python files in cite_agent folder
quit
TESTINPUT

echo "🔬 TEST 3: Directory Listing"
echo "Query: list python files in cite_agent folder"
echo "Expected: List of .py files, clean output"
echo ""
cat /tmp/cite_agent_test_input3.txt | cite-agent 2>&1 | grep -E "Agent:|\.py|enhanced" | head -15
echo ""
echo "================================================================================"

# Test 4: Error handling - non-existent file
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input4.txt << 'TESTINPUT'
show me nonexistent_file_xyz.txt
quit
TESTINPUT

echo "🔬 TEST 4: Error Handling (Non-existent File)"
echo "Query: show me nonexistent_file_xyz.txt"
echo "Expected: Clear error message, no crash"
echo ""
cat /tmp/cite_agent_test_input4.txt | cite-agent 2>&1 | grep -E "Agent:|error|not found|No such" | head -5
echo ""
echo "Result: $(cat /tmp/cite_agent_test_input4.txt | cite-agent 2>&1 | grep -qi 'error\|not found\|no such' && echo '✅ PASS - Error handled' || echo '❌ FAIL')"
echo ""
echo "================================================================================"

# Test 5: Data operations
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input5.txt << 'TESTINPUT'
load sample_data.csv
quit
TESTINPUT

echo "🔬 TEST 5: Data Loading"
echo "Query: load sample_data.csv"
echo "Expected: Data loaded or clear error if file doesn't exist"
echo ""
cat /tmp/cite_agent_test_input5.txt | cite-agent 2>&1 | grep -E "Agent:|data|csv|loaded" | head -10
echo ""
echo "================================================================================"

# Test 6: Empty query
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input6.txt << 'TESTINPUT'

quit
TESTINPUT

echo "🔬 TEST 6: Empty Query Handling"
echo "Query: (empty line)"
echo "Expected: Graceful handling, no crash"
echo ""
timeout 15 bash -c "cat /tmp/cite_agent_test_input6.txt | cite-agent 2>&1" | grep -E "Agent:|error|Goodbye" | head -5
echo ""
echo "Result: $(timeout 15 bash -c 'echo "" | cite-agent 2>&1' | grep -q 'Goodbye' && echo '✅ PASS - No crash' || echo '❌ FAIL')"
echo ""
echo "================================================================================"

# Test 7: Shell command with clean output (no echoes)
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input7.txt << 'TESTINPUT'
what is the current directory?
quit
TESTINPUT

echo "🔬 TEST 7: Shell Command (No Command Echoes)"
echo "Query: what is the current directory?"
echo "Expected: Just the path, no '$ pwd' echo"
echo ""
cat /tmp/cite_agent_test_input7.txt | cite-agent 2>&1 | grep -E "Agent:|Cite-Agent|cite-agent|pwd" | head -5
echo ""
echo "================================================================================"

# Test 8: Multi-step with progress indicators
rm -f ~/.nocturnal_archive/session.json
cat > /tmp/cite_agent_test_input8.txt << 'TESTINPUT'
list files, read README.md, then summarize the project
quit
TESTINPUT

echo "🔬 TEST 8: Multi-Step Query (Progress Indicators)"
echo "Query: list files, read README.md, then summarize the project"
echo "Expected: 💭 Processing step X/Y, 🔧 tool indicators"
echo ""
cat /tmp/cite_agent_test_input8.txt | cite-agent 2>&1 | grep -E "💭|🔧|Processing|step" | head -10
echo ""
echo "================================================================================"

echo ""
echo "TESTING COMPLETE!"
echo "Review results above for detailed analysis"
echo ""

# Cleanup
rm -f /tmp/cite_agent_test_input*.txt
