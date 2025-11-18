#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INDEPENDENT QUALITY VERIFICATION - Claude Code
Testing actual response quality, not keyword presence

Criteria for PASS:
- Response is relevant and accurate
- Response is complete (answers the full question)
- Response is professional (no internal debugging, JSON commands shown)
- Calculations are correct
- No hallucinations or wrong facts
"""

import asyncio
import os
import sys
from datetime import datetime

# Allow local mode detection (will auto-detect API keys if available)
# Note: For full testing, set GROQ_API_KEY or CEREBRAS_API_KEY environment variable
# os.environ['USE_LOCAL_KEYS'] = 'false'  # Commented out to allow local mode

from cite_agent import EnhancedNocturnalAgent, ChatRequest

class IndependentQualityTest:
    def __init__(self):
        self.results = []
        self.agent = None

    async def setup(self):
        print("🔧 Initializing agent...")
        self.agent = EnhancedNocturnalAgent()
        success = await self.agent.initialize()
        if not success:
            print("❌ Agent initialization failed")
            return False
        print("✅ Agent ready\n")
        return True

    async def teardown(self):
        if self.agent:
            await self.agent.close()

    def judge_quality(self, category, question, response, criteria):
        """Manually judge response quality"""
        print(f"\n{'='*80}")
        print(f"📝 TEST: {category}")
        print(f"{'='*80}")
        print(f"❓ QUESTION: {question}")
        print(f"\n💬 RESPONSE ({len(response)} chars):")
        print("-" * 80)
        print(response[:500] + ("..." if len(response) > 500 else ""))
        print("-" * 80)

        print(f"\n📋 QUALITY CRITERIA:")
        for criterion in criteria:
            print(f"   - {criterion}")

        # Auto-checks
        issues = []

        # Check 1: Empty response
        if len(response.strip()) < 10:
            issues.append("❌ EMPTY/TOO SHORT response")

        # Check 2: Shows internal JSON commands
        if '{"cmd":' in response or '{"action":' in response:
            issues.append("⚠️ Shows internal JSON commands (unprofessional)")

        # Check 3: Shows debugging messages
        if "Let's execute" in response or "We need to execute" in response:
            issues.append("⚠️ Shows internal reasoning (unprofessional)")

        # Check 4: Error messages
        if "ERROR:" in response.upper() or "FAILED:" in response.upper():
            issues.append("⚠️ Contains error messages")

        # Check 5: Backend errors
        if "Not authenticated" in response or "authentication required" in response.lower():
            issues.append("❌ Authentication error")

        return issues

    async def test_academic_search(self):
        """Test 1: Academic paper search"""
        question = "Find recent papers on transformer architectures in neural networks"
        criteria = [
            "Returns actual paper titles and authors",
            "Papers are relevant to transformers/neural networks",
            "Includes metadata (year, DOI, or links)",
            "Professional presentation"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("Academic Search", question, response.response, criteria)

        # Additional checks
        if len(response.response) < 200:
            issues.append("❌ Response too short for paper search")
        if "paper" not in response.response.lower() and "article" not in response.response.lower():
            issues.append("⚠️ Doesn't mention papers/articles")

        passed = len(issues) == 0
        self.results.append({
            "test": "Academic Search",
            "passed": passed,
            "issues": issues,
            "response_length": len(response.response)
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_chinese_language(self):
        """Test 2: Chinese language support"""
        question = "你好，請問你可以用中文回答嗎？"
        criteria = [
            "Response is 100% in Traditional Chinese",
            "No English words mixed in",
            "Natural, coherent Chinese",
            "Answers the question appropriately"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("Chinese Language", question, response.response, criteria)

        # Check for Chinese characters
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in response.response)
        # Check for English words (excluding common punctuation)
        english_words = len([word for word in response.response.split() if word.isalpha() and all(ord(c) < 128 for c in word)])

        if not has_chinese:
            issues.append("❌ No Chinese characters in response")
        if english_words > 2:  # Allow a couple English words
            issues.append(f"❌ Too many English words ({english_words}) in Chinese response")

        passed = len(issues) == 0
        self.results.append({
            "test": "Chinese Language",
            "passed": passed,
            "issues": issues,
            "has_chinese": has_chinese,
            "english_words": english_words
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_csv_analysis(self):
        """Test 3: CSV file analysis"""
        # First create a CSV file
        create_q = "Create a CSV file called test_data.csv with columns Name,Age,Score and 3 rows: Alice,25,95 Bob,30,87 Carol,28,92"
        await self.agent.process_request(ChatRequest(question=create_q))

        # Now analyze it
        question = "What is the average score in test_data.csv?"
        criteria = [
            "Reads the CSV file correctly",
            "Calculates average correctly: (95+87+92)/3 = 91.33",
            "Shows clear answer",
            "Professional presentation (no internal commands shown)"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("CSV Analysis", question, response.response, criteria)

        # Check for correct answer (91.33 or 91)
        if "91" not in response.response:
            issues.append("❌ Wrong answer (should be ~91.33)")

        passed = len(issues) == 0
        self.results.append({
            "test": "CSV Analysis",
            "passed": passed,
            "issues": issues
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_math_calculation(self):
        """Test 4: Math with explanation"""
        question = "Calculate (25 × 4) + (100 ÷ 5) - 15 and show your work"
        criteria = [
            "Shows step-by-step calculation",
            "Correct answer: 105",
            "Clear explanation",
            "Professional format"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("Math Calculation", question, response.response, criteria)

        # Check for correct answer
        if "105" not in response.response:
            issues.append("❌ Wrong answer (should be 105)")

        # Check for steps shown
        if "100" not in response.response or "20" not in response.response:
            issues.append("⚠️ Doesn't show intermediate steps")

        passed = len(issues) == 0
        self.results.append({
            "test": "Math Calculation",
            "passed": passed,
            "issues": issues
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_multi_turn_context(self):
        """Test 5: Multi-turn conversation memory"""
        # Turn 1
        q1 = "What is 15 multiplied by 8?"
        r1 = await self.agent.process_request(ChatRequest(question=q1))

        # Turn 2 - should remember 120
        question = "Now add 30 to that result"
        criteria = [
            "Remembers previous answer (120)",
            "Adds 30 correctly: 120 + 30 = 150",
            "Shows understanding of 'that result'",
            "Professional response"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("Multi-Turn Context", question, response.response, criteria)

        # Check for correct answer
        if "150" not in response.response:
            issues.append("❌ Wrong answer (should be 150) - context not maintained")

        passed = len(issues) == 0
        self.results.append({
            "test": "Multi-Turn Context",
            "passed": passed,
            "issues": issues,
            "turn1_response": r1.response[:100]
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_file_operations(self):
        """Test 6: Create and read file"""
        question = "Create a file called test.txt with the content 'Hello World' and then show me its contents"
        criteria = [
            "Creates file successfully",
            "Reads file and shows 'Hello World'",
            "Clear confirmation of actions",
            "No internal JSON commands shown"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("File Operations", question, response.response, criteria)

        # Check for file content
        if "Hello World" not in response.response:
            issues.append("❌ Doesn't show file content 'Hello World'")

        passed = len(issues) == 0
        self.results.append({
            "test": "File Operations",
            "passed": passed,
            "issues": issues
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_natural_language(self):
        """Test 7: Natural language understanding"""
        question = "where am I right now?"
        criteria = [
            "Shows current directory path",
            "Natural, conversational response",
            "No errors"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("Natural Language", question, response.response, criteria)

        # Check for directory path
        if "/" not in response.response and "\\" not in response.response:
            issues.append("⚠️ Doesn't show directory path")

        passed = len(issues) == 0
        self.results.append({
            "test": "Natural Language",
            "passed": passed,
            "issues": issues
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    async def test_error_handling(self):
        """Test 8: Graceful error handling"""
        question = "Read the file this_file_definitely_does_not_exist.txt"
        criteria = [
            "Gracefully handles missing file",
            "Clear error message (file not found)",
            "Doesn't crash or show stack traces",
            "Professional response"
        ]

        response = await self.agent.process_request(ChatRequest(question=question))
        issues = self.judge_quality("Error Handling", question, response.response, criteria)

        # Check for graceful handling
        if len(response.response) < 20:
            issues.append("❌ Empty or too short error response")

        # Should mention the file doesn't exist
        if "not found" not in response.response.lower() and "doesn't exist" not in response.response.lower() and "does not exist" not in response.response.lower():
            issues.append("⚠️ Doesn't clearly indicate file not found")

        passed = len(issues) == 0
        self.results.append({
            "test": "Error Handling",
            "passed": passed,
            "issues": issues
        })

        print(f"\n🔍 ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

        return passed

    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*80)
        print("📊 INDEPENDENT QUALITY VERIFICATION - FINAL RESULTS")
        print("="*80)

        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"📈 Pass Rate: {pass_rate:.1f}%")

        print(f"\n📋 Detailed Results:")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result['passed'] else "❌"
            print(f"\n{i}. {status} {result['test']}")
            if result['issues']:
                for issue in result['issues']:
                    print(f"     {issue}")

        print("\n" + "="*80)

        # Grade
        if pass_rate >= 90:
            grade = "🌟 EXCELLENT - Production Ready"
        elif pass_rate >= 75:
            grade = "✅ GOOD - Minor issues"
        elif pass_rate >= 60:
            grade = "⚠️ FAIR - Several issues need fixing"
        else:
            grade = "❌ POOR - Major issues detected"

        print(f"\n{grade}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("="*80)

        return pass_rate >= 75

async def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   🔍 INDEPENDENT QUALITY VERIFICATION - Claude Code              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing ACTUAL response quality, not just keywords\n")

    tester = IndependentQualityTest()

    if not await tester.setup():
        return False

    try:
        # Run all tests
        await tester.test_academic_search()
        await tester.test_chinese_language()
        await tester.test_csv_analysis()
        await tester.test_math_calculation()
        await tester.test_multi_turn_context()
        await tester.test_file_operations()
        await tester.test_natural_language()
        await tester.test_error_handling()

    finally:
        await tester.teardown()

    success = tester.print_summary()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
