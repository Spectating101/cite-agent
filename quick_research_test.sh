#!/bin/bash
# Quick 3-Test Validation for Research Quality
# Tests the core fixes: no JSON leaking, proper synthesis, good citations

export NOCTURNAL_DEBUG=1

echo "🎓 QUICK RESEARCH QUALITY TEST (3 critical tests)"
echo ""

# Test 1: Multi-paper synthesis (tests JSON leaking fix)
echo "=========================================="
echo "TEST 1: Paper Search with Synthesis"
echo "Testing: JSON leaking, citation formatting, synthesis quality"
echo "=========================================="
echo "find papers on transformers" | python3 -m cite_agent.cli
echo ""
echo "CHECK:"
echo "  ✅ No raw JSON (no {\"query\":, no {\"papers\":)"
echo "  ✅ Numbered list with proper citations"
echo "  ✅ Natural language response, not tool output"
echo ""
read -p "Did it PASS? (y/n): " test1
echo ""

# Test 2: Comparative analysis (tests synthesis intelligence)
echo "=========================================="
echo "TEST 2: Comparative Research Query"
echo "Testing: Multi-paper synthesis, intelligent analysis"
echo "=========================================="
echo "Compare BERT and GPT-3 approaches to language understanding" | python3 -m cite_agent.cli
echo ""
echo "CHECK:"
echo "  ✅ Synthesizes information from multiple papers"
echo "  ✅ Explains key differences (bidirectional vs autoregressive)"
echo "  ✅ Proper academic tone and citations"
echo ""
read -p "Did it PASS? (y/n): " test2
echo ""

# Test 3: Domain-specific research (tests quality and hallucination prevention)
echo "=========================================="
echo "TEST 3: Domain-Specific Research"
echo "Testing: No hallucinations, proper paper filtering"
echo "=========================================="
echo "Find recent papers on vision transformers for medical imaging" | python3 -m cite_agent.cli
echo ""
echo "CHECK:"
echo "  ✅ Papers are actually about medical imaging + ViT"
echo "  ✅ Recent papers (not outdated)"
echo "  ✅ No invented/hallucinated papers"
echo ""
read -p "Did it PASS? (y/n): " test3
echo ""

# Results
echo "=========================================="
echo "RESULTS:"
echo "=========================================="
echo "Test 1 (JSON/Formatting): $test1"
echo "Test 2 (Synthesis Quality): $test2"
echo "Test 3 (Domain Accuracy): $test3"
echo ""

if [[ "$test1" == "y" && "$test2" == "y" && "$test3" == "y" ]]; then
    echo "🎉 ALL TESTS PASSED - Professor ready!"
    echo ""
    echo "Next steps:"
    echo "1. Run full test suite: ./test_professor_workflows.sh"
    echo "2. Test with your own research queries"
    echo "3. Ready to show professors"
else
    echo "⚠️  SOME TESTS FAILED - Needs more work"
    echo ""
    echo "Debug with NOCTURNAL_DEBUG=1 to see what's happening"
fi
