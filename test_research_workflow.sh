#!/bin/bash
# LIVE RESEARCH WORKFLOW TEST - Prove cite-agent can do real research

echo "🎓 LIVE RESEARCH WORKFLOW TEST"
echo "================================"
echo ""
echo "Testing cite-agent as a REAL research assistant"
echo "Scenario: Graduate student analyzing survey data + literature review"
echo ""

# Setup
export $(cat .env.local | grep -v '^#' | xargs)
export NOCTURNAL_FUNCTION_CALLING=1

# Create test dataset
cat > research_survey.csv << 'EOF'
participant_id,age,education_years,hours_studied,exam_score,stress_level
1,22,16,10,85,3
2,24,18,15,92,4
3,21,15,8,78,2
4,23,17,12,88,3
5,25,19,18,95,5
6,22,16,9,82,3
7,24,18,14,90,4
8,21,15,7,75,2
9,23,17,11,86,3
10,25,19,17,94,5
11,22,16,10,84,3
12,24,18,16,91,4
13,21,15,8,79,2
14,23,17,13,89,3
15,25,19,19,96,5
EOF

echo "✅ Created test dataset: research_survey.csv (15 participants)"
echo ""

# Test 1: Load and analyze data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST 1: Data Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Query: 'Load research_survey.csv and show me summary statistics'"
echo ""

rm -f ~/.nocturnal_archive/session.json
timeout 45 bash -c 'echo -e "load research_survey.csv\nquit" | cite-agent 2>&1' | grep -A 20 "Agent:" | head -25

echo ""
echo "✅ Data loaded successfully? Check for statistics above"
echo ""
sleep 2

# Test 2: Correlation analysis
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 TEST 2: Correlation Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Query: 'Is there a correlation between hours_studied and exam_score?'"
echo ""

rm -f ~/.nocturnal_archive/session.json
timeout 45 bash -c 'echo -e "load research_survey.csv\nis there a correlation between hours_studied and exam_score\nquit" | cite-agent 2>&1' | grep -A 15 "Agent:" | tail -20

echo ""
echo "✅ Correlation analysis completed? Check results above"
echo ""
sleep 2

# Test 3: Multi-turn with context
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 TEST 3: Multi-Turn Context Memory"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Turn 1: 'Load research_survey.csv'"
echo "Turn 2: 'What's the average exam score?'"
echo "Turn 3: 'Filter for ages above 23'"
echo ""

rm -f ~/.nocturnal_archive/session.json
timeout 60 bash -c 'echo -e "load research_survey.csv\nwhat is the average exam score\nfilter for ages above 23\nquit" | cite-agent 2>&1' | grep -E "(Agent:|🎯)" | tail -30

echo ""
echo "✅ Multi-turn context working? Agent should answer all 3 questions"
echo ""
sleep 2

# Test 4: Literature search (if APIs available)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 TEST 4: Literature Search"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Query: 'Search for papers on student stress and academic performance'"
echo ""

rm -f ~/.nocturnal_archive/session.json
timeout 45 bash -c 'echo -e "search for papers on student stress and academic performance\nquit" | cite-agent 2>&1' | grep -A 30 "Agent:" | head -35

echo ""
echo "✅ Literature search working? Should show paper results"
echo ""

# Cleanup
rm -f research_survey.csv

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Tested:"
echo "  ✅ Data loading & statistics"
echo "  ✅ Correlation analysis"
echo "  ✅ Multi-turn context memory"
echo "  ✅ Literature search"
echo ""
echo "Can cite-agent work as a research assistant?"
echo "See results above to judge! 🎓"
echo ""
