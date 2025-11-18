#!/usr/bin/env python3
"""
Test to see what the backend is actually returning
and if response cleaning is being applied
"""

import asyncio
import sys
import os

# Enable debug mode to see what's happening
os.environ['NOCTURNAL_DEBUG'] = '1'

sys.path.insert(0, '/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent')

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_backend_response():
    """Test what backend returns and how it's cleaned"""
    
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    
    print("\n" + "="*80)
    print("TESTING BACKEND RESPONSE CLEANING")
    print("="*80)
    
    # Simple query that should work even with backend
    query = "hello, what can you do?"
    
    print(f"\n📝 Query: {query}")
    print("-"*80)
    
    request = ChatRequest(
        question=query,
        user_id="test_user",
        context={}
    )
    
    try:
        response = await agent.process_request(request)
        
        print(f"\n🤖 Response:\n{response.response}\n")
        print(f"📊 Tools used: {response.tools_used}")
        print(f"💬 Tokens: {response.tokens_used}")
        
        # Check for issues
        issues = []
        if 'We need to' in response.response:
            issues.append("❌ Found 'We need to'")
        if 'Probably' in response.response:
            issues.append("❌ Found 'Probably'")
        if '{"command":' in response.response or '{"tool":' in response.response or '{"type":' in response.response:
            issues.append("❌ Found JSON tool call")
        if 'Will run:' in response.response:
            issues.append("❌ Found 'Will run:'")
        
        if issues:
            print("\n⚠️ ISSUES:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("\n✅ Response is clean!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_backend_response())
    sys.exit(0 if result else 1)
