#!/bin/bash
# Comprehensive test of ALL advanced research tools
# Tests: Plotting, Qualitative Coding, Power Analysis, Advanced Stats, Literature Synthesis

set -e

echo "=========================================="
echo "COMPREHENSIVE ADVANCED TOOLS TEST"
echo "Testing: plot_data, qualitative coding, power analysis, advanced stats, lit synthesis"
echo "=========================================="
echo ""

# Load environment
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

run_test() {
    test_count=$((test_count + 1))
    test_name="$1"
    prompt="$2"
    expected_tool="$3"
    
    echo -e "${YELLOW}TEST $test_count: $test_name${NC}"
    echo "Prompt: $prompt"
    echo "Expected Tool: $expected_tool"
    echo ""
    
    # Run cite-agent with the prompt
    output=$(echo "$prompt" | timeout 60s cite-agent --debug 2>&1 || true)
    
    # Check if expected tool was called
    if echo "$output" | grep -q "\[$expected_tool\]"; then
        echo -e "${GREEN}✅ PASS${NC} - Tool '$expected_tool' was called"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC} - Tool '$expected_tool' was NOT called"
        echo "Output preview:"
        echo "$output" | grep -E "Tool:|Executing:|Error:" | head -20
        fail_count=$((fail_count + 1))
    fi
    
    echo ""
    echo "---"
    echo ""
}

# Create test data
echo "📊 Creating test dataset for analysis..."
cat > test_dataset.csv << 'EOF'
id,age,score,group,satisfaction
1,25,85,A,4.5
2,30,92,B,4.8
3,35,78,A,3.9
4,28,88,B,4.6
5,32,95,A,4.9
6,27,82,B,4.2
7,29,89,A,4.7
8,31,91,B,4.8
9,26,84,A,4.4
10,33,93,B,4.9
11,24,79,A,3.8
12,34,90,B,4.7
13,28,86,A,4.5
14,30,94,B,4.9
15,29,81,A,4.3
EOF

# Create sample transcript for qualitative coding
cat > interview_transcript.txt << 'EOF'
Interviewer: How do you feel about the new system?
Participant 1: I feel hopeful about it, but there are some barriers.
Participant 1: The main barrier is time - we don't have enough time to learn it.
Interviewer: What would make it better?
Participant 1: More training and support would help with motivation.
EOF

echo "✅ Test data created"
echo ""

# ============================================================================
# TEST 1: ASCII Plotting - plot_data tool
# ============================================================================
run_test "ASCII Plotting - Scatter Plot" \
    "Load test_dataset.csv and create a scatter plot of age vs score" \
    "ASCII Plotter"

run_test "ASCII Plotting - Bar Chart" \
    "Load test_dataset.csv and create a bar chart of average satisfaction by group" \
    "ASCII Plotter"

run_test "ASCII Plotting - Histogram" \
    "Load test_dataset.csv and create a histogram of the score distribution" \
    "ASCII Plotter"

# ============================================================================
# TEST 2: Qualitative Coding
# ============================================================================
run_test "Qualitative Coding - Create Codebook" \
    "Create a qualitative code called 'hope' with description 'expressions of optimism or positive expectations'" \
    "Qual Coding"

run_test "Qualitative Coding - Load Transcript" \
    "Load the interview_transcript.txt file as transcript ID 'int_001' for coding" \
    "Qual Coding"

run_test "Qualitative Coding - Auto Extract Themes" \
    "Automatically extract themes from the loaded transcripts with minimum frequency of 2" \
    "Qual Coding"

# ============================================================================
# TEST 3: Power Analysis
# ============================================================================
run_test "Power Analysis - Sample Size for t-test" \
    "Calculate the required sample size for a t-test with medium effect size (0.5) and 80% power" \
    "Power"

run_test "Power Analysis - Calculate Power" \
    "Calculate the statistical power for a t-test with n=30 per group and effect size 0.5" \
    "Power"

run_test "Power Analysis - Minimum Detectable Effect" \
    "What is the minimum detectable effect size for a t-test with n=50 per group and 80% power?" \
    "Power"

# ============================================================================
# TEST 4: Advanced Statistics
# ============================================================================
run_test "Advanced Stats - PCA" \
    "Load test_dataset.csv and run principal component analysis on age, score, and satisfaction" \
    "PCA"

run_test "Advanced Stats - Factor Analysis" \
    "Load test_dataset.csv and run factor analysis with 2 factors on age, score, and satisfaction" \
    "Factor Analysis"

run_test "Advanced Stats - Mediation Analysis" \
    "Load test_dataset.csv and test if score mediates the relationship between age and satisfaction" \
    "Mediation"

run_test "Advanced Stats - Moderation Analysis" \
    "Load test_dataset.csv and test if group moderates the relationship between age and score" \
    "Moderation"

# ============================================================================
# TEST 5: Data Cleaning
# ============================================================================
run_test "Data Cleaning - Quality Scan" \
    "Load test_dataset.csv and scan for data quality issues" \
    "Data Cleaning"

# ============================================================================
# TEST 6: Literature Synthesis
# ============================================================================
run_test "Literature Synthesis - Add Paper" \
    "Add a paper to literature synthesis: ID='paper1', title='AI in Education', abstract='This study examines AI applications in educational contexts'" \
    "Lit Synth"

run_test "Literature Synthesis - Extract Themes" \
    "Extract common themes from papers in the literature synthesis" \
    "Lit Synth"

run_test "Literature Synthesis - Find Gaps" \
    "Identify research gaps in the current literature synthesis" \
    "Lit Synth"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo "Total Tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "All advanced research tools are working correctly."
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo "Pass rate: $(awk "BEGIN {printf \"%.1f\", ($pass_count/$test_count)*100}")%"
    exit 1
fi
