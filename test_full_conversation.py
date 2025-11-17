#!/usr/bin/env python3
"""
Full-scale conversational test of Cite-Agent
Simulates a real professor using the chatbot for research
"""

import asyncio
import os
import json
from datetime import datetime

# Configure for testing
os.environ['USE_LOCAL_KEYS'] = 'false'  # Use backend auth
os.environ['NOCTURNAL_DEBUG'] = '0'
os.environ['CITE_AGENT_CACHE'] = 'true'

from cite_agent import EnhancedNocturnalAgent, ChatRequest
from cite_agent.query_cache import cache_stats, clear_cache
from cite_agent.workflow import WorkflowManager, Paper


class ConversationTester:
    def __init__(self):
        self.agent = None
        self.user_id = "professor_test"
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_log = []
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "total_tokens": 0,
            "cache_hits": 0,
        }

    async def setup(self):
        """Initialize agent"""
        print("=" * 70)
        print("🎓 CITE-AGENT FULL CONVERSATION TEST")
        print("=" * 70)
        print(f"Session: {self.session_id}")
        print(f"User: {self.user_id}")
        print("=" * 70)

        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()

        # Clear cache for fresh test
        clear_cache()
        print("✅ Agent initialized, cache cleared\n")

    async def ask(self, question: str, test_name: str = None):
        """Send a question and log the response"""
        request = ChatRequest(
            question=question,
            user_id=self.user_id,
            conversation_id=self.session_id
        )

        print(f"\n👤 PROFESSOR: {question}")
        print("-" * 70)

        start_time = datetime.now()
        response = await self.agent.process_request(request)
        elapsed = (datetime.now() - start_time).total_seconds()

        # Log response
        self.conversation_log.append({
            "test": test_name or "general",
            "question": question,
            "response": response.response,
            "tools": response.tools_used,
            "tokens": response.tokens_used,
            "elapsed": elapsed,
            "cached": "cache_hit" in response.tools_used,
        })

        # Track metrics
        self.test_results["total_tokens"] += response.tokens_used
        if "cache_hit" in response.tools_used:
            self.test_results["cache_hits"] += 1

        # Display response
        print(f"🤖 CITE-AGENT:")
        print(response.response)
        print("-" * 70)
        print(f"📊 Tools: {', '.join(response.tools_used)}")
        print(f"⏱️  Time: {elapsed:.2f}s | Tokens: {response.tokens_used}")

        return response

    def test_passed(self, name: str, condition: bool, details: str = ""):
        """Record test result"""
        self.test_results["total_tests"] += 1
        if condition:
            self.test_results["passed"] += 1
            print(f"  ✅ {name}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{name}: {details}")
            print(f"  ❌ {name} - {details}")

    async def test_workflow_commands(self):
        """Test workflow features"""
        print("\n" + "=" * 70)
        print("📚 TEST SUITE 1: Workflow Commands")
        print("=" * 70)

        # Test 1: Show empty library
        response = await self.ask("show my library", "workflow_library")
        self.test_passed(
            "Empty library detection",
            "empty" in response.response.lower() or "no papers" in response.response.lower(),
            response.response[:100]
        )

        # Test 2: Show history
        response = await self.ask("show my history", "workflow_history")
        self.test_passed(
            "History command works",
            "workflow_history" in response.tools_used,
            f"Tools: {response.tools_used}"
        )

        # Test 3: Add a paper manually to library
        print("\n📝 Adding test paper to library...")
        wf = WorkflowManager()
        test_paper = Paper(
            title="Attention Is All You Need",
            authors=["Vaswani et al."],
            year=2017,
            doi="10.48550/arXiv.1706.03762",
            venue="NeurIPS"
        )
        success = wf.add_paper(test_paper)
        self.test_passed("Paper added to library", success, "Failed to add paper")

        # Test 4: Show library with paper
        response = await self.ask("show my library", "workflow_library_populated")
        self.test_passed(
            "Library shows added paper",
            "attention" in response.response.lower() or "vaswani" in response.response.lower(),
            response.response[:100]
        )

        # Test 5: Export to BibTeX
        response = await self.ask("export to bibtex", "workflow_export")
        self.test_passed(
            "BibTeX export works",
            "workflow_export" in response.tools_used or "exported" in response.response.lower(),
            f"Tools: {response.tools_used}"
        )

    async def test_quick_replies(self):
        """Test quick reply detection"""
        print("\n" + "=" * 70)
        print("⚡ TEST SUITE 2: Quick Replies & Edge Cases")
        print("=" * 70)

        # Test 1: Generic test prompt
        response = await self.ask("test", "quick_reply_test")
        self.test_passed(
            "Test prompt detected",
            "quick_reply" in response.tools_used,
            f"Tools: {response.tools_used}"
        )

        # Test 2: Hello greeting
        response = await self.ask("hello", "quick_reply_hello")
        # Should handle conversationally
        self.test_passed(
            "Greeting handled",
            len(response.response) > 0,
            "No response"
        )

        # Test 3: Short vague query
        response = await self.ask("papers?", "vague_query")
        # Should detect vagueness
        self.test_passed(
            "Vague query handled",
            len(response.response) > 0,
            "No response"
        )

    async def test_cache_behavior(self):
        """Test caching functionality"""
        print("\n" + "=" * 70)
        print("💾 TEST SUITE 3: Cache Behavior")
        print("=" * 70)

        # Pre-populate cache
        from cite_agent.query_cache import cache_query
        cache_query(
            "What is machine learning?",
            "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. Key types include supervised learning (labeled data), unsupervised learning (pattern discovery), and reinforcement learning (reward-based).",
            ["web_search", "backend_llm"],
            1200
        )

        # Test 1: Cache hit
        response = await self.ask("What is machine learning?", "cache_hit_test")
        self.test_passed(
            "Cache hit detected",
            "cache_hit" in response.tools_used,
            f"Tools: {response.tools_used}"
        )
        self.test_passed(
            "Zero tokens on cache hit",
            response.tokens_used == 0,
            f"Tokens used: {response.tokens_used}"
        )
        self.test_passed(
            "Cache indicator in response",
            "cached" in response.response.lower(),
            "No cache indicator"
        )

        # Test 2: Cache normalization (same query, different case)
        response = await self.ask("what is machine learning", "cache_normalize")
        self.test_passed(
            "Query normalization works",
            "cache_hit" in response.tools_used,
            f"Different case should still hit cache"
        )

        # Test 3: Cache miss
        response = await self.ask("What is deep learning?", "cache_miss")
        self.test_passed(
            "Cache miss handled",
            "cache_hit" not in response.tools_used,
            "Should not be cached"
        )

        # Test 4: Cache stats
        stats = cache_stats()
        self.test_passed(
            "Cache stats available",
            stats["hits"] > 0,
            f"Hits: {stats['hits']}"
        )
        print(f"\n📊 Cache Stats: {stats}")

    async def test_request_type_detection(self):
        """Test if agent correctly identifies request types"""
        print("\n" + "=" * 70)
        print("🔍 TEST SUITE 4: Request Type Detection")
        print("=" * 70)

        # These will show auth required, but we can see if it routes correctly

        # Test 1: Research query
        response = await self.ask(
            "Find papers on neural architecture search",
            "research_detection"
        )
        self.test_passed(
            "Research query routes to archive",
            "archive_api" in response.tools_used,
            f"Tools: {response.tools_used}"
        )

        # Test 2: Financial query
        response = await self.ask(
            "What is Tesla stock price?",
            "financial_detection"
        )
        self.test_passed(
            "Financial query routes to finsight",
            "finsight_api" in response.tools_used or "auth" in response.response.lower(),
            f"Tools: {response.tools_used}"
        )

        # Test 3: System/location query
        response = await self.ask(
            "What directory am I in?",
            "system_detection"
        )
        self.test_passed(
            "Location query handled",
            "directory" in response.response.lower() or "/" in response.response,
            response.response[:100]
        )

    async def test_shell_command_detection(self):
        """Test shell command vs regular query detection"""
        print("\n" + "=" * 70)
        print("🖥️  TEST SUITE 5: Shell Command Detection")
        print("=" * 70)

        # Test 1: Regular "find" query (NOT a shell command)
        is_shell = self.agent._is_shell_command("Find papers on transformers")
        self.test_passed(
            "Natural language 'Find' not detected as shell",
            not is_shell,
            "False positive"
        )

        # Test 2: Actual shell command
        is_shell = self.agent._is_shell_command("ls -la")
        self.test_passed(
            "Shell 'ls' command detected",
            is_shell,
            "False negative"
        )

        # Test 3: grep shell command
        is_shell = self.agent._is_shell_command("grep pattern file.txt")
        self.test_passed(
            "Shell 'grep' command detected",
            is_shell,
            "False negative"
        )

        # Test 4: Natural grep mention
        is_shell = self.agent._is_shell_command("Can you grep through my code?")
        self.test_passed(
            "Natural 'grep' mention not detected as shell",
            not is_shell,
            "False positive"
        )

    async def test_response_validation(self):
        """Test response validation utilities"""
        print("\n" + "=" * 70)
        print("🛡️  TEST SUITE 6: Response Validation")
        print("=" * 70)

        from cite_agent.response_validation import safe_get, safe_list, safe_str, safe_int
        from cite_agent.workflow import safe_create_paper_from_dict

        # Test 1: safe_get with nested dict
        data = {"a": {"b": {"c": "value"}}}
        result = safe_get(data, "a", "b", "c", default="not found")
        self.test_passed(
            "safe_get nested dict",
            result == "value",
            f"Got: {result}"
        )

        # Test 2: safe_get with missing key
        result = safe_get(data, "x", "y", "z", default="not found")
        self.test_passed(
            "safe_get missing key returns default",
            result == "not found",
            f"Got: {result}"
        )

        # Test 3: safe_list with malformed data
        result = safe_list({"papers": "not a list"}, "papers", default=[])
        self.test_passed(
            "safe_list handles non-list",
            result == [],
            f"Got: {result}"
        )

        # Test 4: safe_int from string
        result = safe_int({"year": "2024"}, "year", default=0)
        self.test_passed(
            "safe_int parses string",
            result == 2024,
            f"Got: {result}"
        )

        # Test 5: Safe paper creation with dict authors
        paper = safe_create_paper_from_dict({
            "title": "Test Paper",
            "authors": [{"name": "John Doe"}, {"given": "Jane", "family": "Smith"}],
            "year": "2023"
        })
        self.test_passed(
            "safe_create_paper handles dict authors",
            paper is not None and "Jane Smith" in paper.authors,
            f"Authors: {paper.authors if paper else 'None'}"
        )

    async def run_all_tests(self):
        """Run complete test suite"""
        await self.setup()

        # Run test suites
        await self.test_workflow_commands()
        await self.test_quick_replies()
        await self.test_cache_behavior()
        await self.test_request_type_detection()
        await self.test_shell_command_detection()
        await self.test_response_validation()

        # Cleanup
        await self.agent.close()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)

        results = self.test_results
        total = results["total_tests"]
        passed = results["passed"]
        failed = results["failed"]

        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        print(f"\nTotal Tokens Used: {results['total_tokens']}")
        print(f"Cache Hits: {results['cache_hits']}")

        if results["errors"]:
            print(f"\n❌ Failed Tests:")
            for error in results["errors"]:
                print(f"  - {error}")

        # Save results
        with open("conversation_test_results.json", "w") as f:
            json.dump({
                "summary": results,
                "conversation": self.conversation_log,
                "timestamp": datetime.now().isoformat(),
            }, f, indent=2)
        print(f"\n💾 Results saved to conversation_test_results.json")

        print("\n" + "=" * 70)
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed} test(s) need attention")
        print("=" * 70)


async def main():
    tester = ConversationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
