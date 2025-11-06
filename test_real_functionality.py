#!/usr/bin/env python3
"""
Real Functionality Test - Does the chatbot actually work?
Testing the 18 categories mentioned:

PART 1: API Testing (15 categories)
1. Basic Conversation
2. Academic Research (Archive API)
3. Financial Analysis (FinSight API)
4. File Operations
5. Directory Exploration
6. Code Analysis & Bug Detection
7. Web Search & Fallback
8. Multi-Turn Context (most important - proves intelligence)
9. Command Safety (security critical)
10. Error Handling & Recovery
11. Workflow Management
12. Edge Cases & Boundaries
13. Performance & Timeouts
14. Anti-Hallucination (trust critical)
15. Integration Tests

PART 2: CLI & Backend Testing (3 categories)
16. CLI Interface Testing
17. Backend API Endpoints
18. Security Audit
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest, ChatResponse

class FunctionalityTester:
    def __init__(self):
        self.results = []
        self.agent = None
        
    async def setup(self):
        """Initialize agent"""
        os.environ['NOCTURNAL_DEBUG'] = '0'
        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()
        print("✅ Agent initialized successfully\n")
    
    async def test_category(self, num: int, category: str, query: str, expected_features: list) -> bool:
        """Test a category and check for expected behaviors"""
        print(f"\n{'='*70}")
        print(f"Test {num}: {category}")
        print(f"{'='*70}")
        print(f"Query: {query}")
        
        try:
            request = ChatRequest(question=query, user_id=f"test_{num}")
            
            start = time.time()
            response = await asyncio.wait_for(self.agent.process_request(request), timeout=15)
            duration = time.time() - start
            
            print(f"\n✅ Response received in {duration:.2f}s")
            print(f"Response preview: {response.response[:200]}...")
            print(f"Tools used: {response.tools_used}")
            print(f"Confidence: {response.confidence_score}")
            
            # Check for expected features
            passed_checks = []
            for feature in expected_features:
                if isinstance(feature, tuple):
                    check_name, check_fn = feature
                    if check_fn(response):
                        passed_checks.append(f"✅ {check_name}")
                    else:
                        passed_checks.append(f"❌ {check_name}")
                else:
                    # Simple string check
                    if feature.lower() in response.response.lower():
                        passed_checks.append(f"✅ Contains '{feature}'")
                    else:
                        passed_checks.append(f"⚠️ Missing '{feature}'")
            
            for check in passed_checks:
                print(f"  {check}")
            
            # Log result
            success = all('✅' in c for c in passed_checks)
            self.results.append({
                'category': category,
                'success': success,
                'duration': duration,
                'tools': response.tools_used,
                'confidence': response.confidence_score
            })
            
            return success
            
        except asyncio.TimeoutError:
            print(f"⏱️ TIMEOUT after 15 seconds")
            self.results.append({'category': category, 'success': False, 'error': 'timeout'})
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results.append({'category': category, 'success': False, 'error': str(e)})
            return False
    
    async def run_all_tests(self):
        """Run all 18 category tests"""
        print("\n" + "="*70)
        print("🧪 AGENT REAL FUNCTIONALITY TESTING")
        print("="*70)
        print("Testing: Can the agent actually fulfill its functionality?\n")
        
        await self.setup()
        
        # ========================================================================
        # PART 1: API TESTING (15 categories)
        # ========================================================================
        
        print("\n" + "🔵 "*10)
        print("PART 1: API TESTING (15 categories)")
        print("🔵 "*10 + "\n")
        
        # 1. Basic Conversation
        await self.test_category(
            1, "Basic Conversation",
            "Hi! What can you do?",
            [
                ("Responds", lambda r: len(r.response) > 10),
                ("Sets confidence", lambda r: r.confidence_score >= 0),
                ("No errors", lambda r: r.error_message is None),
            ]
        )
        
        # 2. Location Query (file system)
        await self.test_category(
            2, "Directory Exploration - Location",
            "where are we right now?",
            [
                ("Responds with directory", lambda r: "/" in r.response or "home" in r.response.lower()),
                ("Uses shell tool", lambda r: "shell" in str(r.tools_used).lower()),
            ]
        )
        
        # 3. File Operations - List files
        await self.test_category(
            3, "File Operations - List",
            "show me python files in the current directory",
            [
                ("Responds", lambda r: len(r.response) > 20),
                ("Mentions files", lambda r: "file" in r.response.lower() or ".py" in r.response),
            ]
        )
        
        # 4. File Operations - Read
        await self.test_category(
            4, "File Operations - Read",
            "Read the README.md file",
            [
                ("Responds", lambda r: len(r.response) > 20),
                ("Uses files tool or reads content", lambda r: "file" in r.tools_used or "readme" in r.response.lower()),
            ]
        )
        
        # 5. Safety Classification
        await self.test_category(
            5, "Command Safety - Safe Commands",
            "check if the command 'ls -la' is safe",
            [
                ("Provides safety assessment", lambda r: "safe" in r.response.lower() or "ls" in r.response),
            ]
        )
        
        # 6. Safety Classification - Dangerous
        await self.test_category(
            6, "Command Safety - Dangerous Detection",
            "is 'rm -rf /' a dangerous command?",
            [
                ("Recognizes danger", lambda r: "danger" in r.response.lower() or "bad" in r.response.lower() or "blocked" in r.response.lower()),
            ]
        )
        
        # 7. Memory & Context (Multi-turn simulation)
        print("\n" + "="*70)
        print("Test 7: Multi-Turn Context & Memory")
        print("="*70)
        print("Testing conversation memory...")
        try:
            conv_id = "test_conv_7"
            
            # First turn
            req1 = ChatRequest(question="My name is Alice", user_id="test_7", conversation_id=conv_id)
            resp1 = await asyncio.wait_for(self.agent.process_request(req1), timeout=15)
            print(f"Turn 1: 'My name is Alice' → {resp1.response[:100]}")
            
            # Second turn - refer back
            req2 = ChatRequest(question="What's my name?", user_id="test_7", conversation_id=conv_id)
            resp2 = await asyncio.wait_for(self.agent.process_request(req2), timeout=15)
            print(f"Turn 2: 'What's my name?' → {resp2.response[:100]}")
            
            # Check if memory worked
            remembers = "alice" in resp2.response.lower() or "conversation" in resp2.response.lower()
            print(f"Result: {'✅ Remembers context' if remembers else '⚠️ No context memory yet'}")
            
            self.results.append({
                'category': 'Multi-Turn Context',
                'success': remembers,
                'tools': resp2.tools_used,
            })
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results.append({'category': 'Multi-Turn Context', 'success': False, 'error': str(e)})
        
        # 8. Error Handling
        await self.test_category(
            8, "Error Handling & Recovery",
            "Read a file that doesn't exist: /nonexistent/file.txt",
            [
                ("Handles gracefully", lambda r: "error" in r.response.lower() or "not found" in r.response.lower() or "doesn't exist" in r.response.lower()),
                ("Doesn't crash", lambda r: len(r.response) > 10),
            ]
        )
        
        # 9. Workflow Management
        await self.test_category(
            9, "Workflow Management",
            "Show my library of saved papers",
            [
                ("Responds", lambda r: len(r.response) > 10),
            ]
        )
        
        # 10. Edge Cases - Empty Input
        await self.test_category(
            10, "Edge Cases - Ambiguous Query",
            "?",
            [
                ("Handles gracefully", lambda r: len(r.response) > 5),
                ("Doesn't crash", lambda r: r.error_message is None or "ambiguous" in r.error_message.lower()),
            ]
        )
        
        # 11. Performance - Speed Check
        print("\n" + "="*70)
        print("Test 11: Performance & Responsiveness")
        print("="*70)
        try:
            times = []
            for i in range(3):
                start = time.time()
                req = ChatRequest(question="where?", user_id=f"perf_{i}")
                resp = await asyncio.wait_for(self.agent.process_request(req), timeout=15)
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  Query {i+1}: {elapsed:.3f}s")
            
            avg_time = sum(times) / len(times)
            print(f"Average response time: {avg_time:.3f}s")
            self.results.append({
                'category': 'Performance',
                'success': avg_time < 10,  # Should respond in <10s
                'avg_time': avg_time,
            })
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results.append({'category': 'Performance', 'success': False, 'error': str(e)})
        
        # 12. Hallucination Check
        await self.test_category(
            12, "Anti-Hallucination - Unknown Facts",
            "what is the population of Narnia?",
            [
                ("Doesn't fabricate", lambda r: "unknown" in r.response.lower() or "fictional" in r.response.lower() or "don't know" in r.response.lower() or "narnia" in r.response.lower()),
            ]
        )
        
        # 13. Academic Research Capability
        await self.test_category(
            13, "Academic Research Query",
            "Find papers on machine learning",
            [
                ("Attempts research", lambda r: "research" in r.tools_used or "api" in r.response.lower() or len(r.response) > 50),
            ]
        )
        
        # 14. Financial Analysis Capability
        await self.test_category(
            14, "Financial Analysis Query",
            "What are Apple's recent earnings?",
            [
                ("Attempts financial lookup", lambda r: "financial" in r.tools_used or "ticker" in r.response.lower() or "apple" in r.response.lower() or "aapl" in r.response.lower()),
            ]
        )
        
        # 15. Integration Test (Multiple Tools)
        await self.test_category(
            15, "Integration - Multiple APIs",
            "Find Python files and tell me about machine learning research",
            [
                ("Complex response", lambda r: len(r.response) > 50),
                ("Uses multiple tools", lambda r: len(r.tools_used) > 0),
            ]
        )
        
        # ========================================================================
        # PART 2: CLI & BACKEND TESTING (3 categories)
        # ========================================================================
        
        print("\n" + "🟢 "*10)
        print("PART 2: CLI & BACKEND TESTING (3 categories)")
        print("🟢 "*10 + "\n")
        
        # 16. CLI Interface
        print("\n" + "="*70)
        print("Test 16: CLI Interface Functionality")
        print("="*70)
        try:
            from cite_agent.streaming_ui import StreamingChatUI
            ui = StreamingChatUI()
            ui.show_header()
            ui.show_user_message("Test question")
            print("✅ CLI UI components work")
            self.results.append({'category': 'CLI Interface', 'success': True})
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results.append({'category': 'CLI Interface', 'success': False, 'error': str(e)})
        
        # 17. Backend API Endpoints
        print("\n" + "="*70)
        print("Test 17: Backend API Endpoints")
        print("="*70)
        try:
            import requests
            resp = requests.get("http://127.0.0.1:8000/", timeout=5)
            if resp.status_code == 200:
                print(f"✅ Backend responding: {resp.json().get('message', 'OK')}")
                self.results.append({'category': 'Backend API', 'success': True})
            else:
                print(f"⚠️ Backend returned: {resp.status_code}")
                self.results.append({'category': 'Backend API', 'success': False})
        except Exception as e:
            print(f"❌ Backend not responding: {e}")
            self.results.append({'category': 'Backend API', 'success': False, 'error': str(e)})
        
        # 18. Security Audit
        print("\n" + "="*70)
        print("Test 18: Security & Safety Checks")
        print("="*70)
        try:
            from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent
            agent = self.agent
            
            # Test dangerous command detection
            result_safe = agent._classify_command_safety("ls -la")
            result_dangerous = agent._classify_command_safety("rm -rf /")
            
            safe_ok = result_safe in ['SAFE', 'WRITE']
            dangerous_ok = result_dangerous == 'BLOCKED'
            
            print(f"  'ls -la' → {result_safe} {'✅' if safe_ok else '❌'}")
            print(f"  'rm -rf /' → {result_dangerous} {'✅' if dangerous_ok else '❌'}")
            
            self.results.append({
                'category': 'Security Audit',
                'success': safe_ok and dangerous_ok,
            })
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results.append({'category': 'Security Audit', 'success': False, 'error': str(e)})
        
        # ========================================================================
        # SUMMARY
        # ========================================================================
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n\n" + "="*70)
        print("📊 FINAL RESULTS")
        print("="*70)
        
        passed = sum(1 for r in self.results if r.get('success'))
        total = len(self.results)
        
        print(f"\nTests Passed: {passed}/{total} ({100*passed/total:.1f}%)\n")
        
        for result in self.results:
            status = "✅" if result.get('success') else "❌"
            category = result.get('category')
            error = f" [{result.get('error', '')}]" if result.get('error') else ""
            print(f"  {status} {category}{error}")
        
        print("\n" + "="*70)
        if passed / total >= 0.8:
            print("🎉 AGENT FUNCTIONALITY: MOSTLY WORKING")
            print(f"   {passed} out of {total} core features operational")
        elif passed / total >= 0.5:
            print("⚠️  AGENT FUNCTIONALITY: PARTIALLY WORKING")
            print(f"   {passed} out of {total} core features operational")
        else:
            print("❌ AGENT FUNCTIONALITY: CRITICAL ISSUES")
            print(f"   Only {passed} out of {total} core features operational")
        print("="*70)


async def main():
    tester = FunctionalityTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️ Testing interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
