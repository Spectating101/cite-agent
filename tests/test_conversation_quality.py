#!/usr/bin/env python3
"""
Integration tests for conversation quality - shows FULL workflows, not just isolated queries.

These tests verify:
1. User asks a question
2. Agent responds cleanly (no code leaks, no ANSI codes, no artifacts)
3. Follow-up questions work naturally
4. The ENTIRE conversation feels natural

Run with: pytest tests/test_conversation_quality.py -v
"""

import asyncio
import os
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent import EnhancedNocturnalAgent, ChatRequest


class ConversationTester:
    """Helper to test full conversation workflows"""

    def __init__(self):
        self.agent = None
        self.conversation_id = "test_conversation"
        self.conversation_history = []

    async def setup(self):
        """Initialize agent with test credentials"""
        # Set up test environment
        os.environ["USE_LOCAL_KEYS"] = "true"

        self.agent = EnhancedNocturnalAgent()
        success = await self.agent.initialize()

        if not success:
            raise RuntimeError("Failed to initialize agent for testing")

        return self

    async def ask(self, question: str) -> str:
        """Ask a question and return clean response"""
        request = ChatRequest(
            question=question,
            user_id="test_user",
            conversation_id=self.conversation_id
        )

        response = await self.agent.process_request(request)

        # Record conversation
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response.response
        })

        return response.response

    async def cleanup(self):
        """Clean up resources"""
        if self.agent:
            await self.agent.close()

    def print_conversation(self):
        """Print the full conversation for manual review"""
        print("\n" + "="*80)
        print("FULL CONVERSATION:")
        print("="*80)

        for i, msg in enumerate(self.conversation_history):
            role_label = "👤 User" if msg["role"] == "user" else "🤖 Agent"
            print(f"\n{role_label}:")
            print(msg["content"])
            print("-"*80)

        print("="*80 + "\n")

    # Quality checks
    def has_python_code_leak(self, text: str) -> bool:
        """Check if response contains leaked Python code"""
        patterns = [
            r'```python',  # Code blocks
            r'^import \w+',  # Import statements at start of line
            r'^from \w+ import',  # From imports
            r'def \w+\(',  # Function definitions
            r'= \[.*\]$',  # List assignments
            r'params\s*=\s*\{',  # params dict
        ]

        for pattern in patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False

    def has_ansi_codes(self, text: str) -> bool:
        """Check if response contains ANSI escape codes"""
        ansi_pattern = r'\x1b\[[0-9;]*m|\033\[[0-9;]*m|\[[0-9]+m'
        return bool(re.search(ansi_pattern, text))

    def has_json_artifacts(self, text: str) -> bool:
        """Check if response contains leaked JSON tool calls"""
        json_patterns = [
            r'\{.*"type".*:.*".*".*\}',  # {"type": "..."}
            r'\{.*"query".*:.*".*".*\}',  # {"query": "..."}
            r'\{.*"command".*:.*".*".*\}',  # {"command": "..."}
        ]

        for pattern in json_patterns:
            if re.search(pattern, text):
                return True
        return False

    def has_reasoning_leaks(self, text: str) -> bool:
        """Check if response contains internal reasoning phrases"""
        reasoning_phrases = [
            "we need to",
            "i need to",
            "will run:",
            "executing:",
            "let me try",
            "probably",
        ]

        text_lower = text.lower()
        return any(phrase in text_lower for phrase in reasoning_phrases)


# ==============================================================================
# CONVERSATION WORKFLOW TESTS
# ==============================================================================

async def test_paper_search_workflow():
    """
    Test full conversation: Search papers → Ask follow-up → Verify quality

    User story:
    - User searches for BERT papers
    - Agent provides clean list with DOIs
    - User asks follow-up about specific paper
    - Agent responds naturally
    """
    print("\n" + "="*80)
    print("TEST: Paper Search Workflow")
    print("="*80)

    tester = await ConversationTester().setup()

    try:
        # Turn 1: Initial search
        response1 = await tester.ask("Find papers on BERT from 2018")

        # Turn 2: Follow-up question
        response2 = await tester.ask("What was the most cited paper?")

        # Print full conversation
        tester.print_conversation()

        # Quality checks
        print("QUALITY CHECKS:")
        print("-"*80)

        # Check response 1
        has_code = tester.has_python_code_leak(response1)
        has_ansi = tester.has_ansi_codes(response1)
        has_json = tester.has_json_artifacts(response1)
        has_reasoning = tester.has_reasoning_leaks(response1)

        print(f"Response 1:")
        print(f"  ✓ No Python code leaks: {not has_code}")
        print(f"  ✓ No ANSI codes: {not has_ansi}")
        print(f"  ✓ No JSON artifacts: {not has_json}")
        print(f"  ✓ No reasoning leaks: {not has_reasoning}")

        # Check response 2
        has_code2 = tester.has_python_code_leak(response2)
        has_ansi2 = tester.has_ansi_codes(response2)

        print(f"\nResponse 2:")
        print(f"  ✓ No Python code leaks: {not has_code2}")
        print(f"  ✓ No ANSI codes: {not has_ansi2}")

        # Overall assessment
        all_clean = not any([has_code, has_ansi, has_json, has_reasoning, has_code2, has_ansi2])

        print(f"\n{'✅ PASS' if all_clean else '❌ FAIL'}: Paper search workflow")
        print("="*80)

        assert not has_code, "Response 1 contains Python code leaks"
        assert not has_ansi, "Response 1 contains ANSI codes"
        assert not has_json, "Response 1 contains JSON artifacts"
        assert not has_code2, "Response 2 contains Python code leaks"
        assert not has_ansi2, "Response 2 contains ANSI codes"

    finally:
        await tester.cleanup()


async def test_financial_comparison_workflow():
    """
    Test full conversation: Compare companies → Ask follow-up

    User story:
    - User asks to compare Apple and Microsoft
    - Agent provides revenue comparison
    - User asks which is more profitable
    - Agent provides profit margin comparison
    """
    print("\n" + "="*80)
    print("TEST: Financial Comparison Workflow")
    print("="*80)

    tester = await ConversationTester().setup()

    try:
        # Turn 1: Initial comparison
        response1 = await tester.ask("Compare Apple and Microsoft revenue")

        # Turn 2: Follow-up about profitability
        response2 = await tester.ask("Which is more profitable?")

        # Print full conversation
        tester.print_conversation()

        # Quality checks
        print("QUALITY CHECKS:")
        print("-"*80)

        has_ansi1 = tester.has_ansi_codes(response1)
        has_code1 = tester.has_python_code_leak(response1)
        has_ansi2 = tester.has_ansi_codes(response2)

        print(f"Response 1:")
        print(f"  ✓ No ANSI codes: {not has_ansi1}")
        print(f"  ✓ No Python code: {not has_code1}")

        print(f"\nResponse 2:")
        print(f"  ✓ No ANSI codes: {not has_ansi2}")

        all_clean = not any([has_ansi1, has_code1, has_ansi2])

        print(f"\n{'✅ PASS' if all_clean else '❌ FAIL'}: Financial comparison workflow")
        print("="*80)

        assert not has_ansi1, "Response 1 contains ANSI codes"
        assert not has_code1, "Response 1 contains Python code leaks"
        assert not has_ansi2, "Response 2 contains ANSI codes"

    finally:
        await tester.cleanup()


async def test_data_analysis_workflow():
    """
    Test full conversation: Load CSV → Analyze → Follow-up

    User story:
    - User loads a CSV file
    - Agent shows summary statistics
    - User asks for specific column analysis
    - Agent provides detailed analysis
    """
    print("\n" + "="*80)
    print("TEST: Data Analysis Workflow")
    print("="*80)

    # Create test CSV
    test_csv = Path("/tmp/test_scores.csv")
    test_csv.write_text("""Student,Math,English,Science
Alice,85,92,88
Bob,78,85,90
Charlie,92,88,85
David,88,90,92
Eve,95,93,97
""")

    tester = await ConversationTester().setup()

    try:
        # Turn 1: Load and describe data
        response1 = await tester.ask(f"Load {test_csv} and show me the summary")

        # Turn 2: Ask for specific column analysis
        response2 = await tester.ask("What's the average Math score?")

        # Turn 3: Compare columns
        response3 = await tester.ask("Which subject has the highest average?")

        # Print full conversation
        tester.print_conversation()

        # Quality checks
        print("QUALITY CHECKS:")
        print("-"*80)

        has_code1 = tester.has_python_code_leak(response1)
        has_code2 = tester.has_python_code_leak(response2)
        has_code3 = tester.has_python_code_leak(response3)

        print(f"Response 1 (load data):")
        print(f"  ✓ No Python code leaks: {not has_code1}")

        print(f"\nResponse 2 (average):")
        print(f"  ✓ No Python code leaks: {not has_code2}")

        print(f"\nResponse 3 (comparison):")
        print(f"  ✓ No Python code leaks: {not has_code3}")

        # Check if Math column was found (case-insensitive)
        found_math = "math" in response2.lower() or "87.6" in response2 or "87.60" in response2
        print(f"\nData accuracy:")
        print(f"  ✓ Found Math column: {found_math}")

        all_clean = not any([has_code1, has_code2, has_code3])

        print(f"\n{'✅ PASS' if all_clean and found_math else '❌ FAIL'}: Data analysis workflow")
        print("="*80)

        assert not has_code1, "Response 1 contains Python code leaks"
        assert not has_code2, "Response 2 contains Python code leaks"
        assert not has_code3, "Response 3 contains Python code leaks"
        assert found_math, "Failed to find Math column (case sensitivity issue)"

    finally:
        await tester.cleanup()
        # Cleanup test file
        if test_csv.exists():
            test_csv.unlink()


async def test_file_operations_workflow():
    """
    Test full conversation: List files → Count files → Read file

    User story:
    - User asks to list files
    - Agent shows reasonable number of files (not 400+)
    - User asks how many Python files
    - Agent gives accurate count
    """
    print("\n" + "="*80)
    print("TEST: File Operations Workflow")
    print("="*80)

    tester = await ConversationTester().setup()

    try:
        # Turn 1: List files
        response1 = await tester.ask("List files in cite_agent directory")

        # Turn 2: Count specific files
        response2 = await tester.ask("How many Python files are there?")

        # Print full conversation
        tester.print_conversation()

        # Quality checks
        print("QUALITY CHECKS:")
        print("-"*80)

        # Check if file listing is reasonable (not overwhelming)
        line_count = len(response1.split('\n'))
        is_reasonable = line_count < 100  # Should be much less than 400

        print(f"Response 1 (list files):")
        print(f"  ✓ Reasonable output length: {is_reasonable} ({line_count} lines)")
        print(f"  ✓ No reasoning leaks: {not tester.has_reasoning_leaks(response1)}")

        # Check file count accuracy
        has_number = bool(re.search(r'\d+', response2))
        print(f"\nResponse 2 (count files):")
        print(f"  ✓ Contains a number: {has_number}")
        print(f"  ✓ No code leaks: {not tester.has_python_code_leak(response2)}")

        all_clean = is_reasonable and has_number

        print(f"\n{'✅ PASS' if all_clean else '❌ FAIL'}: File operations workflow")
        print("="*80)

        assert is_reasonable, f"File listing too long: {line_count} lines (should be < 100)"
        assert has_number, "File count response doesn't contain a number"

    finally:
        await tester.cleanup()


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

async def run_all_tests():
    """Run all conversation workflow tests"""
    print("\n" + "="*80)
    print("CITE-AGENT CONVERSATION QUALITY TESTS")
    print("Testing full workflows to ensure natural conversations")
    print("="*80)

    tests = [
        ("Paper Search", test_paper_search_workflow),
        ("Financial Comparison", test_financial_comparison_workflow),
        ("Data Analysis", test_data_analysis_workflow),
        ("File Operations", test_file_operations_workflow),
    ]

    results = []

    for name, test_func in tests:
        try:
            await test_func()
            results.append((name, "PASS", None))
        except AssertionError as e:
            results.append((name, "FAIL", str(e)))
        except Exception as e:
            results.append((name, "ERROR", str(e)))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for name, status, error in results:
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {name}: {status}")
        if error:
            print(f"   Error: {error}")

    passed = sum(1 for _, status, _ in results if status == "PASS")
    total = len(results)

    print(f"\nPassed: {passed}/{total}")
    print("="*80)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
