#!/usr/bin/env python3
"""
COMPREHENSIVE STRESS TEST for cite-agent v1.4.12
Tests ALL features, capabilities, and known failure modes

Based on user reports:
1. File listing dumps everything instead of limiting to 5-10
2. Folder search outside directory leaks thinking and doesn't execute
3. Follow-up queries print nothing
4. Must test EVERY tool and feature
"""

import asyncio
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.absolute()))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

class ComprehensiveStressTest:
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize agent"""
        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()
        print("✅ Agent initialized\n")
    
    async def run_test(self, name, query, expected_behaviors, avoid_behaviors, timeout=30):
        """Run a single test and validate response"""
        print(f"\n{'='*80}")
        print(f"TEST: {name}")
        print(f"{'='*80}")
        print(f"📝 Query: {query}")
        print("-"*80)
        
        request = ChatRequest(
            question=query,
            user_id="stress_test_user",
            context={}
        )
        
        try:
            start_time = time.time()
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                self.agent.process_request(request),
                timeout=timeout
            )
            elapsed = time.time() - start_time
            
            print(f"\n🤖 Response ({elapsed:.1f}s):")
            print("-"*80)
            print(response.response)
            print("-"*80)
            
            # Store for conversation continuity
            self.conversation_history.append({
                'query': query,
                'response': response.response
            })
            
            # Validate response
            issues = []
            warnings = []
            
            # Check for thinking leakage
            thinking_patterns = [
                ('We need to', "internal reasoning leaked"),
                ('I need to', "internal reasoning leaked"),
                ('Probably', "uncertainty language leaked"),
                ('Will run:', "planning language leaked"),
                ('Let me try', "planning language leaked"),
                ('According to system', "meta reasoning leaked"),
                ('{"command":', "JSON tool call leaked"),
                ('{"tool":', "JSON tool call leaked"),
                ('{"type":', "JSON tool call leaked"),
            ]
            
            for pattern, desc in thinking_patterns:
                if pattern in response.response:
                    issues.append(f"❌ LEAKED: '{pattern}' - {desc}")
            
            # Check expected behaviors
            for behavior in expected_behaviors:
                if behavior not in response.response.lower() and behavior != "EXECUTED":
                    if behavior == "LIMITED_OUTPUT":
                        # Check if response is too long (>2000 chars suggests dump)
                        if len(response.response) > 2000:
                            warnings.append(f"⚠️ VERBOSE: Response is {len(response.response)} chars (might be full dump)")
                    else:
                        warnings.append(f"⚠️ MISSING: Expected '{behavior}' in response")
            
            # Check avoid behaviors
            for behavior in avoid_behaviors:
                if behavior in response.response.lower():
                    issues.append(f"❌ FOUND: Should NOT contain '{behavior}'")
            
            # Check for empty response
            if not response.response or response.response.strip() == "":
                issues.append("❌ EMPTY RESPONSE")
            
            # Check if response is just error message
            if "❌" in response.response and len(response.response) < 100:
                warnings.append("⚠️ ERROR RESPONSE: Agent returned error message")
            
            # Report
            print(f"\n📊 Metadata:")
            print(f"  • Tools: {response.tools_used}")
            print(f"  • Tokens: {response.tokens_used}")
            print(f"  • Confidence: {response.confidence_score}")
            print(f"  • Time: {elapsed:.1f}s")
            
            if issues:
                print(f"\n❌ CRITICAL ISSUES:")
                for issue in issues:
                    print(f"  {issue}")
                result = "FAIL"
            elif warnings:
                print(f"\n⚠️ WARNINGS:")
                for warning in warnings:
                    print(f"  {warning}")
                result = "WARN"
            else:
                print(f"\n✅ PASSED")
                result = "PASS"
            
            self.test_results.append({
                'name': name,
                'result': result,
                'issues': issues,
                'warnings': warnings,
                'response_length': len(response.response),
                'elapsed': elapsed
            })
            
            return result
        
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"\n❌ TIMEOUT: Test exceeded {timeout}s limit")
            self.test_results.append({
                'name': name,
                'result': "TIMEOUT",
                'issues': [f"Exceeded {timeout}s timeout"],
                'warnings': [],
                'response_length': 0,
                'elapsed': elapsed
            })
            return "TIMEOUT"
            
        except Exception as e:
            print(f"\n❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append({
                'name': name,
                'result': "ERROR",
                'issues': [str(e)],
                'warnings': [],
                'response_length': 0,
                'elapsed': 0
            })
            return "ERROR"
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        
        print("\n" + "="*80)
        print("CITE-AGENT COMPREHENSIVE STRESS TEST")
        print("Testing ALL features and known failure modes")
        print("="*80)
        
        # TEST 1: File listing (KNOWN ISSUE: dumps everything)
        await self.run_test(
            name="File Listing Limit",
            query="what files are in this directory?",
            expected_behaviors=["LIMITED_OUTPUT"],  # Should summarize, not dump all
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 2: System-wide folder search (KNOWN ISSUE: leaks thinking, doesn't execute)
        await self.run_test(
            name="Folder Search Outside Directory",
            query="can you find a folder called 'Downloads' on this system?",
            expected_behaviors=["found", "downloads"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 3: Follow-up query (KNOWN ISSUE: prints nothing)
        await self.run_test(
            name="Conversation Continuity",
            query="what was the first query I asked you?",
            expected_behaviors=["file", "directory"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 4: CSV data analysis
        await self.run_test(
            name="CSV Data Analysis",
            query="if I had a CSV with student grades, how would you analyze it?",
            expected_behaviors=["average", "analysis", "statistics"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 5: Shell command execution
        await self.run_test(
            name="Shell Command Execution",
            query="run 'echo hello world' for me",
            expected_behaviors=["hello", "world"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 6: File reading
        await self.run_test(
            name="File Reading",
            query="show me the first 10 lines of setup.py",
            expected_behaviors=["setup", "cite-agent"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 7: Research paper search
        await self.run_test(
            name="Academic Research",
            query="find papers about transformer neural networks",
            expected_behaviors=["paper", "transformer"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 8: Chinese language
        await self.run_test(
            name="Chinese Language Support",
            query="你好，你能帮我分析数据吗？",
            expected_behaviors=["可以", "能", "数据"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 9: Web search
        await self.run_test(
            name="Web Search",
            query="search for latest news about AI research",
            expected_behaviors=["search", "ai"],
            avoid_behaviors=[]
        )
        
        await asyncio.sleep(2)
        
        # TEST 10: Complex multi-step task
        await self.run_test(
            name="Multi-step Task",
            query="list all Python files, then tell me which one is the largest",
            expected_behaviors=["python", "file", "largest"],
            avoid_behaviors=[]
        )
        
    def print_summary(self):
        """Print test summary"""
        print("\n\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        pass_count = sum(1 for r in self.test_results if r['result'] == 'PASS')
        warn_count = sum(1 for r in self.test_results if r['result'] == 'WARN')
        fail_count = sum(1 for r in self.test_results if r['result'] == 'FAIL')
        error_count = sum(1 for r in self.test_results if r['result'] == 'ERROR')
        timeout_count = sum(1 for r in self.test_results if r['result'] == 'TIMEOUT')
        total = len(self.test_results)
        
        print(f"\n📊 Results:")
        print(f"  ✅ PASS: {pass_count}/{total}")
        print(f"  ⚠️ WARN: {warn_count}/{total}")
        print(f"  ❌ FAIL: {fail_count}/{total}")
        print(f"  ⏱️ TIMEOUT: {timeout_count}/{total}")
        print(f"  💥 ERROR: {error_count}/{total}")
        
        print(f"\n📝 Detailed Results:")
        for result in self.test_results:
            status_emoji = {
                'PASS': '✅',
                'WARN': '⚠️',
                'FAIL': '❌',
                'TIMEOUT': '⏱️',
                'ERROR': '💥'
            }[result['result']]
            
            print(f"\n{status_emoji} {result['name']}: {result['result']}")
            if result['issues']:
                for issue in result['issues']:
                    print(f"    {issue}")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"    {warning}")
        
        print("\n" + "="*80)
        critical_failures = fail_count + error_count + timeout_count
        if critical_failures == 0:
            print("✅ ALL CRITICAL TESTS PASSED")
            if warn_count > 0:
                print(f"⚠️ {warn_count} warnings need review")
            print("🚀 READY FOR PROFESSOR BETA LAUNCH")
        else:
            print(f"❌ {critical_failures} CRITICAL FAILURES")
            print("🛑 DO NOT SHIP - NEEDS FIXES")
        print("="*80)
        
        return critical_failures == 0

async def main():
    tester = ComprehensiveStressTest()
    await tester.initialize()
    await tester.run_all_tests()
    success = tester.print_summary()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    asyncio.run(main())
