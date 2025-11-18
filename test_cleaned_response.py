#!/usr/bin/env python3
"""
Quick test of response cleaning to verify the fix works
"""

import asyncio
import sys
import os
sys.path.insert(0, '/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent')

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_cleaning():
    """Test that response cleaning works"""
    
    # Create agent instance
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    
    # Test queries that previously caused issues
    test_queries = [
        "what is the current directory?",
        "can you find a folder called test_ something?",
    ]
    
    print("="*80)
    print("TESTING RESPONSE CLEANING")
    print("="*80)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-"*80)
        
        request = ChatRequest(
            question=query,
            user_id="test_user",
            context={"mode": "test"}
        )
        
        response = await agent.process_request(request)
        
        print(f"🤖 Response:\n{response.response}\n")
        
        # Check for issues
        issues = []
        if 'We need to' in response.response:
            issues.append("❌ Found 'We need to' - internal thinking leaked")
        if 'Probably' in response.response:
            issues.append("❌ Found 'Probably' - uncertainty language leaked")
        if '{"command":' in response.response or '{"tool":' in response.response:
            issues.append("❌ Found JSON - tool call leaked")
        if 'Will run:' in response.response:
            issues.append("❌ Found 'Will run:' - planning language leaked")
        if 'According to system' in response.response:
            issues.append("❌ Found 'According to system' - meta reasoning leaked")
        
        if issues:
            print("⚠️ ISSUES DETECTED:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ Response looks clean!")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(test_cleaning())
