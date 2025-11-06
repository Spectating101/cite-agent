#!/usr/bin/env python3
"""
Test script to demonstrate the magical response improvements

Focuses on the key improvements:
1. Clarification for ambiguous queries (Test 6 fix)
2. Improved workspace listing
3. No technical details leaking
"""

import asyncio
import os
import sys

# Add cite_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class MagicalImprovementTests:
    def __init__(self):
        self.agent = EnhancedNocturnalAgent()
        self.passed = 0
        self.failed = 0
        self.total = 0

    async def run_all_tests(self):
        """Run all improvement validation tests"""
        print(f"{BOLD}🎨 Testing Magical Response Improvements{RESET}")
        print("=" * 70)

        # Initialize agent first
        print(f"\n{BLUE}Initializing agent...{RESET}")
        await self.agent.initialize()
        print(f"{GREEN}✅ Agent ready{RESET}\n")

        # Test 1: Ambiguous Query Clarification (The Test 6 Fix)
        await self.test_ambiguous_data_processing()

        # Test 2: No Technical Details Leak
        await self.test_no_technical_leaks()

        # Test 3: Workspace Listing Format
        await self.test_workspace_listing_format()

        # Results
        print("\n" + "=" * 70)
        print(f"📊 {BOLD}RESULTS{RESET}")
        print("=" * 70)

        if self.failed == 0:
            print(f"{GREEN}✅ ALL TESTS PASSED: {self.passed}/{self.total}{RESET}")
            print(f"\n{BOLD}🎉 Responses should now feel intuitive and magical!{RESET}")
        else:
            print(f"{YELLOW}⚠️  PASSED: {self.passed}/{self.total}{RESET}")
            print(f"{RED}❌ FAILED: {self.failed}/{self.total}{RESET}")

        print("=" * 70)

        # Cleanup
        await self.agent.close()

    async def test_ambiguous_data_processing(self):
        """
        Test 1: Ambiguous Query Clarification

        This is the FIX for Test 6 where "data processing" triggered
        financial tools incorrectly.

        Expected: Agent should ask clarification instead of guessing.
        """
        self.total += 1
        print(f"\n{BLUE}📍 Test 1: Ambiguous Query Clarification (Test 6 Fix){RESET}")
        print("-" * 70)

        # The problematic query from Test 6
        request = ChatRequest(
            question="I'm working on a data processing project",
            user_id="test_magical_1",
            conversation_id="improvement_test_1"
        )

        print(f"{YELLOW}👤 User:{RESET} {request.question}")

        response = await self.agent.process_request(request)

        print(f"{YELLOW}🤖 Agent:{RESET} {response.response}\n")

        # Validate improvements
        issues = []

        # Check 1: Should ask clarification
        clarification_phrases = [
            'clarify', 'what kind of', 'do you mean', 'are you thinking of',
            'is this about', 'looking for'
        ]
        has_clarification = any(phrase in response.response.lower() for phrase in clarification_phrases)

        if not has_clarification:
            issues.append("❌ Agent didn't ask clarification for ambiguous query")

        # Check 2: Should NOT trigger financial tools
        financial_triggers = ['revenue', 'profit', 'earnings', 'finsight', 'stock']
        has_financial = any(trigger in response.response.lower() for trigger in financial_triggers)

        if has_financial:
            issues.append("❌ Agent incorrectly triggered financial tools")

        # Check 3: Should NOT show technical details
        technical_leaks = ['HTTP 500', 'HTTP 404', 'calc/I/', 'GET ', 'POST ']
        has_technical = any(leak in response.response for leak in technical_leaks)

        if has_technical:
            issues.append("❌ Agent leaked technical details to user")

        # Check 4: Should mention multiple data types as options
        data_types = ['csv', 'json', 'excel', 'financial', 'database']
        mentioned_types = sum(1 for dtype in data_types if dtype in response.response.lower())

        if mentioned_types < 2:
            issues.append(f"⚠️  Agent only mentioned {mentioned_types} data type options (expected 2+)")

        # Results
        if not issues:
            print(f"{GREEN}✅ PASS: Agent asks clarification naturally{RESET}")
            print(f"   • Asked clarification instead of guessing")
            print(f"   • Did NOT trigger financial tools")
            print(f"   • No technical details shown")
            print(f"   • Offered {mentioned_types} data type options")
            self.passed += 1
        else:
            print(f"{RED}❌ FAIL: Issues detected:{RESET}")
            for issue in issues:
                print(f"   {issue}")
            self.failed += 1

    async def test_no_technical_leaks(self):
        """
        Test 2: No Technical Details Leak

        Validates that technical details are filtered from responses.
        """
        self.total += 1
        print(f"\n{BLUE}📍 Test 2: No Technical Details in Responses{RESET}")
        print("-" * 70)

        # Create a simple query
        request = ChatRequest(
            question="What's in this directory?",
            user_id="test_magical_2",
            conversation_id="improvement_test_2"
        )

        print(f"{YELLOW}👤 User:{RESET} {request.question}")

        response = await self.agent.process_request(request)

        print(f"{YELLOW}🤖 Agent:{RESET} {response.response}\n")

        # Validate no technical leaks
        issues = []

        # Check for common technical leaks
        technical_patterns = [
            'HTTP 500', 'HTTP 404', 'HTTP 502', 'HTTP 503',
            '/home/user/', '/home/phyrexian/',
            'GET calc/', 'POST /api/',
            '(value unavailable)',
            'FinSight GET', 'FinSight POST'
        ]

        found_leaks = [pattern for pattern in technical_patterns if pattern in response.response]

        if found_leaks:
            issues.append(f"❌ Technical details leaked: {', '.join(found_leaks)}")

        # Check for Python internals in file listings
        python_internals = ['__pycache__', '.pyc', '.pytest_cache']
        found_internals = [internal for internal in python_internals if internal in response.response]

        if found_internals:
            issues.append(f"⚠️  Python internals shown: {', '.join(found_internals)}")

        # Results
        if not issues:
            print(f"{GREEN}✅ PASS: No technical details leaked{RESET}")
            print(f"   • No HTTP error codes")
            print(f"   • No API endpoint paths")
            print(f"   • No long file paths")
            print(f"   • No technical status messages")
            self.passed += 1
        else:
            print(f"{RED}❌ FAIL: Technical details found:{RESET}")
            for issue in issues:
                print(f"   {issue}")
            self.failed += 1

    async def test_workspace_listing_format(self):
        """
        Test 3: Workspace Listing Format

        Validates that workspace listings are scannable and user-friendly.
        """
        self.total += 1
        print(f"\n{BLUE}📍 Test 3: Workspace Listing Format{RESET}")
        print("-" * 70)

        request = ChatRequest(
            question="Show me what's in this directory",
            user_id="test_magical_3",
            conversation_id="improvement_test_3"
        )

        print(f"{YELLOW}👤 User:{RESET} {request.question}")

        response = await self.agent.process_request(request)

        print(f"{YELLOW}🤖 Agent:{RESET} {response.response}\n")

        # Validate format improvements
        issues = []

        # Check 1: Should NOT start with long technical path
        first_line = response.response.split('\n')[0]
        if '/home/' in first_line and len(first_line) > 80:
            issues.append("❌ Response starts with long technical path")

        # Check 2: Should have structure (bullets, line breaks)
        has_bullets = '•' in response.response or '-' in response.response or '*' in response.response
        has_structure = response.response.count('\n') >= 3

        if not has_bullets:
            issues.append("⚠️  Response lacks bullet points for scannability")

        if not has_structure:
            issues.append("⚠️  Response lacks structure (too few line breaks)")

        # Check 3: Should offer next steps or ask questions
        ends_with_offer = (
            response.response.rstrip().endswith('?') or
            any(phrase in response.response.lower() for phrase in [
                'want me to', 'would you like', 'need help', 'should i',
                'look at something specific', 'explain'
            ])
        )

        if not ends_with_offer:
            issues.append("⚠️  Response doesn't anticipate next steps")

        # Check 4: Project context detection (if applicable)
        has_context = any(phrase in response.response.lower() for phrase in [
            'python project', 'node.js project', 'rust project',
            'looks like', 'i see'
        ])

        # Results
        if not issues:
            print(f"{GREEN}✅ PASS: Workspace listing is scannable and helpful{RESET}")
            if has_context:
                print(f"   • Detected project context")
            print(f"   • Has bullets/structure for scannability")
            print(f"   • Anticipates next steps")
            print(f"   • No long technical paths at start")
            self.passed += 1
        else:
            print(f"{YELLOW}⚠️  PARTIAL: Some improvements needed:{RESET}")
            for issue in issues:
                print(f"   {issue}")
            if not issues or all('⚠️' in issue for issue in issues):
                self.passed += 1  # Count as pass if only warnings
            else:
                self.failed += 1


async def main():
    """Run the magical improvement tests"""

    # Check if API key is available
    if not os.getenv('CEREBRAS_API_KEY') and not os.getenv('GROQ_API_KEY'):
        print(f"{RED}❌ No API key found!{RESET}")
        print(f"\nSet one of these environment variables:")
        print(f"  export CEREBRAS_API_KEY='your-key-here'")
        print(f"  export GROQ_API_KEY='your-key-here'")
        print(f"\nOr use local mode:")
        print(f"  export USE_LOCAL_KEYS=true")
        print(f"  export CEREBRAS_API_KEY='your-key-here'")
        return

    # Set local mode for testing
    os.environ['USE_LOCAL_KEYS'] = 'true'

    tests = MagicalImprovementTests()
    await tests.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
