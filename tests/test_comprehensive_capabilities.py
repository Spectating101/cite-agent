#!/usr/bin/env python3
"""
Comprehensive Agent Capability Test
Tests 12 core capabilities to verify agent is production-ready

Target: 90%+ pass rate (currently 58.3% = 7/12)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


class CapabilityTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def test_pass(self, name: str, reason: str = ""):
        self.passed += 1
        self.results.append({"name": name, "status": "✅ PASS", "reason": reason})
        print(f"✅ {name}")
        if reason:
            print(f"   {reason}")

    def test_fail(self, name: str, reason: str):
        self.failed += 1
        self.results.append({"name": name, "status": "❌ FAIL", "reason": reason})
        print(f"❌ {name}")
        print(f"   {reason}")

    def summary(self):
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Passed: {self.passed}/{total} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed}/{total} ({100-pass_rate:.1f}%)")
        print(f"\nTarget: 90%+ pass rate")

        if pass_rate >= 90:
            print(f"✅ PRODUCTION-READY!")
            return True
        else:
            print(f"❌ NOT READY - Need {int((0.9 * total) - self.passed)} more passes")
            return False


async def test_comprehensive_capabilities():
    """Test all 12 core capabilities"""

    tester = CapabilityTest()
    agent = EnhancedNocturnalAgent()

    try:
        await agent.initialize()

        print("="*80)
        print("COMPREHENSIVE AGENT CAPABILITY TEST (12 capabilities)")
        print("="*80)
        print()

        # 1. File Reading (short file)
        print("\n[1/12] Testing: File Reading (short file)")
        result = await agent.process_request(ChatRequest(
            question="Read README.md and tell me what this project does"
        ))
        if "read_file" in result.tools_used and len(result.response) > 50:
            tester.test_pass("File Reading", "Successfully read and described README.md")
        else:
            tester.test_fail("File Reading", f"Tools: {result.tools_used}, Response length: {len(result.response)}")

        # 2. Code Analysis - Can find methods in large files
        print("\n[2/12] Testing: Code Analysis (find method in large file)")
        result = await agent.process_request(ChatRequest(
            question="In enhanced_ai_agent.py, what are the main steps in the process_request method?"
        ))
        has_shell = "shell_execution" in result.tools_used
        has_method_content = "async def" in result.response.lower() or "process_request" in result.response
        if has_shell and has_method_content and len(result.response) > 200:
            tester.test_pass("Code Analysis", "Found and explained method in large file")
        else:
            tester.test_fail("Code Analysis", f"Shell: {has_shell}, Has content: {has_method_content}, Length: {len(result.response)}")

        # 3. Multi-step Reasoning
        print("\n[3/12] Testing: Multi-step Reasoning")
        result = await agent.process_request(ChatRequest(
            question="What files are in cite_agent/ directory and what do they do?"
        ))
        has_files = any(ext in result.response for ext in [".py", "agent", "enhanced"])
        has_reasoning = len(result.response) > 100
        if has_files and has_reasoning:
            tester.test_pass("Multi-step Reasoning", "Listed files and explained their purpose")
        else:
            tester.test_fail("Multi-step Reasoning", f"Has files: {has_files}, Has reasoning: {has_reasoning}")

        # 4. Ambiguous Requests
        print("\n[4/12] Testing: Ambiguous Requests")
        result = await agent.process_request(ChatRequest(
            question="Tell me about the agent"
        ))
        if len(result.response) > 50:
            tester.test_pass("Ambiguous Requests", "Handled vague request appropriately")
        else:
            tester.test_fail("Ambiguous Requests", f"Response too short: {len(result.response)} chars")

        # 5. Project Architecture
        print("\n[5/12] Testing: Project Architecture Understanding")
        result = await agent.process_request(ChatRequest(
            question="What are the main components of this codebase?"
        ))
        has_components = any(word in result.response.lower() for word in ["agent", "api", "client", "module"])
        if has_components and len(result.response) > 100:
            tester.test_pass("Project Architecture", "Identified main components")
        else:
            tester.test_fail("Project Architecture", f"Has components: {has_components}, Length: {len(result.response)}")

        # 6. Shell Execution
        print("\n[6/12] Testing: Shell Execution")
        result = await agent.process_request(ChatRequest(
            question="List Python files in cite_agent directory"
        ))
        if "shell_execution" in result.tools_used:
            tester.test_pass("Shell Execution", "Executed shell command successfully")
        else:
            tester.test_fail("Shell Execution", f"Tools: {result.tools_used}")

        # 7. Contextual Understanding - Searches for related files
        print("\n[7/12] Testing: Contextual Understanding")
        result = await agent.process_request(ChatRequest(
            question="How does authentication work in this codebase?"
        ))
        searched_for_auth = "shell_execution" in result.tools_used or "grep" in result.response.lower()
        has_auth_info = any(word in result.response.lower() for word in ["auth", "token", "login", "credential"])
        if searched_for_auth and has_auth_info:
            tester.test_pass("Contextual Understanding", "Searched for and found auth-related code")
        else:
            tester.test_fail("Contextual Understanding", f"Searched: {searched_for_auth}, Found auth: {has_auth_info}")

        # 8. Deep File Analysis
        print("\n[8/12] Testing: Deep File Analysis")
        result = await agent.process_request(ChatRequest(
            question="What does enhanced_ai_agent.py do? Give me details"
        ))
        is_detailed = len(result.response) > 200
        has_specifics = any(word in result.response.lower() for word in ["function", "method", "class", "process"])
        if is_detailed and has_specifics:
            tester.test_pass("Deep File Analysis", "Provided detailed analysis")
        else:
            tester.test_fail("Deep File Analysis", f"Detailed: {is_detailed}, Specific: {has_specifics}")

        # 9. Comparative Analysis - Read multiple files
        print("\n[9/12] Testing: Comparative Analysis")
        result = await agent.process_request(ChatRequest(
            question="Compare README.md and ARCHITECTURE.md - what's different?"
        ))
        read_multiple = result.tools_used.count("read_file") >= 2 or "shell_execution" in result.tools_used
        has_comparison = any(word in result.response.lower() for word in ["differ", "whereas", "while", "compare", "contrast"])
        if read_multiple and has_comparison:
            tester.test_pass("Comparative Analysis", "Compared multiple files")
        else:
            tester.test_fail("Comparative Analysis", f"Read multiple: {read_multiple}, Has comparison: {has_comparison}")

        # 10. Context Retention
        print("\n[10/12] Testing: Context Retention")
        # First query
        await agent.process_request(ChatRequest(
            question="What's in cite_agent directory?"
        ))
        # Follow-up
        result = await agent.process_request(ChatRequest(
            question="What about the tests directory?"
        ))
        if len(result.response) > 50:
            tester.test_pass("Context Retention", "Understood follow-up question")
        else:
            tester.test_fail("Context Retention", f"Response too short: {len(result.response)}")

        # 11. Debugging Help - Grep for relevant code
        print("\n[11/12] Testing: Debugging Help")
        result = await agent.process_request(ChatRequest(
            question="Where is authentication logic implemented?"
        ))
        searched_code = "shell_execution" in result.tools_used
        found_location = any(word in result.response.lower() for word in ["line", "file", ".py", "auth"])
        if searched_code and found_location:
            tester.test_pass("Debugging Help", "Found and located relevant code")
        else:
            tester.test_fail("Debugging Help", f"Searched: {searched_code}, Found location: {found_location}")

        # 12. Error Recovery
        print("\n[12/12] Testing: Error Recovery")
        result = await agent.process_request(ChatRequest(
            question="Read nonexistent_file_12345.txt"
        ))
        handles_gracefully = len(result.response) > 20 and not result.response.startswith("ERROR")
        says_not_found = "not found" in result.response.lower() or "doesn't exist" in result.response.lower()
        if handles_gracefully and says_not_found:
            tester.test_pass("Error Recovery", "Handled missing file gracefully")
        else:
            tester.test_fail("Error Recovery", f"Graceful: {handles_gracefully}, Says not found: {says_not_found}")

    finally:
        await agent.session.close()

    return tester.summary()


if __name__ == "__main__":
    result = asyncio.run(test_comprehensive_capabilities())
    sys.exit(0 if result else 1)
