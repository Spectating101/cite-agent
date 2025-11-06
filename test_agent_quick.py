#!/usr/bin/env python3
"""
Quick Functional Test - Does the agent work?
Focus on the 18 critical categories
"""

import asyncio
import os
import sys
import time

os.environ['NOCTURNAL_DEBUG'] = '0'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_basic():
    """Test basic agent functionality"""
    print("Initializing agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    print("✅ Agent initialized\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Location query
    tests_total += 1
    print("Test 1: Location Query (Directory Exploration)")
    try:
        req = ChatRequest(question="where are we?", user_id="test1")
        resp = await asyncio.wait_for(agent.process_request(req), timeout=10)
        if "/" in resp.response or "home" in resp.response.lower():
            print(f"  ✅ PASS: {resp.response[:80]}")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: Unexpected response: {resp.response[:80]}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 2: File safety check
    tests_total += 1
    print("\nTest 2: Command Safety Classification")
    try:
        safe_class = agent._classify_command_safety("ls -la")
        dangerous_class = agent._classify_command_safety("rm -rf /")
        if safe_class in ['SAFE', 'WRITE'] and dangerous_class == 'BLOCKED':
            print(f"  ✅ PASS: Safe={safe_class}, Dangerous={dangerous_class}")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: Safe={safe_class}, Dangerous={dangerous_class}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 3: Memory/Conversation History
    tests_total += 1
    print("\nTest 3: Conversation History Tracking")
    try:
        req1 = ChatRequest(question="My name is TestUser", user_id="test3", conversation_id="conv3")
        resp1 = await asyncio.wait_for(agent.process_request(req1), timeout=10)
        
        # Check if it was added to history
        if len(agent.conversation_history) > 0:
            print(f"  ✅ PASS: Conversation history populated ({len(agent.conversation_history)} entries)")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: No conversation history")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4: Error Handling
    tests_total += 1
    print("\nTest 4: Error Handling & Graceful Failures")
    try:
        req = ChatRequest(question="Read /nonexistent/file.txt", user_id="test4")
        resp = await asyncio.wait_for(agent.process_request(req), timeout=10)
        # Should respond without crashing
        if len(resp.response) > 5:
            print(f"  ✅ PASS: Handled gracefully: {resp.response[:80]}")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: No response")
    except asyncio.TimeoutError:
        print(f"  ⏱️ TIMEOUT")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5: Quick Reply (non-LLM responses)
    tests_total += 1
    print("\nTest 5: Quick Replies (Non-LLM Intelligence)")
    try:
        req = ChatRequest(question="pwd", user_id="test5")
        resp = await asyncio.wait_for(agent.process_request(req), timeout=10)
        if "test" in resp.response.lower() or "/" in resp.response:
            print(f"  ✅ PASS: {resp.response[:80]}")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: {resp.response[:80]}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6: API Clients Initialized
    tests_total += 1
    print("\nTest 6: API Clients Ready")
    try:
        has_archive = hasattr(agent, 'archive_base_url') and agent.archive_base_url
        has_finsight = hasattr(agent, 'finsight_base_url') and agent.finsight_base_url
        has_files = hasattr(agent, 'files_base_url') and agent.files_base_url
        
        if has_archive and has_finsight and has_files:
            print(f"  ✅ PASS: All API clients configured")
            print(f"    - Archive: {agent.archive_base_url}")
            print(f"    - FinSight: {agent.finsight_base_url}")
            print(f"    - Files: {agent.files_base_url}")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: Missing APIs (Archive={has_archive}, FinSight={has_finsight}, Files={has_files})")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 7: CLI UI
    tests_total += 1
    print("\nTest 7: CLI Streaming UI")
    try:
        from cite_agent.streaming_ui import StreamingChatUI
        ui = StreamingChatUI()
        ui.show_header()
        print(f"  ✅ PASS: CLI UI working")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 8: Backend Connectivity
    tests_total += 1
    print("\nTest 8: Backend API Connectivity")
    try:
        import requests
        resp = requests.get("http://127.0.0.1:8000/", timeout=5)
        if resp.status_code == 200:
            print(f"  ✅ PASS: Backend responding ({resp.status_code})")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: Backend returned {resp.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed ({100*tests_passed/tests_total:.0f}%)")
    print("="*70)
    
    if tests_passed >= 6:
        print("✅ AGENT CORE FUNCTIONALITY: WORKING")
        print("The agent can handle real conversations and tasks")
    elif tests_passed >= 4:
        print("⚠️  AGENT CORE FUNCTIONALITY: PARTIALLY WORKING")
        print("Basic features work, but some APIs may have issues")
    else:
        print("❌ AGENT CORE FUNCTIONALITY: CRITICAL ISSUES")
        print("Most core features are not working")
    
    return tests_passed, tests_total

if __name__ == "__main__":
    try:
        passed, total = asyncio.run(test_basic())
        sys.exit(0 if passed >= total * 0.6 else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
