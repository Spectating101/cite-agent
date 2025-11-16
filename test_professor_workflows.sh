#!/bin/bash
# Professor-Level Research Assistant Tests
# These test REAL academic workflows, not toy examples

set -e
export NOCTURNAL_DEBUG=1

echo "=========================================="
echo "🎓 PROFESSOR-LEVEL RESEARCH ASSISTANT TESTS"
echo "=========================================="
echo ""

# Test 1: Literature Review (Multi-paper analysis)
echo "📚 TEST 1: Literature Review with Comparative Analysis"
echo "Query: Compare BERT and GPT-3 approaches to language modeling"
echo ""
echo "Compare BERT and GPT-3 approaches to language modeling. Find papers for both, then explain the key architectural and training differences." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Clean synthesis comparing bidirectional vs autoregressive, masked LM vs next-token prediction"
echo "❌ Fail if: Raw JSON, no synthesis, or just lists papers without analysis"
echo ""
read -p "Press Enter to continue..."

# Test 2: Citation-Heavy Query (Top papers by citations)
echo ""
echo "=========================================="
echo "📊 TEST 2: Find Top Cited Papers"
echo "Query: Find the 5 most influential papers on transformers"
echo ""
echo "Find the 5 most influential papers on transformer architectures. I need the highly cited foundational work." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Papers sorted by citation count, formatted with author/year/DOI"
echo "❌ Fail if: Random ordering, missing citation counts, or JSON leaking"
echo ""
read -p "Press Enter to continue..."

# Test 3: Narrow Domain Research
echo ""
echo "=========================================="
echo "🔬 TEST 3: Domain-Specific Research Query"
echo "Query: Vision transformers for medical imaging"
echo ""
echo "Find recent papers on vision transformers applied to medical image analysis. Focus on 2021-2023 work." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Domain-specific results with context about medical imaging applications"
echo "❌ Fail if: Generic transformer papers, no medical context, or hallucinated papers"
echo ""
read -p "Press Enter to continue..."

# Test 4: Methodology Comparison
echo ""
echo "=========================================="
echo "⚙️ TEST 4: Methodology Deep Dive"
echo "Query: How do vision transformers differ from CNNs for image classification?"
echo ""
echo "Explain how vision transformers (ViT) differ from traditional CNNs for image classification. Find relevant papers and summarize the key architectural innovations." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Technical explanation with paper citations, discusses patch embeddings vs convolutions"
echo "❌ Fail if: Vague answer, no citations, or wrong technical details"
echo ""
read -p "Press Enter to continue..."

# Test 5: Research Gap Identification
echo ""
echo "=========================================="
echo "🔍 TEST 5: Identify Research Gaps"
echo "Query: What are the limitations of current transformer models?"
echo ""
echo "Based on recent research, what are the main limitations and open challenges for transformer models? Find papers discussing these issues." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Synthesis of multiple papers identifying gaps (efficiency, interpretability, etc.)"
echo "❌ Fail if: Generic answer, no paper citations, or doesn't identify specific open problems"
echo ""
read -p "Press Enter to continue..."

# Test 6: Multi-Domain Cross-Reference
echo ""
echo "=========================================="
echo "🌐 TEST 6: Cross-Domain Research"
echo "Query: Transformers in reinforcement learning"
echo ""
echo "Find papers applying transformer architectures to reinforcement learning. How are they being used and what are the results?" | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Cross-domain papers with context on how transformers improve RL"
echo "❌ Fail if: Only general transformer papers, no RL context, or missed the domain connection"
echo ""
read -p "Press Enter to continue..."

# Test 7: Author-Specific Research
echo ""
echo "=========================================="
echo "👤 TEST 7: Author-Based Query"
echo "Query: Papers by Yoshua Bengio on deep learning"
echo ""
echo "Find recent influential papers by Yoshua Bengio on deep learning. Focus on his work from the last 5 years." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Papers filtered by author, properly attributed"
echo "❌ Fail if: Wrong authors, no author filtering, or papers from wrong time period"
echo ""
read -p "Press Enter to continue..."

# Test 8: Technical Concept Deep Dive
echo ""
echo "=========================================="
echo "🧠 TEST 8: Technical Concept Explanation"
echo "Query: Explain attention mechanisms in transformers"
echo ""
echo "Explain how attention mechanisms work in transformer models. Find the key papers and break down the math and intuition." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Technical explanation with citations to Attention Is All You Need + follow-up work"
echo "❌ Fail if: Surface-level explanation, no math/intuition, or missing key papers"
echo ""
read -p "Press Enter to continue..."

# Test 9: Application-Focused Research
echo ""
echo "=========================================="
echo "💼 TEST 9: Real-World Application Research"
echo "Query: Transformer applications in drug discovery"
echo ""
echo "How are transformers being applied to drug discovery and molecular design? Find papers and summarize the approaches." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Domain-specific applications with concrete examples from papers"
echo "❌ Fail if: Generic transformer descriptions, no drug discovery context, or hallucinated applications"
echo ""
read -p "Press Enter to continue..."

# Test 10: Comprehensive Literature Review
echo ""
echo "=========================================="
echo "📖 TEST 10: Comprehensive Literature Review"
echo "Query: Survey of self-supervised learning methods"
echo ""
echo "I need to write a literature review on self-supervised learning methods. Find key papers covering contrastive learning, masked modeling, and other major approaches." | python3 -m cite_agent.cli
echo ""
echo "✅ Expected: Categorized papers by approach, comprehensive coverage, synthesis of themes"
echo "❌ Fail if: Random papers, no categorization, or missed major sub-areas"
echo ""

echo ""
echo "=========================================="
echo "🏁 TESTING COMPLETE"
echo "=========================================="
echo ""
echo "EVALUATION CRITERIA:"
echo "✅ PASS: Clean formatting, proper citations, intelligent synthesis, no JSON"
echo "⚠️  PARTIAL: Works but output quality needs improvement"
echo "❌ FAIL: JSON leaking, hallucinations, or missing core functionality"
echo ""
echo "This agent is professor-ready if 8+/10 tests PASS"
