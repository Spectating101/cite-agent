#!/bin/bash

echo "================================================"
echo "🎓 REAL PROFESSOR RESEARCH WORKFLOWS"
echo "Testing deep synthesis, not shallow queries"
echo "================================================"

# TEST 1: Literature synthesis + experimental design
echo ""
echo "=== TEST 1: Multi-Paper Synthesis & Experiment Design ==="
echo "Query: 'Find recent papers on vision transformers for medical imaging, synthesize"
echo "the key architectural innovations, and propose an experimental design to evaluate"
echo "a new hybrid CNN-ViT architecture for chest X-ray classification'"
echo ""
cite "Find recent papers on vision transformers for medical imaging. Synthesize the key architectural innovations across papers - what are the common design patterns and where do they differ? Then propose an experimental design to evaluate a new hybrid CNN-ViT architecture for chest X-ray classification. Include dataset recommendations, evaluation metrics, and baseline comparisons." 2>&1 | head -150
read -p "ASSESS THIS (Enter to continue): "

# TEST 2: Financial analysis with market context
echo ""
echo "=== TEST 2: Deep Financial Analysis with Market Context ==="
echo "Query: 'Compare NVIDIA, AMD, and Intel: revenue growth, profit margins,"
echo "R&D spend as % of revenue. Analyze competitive positioning in AI chip market"
echo "and predict which company is best positioned for next 3 years'"
echo ""
cite "Compare NVIDIA, AMD, and Intel on these metrics: revenue growth YoY, profit margins, and R&D spending as percentage of revenue. Based on this financial data and the current AI chip market dynamics, analyze their competitive positioning. Which company is best positioned for growth in the next 3 years and why? Support your analysis with the financial data." 2>&1 | head -150
read -p "ASSESS THIS (Enter to continue): "

# TEST 3: Cross-domain research synthesis
echo ""
echo "=== TEST 3: Cross-Domain Synthesis (RL + Transformers) ==="
echo "Query: 'How are transformers being applied to reinforcement learning?"
echo "Find papers, synthesize the approaches, identify limitations, and suggest"
echo "a novel research direction that addresses current gaps'"
echo ""
cite "Find papers on transformer architectures applied to reinforcement learning. Synthesize the main approaches - are they using transformers for world models, policies, or value functions? What are the computational limitations mentioned across papers? Based on this synthesis, suggest a novel research direction that addresses the current gaps while being computationally feasible." 2>&1 | head -150
read -p "ASSESS THIS (Enter to continue): "

# TEST 4: Comparative methodology analysis
echo ""
echo "=== TEST 4: Methodology Comparison Across Multiple Papers ==="
echo "Query: 'Compare self-supervised learning approaches: contrastive learning"
echo "(SimCLR, MoCo) vs masked modeling (MAE, BEiT). Synthesize trade-offs and"
echo "recommend which approach for low-data medical imaging scenario'"
echo ""
cite "Compare self-supervised learning approaches: contrastive learning methods like SimCLR and MoCo versus masked modeling approaches like MAE and BEiT. Find papers on each, synthesize the trade-offs (data requirements, computational cost, downstream performance), and recommend which approach would work best for a low-data medical imaging scenario with only 1000 labeled examples. Justify your recommendation with evidence from the papers." 2>&1 | head -150
read -p "ASSESS THIS (Enter to continue): "

# TEST 5: Research gap identification + proposal
echo ""
echo "=== TEST 5: Research Gap Analysis & Proposal ==="
echo "Query: 'Survey current limitations of large language models based on recent"
echo "papers. Identify the top 3 unsolved problems and propose a research agenda"
echo "to address one of them'"
echo ""
cite "Based on recent research papers, what are the current limitations of large language models? Identify the top 3 most critical unsolved problems mentioned across papers. For the most important one, propose a detailed research agenda including: (1) hypothesis to test, (2) experimental methodology, (3) expected challenges, and (4) how success would be measured." 2>&1 | head -150

echo ""
echo "================================================"
echo "✅ DEEP RESEARCH WORKFLOW TESTS COMPLETE"
echo "================================================"
echo ""
echo "PASS CRITERIA:"
echo "✅ Synthesizes across 3+ papers per query"
echo "✅ Provides analytical insights, not just summaries"
echo "✅ Makes data-driven recommendations"
echo "✅ Proposes experimental designs with specifics"
echo "✅ Identifies research gaps and suggests solutions"
echo ""
