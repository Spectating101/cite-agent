"""
Stress Testing for Agent Robustness

Tests the agent under various stress conditions to ensure stability.
"""

import asyncio
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


class StressTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.timings = []

    def check(self, test_name: str, condition: bool, details: str = ""):
        if condition:
            print(f"✅ {test_name}")
            self.passed += 1
            self.results.append((test_name, True, details))
        else:
            print(f"❌ {test_name}: {details}")
            self.failed += 1
            self.results.append((test_name, False, details))

    def record_timing(self, test_name: str, duration: float):
        self.timings.append((test_name, duration))

    def summary(self):
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"STRESS TEST RESULTS")
        print(f"{'='*60}")
        print(f"Passed: {self.passed}/{total}")
        print(f"Failed: {self.failed}/{total}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"\n{'='*60}")
        print(f"TIMING ANALYSIS")
        print(f"{'='*60}")
        if self.timings:
            avg_time = sum(t[1] for t in self.timings) / len(self.timings)
            max_time = max(self.timings, key=lambda x: x[1])
            min_time = min(self.timings, key=lambda x: x[1])
            print(f"Average response time: {avg_time:.2f}s")
            print(f"Fastest: {min_time[0]} ({min_time[1]:.2f}s)")
            print(f"Slowest: {max_time[0]} ({max_time[1]:.2f}s)")
        print(f"{'='*60}\n")


async def test_stress():
    """Run stress tests on the agent"""

    tester = StressTester()
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("Starting Stress Testing...\n")

    # =========================================================================
    # Test 1: Rapid sequential requests (no delay)
    # =========================================================================
    print("Test 1: Rapid sequential requests (10 queries)")
    try:
        start_time = time.time()
        success_count = 0

        for i in range(10):
            result = await agent.process_request(ChatRequest(
                question=f"What is {i} + 1?",
                conversation_id="rapid_test"
            ))
            if len(result.response) > 0:
                success_count += 1

        duration = time.time() - start_time
        tester.record_timing("Rapid sequential (10 queries)", duration)

        tester.check(
            "Rapid sequential requests",
            success_count == 10,
            f"Completed {success_count}/10 in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Rapid sequential requests", False, f"Exception: {e}")

    # =========================================================================
    # Test 2: Long conversation context (memory test)
    # =========================================================================
    print("\nTest 2: Long conversation (20 exchanges)")
    try:
        start_time = time.time()
        success_count = 0
        conversation_id = "long_conv_test"

        for i in range(20):
            if i == 0:
                question = "List files in current directory"
            elif i % 2 == 0:
                question = f"What about the {i}th file?"
            else:
                question = "Tell me more"

            result = await agent.process_request(ChatRequest(
                question=question,
                conversation_id=conversation_id
            ))
            if len(result.response) > 0:
                success_count += 1

        duration = time.time() - start_time
        tester.record_timing("Long conversation (20 exchanges)", duration)

        tester.check(
            "Long conversation context",
            success_count >= 18,  # Allow 2 failures
            f"Completed {success_count}/20 in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Long conversation context", False, f"Exception: {e}")

    # =========================================================================
    # Test 3: Complex nested queries
    # =========================================================================
    print("\nTest 3: Complex nested queries")
    try:
        complex_queries = [
            "Find all Python files and show me the ones that contain authentication logic",
            "Compare the authentication implementations in file1.py and file2.py and tell me which is more secure",
            "Search for configuration files, read them, and explain what database connection settings are used",
        ]

        start_time = time.time()
        success_count = 0

        for query in complex_queries:
            result = await agent.process_request(ChatRequest(question=query))
            if len(result.response) > 50:  # Expect substantial response
                success_count += 1

        duration = time.time() - start_time
        tester.record_timing("Complex nested queries", duration)

        tester.check(
            "Complex nested queries",
            success_count >= 2,  # Allow 1 failure
            f"Completed {success_count}/{len(complex_queries)} in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Complex nested queries", False, f"Exception: {e}")

    # =========================================================================
    # Test 4: Mixed valid/invalid requests
    # =========================================================================
    print("\nTest 4: Mixed valid/invalid requests")
    try:
        mixed_queries = [
            ("List files", True),  # Valid
            ("Read nonexistent_xyz_123.txt", False),  # Invalid
            ("Show me README.md", True),  # Valid
            ("Compare fake1.txt and fake2.txt", False),  # Invalid
            ("What files are here?", True),  # Valid
        ]

        start_time = time.time()
        handled_correctly = 0

        for query, should_succeed in mixed_queries:
            result = await agent.process_request(ChatRequest(question=query))

            # Check if error handling is appropriate
            has_error_msg = any(phrase in result.response.lower() for phrase in [
                "not found", "couldn't find", "doesn't exist", "error"
            ])

            if should_succeed:
                # Valid query should have substantial response without error
                if len(result.response) > 20 and not has_error_msg:
                    handled_correctly += 1
            else:
                # Invalid query should have error message
                if has_error_msg:
                    handled_correctly += 1

        duration = time.time() - start_time
        tester.record_timing("Mixed valid/invalid", duration)

        tester.check(
            "Mixed valid/invalid requests",
            handled_correctly >= 4,  # Allow 1 mistake
            f"Handled {handled_correctly}/{len(mixed_queries)} correctly in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Mixed valid/invalid requests", False, f"Exception: {e}")

    # =========================================================================
    # Test 5: Repeated identical queries (caching test)
    # =========================================================================
    print("\nTest 5: Repeated identical queries")
    try:
        start_time = time.time()
        responses = []

        for i in range(5):
            result = await agent.process_request(ChatRequest(
                question="List files in current directory",
                conversation_id="repeat_test"
            ))
            responses.append(result.response)

        duration = time.time() - start_time
        tester.record_timing("Repeated queries (5x)", duration)

        # All responses should be generated (not cached, but should work)
        all_successful = all(len(r) > 0 for r in responses)

        tester.check(
            "Repeated identical queries",
            all_successful,
            f"All 5 queries returned responses in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Repeated identical queries", False, f"Exception: {e}")

    # =========================================================================
    # Test 6: Memory pressure (large responses)
    # =========================================================================
    print("\nTest 6: Memory pressure (large file reads)")
    try:
        start_time = time.time()
        success_count = 0

        # Try to read large files
        large_file_queries = [
            "Show me enhanced_ai_agent.py",
            "Show me README.md",
            "List all files recursively",
        ]

        for query in large_file_queries:
            result = await agent.process_request(ChatRequest(question=query))
            if len(result.response) > 0:
                success_count += 1

        duration = time.time() - start_time
        tester.record_timing("Large file reads", duration)

        tester.check(
            "Memory pressure test",
            success_count >= 2,  # Allow 1 failure
            f"Completed {success_count}/{len(large_file_queries)} in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Memory pressure test", False, f"Exception: {e}")

    # =========================================================================
    # Test 7: Error recovery sequence
    # =========================================================================
    print("\nTest 7: Error recovery sequence")
    try:
        start_time = time.time()
        errors_then_success = []

        # Generate several errors
        for i in range(3):
            result = await agent.process_request(ChatRequest(
                question=f"Read nonexistent_file_{i}.txt",
                conversation_id="error_recovery"
            ))
            has_error = "not found" in result.response.lower() or "couldn't find" in result.response.lower()
            errors_then_success.append(has_error)

        # Then a valid query to see if agent recovers
        result = await agent.process_request(ChatRequest(
            question="List files",
            conversation_id="error_recovery"
        ))
        recovered = len(result.response) > 20 and "not found" not in result.response.lower()
        errors_then_success.append(recovered)

        duration = time.time() - start_time
        tester.record_timing("Error recovery sequence", duration)

        tester.check(
            "Error recovery after failures",
            all(errors_then_success),
            f"Handled errors gracefully and recovered in {duration:.2f}s"
        )
    except Exception as e:
        tester.check("Error recovery sequence", False, f"Exception: {e}")

    await agent.session.close()

    # Print summary
    tester.summary()

    return tester.passed, tester.failed


if __name__ == "__main__":
    print("="*60)
    print("AGENT STRESS TESTING")
    print("="*60)
    print("\nThis test suite verifies the agent handles stress conditions.")
    print("Testing rapid requests, long conversations, complex queries...\n")

    passed, failed = asyncio.run(test_stress())

    total = passed + failed
    if total > 0:
        pass_rate = passed / total * 100
        if pass_rate >= 85:
            print("✅ ROBUST - Agent handles stress well")
        elif pass_rate >= 70:
            print("⚠️  ACCEPTABLE - Some stress issues")
        else:
            print("❌ FRAGILE - Significant stress problems")

    sys.exit(0 if failed == 0 else 1)
