#!/usr/bin/env python3
"""
REAL Research Assistant Test Suite
===================================

Tests the features that ACTUAL professors and researchers need.
No more "what is 2+2" - these are legitimate research tasks.
"""

import asyncio
import os
import sys

os.environ['CEREBRAS_API_KEY_1'] = 'csk-edrc3v63k43fe4hdt529ynt4h9mfd9k9wjpjj3nn5pcvm2t4'
os.environ['USE_LOCAL_KEYS'] = 'true'
os.environ['NOCTURNAL_DEBUG'] = '0'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


RESEARCH_QUERIES = [
    {
        "name": "Literature Synthesis",
        "query": "Find 5 papers on vision transformers and synthesize their key contributions. What are the main innovations across these papers?",
        "expected": "Should find papers, extract findings, synthesize",
        "features": ["archive_api", "synthesis"]
    },
    {
        "name": "Data Analysis Request",
        "query": "I have a CSV file at /tmp/test_data.csv with columns 'hours_studied' and 'test_score'. Can you analyze if there's a relationship between study hours and test scores?",
        "expected": "Should offer to load data, run correlation/regression",
        "features": ["file_operations", "statistical_analysis"]
    },
    {
        "name": "R Code Help",
        "query": "I'm trying to run a linear regression in R: lm(score ~ hours, data=mydata) but getting an error. How can I check if my assumptions are met?",
        "expected": "Should explain regression assumptions and how to check them in R",
        "features": ["r_integration", "statistics_knowledge"]
    },
    {
        "name": "Zotero Export",
        "query": "Find papers on transformers in computer vision and export them to Zotero with proper citations",
        "expected": "Should find papers and format for Zotero export",
        "features": ["archive_api", "zotero_export"]
    },
    {
        "name": "Methodological Comparison",
        "query": "Compare the methodologies used in recent meta-analyses of online learning effectiveness. What statistical approaches are most common?",
        "expected": "Should find meta-analysis papers and compare methods",
        "features": ["archive_api", "synthesis", "methodology_analysis"]
    },
    {
        "name": "Qualitative Analysis",
        "query": "I have interview transcripts about student motivation. What themes should I look for when coding this qualitative data?",
        "expected": "Should suggest coding approach and common themes",
        "features": ["qualitative_methods", "thematic_analysis"]
    },
    {
        "name": "Statistical Assumption Check",
        "query": "Before running ANOVA, what assumptions do I need to check and how do I test them?",
        "expected": "Should explain ANOVA assumptions and testing procedures",
        "features": ["statistics_knowledge"]
    },
    {
        "name": "Literature Gap Identification",
        "query": "Based on recent papers on self-efficacy in online education, what research gaps exist that I could address?",
        "expected": "Should find papers and identify unexplored areas",
        "features": ["archive_api", "gap_analysis"]
    },
    {
        "name": "Regression Interpretation",
        "query": "My regression gave me β=0.45, p<0.001, R²=0.23. How do I interpret these results for my paper?",
        "expected": "Should explain coefficient, significance, and effect size",
        "features": ["statistics_interpretation"]
    },
    {
        "name": "Research Design Advice",
        "query": "I want to study the effect of feedback timing on learning outcomes. What experimental design would be most appropriate?",
        "expected": "Should suggest RCT, quasi-experimental, or other design",
        "features": ["research_methods", "experimental_design"]
    }
]


async def test_research_query(query_info: dict, agent: EnhancedNocturnalAgent):
    """Test a single research query"""
    print(f"\n{'═'*80}")
    print(f"TEST: {query_info['name']}")
    print(f"{'═'*80}")
    print(f"Query: {query_info['query']}")
    print(f"Expected: {query_info['expected']}")
    print(f"Features: {', '.join(query_info['features'])}")
    print(f"{'─'*80}\n")

    try:
        request = ChatRequest(question=query_info['query'])
        response = await agent.process_request(request)

        print(f"✅ Response received")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Tools: {response.tools_used}")
        print(f"\n📄 RESPONSE:\n")
        print(response.response)
        print(f"\n{'─'*80}")

        # Manual evaluation prompts
        print(f"\n❓ EVALUATE THIS RESPONSE:")
        print(f"   1. Does it address the research question?")
        print(f"   2. Is it helpful for a real researcher?")
        print(f"   3. Would a professor be satisfied?")
        print(f"   4. Are there factual errors?")
        print(f"   5. Does it use appropriate research terminology?")
        print(f"\n   Rate: [1-5] _____")
        print(f"{'═'*80}\n")

        return {
            "name": query_info['name'],
            "tokens": response.tokens_used,
            "tools": response.tools_used,
            "response_length": len(response.response)
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": query_info['name'],
            "error": str(e)
        }


async def main():
    print("═"*80)
    print("REAL RESEARCH ASSISTANT TEST SUITE")
    print("═"*80)
    print("\nThis tests ACTUAL research tasks, not 'what is 2+2'")
    print("Each query represents something a real professor would ask.")
    print("\nEVALUATE EACH RESPONSE MANUALLY:")
    print("- Is it helpful?")
    print("- Would a researcher be satisfied?")
    print("- Are there errors or gaps?")
    print(f"\n{'═'*80}\n")

    agent = EnhancedNocturnalAgent()

    # Run a subset of tests (user can choose which)
    print("Which tests to run?")
    print("1. All tests (10 queries)")
    print("2. Core features only (5 queries)")
    print("3. Single test (choose one)")
    print("\nDefaulting to core features test (5 queries)...\n")

    # Core test suite: most important features
    core_tests = [
        RESEARCH_QUERIES[0],  # Literature synthesis
        RESEARCH_QUERIES[1],  # Data analysis
        RESEARCH_QUERIES[3],  # Zotero export
        RESEARCH_QUERIES[6],  # Statistical assumptions
        RESEARCH_QUERIES[7],  # Literature gaps
    ]

    results = []
    for query_info in core_tests:
        result = await test_research_query(query_info, agent)
        results.append(result)

        # Pause between queries to avoid rate limits
        await asyncio.sleep(2)

    # Summary
    print("\n" + "═"*80)
    print("TEST SUMMARY")
    print("═"*80)

    for r in results:
        if 'error' in r:
            print(f"❌ {r['name']}: ERROR - {r['error'][:50]}")
        else:
            print(f"✅ {r['name']}: {r['tokens']} tokens, tools: {r['tools']}")

    print("\n" + "═"*80)
    print("NEXT STEPS:")
    print("═"*80)
    print("1. Review each response above")
    print("2. Identify which features are missing")
    print("3. Build out missing capabilities")
    print("4. Re-run tests to validate improvements")
    print("═"*80)


if __name__ == "__main__":
    asyncio.run(main())
