#!/usr/bin/env python3
"""
COMPREHENSIVE STRESS TEST FOR CITE-AGENT

Tests:
1. High volume cache operations (100+ entries)
2. Edge cases and error handling
3. Conversation context limits (50+ turns)
4. Response validation with malformed data
5. File system operations (large library)
6. Memory usage monitoring
7. Concurrent query patterns
8. Encoding and special characters
9. Boundary conditions
10. Recovery from failures
"""

import asyncio
import os
import sys
import time
import json
import psutil
import traceback
from datetime import datetime
from pathlib import Path

os.environ['USE_LOCAL_KEYS'] = 'false'
os.environ['NOCTURNAL_DEBUG'] = '0'
os.environ['CITE_AGENT_CACHE'] = 'true'

from cite_agent import EnhancedNocturnalAgent, ChatRequest
from cite_agent.query_cache import get_cache, cache_query, get_cached_response, clear_cache, cache_stats
from cite_agent.response_validation import (
    safe_get, safe_list, safe_str, safe_int, safe_float,
    validate_paper_response, validate_finance_response
)
from cite_agent.workflow import WorkflowManager, Paper, safe_create_paper_from_dict


class StressTestSuite:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "errors": [],
            "warnings_list": [],
            "performance": {},
        }
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024

    def test(self, name: str, condition: bool, details: str = ""):
        """Record test result"""
        self.results["total_tests"] += 1
        if condition:
            self.results["passed"] += 1
            print(f"  ✅ {name}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{name}: {details}")
            print(f"  ❌ {name}")
            if details:
                print(f"     {details[:100]}")

    def warn(self, message: str):
        """Record warning"""
        self.results["warnings"] += 1
        self.results["warnings_list"].append(message)
        print(f"  ⚠️  {message}")

    def get_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        return psutil.Process().memory_info().rss / 1024 / 1024

    async def test_cache_stress(self):
        """Test cache under heavy load"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 1: Cache Performance")
        print("=" * 70)

        clear_cache()
        cache = get_cache()

        # Test 1: Fill cache to max capacity
        print("\n📊 Filling cache to 100 entries...")
        start = time.time()
        for i in range(100):
            cache_query(
                f"Query number {i} about research topic {i}",
                f"Response {i}: This is a detailed answer about topic {i} with citations and data.",
                [f"tool_{i % 5}"],
                500 + (i * 10)
            )
        fill_time = time.time() - start
        self.results["performance"]["cache_fill_100"] = fill_time

        stats = cache_stats()
        self.test("Cache holds 100 entries", stats["entries"] == 100, f"Got {stats['entries']}")
        self.test("Fill time < 1s", fill_time < 1.0, f"Took {fill_time:.2f}s")

        # Test 2: Cache eviction (LRU)
        print("\n📊 Testing LRU eviction...")
        cache_query("Query 101", "Response 101", ["test"], 100)
        stats = cache_stats()
        self.test("LRU eviction works", stats["evictions"] >= 1, f"Evictions: {stats['evictions']}")
        self.test("Cache stays at max size", stats["entries"] == 100, f"Entries: {stats['entries']}")

        # Test 3: Cache hit performance
        print("\n📊 Testing cache hit performance...")
        start = time.time()
        hits = 0
        for i in range(50):
            result = get_cached_response(f"Query number {i+50} about research topic {i+50}")
            if result:
                hits += 1
        hit_time = time.time() - start
        self.results["performance"]["cache_50_hits"] = hit_time

        self.test("Cache hit rate > 90%", hits >= 45, f"Got {hits}/50 hits")
        self.test("50 cache lookups < 100ms", hit_time < 0.1, f"Took {hit_time*1000:.2f}ms")

        # Test 4: Query normalization stress
        print("\n📊 Testing query normalization...")
        cache_query("Test QUERY with CAPS", "Response", ["test"], 100)
        variations = [
            "test query with caps",
            "TEST QUERY WITH CAPS",
            "Test Query With Caps",
            "test query with caps?",
            "  test query with caps  ",
        ]
        normalized_hits = sum(1 for v in variations if get_cached_response(v))
        self.test("Query normalization (5 variations)", normalized_hits == 5, f"Hit {normalized_hits}/5")

        # Test 5: Cache persistence (save/load without clearing)
        print("\n📊 Testing cache persistence...")
        entries_before = cache_stats()["entries"]
        cache._save_to_disk()
        # Simulate fresh load (create new cache instance that loads from disk)
        from cite_agent.query_cache import QueryCache
        fresh_cache = QueryCache()  # Should load from disk automatically
        entries_after = fresh_cache.get_stats()["entries"]
        self.test("Cache persistence", entries_after == entries_before, f"Before: {entries_before}, After: {entries_after}")

    async def test_conversation_context_limits(self):
        """Test conversation with many turns"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 2: Conversation Context Limits")
        print("=" * 70)

        agent = EnhancedNocturnalAgent()
        await agent.initialize()

        # Pre-populate cache for 50 different queries
        print("\n📊 Setting up 50-turn conversation...")
        for i in range(50):
            cache_query(
                f"Research question {i}",
                f"Answer {i}: This relates to previous questions about topics {max(0,i-3)} through {i-1}.",
                ["archive_api"],
                1000
            )

        # Run 50-turn conversation
        start_memory = self.get_memory_mb()
        for i in range(50):
            request = ChatRequest(
                question=f"Research question {i}",
                user_id="stress_test",
                conversation_id="long_conversation"
            )
            await agent.process_request(request)

        end_memory = self.get_memory_mb()
        memory_growth = end_memory - start_memory
        history_size = len(agent.conversation_history)

        self.test("50-turn conversation completes", history_size == 100, f"History: {history_size} messages")
        self.test("Memory growth < 50MB", memory_growth < 50, f"Grew {memory_growth:.1f}MB")
        self.results["performance"]["50_turn_memory_mb"] = memory_growth

        # Test conversation history size
        history_json_size = len(json.dumps(agent.conversation_history))
        self.test("History JSON < 1MB", history_json_size < 1_000_000, f"Size: {history_json_size} bytes")

        # Test if context still accessible
        last_msg = agent.conversation_history[-1]["content"]
        self.test("Last message accessible", "Answer 49" in last_msg, last_msg[:50])

        await agent.close()

    async def test_malformed_input_handling(self):
        """Test handling of edge case inputs"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 3: Malformed Input Handling")
        print("=" * 70)

        agent = EnhancedNocturnalAgent()
        await agent.initialize()

        edge_cases = [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("?" * 100, "100 question marks"),
            ("A" * 10000, "10K character query"),
            ("Hello\n\n\nWorld", "Multiple newlines"),
            ("Query with émojis 🔬📚💡", "Emojis and unicode"),
            ("SELECT * FROM users; DROP TABLE;", "SQL injection attempt"),
            ("<script>alert('xss')</script>", "XSS attempt"),
            ("{{jinja}}", "Template injection"),
            ("null", "Null string"),
            ("undefined", "Undefined string"),
            ("true", "Boolean string"),
            ("12345", "Numeric string"),
            ("['array']", "JSON array string"),
            ('{"key": "value"}', "JSON object string"),
        ]

        for query, description in edge_cases:
            try:
                request = ChatRequest(
                    question=query,
                    user_id="edge_test",
                    conversation_id="edge_test"
                )
                response = await agent.process_request(request)
                has_response = len(response.response) > 0
                self.test(f"{description} - handled", has_response, "No response generated")
            except Exception as e:
                self.test(f"{description} - no crash", False, str(e)[:100])

        await agent.close()

    async def test_response_validation_edge_cases(self):
        """Test response validation with malformed data"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 4: Response Validation Edge Cases")
        print("=" * 70)

        # Test safe_get with deeply nested and malformed structures
        test_cases = [
            (None, ["a"], "default", "None input"),
            ({}, ["a", "b", "c"], "default", "Empty dict"),
            ({"a": None}, ["a", "b"], "default", "None in chain"),
            ({"a": {"b": [1,2,3]}}, ["a", "b", 1], 2, "List index access"),
            ({"a": {"b": [1,2,3]}}, ["a", "b", 10], "default", "Out of bounds"),
            ("not a dict", ["a"], "default", "String input"),
            ([1, 2, 3], ["a"], "default", "List input"),
            ({"a": {"b": {"c": {"d": {"e": "deep"}}}}}, ["a", "b", "c", "d", "e"], "deep", "5-level nesting"),
        ]

        for data, keys, expected, desc in test_cases:
            result = safe_get(data, *keys, default="default")
            self.test(f"safe_get: {desc}", result == expected, f"Got {result}")

        # Test safe_list edge cases
        list_cases = [
            (None, None, [], "None input"),
            ({"papers": None}, "papers", [], "None value"),
            ({"papers": "not list"}, "papers", [], "String value"),
            ({"papers": 123}, "papers", [], "Integer value"),
            ({"papers": {"nested": "dict"}}, "papers", [], "Dict value"),
            ({"papers": (1, 2, 3)}, "papers", [1, 2, 3], "Tuple conversion"),
            ({"papers": {1, 2, 3}}, "papers", None, "Set conversion"),  # Sets don't preserve order
        ]

        for data, key, expected, desc in list_cases:
            result = safe_list(data, key, default=[])
            if expected is None:  # Set case - just check it's a list
                self.test(f"safe_list: {desc}", isinstance(result, list), f"Got {type(result)}")
            else:
                self.test(f"safe_list: {desc}", result == expected, f"Got {result}")

        # Test paper validation with malformed data
        malformed_papers = [
            {},  # Empty
            {"title": ""},  # Empty title
            {"title": "Paper", "authors": "string"},  # String authors
            {"title": "Paper", "year": "not a year"},  # Invalid year
            {"title": "Paper", "authors": [{"broken": "format"}]},  # Broken author format
        ]

        for i, paper_data in enumerate(malformed_papers):
            result = validate_paper_response(paper_data)
            # Should not crash and should provide validated structure
            self.test(f"Malformed paper {i+1} handled", result.value is not None, "No value returned")

    async def test_workflow_stress(self):
        """Test workflow with many papers"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 5: Workflow File System Stress")
        print("=" * 70)

        wf = WorkflowManager()

        # Test 1: Add 100 papers rapidly
        print("\n📊 Adding 100 papers to library...")
        start = time.time()
        for i in range(100):
            paper = Paper(
                title=f"Research Paper {i}: A Study of Topic {i}",
                authors=[f"Author {i}A", f"Author {i}B", f"Author {i}C"],
                year=2000 + (i % 25),
                doi=f"10.1234/paper.{i}",
                abstract=f"This paper examines topic {i} in great detail." * 10,
                venue=f"Conference {i % 10}",
                citation_count=i * 10,
            )
            wf.add_paper(paper)
        add_time = time.time() - start
        self.results["performance"]["add_100_papers"] = add_time

        papers = wf.list_papers()
        self.test("100 papers added", len(papers) >= 100, f"Got {len(papers)}")
        self.test("Add time < 5s", add_time < 5.0, f"Took {add_time:.2f}s")

        # Test 2: List performance
        start = time.time()
        papers = wf.list_papers()
        list_time = time.time() - start
        self.test("List 100 papers < 1s", list_time < 1.0, f"Took {list_time:.3f}s")

        # Test 3: Search performance
        start = time.time()
        results = wf.search_library("Topic 50")
        search_time = time.time() - start
        self.test("Search returns results", len(results) > 0, f"Found {len(results)}")
        self.test("Search < 500ms", search_time < 0.5, f"Took {search_time*1000:.1f}ms")

        # Test 4: BibTeX export with 100 papers
        start = time.time()
        success = wf.export_to_bibtex()
        export_time = time.time() - start
        self.test("Export 100 papers to BibTeX", success, "Export failed")
        self.test("Export time < 2s", export_time < 2.0, f"Took {export_time:.2f}s")

        # Check BibTeX file size
        if wf.bibtex_file.exists():
            size_kb = wf.bibtex_file.stat().st_size / 1024
            self.test("BibTeX file reasonable size", 10 < size_kb < 500, f"Size: {size_kb:.1f}KB")

        # Test 5: History stress
        print("\n📊 Testing history with many entries...")
        for i in range(100):
            wf.save_query_result(
                query=f"Historical query {i}",
                response=f"Response to query {i}",
                metadata={"iteration": i}
            )

        history = wf.get_history()
        self.test("History stores 100+ entries", len(history) >= 100, f"Got {len(history)}")

    async def test_shell_detection_comprehensive(self):
        """Comprehensive shell command detection test"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 6: Shell Detection Comprehensive")
        print("=" * 70)

        agent = EnhancedNocturnalAgent()

        # Should NOT be detected as shell commands
        safe_queries = [
            "Find papers on machine learning",
            "Can you find me information about GPT?",
            "I want to find out about neural networks",
            "Please grep through my research notes",
            "The cat is sleeping on my desk",
            "Let me show you my findings",
            "Remove duplicate entries from my library",
            "mkdir is a useful command",
            "What does pwd mean?",
            "Show me how to use grep command",
        ]

        # Should be detected as shell commands
        shell_commands = [
            "ls -la",
            "cd /home/user",
            "pwd",
            "mkdir new_folder",
            "rm -rf temp/",
            "cat file.txt",
            "grep pattern file.py",
            "find . -name *.py",
            "find /usr -type f",
            "!echo hello",
            "run npm install",
            "execute python script.py",
        ]

        print("\n📊 Testing FALSE NEGATIVES (should allow)...")
        for query in safe_queries:
            result = agent._is_shell_command(query)
            self.test(f"'{query[:40]}...' NOT shell", not result, "False positive")

        print("\n📊 Testing TRUE POSITIVES (should block)...")
        for cmd in shell_commands:
            result = agent._is_shell_command(cmd)
            self.test(f"'{cmd}' IS shell", result, "False negative")

    async def test_concurrent_patterns(self):
        """Test rapid sequential queries"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 7: Rapid Sequential Queries")
        print("=" * 70)

        agent = EnhancedNocturnalAgent()
        await agent.initialize()

        # Simulate rapid-fire queries (like auto-complete or impatient user)
        queries = ["test"] * 20 + ["show my library"] * 10 + ["hello"] * 10

        print(f"\n📊 Processing {len(queries)} queries rapidly...")
        start = time.time()
        errors = 0
        for query in queries:
            try:
                request = ChatRequest(question=query, user_id="rapid", conversation_id="rapid")
                await agent.process_request(request)
            except Exception as e:
                errors += 1

        elapsed = time.time() - start
        qps = len(queries) / elapsed

        self.test("All queries processed", errors == 0, f"{errors} errors")
        self.test(f"QPS > 10", qps > 10, f"Got {qps:.1f} QPS")
        self.test("Time < 5s for 40 queries", elapsed < 5.0, f"Took {elapsed:.2f}s")
        self.results["performance"]["queries_per_second"] = qps

        await agent.close()

    async def test_memory_leak_check(self):
        """Check for memory leaks"""
        print("\n" + "=" * 70)
        print("🔥 STRESS TEST 8: Memory Leak Detection")
        print("=" * 70)

        agent = EnhancedNocturnalAgent()
        await agent.initialize()

        # Baseline
        baseline = self.get_memory_mb()

        # Run many operations
        print("\n📊 Running 100 operations...")
        for i in range(100):
            request = ChatRequest(question="test", user_id="mem_test", conversation_id="mem_test")
            await agent.process_request(request)

            if i % 25 == 0:
                current = self.get_memory_mb()
                print(f"   Iteration {i}: {current:.1f}MB (Δ{current - baseline:.1f}MB)")

        # Final check
        final = self.get_memory_mb()
        growth = final - baseline

        self.test("Memory growth < 100MB after 100 ops", growth < 100, f"Grew {growth:.1f}MB")
        self.results["performance"]["memory_growth_100_ops_mb"] = growth

        # Check conversation history size isn't unbounded
        history_size = len(agent.conversation_history)
        self.test("History size reasonable", history_size == 200, f"Size: {history_size}")

        await agent.close()

    async def run_all_stress_tests(self):
        """Run complete stress test suite"""
        print("=" * 70)
        print("🔬 CITE-AGENT COMPREHENSIVE STRESS TEST")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Initial Memory: {self.start_memory:.1f}MB")
        print("=" * 70)

        tests = [
            ("Cache Performance", self.test_cache_stress),
            ("Conversation Limits", self.test_conversation_context_limits),
            ("Malformed Input", self.test_malformed_input_handling),
            ("Response Validation", self.test_response_validation_edge_cases),
            ("Workflow File System", self.test_workflow_stress),
            ("Shell Detection", self.test_shell_detection_comprehensive),
            ("Rapid Queries", self.test_concurrent_patterns),
            ("Memory Leaks", self.test_memory_leak_check),
        ]

        for name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                print(f"\n❌ CRITICAL: {name} test crashed!")
                print(traceback.format_exc())
                self.results["errors"].append(f"{name} CRASHED: {str(e)}")

        self.print_summary()

    def print_summary(self):
        """Print comprehensive summary"""
        end_memory = self.get_memory_mb()
        total_memory_growth = end_memory - self.start_memory

        print("\n" + "=" * 70)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 70)

        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        warnings = self.results["warnings"]

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Warnings: {warnings} ⚠️")
        print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")

        print(f"\n💾 Memory Usage:")
        print(f"  Start: {self.start_memory:.1f}MB")
        print(f"  End: {end_memory:.1f}MB")
        print(f"  Total Growth: {total_memory_growth:.1f}MB")

        if self.results["performance"]:
            print(f"\n⚡ Performance Metrics:")
            for metric, value in self.results["performance"].items():
                if "time" in metric or "second" in metric:
                    print(f"  {metric}: {value:.3f}s")
                elif "mb" in metric.lower():
                    print(f"  {metric}: {value:.1f}MB")
                else:
                    print(f"  {metric}: {value:.2f}")

        if self.results["errors"]:
            print(f"\n❌ Failures:")
            for error in self.results["errors"][:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.results["errors"]) > 10:
                print(f"  ... and {len(self.results['errors']) - 10} more")

        if self.results["warnings_list"]:
            print(f"\n⚠️  Warnings:")
            for warning in self.results["warnings_list"][:5]:
                print(f"  - {warning}")

        # Save results
        with open("stress_test_results.json", "w") as f:
            json.dump({
                "summary": self.results,
                "memory": {
                    "start_mb": self.start_memory,
                    "end_mb": end_memory,
                    "growth_mb": total_memory_growth,
                },
                "timestamp": datetime.now().isoformat(),
            }, f, indent=2)

        print(f"\n💾 Results saved to stress_test_results.json")

        print("\n" + "=" * 70)
        if failed == 0:
            print("🎉 ALL STRESS TESTS PASSED!")
        elif failed <= 5:
            print(f"⚠️  {failed} test(s) failed - minor issues")
        else:
            print(f"❌ {failed} test(s) failed - NEEDS ATTENTION")
        print("=" * 70)


async def main():
    suite = StressTestSuite()
    await suite.run_all_stress_tests()


if __name__ == "__main__":
    asyncio.run(main())
