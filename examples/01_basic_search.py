#!/usr/bin/env python3
"""
Example 1: Basic Academic Paper Search

This example demonstrates how to:
- Initialize the agent
- Search for papers on a topic
- Access paper metadata (title, authors, citations, DOI)
"""

import asyncio
from cite_agent import EnhancedNocturnalAgent

async def main():
    """Basic paper search example"""

    # Initialize agent
    print("🚀 Initializing Cite-Agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Search for papers
    query = "transformer architecture in natural language processing"
    print(f"\n🔍 Searching for: '{query}'")

    results = await agent.search_academic_papers(query, limit=5)

    # Display results
    if results.get("papers"):
        print(f"\n✅ Found {len(results['papers'])} papers:\n")

        for i, paper in enumerate(results["papers"], 1):
            print(f"{i}. {paper.get('title', 'No title')}")

            # Authors
            authors = paper.get('authors', [])
            if authors:
                author_names = [a.get('name', 'Unknown') for a in authors[:3]]
                if len(authors) > 3:
                    author_names.append(f"+ {len(authors) - 3} more")
                print(f"   Authors: {', '.join(author_names)}")

            # Publication info
            year = paper.get('year', 'N/A')
            venue = paper.get('venue', paper.get('journal', 'N/A'))
            print(f"   Published: {year} in {venue}")

            # Citations
            citations = paper.get('citationCount', 0)
            print(f"   Citations: {citations:,}")

            # DOI
            doi = paper.get('doi')
            if doi:
                print(f"   DOI: {doi}")
                print(f"   URL: https://doi.org/{doi}")

            # PDF availability
            if paper.get('openAccessPdf'):
                print(f"   📄 Open Access PDF: {paper['openAccessPdf'].get('url', 'Available')}")

            print()
    else:
        print("❌ No papers found")

    # Clean up
    await agent.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
