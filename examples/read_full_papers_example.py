#!/usr/bin/env python3
"""
Example: How to Use Full Paper Reading
This demonstrates the KILLER FEATURE - reading papers automatically!
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent
from cite_agent.full_paper_reader import read_full_papers_workflow


async def example_basic_usage():
    """Basic example: Read papers on a topic"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Full Paper Reading")
    print("=" * 80)

    agent = EnhancedNocturnalAgent()

    # Read 3 papers on ESG investing
    result = await read_full_papers_workflow(
        agent,
        query="ESG investing financial performance",
        limit=3,
        summarize=True
    )

    # Print results
    print(f"\n📊 Found {result['papers_found']} papers")
    print(f"📖 Successfully read {result['papers_read']} papers ({result['success_rate']})")
    print(f"\n{'-'*80}")
    print("SYNTHESIS:")
    print(result['synthesis'])
    print(f"{'-'*80}\n")

    # Print each paper summary
    for i, paper in enumerate(result['papers'], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   DOI: {paper.get('doi', 'N/A')}")

        if paper.get('full_text_available'):
            print(f"   ✅ Full text read ({paper['word_count']} words)")
            summary = paper.get('summary', {})
            if summary:
                print(f"\n   Research Question: {summary.get('research_question', 'N/A')}")
                print(f"\n   Methodology: {summary.get('methodology', 'N/A')}")
                print(f"\n   Key Findings:")
                for finding in summary.get('key_findings', [])[:3]:
                    print(f"   • {finding}")
        else:
            print(f"   ⚠️ {paper.get('note', 'Could not read')}")


async def example_literature_review():
    """Example: Full literature review workflow"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Literature Review Workflow")
    print("=" * 80)

    agent = EnhancedNocturnalAgent()

    topics = [
        "ESG investing returns",
        "corporate social responsibility financial impact",
        "sustainable investing performance"
    ]

    all_papers = []

    for topic in topics:
        print(f"\n🔍 Reading papers on: {topic}")
        result = await read_full_papers_workflow(
            agent,
            query=topic,
            limit=2,  # 2 papers per topic
            summarize=True
        )
        all_papers.extend(result['papers'])
        print(f"   Read {result['papers_read']}/{result['papers_found']} papers")

    # Count successful reads
    readable = [p for p in all_papers if p.get('full_text_available')]
    print(f"\n📚 TOTAL: Read {len(readable)}/{len(all_papers)} papers across 3 topics")

    # Synthesize findings across all topics
    all_findings = []
    for paper in readable:
        summary = paper.get('summary', {})
        findings = summary.get('key_findings', [])
        all_findings.extend(findings)

    print(f"\n💡 COMBINED INSIGHTS ({len(all_findings)} findings):")
    for i, finding in enumerate(all_findings[:10], 1):
        print(f"{i}. {finding}")


async def example_targeted_reading():
    """Example: Read specific papers by topic with filters"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Targeted Reading")
    print("=" * 80)

    agent = EnhancedNocturnalAgent()

    # Read recent papers (last 2 years) on specific topic
    result = await read_full_papers_workflow(
        agent,
        query="machine learning finance 2023 2024",
        limit=5,
        summarize=True
    )

    print(f"\n📊 Found {result['papers_found']} papers")

    # Filter for high-quality extractions only
    high_quality = [
        p for p in result['papers']
        if p.get('extraction_quality') == 'high'
    ]

    print(f"📖 High-quality reads: {len(high_quality)}/{result['papers_read']}")

    # Show methodologies
    print(f"\n🔬 METHODOLOGIES USED:")
    for i, paper in enumerate(high_quality, 1):
        summary = paper.get('summary', {})
        methodology = summary.get('methodology')
        if methodology:
            print(f"{i}. {paper['title'][:60]}...")
            print(f"   Method: {methodology}")


async def example_comparison():
    """Example: Compare methodologies across papers"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Compare Paper Methodologies")
    print("=" * 80)

    agent = EnhancedNocturnalAgent()

    result = await read_full_papers_workflow(
        agent,
        query="climate change economics regression analysis",
        limit=4,
        summarize=True
    )

    readable = [p for p in result['papers'] if p.get('full_text_available')]

    print(f"\n📊 Comparing methodologies across {len(readable)} papers:\n")

    for i, paper in enumerate(readable, 1):
        summary = paper.get('summary', {})
        print(f"{i}. {paper['title']}")
        print(f"   Method: {summary.get('methodology', 'N/A')}")
        print(f"   Limitations: {summary.get('limitations', 'N/A')}")
        print()


async def main():
    """Run all examples"""
    print("\n" + "🔥" * 40)
    print(" CITE-AGENT: FULL PAPER READING EXAMPLES")
    print("🔥" * 40)

    try:
        # Run examples
        await example_basic_usage()
        await example_literature_review()
        await example_targeted_reading()
        await example_comparison()

        print("\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
