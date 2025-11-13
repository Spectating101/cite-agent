#!/usr/bin/env python3
"""
Example 4: Batch Processing

This example demonstrates how to:
- Process multiple queries efficiently
- Batch search across different topics
- Aggregate and export results
- Handle errors gracefully
"""

import asyncio
from cite_agent import EnhancedNocturnalAgent
from cite_agent.workflow_integration import WorkflowIntegration

async def main():
    """Batch processing example"""

    # Initialize agent
    print("🚀 Initializing Cite-Agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    workflow = WorkflowIntegration()

    # Define multiple research queries
    queries = [
        "machine learning for drug discovery",
        "quantum computing applications",
        "renewable energy storage systems",
        "CRISPR gene editing techniques",
        "autonomous vehicle safety"
    ]

    print(f"\n📚 Processing {len(queries)} research queries in batch...\n")

    all_papers = []
    query_results = {}

    # Process each query
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] 🔍 Searching: '{query}'")

        try:
            results = await agent.search_academic_papers(query, limit=3)

            if results.get("papers"):
                papers = results["papers"]
                query_results[query] = papers
                all_papers.extend(papers)
                print(f"          ✅ Found {len(papers)} papers")
            else:
                print(f"          ⚠️  No results")
                query_results[query] = []

        except Exception as e:
            print(f"          ❌ Error: {str(e)[:50]}")
            query_results[query] = []

        # Small delay to avoid rate limiting
        if i < len(queries):
            await asyncio.sleep(0.5)

    # Summary statistics
    print("\n" + "="*60)
    print("📊 Batch Processing Summary")
    print("="*60)
    print(f"Total queries:        {len(queries)}")
    print(f"Successful searches:  {sum(1 for papers in query_results.values() if papers)}")
    print(f"Total papers found:   {len(all_papers)}")
    print()

    # Results by query
    print("📋 Results by Query:")
    for query, papers in query_results.items():
        print(f"   • {query[:45]:<45} : {len(papers)} papers")

    # Export all results to BibTeX
    if all_papers:
        print(f"\n💾 Exporting all {len(all_papers)} papers to BibTeX...")
        bibtex_file = workflow.export_to_bibtex(all_papers, "batch_results.bib")
        print(f"   ✓ Exported to: {bibtex_file}")

        # Show top cited papers
        print("\n🌟 Top 5 Most Cited Papers:")
        sorted_papers = sorted(
            all_papers,
            key=lambda p: p.get('citationCount', 0),
            reverse=True
        )

        for i, paper in enumerate(sorted_papers[:5], 1):
            title = paper.get('title', 'Unknown')[:50]
            citations = paper.get('citationCount', 0)
            year = paper.get('year', 'N/A')
            print(f"   {i}. [{year}] {title}... ({citations:,} citations)")

    # Clean up
    await agent.close()
    print("\n✅ Batch processing complete!")

if __name__ == "__main__":
    asyncio.run(main())
