#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agent Excellence

Tests every aspect of agent quality:
- Conversation naturalness
- Edge case handling
- Research capabilities
- Context retention
- Error handling
- Response quality
- Sophistication

Goal: Make the agent feel MAGICAL - "holy shit" moment quality
"""

import asyncio
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class ExcellenceTestSuite:
    def __init__(self):
        self.agent = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.total = 0
        self.issues = []

    async def initialize(self):
        """Initialize agent"""
        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()
        print(f"{GREEN}✅ Agent initialized{RESET}\n")

    async def run_all_tests(self):
        """Run comprehensive excellence test suite"""
        print(f"{BOLD}{MAGENTA}🎯 COMPREHENSIVE AGENT EXCELLENCE TEST SUITE{RESET}")
        print("=" * 80)
        print(f"{CYAN}Goal: Make the agent feel MAGICAL and SOPHISTICATED{RESET}")
        print("=" * 80)

        await self.initialize()

        # Category 1: Conversation Naturalness
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 1: CONVERSATION NATURALNESS ━━━{RESET}")
        await self.test_casual_greeting()
        await self.test_thanks_and_appreciation()
        await self.test_follow_up_questions()
        await self.test_topic_transitions()

        # Category 2: Ambiguity & Clarification
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 2: AMBIGUITY HANDLING ━━━{RESET}")
        await self.test_ambiguous_data_query()
        await self.test_ambiguous_company_query()
        await self.test_vague_request()
        await self.test_contradictory_info()

        # Category 3: Context & Memory
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 3: CONTEXT & MEMORY ━━━{RESET}")
        await self.test_multi_turn_context()
        await self.test_pronoun_resolution()
        await self.test_topic_recall()

        # Category 4: Research Capabilities
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 4: RESEARCH CAPABILITIES ━━━{RESET}")
        await self.test_file_exploration()
        await self.test_code_understanding()

        # Category 5: Error & Edge Cases
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 5: ERROR & EDGE CASES ━━━{RESET}")
        await self.test_out_of_scope()
        await self.test_rapid_topic_change()
        await self.test_complex_multipart()

        # Category 6: Response Quality
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 6: RESPONSE QUALITY ━━━{RESET}")
        await self.test_response_scannability()
        await self.test_no_technical_jargon()
        await self.test_actionable_responses()

        # Category 7: Sophistication
        print(f"\n{BOLD}{BLUE}━━━ CATEGORY 7: SOPHISTICATION ━━━{RESET}")
        await self.test_anticipates_needs()
        await self.test_makes_connections()
        await self.test_offers_alternatives()

        # Show results
        await self.show_results()

        # Cleanup
        await self.agent.close()

    async def _evaluate_response(self, test_name: str, response: str,
                                  good_indicators: List[str],
                                  bad_indicators: List[str],
                                  warnings: List[str] = None) -> Dict[str, Any]:
        """Evaluate a response for quality"""
        issues_found = []
        warnings_found = []

        # Check for bad indicators
        for bad in bad_indicators:
            if bad.lower() in response.lower():
                issues_found.append(f"Contains bad indicator: '{bad}'")

        # Check for good indicators
        good_count = sum(1 for good in good_indicators if good.lower() in response.lower())
        if good_count == 0 and good_indicators:
            issues_found.append(f"Missing good indicators (none of: {', '.join(good_indicators[:3])})")

        # Check warnings
        if warnings:
            for warning in warnings:
                if warning.lower() in response.lower():
                    warnings_found.append(f"Warning: {warning}")

        # Determine result
        if issues_found:
            result = "FAIL"
            self.failed += 1
            self.issues.append({
                'test': test_name,
                'issues': issues_found,
                'response_preview': response[:150]
            })
        elif warnings_found:
            result = "WARN"
            self.warnings += 1
        else:
            result = "PASS"
            self.passed += 1

        self.total += 1

        return {
            'result': result,
            'issues': issues_found,
            'warnings': warnings_found,
            'good_count': good_count
        }

    # ===== CATEGORY 1: CONVERSATION NATURALNESS =====

    async def test_casual_greeting(self):
        """Test: Responds naturally to casual greetings"""
        print(f"\n{CYAN}Test 1.1: Casual Greeting{RESET}")

        request = ChatRequest(
            question="Hey there! How's it going?",
            user_id="test_1_1",
            conversation_id="conv_1_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "Casual Greeting",
            response.response,
            good_indicators=['hey', 'hi', 'hello', 'help', 'dig into', 'ready', 'what can'],
            bad_indicators=['executing', 'processing', 'acknowledged', 'affirmative', 'ERROR', 'HTTP'],
            warnings=['let me know what', 'feel free']  # Slightly robotic
        )

        self._print_result(eval_result)

    async def test_thanks_and_appreciation(self):
        """Test: Handles thanks naturally"""
        print(f"\n{CYAN}Test 1.2: Thanks & Appreciation{RESET}")

        request = ChatRequest(
            question="Thanks for your help!",
            user_id="test_1_2",
            conversation_id="conv_1_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "Thanks & Appreciation",
            response.response,
            good_indicators=['no problem', 'happy to help', 'anytime', 'glad', 'sure thing', 'you bet'],
            bad_indicators=['executing', 'processing', 'acknowledged', 'affirmative', 'ERROR']
        )

        self._print_result(eval_result)

    async def test_follow_up_questions(self):
        """Test: Handles follow-up questions smoothly"""
        print(f"\n{CYAN}Test 1.3: Follow-up Questions{RESET}")

        conv_id = "conv_1_3"

        # Turn 1
        req1 = ChatRequest(
            question="What Python files are in this directory?",
            user_id="test_1_3",
            conversation_id=conv_id
        )
        resp1 = await self.agent.process_request(req1)

        # Turn 2 - follow up
        req2 = ChatRequest(
            question="How many did you find?",
            user_id="test_1_3",
            conversation_id=conv_id
        )
        resp2 = await self.agent.process_request(req2)

        print(f"  👤 User: {req1.question}")
        print(f"  🤖 Agent: {resp1.response[:100]}...")
        print(f"  👤 User: {req2.question}")
        print(f"  🤖 Agent: {resp2.response[:200]}")

        # Check if agent uses context from first turn
        has_number = any(str(i) in resp2.response for i in range(1, 100))
        references_previous = any(word in resp2.response.lower() for word in ['found', 'see', 'there are', 'i see'])

        if has_number and references_previous:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Agent uses context from previous turn{RESET}")
        else:
            self.failed += 1
            self.total += 1
            print(f"  {RED}❌ FAIL: Agent doesn't properly use context{RESET}")
            self.issues.append({
                'test': 'Follow-up Questions',
                'issues': ['Did not retain context from previous turn'],
                'response_preview': resp2.response[:150]
            })

    async def test_topic_transitions(self):
        """Test: Handles topic transitions naturally"""
        print(f"\n{CYAN}Test 1.4: Topic Transitions{RESET}")

        conv_id = "conv_1_4"

        # Topic 1: Files
        req1 = ChatRequest(
            question="Show me Python files",
            user_id="test_1_4",
            conversation_id=conv_id
        )
        resp1 = await self.agent.process_request(req1)

        # Topic 2: Something completely different
        req2 = ChatRequest(
            question="Actually, never mind. Can you help me understand what this project does?",
            user_id="test_1_4",
            conversation_id=conv_id
        )
        resp2 = await self.agent.process_request(req2)

        print(f"  👤 User: {req1.question}")
        print(f"  🤖 Agent: {resp1.response[:80]}...")
        print(f"  👤 User: {req2.question}")
        print(f"  🤖 Agent: {resp2.response[:200]}")

        eval_result = await self._evaluate_response(
            "Topic Transitions",
            resp2.response,
            good_indicators=['project', 'does', 'helps', 'designed', 'agent'],
            bad_indicators=['python files', 'ERROR', 'HTTP']
        )

        self._print_result(eval_result)

    # ===== CATEGORY 2: AMBIGUITY HANDLING =====

    async def test_ambiguous_data_query(self):
        """Test: Asks clarification for ambiguous 'data' queries"""
        print(f"\n{CYAN}Test 2.1: Ambiguous Data Query{RESET}")

        request = ChatRequest(
            question="I need help with data processing",
            user_id="test_2_1",
            conversation_id="conv_2_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "Ambiguous Data Query",
            response.response,
            good_indicators=['what kind', 'clarify', 'do you mean', 'are you', 'financial', 'csv', 'files'],
            bad_indicators=['revenue', 'profit', 'finsight', 'HTTP', 'ERROR', 'unavailable']
        )

        self._print_result(eval_result)

    async def test_ambiguous_company_query(self):
        """Test: Asks clarification for vague company queries"""
        print(f"\n{CYAN}Test 2.2: Ambiguous Company Query{RESET}")

        request = ChatRequest(
            question="Tell me about the company",
            user_id="test_2_2",
            conversation_id="conv_2_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "Ambiguous Company Query",
            response.response,
            good_indicators=['which company', 'what company', 'what kind of company', 'clarify', 'which one', 'specific'],
            bad_indicators=['revenue', 'HTTP']  # Removed 'ERROR' since friendly error is OK
        )

        self._print_result(eval_result)

    async def test_vague_request(self):
        """Test: Handles very vague requests gracefully"""
        print(f"\n{CYAN}Test 2.3: Vague Request{RESET}")

        request = ChatRequest(
            question="Help me with my project",
            user_id="test_2_3",
            conversation_id="conv_2_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "Vague Request",
            response.response,
            good_indicators=['what kind', 'tell me more', 'what are you', 'help you with', 'working on'],
            bad_indicators=['ERROR', 'HTTP', 'unavailable']
        )

        self._print_result(eval_result)

    async def test_contradictory_info(self):
        """Test: Handles contradictory information"""
        print(f"\n{CYAN}Test 2.4: Contradictory Information{RESET}")

        conv_id = "conv_2_4"

        req1 = ChatRequest(
            question="I'm working on a Python project",
            user_id="test_2_4",
            conversation_id=conv_id
        )
        resp1 = await self.agent.process_request(req1)

        req2 = ChatRequest(
            question="Actually it's a JavaScript project, not Python",
            user_id="test_2_4",
            conversation_id=conv_id
        )
        resp2 = await self.agent.process_request(req2)

        print(f"  👤 User: {req1.question}")
        print(f"  🤖 Agent: {resp1.response[:80]}...")
        print(f"  👤 User: {req2.question}")
        print(f"  🤖 Agent: {resp2.response[:200]}")

        # Should acknowledge the correction
        acknowledges_correction = any(word in resp2.response.lower() for word in
                                      ['got it', 'javascript', 'understood', 'okay', 'js', 'node'])

        if acknowledges_correction:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Acknowledges correction naturally{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Doesn't acknowledge correction{RESET}")

    # ===== CATEGORY 3: CONTEXT & MEMORY =====

    async def test_multi_turn_context(self):
        """Test: Maintains context across multiple turns"""
        print(f"\n{CYAN}Test 3.1: Multi-Turn Context (5 turns){RESET}")

        conv_id = "conv_3_1"

        turns = [
            "Let's work on a research project about AI agents",
            "I want to focus on conversation quality",
            "What papers should I read?",
            "Which one would be most relevant?",
            "Can you explain why?"
        ]

        responses = []
        for i, question in enumerate(turns, 1):
            req = ChatRequest(
                question=question,
                user_id="test_3_1",
                conversation_id=conv_id
            )
            resp = await self.agent.process_request(req)
            responses.append(resp.response)
            print(f"  Turn {i}")
            print(f"    👤 User: {question}")
            print(f"    🤖 Agent: {resp.response[:100]}...")

        # Check if last response references earlier context
        last_response = responses[-1].lower()
        has_context = any(keyword in last_response for keyword in
                         ['conversation', 'ai', 'agents', 'quality', 'paper', 'research'])

        if has_context:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Maintains context across 5 turns{RESET}")
        else:
            self.failed += 1
            self.total += 1
            print(f"  {RED}❌ FAIL: Lost context{RESET}")
            self.issues.append({
                'test': 'Multi-Turn Context',
                'issues': ['Lost context after multiple turns'],
                'response_preview': last_response[:150]
            })

    async def test_pronoun_resolution(self):
        """Test: Resolves pronouns correctly"""
        print(f"\n{CYAN}Test 3.2: Pronoun Resolution{RESET}")

        conv_id = "conv_3_2"

        req1 = ChatRequest(
            question="Show me the main Python file in cite_agent directory",
            user_id="test_3_2",
            conversation_id=conv_id
        )
        resp1 = await self.agent.process_request(req1)

        req2 = ChatRequest(
            question="What does it do?",
            user_id="test_3_2",
            conversation_id=conv_id
        )
        resp2 = await self.agent.process_request(req2)

        print(f"  👤 User: {req1.question}")
        print(f"  🤖 Agent: {resp1.response[:100]}...")
        print(f"  👤 User: {req2.question}")
        print(f"  🤖 Agent: {resp2.response[:200]}")

        # Should reference the file from previous turn
        references_file = any(word in resp2.response.lower() for word in
                             ['file', 'agent', 'nocturnal', 'enhanced'])

        if references_file:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Resolved 'it' to file from previous turn{RESET}")
        else:
            self.failed += 1
            self.total += 1
            print(f"  {RED}❌ FAIL: Failed to resolve pronoun{RESET}")
            self.issues.append({
                'test': 'Pronoun Resolution',
                'issues': ['Failed to resolve "it" pronoun'],
                'response_preview': resp2.response[:150]
            })

    async def test_topic_recall(self):
        """Test: Recalls topics mentioned earlier"""
        print(f"\n{CYAN}Test 3.3: Topic Recall{RESET}")

        conv_id = "conv_3_3"

        req1 = ChatRequest(
            question="I'm researching machine learning interpretability",
            user_id="test_3_3",
            conversation_id=conv_id
        )
        resp1 = await self.agent.process_request(req1)

        # Distractor turn
        req2 = ChatRequest(
            question="What files are in this directory?",
            user_id="test_3_3",
            conversation_id=conv_id
        )
        resp2 = await self.agent.process_request(req2)

        # Recall earlier topic
        req3 = ChatRequest(
            question="Back to my research topic - what should I focus on first?",
            user_id="test_3_3",
            conversation_id=conv_id
        )
        resp3 = await self.agent.process_request(req3)

        print(f"  👤 User: {req1.question}")
        print(f"  🤖 Agent: {resp1.response[:80]}...")
        print(f"  👤 User: {req2.question}")
        print(f"  🤖 Agent: {resp2.response[:80]}...")
        print(f"  👤 User: {req3.question}")
        print(f"  🤖 Agent: {resp3.response[:200]}")

        # Should recall interpretability research
        recalls_topic = any(word in resp3.response.lower() for word in
                           ['interpretability', 'machine learning', 'ml', 'explainability'])

        if recalls_topic:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Recalled earlier research topic{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Didn't explicitly recall topic{RESET}")

    # ===== CATEGORY 4: RESEARCH CAPABILITIES =====

    async def test_file_exploration(self):
        """Test: Explores and explains files intelligently"""
        print(f"\n{CYAN}Test 4.1: File Exploration{RESET}")

        request = ChatRequest(
            question="What's the main agent file and what does it do?",
            user_id="test_4_1",
            conversation_id="conv_4_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        eval_result = await self._evaluate_response(
            "File Exploration",
            response.response,
            good_indicators=['agent', 'file', 'enhanced', 'nocturnal', 'handles', 'processes'],
            bad_indicators=['ERROR', 'HTTP', 'unavailable']
        )

        self._print_result(eval_result)

    async def test_code_understanding(self):
        """Test: Understands and explains code"""
        print(f"\n{CYAN}Test 4.2: Code Understanding{RESET}")

        request = ChatRequest(
            question="What does the _analyze_request_type method do?",
            user_id="test_4_2",
            conversation_id="conv_4_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        eval_result = await self._evaluate_response(
            "Code Understanding",
            response.response,
            good_indicators=['analyze', 'request', 'type', 'determines', 'detects', 'checks'],
            bad_indicators=['ERROR', 'HTTP', 'unavailable']
        )

        self._print_result(eval_result)

    # ===== CATEGORY 5: ERROR & EDGE CASES =====

    async def test_out_of_scope(self):
        """Test: Handles out-of-scope requests gracefully"""
        print(f"\n{CYAN}Test 5.1: Out of Scope Request{RESET}")

        request = ChatRequest(
            question="Can you make me a sandwich?",
            user_id="test_5_1",
            conversation_id="conv_5_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "Out of Scope",
            response.response,
            good_indicators=['help with', 'can help', 'focus on', 'designed for', 'good at'],
            bad_indicators=['ERROR', 'HTTP', 'executing sandwich']
        )

        self._print_result(eval_result)

    async def test_rapid_topic_change(self):
        """Test: Handles rapid topic changes"""
        print(f"\n{CYAN}Test 5.2: Rapid Topic Changes{RESET}")

        conv_id = "conv_5_2"

        topics = [
            "Show me Python files",
            "What's 2+2?",
            "List directories",
            "What's the weather?",
            "Back to the files - how many Python files?"
        ]

        for i, topic in enumerate(topics, 1):
            req = ChatRequest(
                question=topic,
                user_id="test_5_2",
                conversation_id=conv_id
            )
            resp = await self.agent.process_request(req)
            print(f"  Turn {i}: {topic[:40]} → {resp.response[:60]}...")

        # If it doesn't crash, that's good enough
        self.passed += 1
        self.total += 1
        print(f"  {GREEN}✅ PASS: Handled rapid topic changes{RESET}")

    async def test_complex_multipart(self):
        """Test: Handles complex multi-part questions"""
        print(f"\n{CYAN}Test 5.3: Complex Multi-Part Question{RESET}")

        request = ChatRequest(
            question="Can you find Python files related to testing, check if they import pytest, and tell me which ones have the most test cases?",
            user_id="test_5_3",
            conversation_id="conv_5_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        # Check if it addresses multiple parts
        addresses_parts = sum([
            'python' in response.response.lower() or 'test' in response.response.lower(),
            'pytest' in response.response.lower() or 'import' in response.response.lower(),
            'cases' in response.response.lower() or 'most' in response.response.lower()
        ])

        if addresses_parts >= 2:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Addressed {addresses_parts}/3 parts{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Only addressed {addresses_parts}/3 parts{RESET}")

    # ===== CATEGORY 6: RESPONSE QUALITY =====

    async def test_response_scannability(self):
        """Test: Responses are scannable"""
        print(f"\n{CYAN}Test 6.1: Response Scannability{RESET}")

        request = ChatRequest(
            question="What's in this project?",
            user_id="test_6_1",
            conversation_id="conv_6_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        # Check for structure
        has_bullets = '•' in response.response or '-' in response.response or '*' in response.response
        has_line_breaks = response.response.count('\n') >= 3
        not_wall_of_text = len(response.response.split('\n')[0]) < 150

        score = sum([has_bullets, has_line_breaks, not_wall_of_text])

        if score >= 2:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Scannable (bullets: {has_bullets}, breaks: {has_line_breaks}, not wall: {not_wall_of_text}){RESET}")
        else:
            self.failed += 1
            self.total += 1
            print(f"  {RED}❌ FAIL: Not scannable enough{RESET}")
            self.issues.append({
                'test': 'Response Scannability',
                'issues': [f'Score: {score}/3'],
                'response_preview': response.response[:150]
            })

    async def test_no_technical_jargon(self):
        """Test: No technical jargon leaked"""
        print(f"\n{CYAN}Test 6.2: No Technical Jargon{RESET}")

        request = ChatRequest(
            question="Help me understand the project",
            user_id="test_6_2",
            conversation_id="conv_6_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        eval_result = await self._evaluate_response(
            "No Technical Jargon",
            response.response,
            good_indicators=['project', 'helps', 'designed', 'works'],
            bad_indicators=['HTTP', 'ERROR', 'GET calc/', 'POST /api/', '(value unavailable)', 'FinSight GET']
        )

        self._print_result(eval_result)

    async def test_actionable_responses(self):
        """Test: Responses are actionable"""
        print(f"\n{CYAN}Test 6.3: Actionable Responses{RESET}")

        request = ChatRequest(
            question="I want to add a new feature to this project",
            user_id="test_6_3",
            conversation_id="conv_6_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:200]}")

        # Should ask about the feature or offer guidance
        is_actionable = any(word in response.response.lower() for word in
                           ['what kind', 'tell me', 'which', 'where', 'how', 'first', 'start'])

        if is_actionable:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Response is actionable{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Response could be more actionable{RESET}")

    # ===== CATEGORY 7: SOPHISTICATION =====

    async def test_anticipates_needs(self):
        """Test: Anticipates user needs"""
        print(f"\n{CYAN}Test 7.1: Anticipates Needs{RESET}")

        request = ChatRequest(
            question="Show me the test files",
            user_id="test_7_1",
            conversation_id="conv_7_1"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        # Should offer next steps
        offers_next_steps = any(phrase in response.response.lower() for phrase in
                               ['want me to', 'would you like', 'should i', 'can also', 'need help'])

        if offers_next_steps:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Anticipates next steps{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Doesn't anticipate next steps{RESET}")

    async def test_makes_connections(self):
        """Test: Makes intelligent connections"""
        print(f"\n{CYAN}Test 7.2: Makes Connections{RESET}")

        request = ChatRequest(
            question="I see there's a test_magical_improvements.py file. What's that about?",
            user_id="test_7_2",
            conversation_id="conv_7_2"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        # Should connect it to the improvement work
        makes_connection = any(word in response.response.lower() for word in
                              ['test', 'improvement', 'magical', 'response', 'quality'])

        if makes_connection:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Makes intelligent connections{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Doesn't make connections{RESET}")

    async def test_offers_alternatives(self):
        """Test: Offers alternatives when needed"""
        print(f"\n{CYAN}Test 7.3: Offers Alternatives{RESET}")

        request = ChatRequest(
            question="I want to search for something but I'm not sure where to start",
            user_id="test_7_3",
            conversation_id="conv_7_3"
        )

        response = await self.agent.process_request(request)
        print(f"  👤 User: {request.question}")
        print(f"  🤖 Agent: {response.response[:300]}")

        # Should offer multiple options
        offers_options = response.response.count('•') >= 2 or response.response.count('-') >= 2

        if offers_options:
            self.passed += 1
            self.total += 1
            print(f"  {GREEN}✅ PASS: Offers multiple alternatives{RESET}")
        else:
            self.warnings += 1
            self.total += 1
            print(f"  {YELLOW}⚠️  WARN: Could offer more alternatives{RESET}")

    def _print_result(self, eval_result: Dict[str, Any]):
        """Print evaluation result"""
        result = eval_result['result']
        if result == 'PASS':
            print(f"  {GREEN}✅ PASS{RESET}")
        elif result == 'WARN':
            print(f"  {YELLOW}⚠️  WARN: {', '.join(eval_result['warnings'])}{RESET}")
        else:
            print(f"  {RED}❌ FAIL: {', '.join(eval_result['issues'])}{RESET}")

    async def show_results(self):
        """Show comprehensive test results"""
        print(f"\n{'=' * 80}")
        print(f"{BOLD}{MAGENTA}📊 COMPREHENSIVE EXCELLENCE TEST RESULTS{RESET}")
        print(f"{'=' * 80}")

        total_score = (self.passed / self.total * 100) if self.total > 0 else 0

        print(f"\n{BOLD}Score: {total_score:.1f}% ({self.passed}/{self.total}){RESET}")
        print(f"  {GREEN}✅ Passed: {self.passed}{RESET}")
        print(f"  {YELLOW}⚠️  Warnings: {self.warnings}{RESET}")
        print(f"  {RED}❌ Failed: {self.failed}{RESET}")

        if total_score >= 90:
            print(f"\n{GREEN}{BOLD}🎉 EXCELLENT! Agent is sophisticated and magical!{RESET}")
        elif total_score >= 75:
            print(f"\n{YELLOW}{BOLD}✨ GOOD! Agent is solid but needs polish{RESET}")
        elif total_score >= 60:
            print(f"\n{YELLOW}{BOLD}⚠️  DECENT: Agent works but needs significant improvements{RESET}")
        else:
            print(f"\n{RED}{BOLD}❌ NEEDS WORK: Agent requires major improvements{RESET}")

        # Show critical issues
        if self.issues:
            print(f"\n{BOLD}{RED}Critical Issues to Fix:{RESET}")
            for i, issue in enumerate(self.issues[:10], 1):  # Show top 10
                print(f"\n{i}. {issue['test']}")
                for problem in issue['issues']:
                    print(f"   • {problem}")
                if issue.get('response_preview'):
                    print(f"   Preview: {issue['response_preview']}...")

        print(f"\n{'=' * 80}")


async def main():
    """Run the comprehensive excellence test suite"""

    # Check API key
    if not os.getenv('CEREBRAS_API_KEY') and not os.getenv('GROQ_API_KEY'):
        print(f"{RED}❌ No API key found!{RESET}")
        print(f"Set: export CEREBRAS_API_KEY='your-key' or export GROQ_API_KEY='your-key'")
        return

    os.environ['USE_LOCAL_KEYS'] = 'true'

    suite = ExcellenceTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
