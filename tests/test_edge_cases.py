"""
Edge Case Testing for Agent Robustness

Tests various edge cases and error scenarios to ensure the agent handles them gracefully.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


class EdgeCaseTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def check(self, test_name: str, condition: bool, details: str = ""):
        if condition:
            print(f"✅ {test_name}")
            self.passed += 1
            self.results.append((test_name, True, details))
        else:
            print(f"❌ {test_name}: {details}")
            self.failed += 1
            self.results.append((test_name, False, details))

    def summary(self):
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"EDGE CASE TEST RESULTS")
        print(f"{'='*60}")
        print(f"Passed: {self.passed}/{total}")
        print(f"Failed: {self.failed}/{total}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"{'='*60}\n")


async def test_edge_cases():
    """Test various edge cases for agent robustness"""

    tester = EdgeCaseTester()
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("Starting Edge Case Testing...\n")

    # =========================================================================
    # Test 1: Nonexistent file (single file)
    # =========================================================================
    print("Test 1: Nonexistent file")
    try:
        result = await agent.process_request(ChatRequest(
            question="Read nonexistent_edge_case_file_12345.txt"
        ))

        # Check for friendly error message
        response_lower = result.response.lower()
        has_friendly_msg = any(phrase in response_lower for phrase in [
            "couldn't find", "not found", "doesn't exist", "unable to locate"
        ])
        no_technical_jargon = "error:" not in response_lower and "exception" not in response_lower

        tester.check(
            "Nonexistent file - friendly message",
            has_friendly_msg,
            f"Response: {result.response[:100]}"
        )
        tester.check(
            "Nonexistent file - no technical jargon",
            no_technical_jargon,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Nonexistent file", False, f"Exception: {e}")

    # =========================================================================
    # Test 2: Compare files where one doesn't exist
    # =========================================================================
    print("\nTest 2: Compare files with one missing")
    try:
        result = await agent.process_request(ChatRequest(
            question="Compare README.md and nonexistent_file_xyz.md"
        ))

        response_lower = result.response.lower()
        mentions_missing = any(phrase in response_lower for phrase in [
            "not found", "doesn't exist", "couldn't find", "missing"
        ])

        tester.check(
            "Missing file in comparison - error detected",
            mentions_missing or "error" in response_lower,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Compare with missing file", False, f"Exception: {e}")

    # =========================================================================
    # Test 3: Empty/whitespace query
    # =========================================================================
    print("\nTest 3: Empty or whitespace query")
    try:
        result = await agent.process_request(ChatRequest(
            question="   "
        ))

        # Should handle gracefully, not crash
        tester.check(
            "Whitespace query - handles gracefully",
            len(result.response) > 0,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Whitespace query", False, f"Exception: {e}")

    # =========================================================================
    # Test 4: Very long query (stress test)
    # =========================================================================
    print("\nTest 4: Very long query")
    try:
        long_query = "Find information about " + " and ".join([f"topic{i}" for i in range(100)])
        result = await agent.process_request(ChatRequest(
            question=long_query
        ))

        # Should handle without crashing
        tester.check(
            "Long query - handles without crash",
            len(result.response) > 0,
            f"Query length: {len(long_query)}"
        )
    except Exception as e:
        tester.check("Long query", False, f"Exception: {e}")

    # =========================================================================
    # Test 5: Special characters in filename
    # =========================================================================
    print("\nTest 5: Special characters in query")
    try:
        result = await agent.process_request(ChatRequest(
            question="Read file named 'weird@#$file.txt'"
        ))

        # Should handle gracefully, not crash
        tester.check(
            "Special characters - handles gracefully",
            len(result.response) > 0,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Special characters", False, f"Exception: {e}")

    # =========================================================================
    # Test 6: Ambiguous conceptual search
    # =========================================================================
    print("\nTest 6: Ambiguous conceptual search")
    try:
        result = await agent.process_request(ChatRequest(
            question="How does the authentication work?"
        ))

        # Should either:
        # 1. Execute grep search (tools_used contains shell_execution or grep_search)
        # 2. Provide helpful response asking for clarification
        attempted_search = any(tool in result.tools_used for tool in [
            "shell_execution", "grep_search"
        ])
        helpful_response = len(result.response) > 50

        tester.check(
            "Conceptual search - attempts grep or provides help",
            attempted_search or helpful_response,
            f"Tools: {result.tools_used}, Response length: {len(result.response)}"
        )
    except Exception as e:
        tester.check("Conceptual search", False, f"Exception: {e}")

    # =========================================================================
    # Test 7: Rapid-fire queries (context retention)
    # =========================================================================
    print("\nTest 7: Rapid-fire queries (context retention)")
    try:
        # First query
        result1 = await agent.process_request(ChatRequest(
            question="What files are in the current directory?",
            conversation_id="test_conversation"
        ))

        # Second query referring to first
        result2 = await agent.process_request(ChatRequest(
            question="Show me the first one",
            conversation_id="test_conversation"
        ))

        # Should maintain context
        tester.check(
            "Context retention - handles follow-up query",
            len(result2.response) > 0,
            f"Response: {result2.response[:100]}"
        )
    except Exception as e:
        tester.check("Context retention", False, f"Exception: {e}")

    # =========================================================================
    # Test 8: Permission denied scenario (simulate)
    # =========================================================================
    print("\nTest 8: Permission denied file")
    try:
        result = await agent.process_request(ChatRequest(
            question="Read /etc/shadow"
        ))

        response_lower = result.response.lower()
        # Should either refuse or handle gracefully
        handled_gracefully = any(phrase in response_lower for phrase in [
            "permission", "access", "not allowed", "restricted", "forbidden"
        ]) or "error" in response_lower

        tester.check(
            "Permission denied - handles gracefully",
            handled_gracefully,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Permission denied", False, f"Exception: {e}")

    # =========================================================================
    # Test 9: Directory instead of file
    # =========================================================================
    print("\nTest 9: Reading a directory (not a file)")
    try:
        result = await agent.process_request(ChatRequest(
            question="Read the cite_agent directory"
        ))

        response_lower = result.response.lower()
        # Should handle gracefully - either list contents or explain it's a directory
        handled_gracefully = any(phrase in response_lower for phrase in [
            "directory", "folder", "list", "contents"
        ]) or len(result.response) > 20

        tester.check(
            "Directory instead of file - handles gracefully",
            handled_gracefully,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Directory read", False, f"Exception: {e}")

    # =========================================================================
    # Test 10: Unicode and international characters
    # =========================================================================
    print("\nTest 10: Unicode and international characters")
    try:
        result = await agent.process_request(ChatRequest(
            question="Find files with names like café or naïve or 日本語"
        ))

        # Should handle without crashing
        tester.check(
            "Unicode characters - handles without crash",
            len(result.response) > 0,
            f"Response: {result.response[:100]}"
        )
    except Exception as e:
        tester.check("Unicode characters", False, f"Exception: {e}")

    await agent.session.close()

    # Print summary
    tester.summary()

    return tester.passed, tester.failed


if __name__ == "__main__":
    print("="*60)
    print("AGENT EDGE CASE TESTING")
    print("="*60)
    print("\nThis test suite verifies the agent handles edge cases gracefully.")
    print("Testing various error scenarios, malformed inputs, and edge cases...\n")

    passed, failed = asyncio.run(test_edge_cases())

    total = passed + failed
    if total > 0:
        pass_rate = passed / total * 100
        if pass_rate >= 80:
            print("✅ ROBUST - Agent handles most edge cases gracefully")
        elif pass_rate >= 60:
            print("⚠️  NEEDS IMPROVEMENT - Some edge cases not handled")
        else:
            print("❌ FRAGILE - Many edge cases cause problems")

    sys.exit(0 if failed == 0 else 1)
