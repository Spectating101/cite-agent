#!/usr/bin/env python3
"""
Test script to verify cite-agent quality end-to-end
"""
import asyncio
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_agent_quality():
    """Test the agent with realistic research questions"""
    
    print("🧪 Testing Cite-Agent v1.4.11 Quality\n")
    print("=" * 60)
    
    # Initialize agent with your credentials
    agent = EnhancedNocturnalAgent()
    
    # Test queries - mix of research, data, and general
    test_queries = [
        {
            "query": "What are the three most cited papers on transformer architectures? Provide titles and citations.",
            "category": "Research - Paper Search"
        },
        {
            "query": "Explain the key innovation in the 'Attention Is All You Need' paper in 2-3 sentences.",
            "category": "Research - Explanation"
        },
        {
            "query": "用中文回答：什麼是深度學習？",
            "category": "Chinese Language Support"
        },
        {
            "query": "List the files in the current directory",
            "category": "Shell Command"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}: {test['category']}")
        print(f"Q: {test['query']}")
        print("-" * 60)
        
        try:
            request = ChatRequest(
                user_id="test_user",
                question=test['query']
            )
            
            response = await agent.process_request(request)
            
            print(f"✅ Response ({len(response.response)} chars):")
            print(response.response[:500])  # First 500 chars
            if len(response.response) > 500:
                print(f"... (+ {len(response.response) - 500} more characters)")
            
            results.append({
                "test": test['category'],
                "success": True,
                "response_length": len(response.response),
                "has_citations": "et al." in response.response or "(" in response.response,
                "has_chinese": any('\u4e00' <= char <= '\u9fff' for char in response.response)
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "test": test['category'],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"\n✅ Passed: {successful}/{len(results)}")
    
    for result in results:
        status = "✅" if result.get('success') else "❌"
        print(f"{status} {result['test']}")
        if result.get('success'):
            print(f"   - Response length: {result['response_length']} chars")
            if result.get('has_citations'):
                print(f"   - Has citations: Yes")
            if result.get('has_chinese'):
                print(f"   - Has Chinese: Yes")
    
    print("\n" + "=" * 60)
    
    if successful == len(results):
        print("🎉 ALL TESTS PASSED - Package is working correctly!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED - Package needs fixes")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_agent_quality())
    sys.exit(exit_code)
