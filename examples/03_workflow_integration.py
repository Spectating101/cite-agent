#!/usr/bin/env python3
"""
Example 3: Workflow Integration

This example demonstrates how to:
- Save papers to local library
- Export citations to BibTeX
- Manage session history
- Integrate with research workflows
"""

import asyncio
from cite_agent import EnhancedNocturnalAgent
from cite_agent.workflow_integration import WorkflowIntegration

async def main():
    """Workflow integration example"""

    # Initialize agent and workflow manager
    print("🚀 Initializing Cite-Agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    workflow = WorkflowIntegration()
    user_id = "researcher_001"

    # Step 1: Search for papers
    query = "deep learning for medical image analysis"
    print(f"\n🔍 Searching for: '{query}'")

    results = await agent.search_academic_papers(query, limit=3)

    if results.get("papers"):
        papers = results["papers"]
        print(f"✅ Found {len(papers)} papers\n")

        # Step 2: Save papers to library
        print("💾 Saving papers to local library...")
        saved_ids = []

        for paper in papers:
            paper_id = workflow.save_paper_to_library(paper, user_id)
            saved_ids.append(paper_id)
            print(f"   ✓ Saved: {paper.get('title', 'Unknown')[:60]}...")

        # Step 3: Export to BibTeX
        print("\n📚 Exporting to BibTeX format...")
        bibtex_file = workflow.export_to_bibtex(papers, "my_citations.bib")
        print(f"   ✓ Exported to: {bibtex_file}")

        # Step 4: Read BibTeX file
        print(f"\n📄 BibTeX Content Preview:")
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:500])
            if len(content) > 500:
                print("   ... (truncated)")

        # Step 5: Save session history
        print("\n📝 Saving session history...")
        response_data = {
            "papers": papers,
            "query": query,
            "timestamp": "2025-11-08"
        }
        session_id = workflow.save_session_history(user_id, query, response_data)
        print(f"   ✓ Session saved: {session_id}")

        # Step 6: Show workflow summary
        print("\n" + "="*60)
        print("📊 Workflow Summary")
        print("="*60)
        print(f"Papers found:     {len(papers)}")
        print(f"Papers saved:     {len(saved_ids)}")
        print(f"BibTeX exported:  {bibtex_file}")
        print(f"Session ID:       {session_id}")
        print()

        # Example: How to use in your research workflow
        print("💡 Research Workflow Tips:")
        print("   1. Search and save papers regularly")
        print("   2. Export BibTeX to import into Zotero/Mendeley")
        print("   3. Use session history to replay previous searches")
        print("   4. Tag papers in library for organization")
        print()

    else:
        print("❌ No papers found")

    # Clean up
    await agent.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
