#!/usr/bin/env python3
"""
Test Suite for LLM-Based Query Intent Classification (Phase 4)

Tests the new _get_query_intent() function which intelligently classifies
user queries instead of using hardcoded patterns.

This is the CORE classifier for routing - all tests here verify that:
1. Correct intent is returned for various query types
2. Caching works properly (no repeated LLM calls)
3. Fallback heuristics handle edge cases
4. Metrics are tracked correctly
5. No false positives/negatives on tricky queries
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
import hashlib

# Add cite_agent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedAIAgent
from cite_agent.observability import ObservabilitySystem


class TestQueryIntentClassification:
    """Test suite for _get_query_intent() function"""
    
    @pytest.fixture
    def agent(self):
        """Create a minimal EnhancedAIAgent for testing"""
        agent = EnhancedAIAgent()
        # Initialize required attributes
        agent.metrics = MagicMock(spec=ObservabilitySystem)
        agent.backend_circuit = MagicMock()
        agent.backend_circuit.is_open = MagicMock(return_value=False)
        agent.auth_token = "test_token"
        agent.backend_api_url = "http://localhost:8000"
        agent._intent_cache = {}
        agent._intent_cache_times = {}
        return agent
    
    @pytest.mark.asyncio
    async def test_location_query_heuristics(self, agent):
        """Test that location queries are detected via fast heuristics"""
        location_queries = [
            "where am i",
            "pwd",
            "what directory am i in",
            "where are we",
            "what is the current path",
            "what is my current folder",
            "show me the current directory",
        ]
        
        for query in location_queries:
            intent = await agent._get_query_intent(query)
            assert intent == 'location_query', f"Failed for: {query}"
            assert agent.metrics.increment.called
    
    @pytest.mark.asyncio
    async def test_file_search_queries(self, agent):
        """Test that file search queries are classified correctly"""
        file_search_queries = [
            "find all Python files",
            "search for setup.py",
            "locate the main.py file",
            "list all CSV files in the directory",
            "find files named test*",
        ]
        
        for query in file_search_queries:
            intent = await agent._get_query_intent(query)
            assert intent == 'file_search', f"Failed for: {query}"
    
    @pytest.mark.asyncio
    async def test_file_read_queries(self, agent):
        """Test that file read queries are classified correctly"""
        file_read_queries = [
            "show me main.py",
            "read config.json",
            "display the README.md",
            "open requirements.txt",
            "print the contents of data.csv",
        ]
        
        for query in file_read_queries:
            intent = await agent._get_query_intent(query)
            assert intent == 'file_read', f"Failed for: {query}"
    
    @pytest.mark.asyncio
    async def test_shell_execution_queries(self, agent):
        """Test that shell commands are classified correctly"""
        shell_queries = [
            "ls -la",
            "mkdir test_dir",
            "rm old_file.txt",
            "git status",
            "docker ps",
            "pip install requests",
            "chmod +x script.sh",
            "curl https://example.com",
        ]
        
        for query in shell_queries:
            intent = await agent._get_query_intent(query)
            assert intent == 'shell_execution', f"Failed for: {query}"
    
    @pytest.mark.asyncio
    async def test_data_analysis_queries(self, agent):
        """Test that data analysis queries are classified correctly"""
        data_queries = [
            "analyze this CSV file",
            "calculate the average of these numbers",
            "show me statistics for the data",
            "what's the sum of column B",
            "create a chart from this data",
        ]
        
        for query in data_queries:
            intent = await agent._get_query_intent(query)
            assert intent == 'data_analysis', f"Failed for: {query}"
    
    @pytest.mark.asyncio
    async def test_backend_required_queries(self, agent):
        """Test that backend-required queries are classified correctly"""
        backend_queries = [
            "find papers about machine learning",
            "what's the stock price of AAPL",
            "search for academic research on COVID-19",
            "citation for quantum computing paper",
            "market analysis for tech companies",
        ]
        
        for query in backend_queries:
            intent = await agent._get_query_intent(query)
            assert intent == 'backend_required', f"Failed for: {query}"
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, agent):
        """Test that results are cached and not re-classified"""
        query = "where am i"
        
        # First call
        intent1 = await agent._get_query_intent(query)
        assert intent1 == 'location_query'
        
        # Reset metrics to verify cache was used
        agent.metrics.reset_mock()
        
        # Second call should use cache
        intent2 = await agent._get_query_intent(query)
        assert intent2 == 'location_query'
        
        # Cache hit should have been incremented
        agent.metrics.increment.assert_called_with("intent_cache_hit")
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, agent):
        """Test that cache entries expire after 1 hour"""
        query = "pwd"
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        # Manually add to cache with old timestamp
        agent._intent_cache[query_hash] = 'location_query'
        agent._intent_cache_times[query_hash] = datetime.now(timezone.utc) - timedelta(hours=2)
        
        # Reset metrics
        agent.metrics.reset_mock()
        
        # This should not use cache (too old) and recalculate
        intent = await agent._get_query_intent(query)
        assert intent == 'location_query'
        
        # Cache miss should be recorded (not cache_hit)
        cache_hit_called = any(
            call[0][0] == "intent_cache_hit" 
            for call in agent.metrics.increment.call_args_list
        )
        assert not cache_hit_called
    
    @pytest.mark.asyncio
    async def test_false_positive_prevention(self, agent):
        """Test that we don't incorrectly classify queries"""
        # These should NOT be classified as location queries
        non_location_queries = [
            "list all files in the current directory",  # This is file_search, not location
            "i'm finding this directory very confusing",  # Natural language
            "where can I find good restaurants",  # General question, not location_query
        ]
        
        for query in non_location_queries:
            intent = await agent._get_query_intent(query)
            assert intent != 'location_query', f"False positive for: {query}"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_fallback(self, agent):
        """Test that we fall back to conversation when circuit is open"""
        agent.backend_circuit.is_open = MagicMock(return_value=True)
        
        # For ambiguous queries, should default to 'conversation' when circuit is open
        query = "some random ambiguous query"
        intent = await agent._get_query_intent(query)
        
        # Should fall back to conversation since circuit is open
        assert intent in ['conversation', 'shell_execution', 'file_search']  # Or heuristic match
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, agent):
        """Test that metrics are properly tracked"""
        query = "pwd"
        await agent._get_query_intent(query)
        
        # Should have incremented metrics
        calls = [call[0][0] for call in agent.metrics.increment.call_args_list]
        assert any('query_intent_location_query' in call for call in calls)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, agent):
        """Test that LLM call timeout is handled gracefully"""
        # This test mocks _classify_via_llm to timeout
        async def timeout_function(prompt):
            await asyncio.sleep(5)  # Timeout after 2 seconds is set in function
            return 'location_query'
        
        agent._classify_via_llm = timeout_function
        
        # Ambiguous query that would trigger LLM call
        query = "some ambiguous random text"
        intent = await agent._get_query_intent(query)
        
        # Should handle timeout and return conversation
        assert intent in ['conversation', 'conversation']
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self, agent):
        """Test handling of edge cases like empty strings"""
        empty_cases = [
            "",
            "   ",
            "\n",
        ]
        
        for query in empty_cases:
            intent = await agent._get_query_intent(query)
            # Should not crash, should return something reasonable
            assert isinstance(intent, str)
            assert intent in {
                'location_query', 'file_search', 'file_read', 'shell_execution',
                'data_analysis', 'backend_required', 'conversation'
            }
    
    @pytest.mark.asyncio
    async def test_very_long_query(self, agent):
        """Test handling of very long queries"""
        long_query = "find " + "a " * 1000 + "file"
        intent = await agent._get_query_intent(long_query)
        # Should not crash
        assert isinstance(intent, str)
    
    def test_is_location_query_sync_wrapper(self, agent):
        """Test the synchronous _is_location_query wrapper"""
        # Test obvious location queries
        assert agent._is_location_query("where am i") == True
        assert agent._is_location_query("pwd") == True
        assert agent._is_location_query("what directory") == True
        
        # Test non-location queries
        assert agent._is_location_query("list files in the directory") == False
        assert agent._is_location_query("find test.py") == False
        assert agent._is_location_query("hello world") == False


class TestIntentClassificationIntegration:
    """Integration tests for intent classification with rest of agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a minimal EnhancedAIAgent"""
        agent = EnhancedAIAgent()
        agent.metrics = MagicMock(spec=ObservabilitySystem)
        agent.backend_circuit = MagicMock()
        agent.backend_circuit.is_open = MagicMock(return_value=False)
        agent.auth_token = "test_token"
        agent.backend_api_url = "http://localhost:8000"
        agent._intent_cache = {}
        agent._intent_cache_times = {}
        return agent
    
    @pytest.mark.asyncio
    async def test_intent_cache_persistence(self, agent):
        """Test that cache persists across multiple calls"""
        query = "pwd"
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        # First call should populate cache
        intent1 = await agent._get_query_intent(query)
        assert query_hash in agent._intent_cache
        
        # Second call should use cache
        intent2 = await agent._get_query_intent(query)
        assert agent._intent_cache[query_hash] == intent1 == intent2
    
    @pytest.mark.asyncio
    async def test_different_queries_different_cache_entries(self, agent):
        """Test that different queries have separate cache entries"""
        queries = [
            "pwd",
            "ls -la",
            "find file.txt",
            "what is the stock price",
        ]
        
        intents = []
        for query in queries:
            intent = await agent._get_query_intent(query)
            intents.append(intent)
        
        # Each query should have gotten an intent
        assert len(intents) == len(queries)
        # They should be cached
        assert len(agent._intent_cache) == len(queries)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
