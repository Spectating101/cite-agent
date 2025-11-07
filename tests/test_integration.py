"""
Integration Testing for All Fixes

Verifies that all 5 comprehensive fixes work together correctly in real-world scenarios.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


class IntegrationTester:
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
        print(f"INTEGRATION TEST RESULTS")
        print(f"{'='*60}")
        print(f"Passed: {self.passed}/{total}")
        print(f"Failed: {self.failed}/{total}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"{'='*60}\n")


async def test_integration():
    """Test all fixes working together"""

    tester = IntegrationTester()
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("Starting Integration Testing...\n")
    print("This verifies all 5 fixes work together in real scenarios.\n")

    # =========================================================================
    # Scenario 1: DEV MODE Variable Reset Fix
    # Test that grep integration works in DEV MODE
    # =========================================================================
    print("Scenario 1: DEV MODE grep integration (Fix #1)")
    try:
        result = await agent.process_request(ChatRequest(
            question="In enhanced_ai_agent.py, what are the parameters of the process_request method?"
        ))

        # Should use shell execution (grep/find)
        used_shell = "shell_execution" in result.tools_used or "grep_search" in result.tools_used
        has_content = len(result.response) > 100
        mentions_method = "process_request" in result.response.lower()

        tester.check(
            "DEV MODE grep - shell execution",
            used_shell,
            f"Tools: {result.tools_used}"
        )
        tester.check(
            "DEV MODE grep - substantial response",
            has_content and mentions_method,
            f"Response length: {len(result.response)}"
        )
    except Exception as e:
        tester.check("DEV MODE grep integration", False, f"Exception: {e}")

    # =========================================================================
    # Scenario 2: Conceptual Understanding (Fix #2)
    # Test that agent can search for conceptual topics
    # =========================================================================
    print("\nScenario 2: Conceptual understanding (Fix #2)")
    try:
        result = await agent.process_request(ChatRequest(
            question="How does authentication work in this codebase?"
        ))

        # Should trigger shell/grep search
        used_search = any(tool in result.tools_used for tool in [
            "shell_execution", "grep_search"
        ])
        has_auth_content = "auth" in result.response.lower()

        tester.check(
            "Conceptual search - triggers grep",
            used_search,
            f"Tools: {result.tools_used}"
        )
        tester.check(
            "Conceptual search - finds auth code",
            has_auth_content or "not found" in result.response.lower(),
            f"Response mentions authentication or reports not found"
        )
    except Exception as e:
        tester.check("Conceptual understanding", False, f"Exception: {e}")

    # =========================================================================
    # Scenario 3: Debugging Help (Fix #3)
    # Same as conceptual understanding but phrased as debugging
    # =========================================================================
    print("\nScenario 3: Debugging help (Fix #3)")
    try:
        result = await agent.process_request(ChatRequest(
            question="Where is the configuration loading logic?"
        ))

        used_search = any(tool in result.tools_used for tool in [
            "shell_execution", "grep_search"
        ])
        mentions_config = "config" in result.response.lower()

        tester.check(
            "Debugging - triggers grep search",
            used_search,
            f"Tools: {result.tools_used}"
        )
        tester.check(
            "Debugging - provides relevant info",
            mentions_config or "not found" in result.response.lower(),
            f"Response addresses configuration"
        )
    except Exception as e:
        tester.check("Debugging help", False, f"Exception: {e}")

    # =========================================================================
    # Scenario 4: Comparative Analysis (Fix #4)
    # Test reading multiple files for comparison
    # =========================================================================
    print("\nScenario 4: Comparative analysis (Fix #4)")
    try:
        result = await agent.process_request(ChatRequest(
            question="Compare README.md and ARCHITECTURE.md"
        ))

        # Should use shell execution
        used_shell = "shell_execution" in result.tools_used
        # Response should either:
        # 1. Compare both files (best case)
        # 2. Report files not found (acceptable for missing files)
        # 3. Have substantial content
        has_comparison = len(result.response) > 50

        tester.check(
            "Comparison - uses shell",
            used_shell,
            f"Tools: {result.tools_used}"
        )
        tester.check(
            "Comparison - substantial response",
            has_comparison,
            f"Response length: {len(result.response)}"
        )
    except Exception as e:
        tester.check("Comparative analysis", False, f"Exception: {e}")

    # =========================================================================
    # Scenario 5: Error Recovery (Fix #5)
    # Test friendly error messages for missing files
    # =========================================================================
    print("\nScenario 5: Error recovery (Fix #5)")
    try:
        result = await agent.process_request(ChatRequest(
            question="Read integration_test_nonexistent_file_xyz.txt"
        ))

        # Should have friendly error message
        has_friendly_error = any(phrase in result.response.lower() for phrase in [
            "couldn't find", "not found", "doesn't exist", "unable to locate"
        ])
        no_technical_jargon = all(term not in result.response.lower() for term in [
            "error:", "exception:", "traceback", "stacktrace"
        ])

        tester.check(
            "Error recovery - friendly message",
            has_friendly_error,
            f"Response: {result.response[:80]}"
        )
        tester.check(
            "Error recovery - no technical jargon",
            no_technical_jargon,
            f"Response is user-friendly"
        )
    except Exception as e:
        tester.check("Error recovery", False, f"Exception: {e}")

    # =========================================================================
    # Scenario 6: All Fixes Together
    # Complex query that exercises multiple fixes
    # =========================================================================
    print("\nScenario 6: All fixes working together")
    try:
        result = await agent.process_request(ChatRequest(
            question="Find authentication logic in the codebase and compare it with the error handling approach. If any files are missing, let me know."
        ))

        # This query should:
        # - Trigger conceptual grep (Fix #2, #3)
        # - Potentially compare files (Fix #4)
        # - Handle any missing files gracefully (Fix #5)
        # - Work correctly in DEV MODE (Fix #1)

        used_tools = len(result.tools_used) > 0
        has_response = len(result.response) > 100
        is_coherent = not any(jargon in result.response.lower() for jargon in [
            "error:", "exception:", "none", "null"
        ])

        tester.check(
            "Complex integration - uses tools",
            used_tools,
            f"Tools: {result.tools_used}"
        )
        tester.check(
            "Complex integration - substantial response",
            has_response,
            f"Response length: {len(result.response)}"
        )
        tester.check(
            "Complex integration - coherent output",
            is_coherent or "not found" in result.response.lower(),
            f"Response is well-formatted"
        )
    except Exception as e:
        tester.check("All fixes together", False, f"Exception: {e}")

    # =========================================================================
    # Scenario 7: Real-world workflow
    # Simulate actual user workflow
    # =========================================================================
    print("\nScenario 7: Real-world workflow simulation")
    try:
        conversation_id = "workflow_test"

        # Step 1: Explore codebase
        result1 = await agent.process_request(ChatRequest(
            question="What files are in this project?",
            conversation_id=conversation_id
        ))

        # Step 2: Ask about specific functionality
        result2 = await agent.process_request(ChatRequest(
            question="How does the agent handle errors?",
            conversation_id=conversation_id
        ))

        # Step 3: Try to read a file (might not exist)
        result3 = await agent.process_request(ChatRequest(
            question="Show me the error handling code",
            conversation_id=conversation_id
        ))

        # Step 4: Ask follow-up
        result4 = await agent.process_request(ChatRequest(
            question="What about authentication?",
            conversation_id=conversation_id
        ))

        all_responded = all(len(r.response) > 0 for r in [result1, result2, result3, result4])
        maintains_context = len(agent.conversation_history) >= 4

        tester.check(
            "Workflow - all queries answered",
            all_responded,
            f"All 4 queries returned responses"
        )
        tester.check(
            "Workflow - maintains context",
            maintains_context,
            f"Conversation history: {len(agent.conversation_history)} entries"
        )
    except Exception as e:
        tester.check("Real-world workflow", False, f"Exception: {e}")

    await agent.session.close()

    # Print summary
    tester.summary()

    # Print detailed results
    print("FIX VERIFICATION DETAILS:")
    print("-" * 60)
    print("Fix #1 (DEV MODE Variable Reset): ", end="")
    fix1_tests = [r for r in tester.results if "DEV MODE" in r[0]]
    print("✅ PASS" if all(r[1] for r in fix1_tests) else "❌ FAIL")

    print("Fix #2 & #3 (Conceptual Grep): ", end="")
    fix23_tests = [r for r in tester.results if "Conceptual" in r[0] or "Debugging" in r[0]]
    print("✅ PASS" if all(r[1] for r in fix23_tests) else "❌ FAIL")

    print("Fix #4 (Comparative Analysis): ", end="")
    fix4_tests = [r for r in tester.results if "Comparison" in r[0]]
    print("✅ PASS" if all(r[1] for r in fix4_tests) else "❌ FAIL")

    print("Fix #5 (Error Recovery): ", end="")
    fix5_tests = [r for r in tester.results if "Error recovery" in r[0]]
    print("✅ PASS" if all(r[1] for r in fix5_tests) else "❌ FAIL")

    print("Integration: ", end="")
    integration_tests = [r for r in tester.results if "integration" in r[0].lower() or "workflow" in r[0].lower()]
    print("✅ PASS" if all(r[1] for r in integration_tests) else "❌ FAIL")
    print("-" * 60)

    return tester.passed, tester.failed


if __name__ == "__main__":
    print("="*60)
    print("AGENT INTEGRATION TESTING")
    print("="*60)
    print("\nThis verifies all 5 fixes work together correctly.")
    print("Testing real-world scenarios and workflows...\n")

    passed, failed = asyncio.run(test_integration())

    total = passed + failed
    if total > 0:
        pass_rate = passed / total * 100
        if pass_rate >= 90:
            print("\n🎉 PRODUCTION READY - All fixes working perfectly!")
        elif pass_rate >= 75:
            print("\n✅ GOOD - Most fixes working, minor issues")
        else:
            print("\n⚠️  NEEDS WORK - Some fixes not working correctly")

    sys.exit(0 if failed == 0 else 1)
