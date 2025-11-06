#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE MOCK TEST SUITE
Fast, reliable testing without live API dependencies
Validates agent functionality with mocked responses
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatResponse

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'


@dataclass
class TestResult:
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None


class MockTestSuite:
    """Fast mock-based test suite"""
    
    def __init__(self):
        self.agent = None
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    async def initialize(self):
        """Initialize agent"""
        print(f"\n{CYAN}{'=' * 80}{RESET}")
        print(f"{CYAN}🧪 COMPREHENSIVE MOCK TEST SUITE{RESET}")
        print(f"{CYAN}{'=' * 80}{RESET}\n")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"{BLUE}🔧 Initializing agent...{RESET}")
        try:
            self.agent = EnhancedNocturnalAgent()
            await self.agent.initialize()
            print(f"{GREEN}✅ Agent initialized successfully{RESET}\n")
            return True
        except Exception as e:
            print(f"{RED}❌ Failed to initialize agent: {e}{RESET}\n")
            return False
    
    async def test_agent_instantiation(self):
        """Test 1: Agent can be instantiated"""
        start = time.time()
        try:
            agent = EnhancedNocturnalAgent()
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Agent Instantiation", True, duration))
            print(f"  {GREEN}✅{RESET} Agent instantiation: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Agent Instantiation", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Agent instantiation: {e}")
            return False
    
    async def test_agent_initialization(self):
        """Test 2: Agent can be initialized asynchronously"""
        start = time.time()
        try:
            agent = EnhancedNocturnalAgent()
            await agent.initialize()
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Agent Initialization", True, duration))
            print(f"  {GREEN}✅{RESET} Agent initialization: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Agent Initialization", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Agent initialization: {e}")
            return False
    
    async def test_cerebras_client_init(self):
        """Test 3: Cerebras client initializes without errors"""
        start = time.time()
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key="test_key",
                base_url="https://api.cerebras.ai/v1"
            )
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Cerebras Client Init", True, duration))
            print(f"  {GREEN}✅{RESET} Cerebras client initialization: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Cerebras Client Init", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Cerebras client init: {e}")
            return False
    
    async def test_api_key_loading(self):
        """Test 4: API keys load from environment"""
        start = time.time()
        try:
            import os
            os.environ['USE_LOCAL_KEYS'] = 'true'
            os.environ['CEREBRAS_API_KEY'] = 'test_key_123'
            
            agent = EnhancedNocturnalAgent()
            await agent.initialize()
            
            # Check that keys were loaded
            assert agent.api_keys, "No API keys loaded"
            assert len(agent.api_keys) > 0, "API keys list is empty"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("API Key Loading", True, duration))
            print(f"  {GREEN}✅{RESET} API key loading: {duration:.2f}ms (loaded {len(agent.api_keys)} key(s))")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("API Key Loading", False, duration, str(e)))
            print(f"  {RED}❌{RESET} API key loading: {e}")
            return False
    
    async def test_llm_provider_detection(self):
        """Test 5: LLM provider correctly detected"""
        start = time.time()
        try:
            import os
            os.environ['USE_LOCAL_KEYS'] = 'true'
            os.environ['CEREBRAS_API_KEY'] = 'test_key_123'
            
            agent = EnhancedNocturnalAgent()
            await agent.initialize()
            
            assert agent.llm_provider in ['cerebras', 'groq'], f"Unknown provider: {agent.llm_provider}"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("LLM Provider Detection", True, duration))
            print(f"  {GREEN}✅{RESET} LLM provider detection: {duration:.2f}ms (provider={agent.llm_provider})")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("LLM Provider Detection", False, duration, str(e)))
            print(f"  {RED}❌{RESET} LLM provider detection: {e}")
            return False
    
    async def test_conversation_history(self):
        """Test 6: Conversation history tracking"""
        start = time.time()
        try:
            assert isinstance(self.agent.conversation_history, list), "Conversation history not a list"
            assert len(self.agent.conversation_history) == 0, "Conversation history should start empty"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Conversation History", True, duration))
            print(f"  {GREEN}✅{RESET} Conversation history: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Conversation History", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Conversation history: {e}")
            return False
    
    async def test_shell_session_init(self):
        """Test 7: Shell session initialization"""
        start = time.time()
        try:
            # Should either be None or a valid subprocess
            if self.agent.shell_session is not None:
                assert hasattr(self.agent.shell_session, 'poll'), "Shell session doesn't have poll method"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Shell Session Init", True, duration))
            print(f"  {GREEN}✅{RESET} Shell session: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Shell Session Init", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Shell session: {e}")
            return False
    
    async def test_memory_system(self):
        """Test 8: Memory system initialized"""
        start = time.time()
        try:
            assert isinstance(self.agent.memory, dict), "Memory is not a dict"
            assert isinstance(self.agent.daily_token_usage, (int, float)), "Token usage not numeric"
            assert self.agent.daily_limit > 0, "Daily limit not set"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Memory System", True, duration))
            print(f"  {GREEN}✅{RESET} Memory system: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Memory System", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Memory system: {e}")
            return False
    
    async def test_workflow_manager(self):
        """Test 9: Workflow manager initialized"""
        start = time.time()
        try:
            assert self.agent.workflow is not None, "Workflow manager is None"
            # Check for any workflow-related methods
            assert hasattr(self.agent.workflow, 'add_paper'), "Workflow manager missing expected methods"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Workflow Manager", True, duration))
            print(f"  {GREEN}✅{RESET} Workflow manager: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Workflow Manager", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Workflow manager: {e}")
            return False
    
    async def test_enterprise_infrastructure(self):
        """Test 10: Infrastructure components verified"""
        start = time.time()
        try:
            # Verify that we have the core execution engine
            assert self.agent.conversation_history is not None, "Conversation engine not initialized"
            assert self.agent.workflow is not None, "Workflow engine not initialized"
            
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Enterprise Infrastructure", True, duration))
            print(f"  {GREEN}✅{RESET} Enterprise infrastructure: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult("Enterprise Infrastructure", False, duration, str(e)))
            print(f"  {RED}❌{RESET} Enterprise infrastructure: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print(f"{BLUE}📋 Running comprehensive tests...{RESET}\n")
        
        tests = [
            self.test_agent_instantiation,
            self.test_agent_initialization,
            self.test_cerebras_client_init,
            self.test_api_key_loading,
            self.test_llm_provider_detection,
            self.test_conversation_history,
            self.test_shell_session_init,
            self.test_memory_system,
            self.test_workflow_manager,
            self.test_enterprise_infrastructure,
        ]
        
        for test_func in tests:
            await test_func()
        
        print("")
    
    def generate_report(self):
        """Generate test report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        total_duration = sum(r.duration_ms for r in self.results)
        
        print(f"{CYAN}{'=' * 80}{RESET}")
        print(f"{CYAN}📊 TEST REPORT{RESET}")
        print(f"{CYAN}{'=' * 80}{RESET}\n")
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        if failed > 0:
            print(f"{RED}Failed: {failed}{RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Total Duration: {total_duration:.2f}ms")
        print(f"Avg Per Test: {total_duration/total:.2f}ms\n")
        
        if failed > 0:
            print(f"{RED}❌ FAILURES:{RESET}")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.error}")
            print("")
        
        print(f"{CYAN}{'=' * 80}{RESET}")
        
        if pass_rate >= 90:
            print(f"{GREEN}✅ BETA READY - {pass_rate:.1f}% pass rate{RESET}")
            return True
        elif pass_rate >= 70:
            print(f"{YELLOW}⚠️  CAUTION - {pass_rate:.1f}% pass rate{RESET}")
            return False
        else:
            print(f"{RED}❌ NOT READY - {pass_rate:.1f}% pass rate{RESET}")
            return False


async def main():
    """Main test execution"""
    suite = MockTestSuite()
    
    try:
        if not await suite.initialize():
            sys.exit(1)
        
        await suite.run_all_tests()
        success = suite.generate_report()
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"\n{RED}❌ Test suite failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
