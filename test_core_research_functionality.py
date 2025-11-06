#!/usr/bin/env python3
"""
Core Research Functionality Test Suite

Tests the ACTUAL use cases:
1. Academic research assistance
2. Data analysis on data files
3. Summarization & synthesis
4. Literature review
5. Research workflow

Not testing conversation pleasantries - testing real research capabilities.
"""

import asyncio
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class CoreResearchTestSuite:
    def __init__(self):
        self.agent = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.total = 0
        self.issues = []

    async def initialize(self):
        """Initialize agent"""
        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()
        print(f"{GREEN}✅ Agent initialized{RESET}\n")

    async def run_all_tests(self):
        """Run comprehensive research capability tests"""
        print(f"{BOLD}{MAGENTA}🎯 CORE RESEARCH FUNCTIONALITY TEST SUITE{RESET}")
        print("=" * 80)
        print(f"{CYAN}Testing ACTUAL use cases: Research, Data Analysis, Literature Review{RESET}")
        print("=" * 80)

        await self.initialize()

        # Category 1: Literature Search
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 1: LITERATURE SEARCH & DISCOVERY ━━━{RESET}")
        await self.test_find_papers_on_topic()
        await self.test_recent_papers_timeframe()
        await self.test_specific_author_search()
        await self.test_methodology_specific_search()

        # Category 2: Paper Analysis & Synthesis
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 2: PAPER ANALYSIS & SYNTHESIS ━━━{RESET}")
        await self.test_summarize_research_area()
        await self.test_identify_research_gaps()
        await self.test_compare_methodologies()
        await self.test_extract_key_findings()

        # Category 3: Data Analysis Support
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 3: DATA ANALYSIS SUPPORT ━━━{RESET}")
        await self.test_csv_data_exploration()
        await self.test_statistical_analysis_suggestion()
        await self.test_data_visualization_recommendations()

        # Category 4: Research Workflow
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 4: RESEARCH WORKFLOW ASSISTANCE ━━━{RESET}")
        await self.test_literature_review_structure()
        await self.test_research_question_refinement()
        await self.test_methodology_recommendation()

        # Category 5: Academic Writing Support
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 5: ACADEMIC WRITING SUPPORT ━━━{RESET}")
        await self.test_citation_formatting()
        await self.test_abstract_writing_guidance()
        await self.test_results_interpretation_help()

        await self.print_summary()

    # ========================================================================
    # CATEGORY 1: LITERATURE SEARCH & DISCOVERY
    # ========================================================================

    async def test_find_papers_on_topic(self):
        """Test: Find recent papers on a research topic"""
        print(f"{CYAN}Test 1.1: Find Papers on Machine Learning Interpretability{RESET}")
        request = ChatRequest(
            question="Find papers on machine learning interpretability from the last 2 years",
            user_id="test_1_1",
            conversation_id="conv_1_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        # Check if agent attempts to search papers (uses Archive API)
        tools_used = response.tools_used or []
        has_search = "archive" in tools_used or "arxiv" in tools_used or any("search" in t.lower() for t in tools_used)

        # Check response quality
        response_lower = response.response.lower()
        mentions_papers = any(word in response_lower for word in ['paper', 'article', 'study', 'research', 'publication'])
        provides_titles = response.response.count('"') >= 2 or response.response.count("'") >= 2  # Has quoted titles

        if has_search and mentions_papers and provides_titles:
            print(f"  {GREEN}✅ PASS: Found and listed research papers{RESET}\n")
            self.passed += 1
        elif not has_search:
            print(f"  {RED}❌ FAIL: Didn't attempt to search papers{RESET}\n")
            self.failed += 1
            self.issues.append(("Find Papers", "No paper search attempted"))
        elif not provides_titles:
            print(f"  {YELLOW}⚠️  WARN: Searched but didn't provide specific paper titles{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Response doesn't mention papers{RESET}\n")
            self.failed += 1
            self.issues.append(("Find Papers", "No papers mentioned in response"))

        self.total += 1
        await asyncio.sleep(3)  # Rate limit protection

    async def test_recent_papers_timeframe(self):
        """Test: Respects timeframe constraints in search"""
        print(f"{CYAN}Test 1.2: Timeframe-Specific Search (2023-2024){RESET}")
        request = ChatRequest(
            question="What are the most cited papers on transformers published in 2023 or 2024?",
            user_id="test_1_2",
            conversation_id="conv_1_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        # Check if response mentions recent years
        mentions_timeframe = any(year in response.response for year in ['2023', '2024'])
        mentions_citations = any(word in response.response.lower() for word in ['cited', 'citations', 'influential'])

        if mentions_timeframe and mentions_citations:
            print(f"  {GREEN}✅ PASS: Respects timeframe and citation criteria{RESET}\n")
            self.passed += 1
        elif not mentions_timeframe:
            print(f"  {RED}❌ FAIL: Doesn't acknowledge timeframe constraint{RESET}\n")
            self.failed += 1
            self.issues.append(("Timeframe Search", "Doesn't mention 2023/2024"))
        else:
            print(f"  {YELLOW}⚠️  WARN: Partial - mentions timeframe but not citations{RESET}\n")
            self.warnings += 1

        self.total += 1

    async def test_specific_author_search(self):
        """Test: Can search for papers by specific author"""
        print(f"{CYAN}Test 1.3: Author-Specific Search{RESET}")
        request = ChatRequest(
            question="Find papers by Yoshua Bengio on deep learning",
            user_id="test_1_3",
            conversation_id="conv_1_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        # Check if agent acknowledges author search
        mentions_author = "bengio" in response.response.lower()
        mentions_deep_learning = "deep learning" in response.response.lower()

        if mentions_author and mentions_deep_learning:
            print(f"  {GREEN}✅ PASS: Acknowledges author and topic{RESET}\n")
            self.passed += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't properly handle author search{RESET}\n")
            self.failed += 1
            self.issues.append(("Author Search", "Doesn't acknowledge author or topic"))

        self.total += 1

    async def test_methodology_specific_search(self):
        """Test: Can search by research methodology"""
        print(f"{CYAN}Test 1.4: Methodology-Specific Search{RESET}")
        request = ChatRequest(
            question="Find qualitative studies using grounded theory on AI ethics",
            user_id="test_1_4",
            conversation_id="conv_1_4"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_qualitative = "qualitative" in response.response.lower()
        mentions_grounded_theory = "grounded theory" in response.response.lower()
        mentions_ethics = "ethics" in response.response.lower()

        if mentions_qualitative and (mentions_grounded_theory or mentions_ethics):
            print(f"  {GREEN}✅ PASS: Understands methodology-specific search{RESET}\n")
            self.passed += 1
        else:
            print(f"  {YELLOW}⚠️  WARN: May not fully understand methodology requirements{RESET}\n")
            self.warnings += 1

        self.total += 1

    # ========================================================================
    # CATEGORY 2: PAPER ANALYSIS & SYNTHESIS
    # ========================================================================

    async def test_summarize_research_area(self):
        """Test: Can summarize state of research in an area"""
        print(f"{CYAN}Test 2.1: Summarize Research Area{RESET}")
        request = ChatRequest(
            question="Summarize the current state of research on federated learning",
            user_id="test_2_1",
            conversation_id="conv_2_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        # Check for synthesis indicators
        has_overview = any(word in response.response.lower() for word in ['current', 'state', 'field', 'area', 'research'])
        has_key_concepts = any(word in response.response.lower() for word in ['federated', 'learning', 'privacy', 'distributed'])
        is_comprehensive = len(response.response) > 300  # Should be detailed

        if has_overview and has_key_concepts and is_comprehensive:
            print(f"  {GREEN}✅ PASS: Provides comprehensive research area summary{RESET}\n")
            self.passed += 1
        elif has_key_concepts:
            print(f"  {YELLOW}⚠️  WARN: Mentions concepts but summary may be incomplete{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide adequate research summary{RESET}\n")
            self.failed += 1
            self.issues.append(("Research Summary", "Inadequate or missing summary"))

        self.total += 1

    async def test_identify_research_gaps(self):
        """Test: Can identify gaps in literature"""
        print(f"{CYAN}Test 2.2: Identify Research Gaps{RESET}")
        request = ChatRequest(
            question="What are the main research gaps in explainable AI for healthcare?",
            user_id="test_2_2",
            conversation_id="conv_2_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_gaps = any(word in response.response.lower() for word in ['gap', 'lacking', 'needed', 'future', 'opportunity', 'unexplored'])
        mentions_domain = any(word in response.response.lower() for word in ['healthcare', 'medical', 'clinical', 'explainable', 'interpretable'])

        if mentions_gaps and mentions_domain:
            print(f"  {GREEN}✅ PASS: Identifies research gaps in domain{RESET}\n")
            self.passed += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't adequately identify research gaps{RESET}\n")
            self.failed += 1
            self.issues.append(("Research Gaps", "Doesn't identify gaps or domain issues"))

        self.total += 1

    async def test_compare_methodologies(self):
        """Test: Can compare different research methodologies"""
        print(f"{CYAN}Test 2.3: Compare Research Methodologies{RESET}")
        request = ChatRequest(
            question="Compare quantitative and qualitative approaches for studying user experience in AI systems",
            user_id="test_2_3",
            conversation_id="conv_2_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_both = ("quantitative" in response.response.lower() and "qualitative" in response.response.lower())
        has_comparison = any(word in response.response.lower() for word in ['compare', 'versus', 'difference', 'strength', 'weakness', 'while', 'whereas'])

        if mentions_both and has_comparison:
            print(f"  {GREEN}✅ PASS: Compares methodologies effectively{RESET}\n")
            self.passed += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't adequately compare methodologies{RESET}\n")
            self.failed += 1
            self.issues.append(("Methodology Comparison", "Missing comparison or mentions only one approach"))

        self.total += 1

    async def test_extract_key_findings(self):
        """Test: Can extract and summarize key findings"""
        print(f"{CYAN}Test 2.4: Extract Key Findings{RESET}")
        request = ChatRequest(
            question="What are the key findings from recent research on large language model alignment?",
            user_id="test_2_4",
            conversation_id="conv_2_4"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        has_findings = any(word in response.response.lower() for word in ['finding', 'found', 'discovered', 'showed', 'demonstrated', 'revealed'])
        mentions_topic = any(word in response.response.lower() for word in ['alignment', 'language model', 'llm'])

        if has_findings and mentions_topic:
            print(f"  {GREEN}✅ PASS: Extracts key findings from research{RESET}\n")
            self.passed += 1
        else:
            print(f"  {YELLOW}⚠️  WARN: May not be extracting specific findings{RESET}\n")
            self.warnings += 1

        self.total += 1

    # ========================================================================
    # CATEGORY 3: DATA ANALYSIS SUPPORT
    # ========================================================================

    async def test_csv_data_exploration(self):
        """Test: Can help explore CSV/data files"""
        print(f"{CYAN}Test 3.1: CSV Data Exploration{RESET}")
        request = ChatRequest(
            question="I have a CSV file called survey_results.csv. Help me explore what's in it.",
            user_id="test_3_1",
            conversation_id="conv_3_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        # Check if agent offers to help with data exploration
        mentions_csv = "csv" in response.response.lower()
        offers_help = any(phrase in response.response.lower() for phrase in [
            'explore', 'look at', 'examine', 'analyze', 'show you', 'check', 'read'
        ])

        if mentions_csv and offers_help:
            print(f"  {GREEN}✅ PASS: Offers to help explore CSV data{RESET}\n")
            self.passed += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't offer meaningful data exploration help{RESET}\n")
            self.failed += 1
            self.issues.append(("CSV Exploration", "Doesn't engage with data exploration request"))

        self.total += 1

    async def test_statistical_analysis_suggestion(self):
        """Test: Suggests appropriate statistical analyses"""
        print(f"{CYAN}Test 3.2: Statistical Analysis Suggestion{RESET}")
        request = ChatRequest(
            question="I have survey data with Likert scale responses. What statistical tests should I use?",
            user_id="test_3_2",
            conversation_id="conv_3_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_tests = any(test in response.response.lower() for test in [
            'mann-whitney', 'kruskal', 'wilcoxon', 'chi-square', 'spearman', 'ordinal'
        ])
        understands_likert = "likert" in response.response.lower() or "ordinal" in response.response.lower()

        if mentions_tests and understands_likert:
            print(f"  {GREEN}✅ PASS: Suggests appropriate statistical tests{RESET}\n")
            self.passed += 1
        elif understands_likert:
            print(f"  {YELLOW}⚠️  WARN: Understands Likert but may not suggest specific tests{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide meaningful statistical guidance{RESET}\n")
            self.failed += 1
            self.issues.append(("Statistical Analysis", "Doesn't understand Likert or suggest appropriate tests"))

        self.total += 1

    async def test_data_visualization_recommendations(self):
        """Test: Recommends appropriate data visualizations"""
        print(f"{CYAN}Test 3.3: Data Visualization Recommendations{RESET}")
        request = ChatRequest(
            question="I want to visualize the relationship between two continuous variables and one categorical variable. What should I use?",
            user_id="test_3_3",
            conversation_id="conv_3_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        suggests_viz = any(viz in response.response.lower() for viz in [
            'scatter', 'plot', 'graph', 'chart', 'visualiz', 'color', 'hue', 'facet'
        ])

        if suggests_viz:
            print(f"  {GREEN}✅ PASS: Recommends visualization approach{RESET}\n")
            self.passed += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide visualization recommendations{RESET}\n")
            self.failed += 1
            self.issues.append(("Visualization", "No visualization recommendations provided"))

        self.total += 1

    # ========================================================================
    # CATEGORY 4: RESEARCH WORKFLOW
    # ========================================================================

    async def test_literature_review_structure(self):
        """Test: Provides structure for literature review"""
        print(f"{CYAN}Test 4.1: Literature Review Structure{RESET}")
        request = ChatRequest(
            question="I'm writing a literature review on reinforcement learning for robotics. How should I structure it?",
            user_id="test_4_1",
            conversation_id="conv_4_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_structure = any(word in response.response.lower() for word in ['structure', 'organize', 'section', 'intro', 'conclusion'])
        mentions_topic = any(word in response.response.lower() for word in ['reinforcement', 'robotics', 'learning'])

        if mentions_structure and mentions_topic:
            print(f"  {GREEN}✅ PASS: Provides literature review structure guidance{RESET}\n")
            self.passed += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide adequate structure guidance{RESET}\n")
            self.failed += 1
            self.issues.append(("Literature Review", "No structure guidance provided"))

        self.total += 1

    async def test_research_question_refinement(self):
        """Test: Helps refine research questions"""
        print(f"{CYAN}Test 4.2: Research Question Refinement{RESET}")
        request = ChatRequest(
            question="My research question is 'How does AI affect society?' Is this specific enough?",
            user_id="test_4_2",
            conversation_id="conv_4_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        provides_feedback = any(word in response.response.lower() for word in ['broad', 'narrow', 'specific', 'refine', 'focus'])
        offers_alternatives = "?" in response.response or any(word in response.response.lower() for word in ['instead', 'consider', 'could'])

        if provides_feedback and offers_alternatives:
            print(f"  {GREEN}✅ PASS: Provides research question refinement guidance{RESET}\n")
            self.passed += 1
        elif provides_feedback:
            print(f"  {YELLOW}⚠️  WARN: Identifies issue but doesn't suggest improvements{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide refinement guidance{RESET}\n")
            self.failed += 1
            self.issues.append(("Research Question", "No refinement guidance"))

        self.total += 1

    async def test_methodology_recommendation(self):
        """Test: Recommends appropriate research methodology"""
        print(f"{CYAN}Test 4.3: Research Methodology Recommendation{RESET}")
        request = ChatRequest(
            question="I want to study how users perceive AI-generated content. What research methodology should I use?",
            user_id="test_4_3",
            conversation_id="conv_4_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        suggests_method = any(method in response.response.lower() for method in [
            'survey', 'interview', 'experiment', 'qualitative', 'quantitative', 'mixed method'
        ])
        explains_rationale = len(response.response) > 200

        if suggests_method and explains_rationale:
            print(f"  {GREEN}✅ PASS: Recommends methodology with rationale{RESET}\n")
            self.passed += 1
        elif suggests_method:
            print(f"  {YELLOW}⚠️  WARN: Suggests method but lacks detailed rationale{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide methodology recommendation{RESET}\n")
            self.failed += 1
            self.issues.append(("Methodology", "No methodology recommendation"))

        self.total += 1

    # ========================================================================
    # CATEGORY 5: ACADEMIC WRITING SUPPORT
    # ========================================================================

    async def test_citation_formatting(self):
        """Test: Understands citation formats"""
        print(f"{CYAN}Test 5.1: Citation Formatting Help{RESET}")
        request = ChatRequest(
            question="How do I format this paper in APA style: 'Attention is All You Need' by Vaswani et al., 2017?",
            user_id="test_5_1",
            conversation_id="conv_5_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_apa = "apa" in response.response.lower()
        mentions_paper = "attention" in response.response.lower() or "vaswani" in response.response.lower()
        provides_format = "(" in response.response and ")" in response.response  # Has parentheses typical of citations

        if mentions_apa and mentions_paper and provides_format:
            print(f"  {GREEN}✅ PASS: Provides citation formatting guidance{RESET}\n")
            self.passed += 1
        elif mentions_apa:
            print(f"  {YELLOW}⚠️  WARN: Acknowledges APA but may not format correctly{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide citation formatting help{RESET}\n")
            self.failed += 1
            self.issues.append(("Citation", "No citation formatting guidance"))

        self.total += 1

    async def test_abstract_writing_guidance(self):
        """Test: Provides abstract writing guidance"""
        print(f"{CYAN}Test 5.2: Abstract Writing Guidance{RESET}")
        request = ChatRequest(
            question="What should I include in my research paper abstract?",
            user_id="test_5_2",
            conversation_id="conv_5_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        mentions_components = sum(1 for component in ['background', 'method', 'result', 'conclusion', 'objective', 'finding']
                                 if component in response.response.lower())

        if mentions_components >= 3:
            print(f"  {GREEN}✅ PASS: Provides comprehensive abstract guidance{RESET}\n")
            self.passed += 1
        elif mentions_components >= 2:
            print(f"  {YELLOW}⚠️  WARN: Provides some guidance but may be incomplete{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide adequate abstract guidance{RESET}\n")
            self.failed += 1
            self.issues.append(("Abstract", "Incomplete or missing abstract guidance"))

        self.total += 1

    async def test_results_interpretation_help(self):
        """Test: Helps interpret research results"""
        print(f"{CYAN}Test 5.3: Results Interpretation Help{RESET}")
        request = ChatRequest(
            question="I found a correlation of r=0.65, p<0.001 between variables A and B. How should I interpret this?",
            user_id="test_5_3",
            conversation_id="conv_5_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}...")

        interprets_correlation = any(word in response.response.lower() for word in ['strong', 'moderate', 'positive', 'relationship'])
        interprets_significance = any(word in response.response.lower() for word in ['significant', 'statistically', 'p-value', 'unlikely'])
        mentions_causation = "causation" in response.response.lower() or "cause" in response.response.lower()

        if interprets_correlation and interprets_significance:
            print(f"  {GREEN}✅ PASS: Provides results interpretation{RESET}\n")
            self.passed += 1
        elif interprets_correlation or interprets_significance:
            print(f"  {YELLOW}⚠️  WARN: Partial interpretation provided{RESET}\n")
            self.warnings += 1
        else:
            print(f"  {RED}❌ FAIL: Doesn't provide meaningful interpretation{RESET}\n")
            self.failed += 1
            self.issues.append(("Results Interpretation", "No interpretation provided"))

        self.total += 1

    async def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print(f"{BOLD}{MAGENTA}📊 CORE RESEARCH FUNCTIONALITY TEST RESULTS{RESET}")
        print("=" * 80)
        print()

        percentage = (self.passed / self.total * 100) if self.total > 0 else 0

        print(f"{BOLD}Score: {percentage:.1f}% ({self.passed}/{self.total}){RESET}")
        print(f"  {GREEN}✅ Passed: {self.passed}{RESET}")
        print(f"  {YELLOW}⚠️  Warnings: {self.warnings}{RESET}")
        print(f"  {RED}❌ Failed: {self.failed}{RESET}")
        print()

        if percentage >= 90:
            print(f"{GREEN}{BOLD}🎉 EXCELLENT: Core research capabilities are strong!{RESET}")
        elif percentage >= 75:
            print(f"{CYAN}{BOLD}✅ GOOD: Strong research support with minor gaps{RESET}")
        elif percentage >= 60:
            print(f"{YELLOW}{BOLD}⚠️  DECENT: Adequate research support but needs improvement{RESET}")
        else:
            print(f"{RED}{BOLD}❌ NEEDS WORK: Research capabilities need significant improvement{RESET}")

        if self.issues:
            print(f"\n{BOLD}{RED}Critical Issues to Fix:{RESET}\n")
            for i, (test_name, issue) in enumerate(self.issues[:10], 1):
                print(f"{i}. {test_name}")
                print(f"   • {issue}\n")

        print("=" * 80)


async def main():
    suite = CoreResearchTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
