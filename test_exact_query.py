#!/usr/bin/env python3
"""
Test the EXACT query that was failing before:
"think you can go find this folder called cm--522 or something?"

Expected BAD output (before fix):
  We need to run a find command.Will run: `find...`
  We need to actually execute.
  Probably need to use the tool...
  {"command": "find..."}

Expected GOOD output (after fix):
  Clean description of what was found or error message
"""

import asyncio
import sys
import os

sys.path.insert(0, '/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent')

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_exact_failing_query():
    """Test the exact query that showed internal thinking leakage"""
    
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    
    print("\n" + "="*80)
    print("TESTING EXACT QUERY THAT PREVIOUSLY FAILED")
    print("="*80)
    
    # The exact query from user's example
    query = "think you can go find this folder called cm--522 or something?"
    
    print(f"\n📝 Query: {query}")
    print("-"*80)
    
    request = ChatRequest(
        question=query,
        user_id="test_user",
        context={}
    )
    
    try:
        print("⏳ Processing (may take 10-30 seconds)...\n")
        response = await agent.process_request(request)
        
        print("🤖 Response:")
        print("-"*80)
        print(response.response)
        print("-"*80)
        
        # Check for the EXACT issues from user's example
        issues = []
        
        if 'We need to run' in response.response:
            issues.append("❌ LEAKED: 'We need to run' (internal reasoning)")
        if 'We need to actually' in response.response:
            issues.append("❌ LEAKED: 'We need to actually' (internal reasoning)")
        if 'We need to send' in response.response:
            issues.append("❌ LEAKED: 'We need to send' (internal reasoning)")
        if 'Probably need to' in response.response or 'Probably the' in response.response:
            issues.append("❌ LEAKED: 'Probably' (uncertainty language)")
        if 'Will run:' in response.response:
            issues.append("❌ LEAKED: 'Will run:' (planning language)")
        if '{"command":' in response.response:
            issues.append("❌ LEAKED: JSON command object")
        if 'According to system' in response.response:
            issues.append("❌ LEAKED: 'According to system' (meta reasoning)")
        if 'But the format is not specified' in response.response:
            issues.append("❌ LEAKED: Format confusion text")
        if 'In previous interactions' in response.response:
            issues.append("❌ LEAKED: Reference to previous interactions")
        if 'We need to output' in response.response or 'We need to produce' in response.response:
            issues.append("❌ LEAKED: Output planning text")
        
        print(f"\n📊 Metadata:")
        print(f"  • Tools used: {response.tools_used}")
        print(f"  • Tokens: {response.tokens_used}")
        print(f"  • Confidence: {response.confidence_score}")
        
        if issues:
            print("\n" + "="*80)
            print("❌ RESPONSE CLEANING FAILED - Issues detected:")
            print("="*80)
            for issue in issues:
                print(f"  {issue}")
            print("\n🔍 The response still contains internal LLM reasoning/planning.")
            print("🔧 _clean_formatting() needs stronger patterns.")
            return False
        else:
            print("\n" + "="*80)
            print("✅ RESPONSE CLEANING SUCCESSFUL!")
            print("="*80)
            print("No internal reasoning or JSON leaked to user.")
            return True
            
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_exact_failing_query())
    print("\n" + "="*80)
    if result:
        print("✅ TEST PASSED - Ready to ship!")
    else:
        print("❌ TEST FAILED - More work needed")
    print("="*80)
    sys.exit(0 if result else 1)
