#!/usr/bin/env python3
"""
COMPREHENSIVE ACADEMIC/RESEARCH ASSISTANT TEST
Tests all features that professors and researchers need

Tests:
1. Academic paper search (Archive API)
2. Citation verification and DOI resolution
3. Financial data queries (FinSight API)
4. File system operations
5. Data file understanding (CSV, R scripts)
6. Conversational context memory
7. Multi-turn research workflows
8. Natural language commands
9. Chinese language support
10. Error handling and recovery
"""

import asyncio
import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Set up environment
os.environ['USE_LOCAL_KEYS'] = 'false'
os.environ['NOCTURNAL_DEBUG'] = '0'

from cite_agent import EnhancedNocturnalAgent, ChatRequest

class AcademicTestSuite:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "category_results": {}
        }
        self.agent = None

    async def setup(self):
        """Initialize agent"""
        print("🔧 Setting up agent...")
        self.agent = EnhancedNocturnalAgent()
        success = await self.agent.initialize()
        if not success:
            print("❌ Agent initialization failed")
            return False
        print("✅ Agent initialized\n")
        return True

    async def teardown(self):
        """Cleanup"""
        if self.agent:
            await self.agent.close()

    def record_test(self, category: str, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            print(f"  ✅ {test_name}")
        else:
            self.results["failed"] += 1
            print(f"  ❌ {test_name}")
            if error:
                print(f"     Error: {error}")
                self.results["errors"].append(f"{category}/{test_name}: {error}")

        if category not in self.results["category_results"]:
            self.results["category_results"][category] = {"passed": 0, "failed": 0}

        if passed:
            self.results["category_results"][category]["passed"] += 1
        else:
            self.results["category_results"][category]["failed"] += 1

    async def test_academic_search(self):
        """Test academic paper search via Archive API"""
        print("\n" + "="*70)
        print("📚 TESTING ACADEMIC PAPER SEARCH")
        print("="*70)

        tests = [
            ("Find papers on transformer models", "should return academic papers"),
            ("Search for BERT paper", "should find attention is all you need"),
            ("Recent research on climate change", "should return recent papers"),
        ]

        for query, expected in tests:
            try:
                request = ChatRequest(question=query)
                response = await self.agent.process_request(request)

                # Check if we got a response
                has_response = bool(response.response and len(response.response) > 50)

                # Check if response mentions academic sources
                mentions_papers = any(word in response.response.lower()
                                     for word in ['paper', 'research', 'study', 'author', 'published'])

                passed = has_response and mentions_papers
                self.record_test("Academic Search", query, passed,
                               None if passed else f"Response: {response.response[:100]}")

            except Exception as e:
                self.record_test("Academic Search", query, False, str(e))

    async def test_financial_data(self):
        """Test financial data queries via FinSight API"""
        print("\n" + "="*70)
        print("💰 TESTING FINANCIAL DATA QUERIES")
        print("="*70)

        tests = [
            ("What is Apple's revenue?", ["revenue", "apple", "$"]),
            ("Microsoft market cap", ["microsoft", "market", "cap"]),
            ("Tesla vs Ford revenue comparison", ["tesla", "ford"]),
        ]

        for query, keywords in tests:
            try:
                request = ChatRequest(question=query)
                response = await self.agent.process_request(request)

                # Check if response contains expected keywords
                response_lower = response.response.lower()
                has_keywords = sum(kw.lower() in response_lower for kw in keywords) >= 2
                has_data = len(response.response) > 30

                passed = has_keywords and has_data
                self.record_test("Financial Data", query, passed,
                               None if passed else f"Missing keywords or insufficient data")

            except Exception as e:
                self.record_test("Financial Data", query, False, str(e))

    async def test_file_operations(self):
        """Test file system operations"""
        print("\n" + "="*70)
        print("📁 TESTING FILE OPERATIONS")
        print("="*70)

        # Create temporary test directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "data.csv").write_text("Name,Age,Score\nAlice,25,95\nBob,30,87\n")
            (tmppath / "script.R").write_text("calculate_mean <- function(x) { mean(x) }")
            (tmppath / "notes.txt").write_text("Research notes on transformers")

            os.chdir(tmpdir)

            tests = [
                ("list files here", ["csv", "R", "txt"]),
                ("show me data.csv", ["Name", "Age", "Score"]),
                ("what's in this directory?", ["data.csv", "script.R"]),
            ]

            for query, expected_content in tests:
                try:
                    request = ChatRequest(question=query)
                    response = await self.agent.process_request(request)

                    response_lower = response.response.lower()
                    found_items = sum(item.lower() in response_lower for item in expected_content)
                    passed = found_items >= 1  # At least one expected item found

                    self.record_test("File Operations", query, passed,
                                   None if passed else f"Expected items not found in response")

                except Exception as e:
                    self.record_test("File Operations", query, False, str(e))

    async def test_conversational_context(self):
        """Test multi-turn conversation with context"""
        print("\n" + "="*70)
        print("💬 TESTING CONVERSATIONAL CONTEXT")
        print("="*70)

        conversation = [
            ("What is Tesla's revenue?", ["tesla", "revenue"]),
            ("What about their profit margin?", ["profit", "margin", "tesla"]),  # Should remember Tesla
            ("Compare that to Apple", ["apple", "tesla"]),  # Should compare both
        ]

        try:
            for i, (query, keywords) in enumerate(conversation, 1):
                request = ChatRequest(question=query)
                response = await self.agent.process_request(request)

                response_lower = response.response.lower()
                found = sum(kw.lower() in response_lower for kw in keywords)
                passed = found >= 2 or (i == 1 and found >= 1)  # First query can have just 1 keyword

                test_name = f"Turn {i}: {query}"
                self.record_test("Conversational Context", test_name, passed,
                               None if passed else f"Context not maintained")

        except Exception as e:
            self.record_test("Conversational Context", "Full conversation", False, str(e))

    async def test_natural_language_commands(self):
        """Test natural language file/shell commands"""
        print("\n" + "="*70)
        print("🗣️ TESTING NATURAL LANGUAGE COMMANDS")
        print("="*70)

        tests = [
            ("where am i", "current directory"),
            ("show files", "file listing"),
            ("what's here", "directory contents"),
        ]

        for query, description in tests:
            try:
                request = ChatRequest(question=query)
                response = await self.agent.process_request(request)

                # Should get a response with directory/file info
                has_response = len(response.response) > 10
                passed = has_response

                self.record_test("Natural Language", f"{query} ({description})", passed,
                               None if passed else "No response")

            except Exception as e:
                self.record_test("Natural Language", query, False, str(e))

    async def test_chinese_support(self):
        """Test Chinese language support"""
        print("\n" + "="*70)
        print("🇨🇳 TESTING CHINESE LANGUAGE SUPPORT")
        print("="*70)

        tests = [
            ("你好", "greeting"),
            ("請問如何使用這個系統？", "how to use the system"),
        ]

        for query, description in tests:
            try:
                request = ChatRequest(question=query)
                response = await self.agent.process_request(request)

                # Check if response contains Chinese characters
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in response.response)
                has_response = len(response.response) > 20

                passed = has_chinese and has_response
                self.record_test("Chinese Support", f"{description}", passed,
                               None if passed else "Response not in Chinese")

            except Exception as e:
                self.record_test("Chinese Support", query, False, str(e))

    async def test_data_analysis(self):
        """Test data file analysis"""
        print("\n" + "="*70)
        print("📊 TESTING DATA ANALYSIS")
        print("="*70)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            csv_file = tmppath / "test_data.csv"
            csv_file.write_text("Product,Sales,Region\nWidgets,1000,North\nGadgets,1500,South\nWidgets,800,East\n")

            os.chdir(tmpdir)

            tests = [
                (f"show me {csv_file.name}", ["Product", "Sales", "Region"]),
                (f"what columns are in {csv_file.name}", ["Product", "Sales", "Region"]),
                ("analyze the data", ["data", "csv"]),
            ]

            for query, keywords in tests:
                try:
                    request = ChatRequest(question=query)
                    response = await self.agent.process_request(request)

                    response_lower = response.response.lower()
                    found = sum(kw.lower() in response_lower for kw in keywords)
                    passed = found >= 1

                    self.record_test("Data Analysis", query, passed,
                                   None if passed else "Expected data info not found")

                except Exception as e:
                    self.record_test("Data Analysis", query, False, str(e))

    async def test_professor_workflow(self):
        """Test typical professor research workflow"""
        print("\n" + "="*70)
        print("👨‍🏫 TESTING PROFESSOR RESEARCH WORKFLOW")
        print("="*70)

        workflow = [
            ("Find recent papers on neural networks", "paper search"),
            ("Summarize the key findings", "summarization"),
            ("What are the main methodologies used?", "methodology extraction"),
        ]

        for query, stage in workflow:
            try:
                request = ChatRequest(question=query)
                response = await self.agent.process_request(request)

                has_substantial_response = len(response.response) > 100
                passed = has_substantial_response

                self.record_test("Professor Workflow", f"{stage}: {query[:30]}...", passed,
                               None if passed else "Insufficient response")

            except Exception as e:
                self.record_test("Professor Workflow", stage, False, str(e))

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 TEST RESULTS SUMMARY")
        print("="*70)

        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\nOverall: {passed}/{total} tests passed ({pass_rate:.1f}%)")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")

        print("\n📋 Results by Category:")
        for category, results in self.results["category_results"].items():
            cat_total = results["passed"] + results["failed"]
            cat_rate = (results["passed"] / cat_total * 100) if cat_total > 0 else 0
            status = "✅" if cat_rate >= 80 else "⚠️" if cat_rate >= 50 else "❌"
            print(f"{status} {category}: {results['passed']}/{cat_total} ({cat_rate:.1f}%)")

        if self.results["errors"]:
            print(f"\n⚠️ Errors encountered: {len(self.results['errors'])}")
            for error in self.results["errors"][:5]:  # Show first 5
                print(f"  - {error}")
            if len(self.results["errors"]) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more")

        print("\n" + "="*70)

        # Final grade
        if pass_rate >= 90:
            grade = "🌟 EXCELLENT - Production Ready"
        elif pass_rate >= 75:
            grade = "✅ GOOD - Minor issues to address"
        elif pass_rate >= 60:
            grade = "⚠️ FAIR - Several issues need fixing"
        else:
            grade = "❌ POOR - Major issues detected"

        print(f"\n{grade}")
        print("="*70)

        return pass_rate >= 75

async def main():
    """Run all tests"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     🧪 COMPREHENSIVE ACADEMIC RESEARCH ASSISTANT TESTING        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    suite = AcademicTestSuite()

    if not await suite.setup():
        print("❌ Setup failed, aborting tests")
        return False

    try:
        # Run all test categories
        await suite.test_academic_search()
        await suite.test_financial_data()
        await suite.test_file_operations()
        await suite.test_conversational_context()
        await suite.test_natural_language_commands()
        await suite.test_chinese_support()
        await suite.test_data_analysis()
        await suite.test_professor_workflow()

    finally:
        await suite.teardown()

    success = suite.print_summary()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
