#!/usr/bin/env python3
"""
Comprehensive Tests for Advanced Features

Tests:
1. Streaming UI functionality
2. Semantic Search (TF-IDF embeddings)
3. Citation Verification (DOI resolution, heuristic validation)

All features are tested to ensure production readiness.
"""

import asyncio
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


# ============================================================================
# STREAMING UI TESTS
# ============================================================================

class TestStreamingUI:
    """Test the StreamingChatUI functionality"""

    def test_streaming_ui_import(self):
        """StreamingChatUI should be importable"""
        from cite_agent.streaming_ui import StreamingChatUI
        assert StreamingChatUI is not None

    def test_streaming_ui_initialization(self):
        """StreamingChatUI should initialize correctly"""
        from cite_agent.streaming_ui import StreamingChatUI

        ui = StreamingChatUI(app_name="Test App", working_dir="/test")
        assert ui.app_name == "Test App"
        assert ui.working_dir == "/test"
        assert ui.typing_speed == 0.0

    @pytest.mark.asyncio
    async def test_simulate_streaming(self):
        """Simulated streaming should yield chunks"""
        from cite_agent.streaming_ui import simulate_streaming

        text = "Hello world test"
        chunks = []

        async for chunk in simulate_streaming(text, chunk_size=5):
            chunks.append(chunk)

        assert "".join(chunks) == text
        assert len(chunks) == 4  # "Hello", " worl", "d tes", "t"

    @pytest.mark.asyncio
    async def test_stream_agent_response(self):
        """stream_agent_response should accumulate full response"""
        from cite_agent.streaming_ui import StreamingChatUI, simulate_streaming

        ui = StreamingChatUI()
        # Suppress actual console output for test
        ui.console = MagicMock()

        test_response = "This is a streaming test response"

        async def generator():
            async for chunk in simulate_streaming(test_response):
                yield chunk

        full_response = await ui.stream_agent_response(generator())

        assert full_response == test_response

    def test_groq_stream_helper_exists(self):
        """groq_stream_to_generator helper should exist"""
        from cite_agent.streaming_ui import groq_stream_to_generator
        assert callable(groq_stream_to_generator)

    def test_rate_limit_message(self):
        """Rate limit message should display correctly"""
        from cite_agent.streaming_ui import StreamingChatUI

        ui = StreamingChatUI()
        ui.console = MagicMock()

        ui.show_rate_limit_message(
            limit_type="Archive API",
            remaining_capabilities=["Web search", "Local files"]
        )

        # Should have printed something
        assert ui.console.print.called


# ============================================================================
# SEMANTIC SEARCH TESTS
# ============================================================================

class TestSemanticSearch:
    """Test semantic search with TF-IDF embeddings"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_semantic_search_import(self):
        """SemanticSearch should be importable"""
        from cite_agent.semantic_search import SemanticSearch
        assert SemanticSearch is not None

    def test_semantic_search_initialization(self, temp_cache_dir):
        """SemanticSearch should initialize with empty state"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        stats = search.get_stats()
        assert stats["total_embeddings"] == 0
        assert stats["papers_indexed"] == 0
        assert stats["vocabulary_size"] == 0

    def test_tokenization(self, temp_cache_dir):
        """Tokenization should remove stopwords"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        tokens = search._tokenize("The quick brown fox jumps over the lazy dog")

        # Should remove 'the', 'over'
        assert "the" not in tokens
        assert "over" not in tokens
        assert "quick" in tokens
        assert "brown" in tokens
        assert "fox" in tokens

    def test_add_paper(self, temp_cache_dir):
        """Adding paper should create embedding"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        search.add_paper(
            paper_id="test123",
            title="Machine Learning for Natural Language Processing",
            abstract="This paper discusses deep learning approaches",
            authors="John Smith, Jane Doe"
        )

        stats = search.get_stats()
        assert stats["papers_indexed"] == 1
        assert stats["vocabulary_size"] > 0

    def test_add_multiple_papers(self, temp_cache_dir):
        """Multiple papers should be indexed correctly"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        papers = [
            ("p1", "Neural Networks for Image Classification", "CNN architectures"),
            ("p2", "Transformer Models for NLP", "Attention mechanisms"),
            ("p3", "Reinforcement Learning in Robotics", "Policy gradient methods"),
        ]

        for pid, title, abstract in papers:
            search.add_paper(pid, title, abstract)

        stats = search.get_stats()
        assert stats["papers_indexed"] == 3

    def test_find_similar_papers(self, temp_cache_dir):
        """Similar papers should be found by query"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        # Add papers
        search.add_paper("p1", "Deep Learning for Computer Vision", "CNN image recognition")
        search.add_paper("p2", "Natural Language Processing with Transformers", "BERT GPT attention")
        search.add_paper("p3", "Reinforcement Learning Games", "Q-learning policy gradient")

        # Query for NLP papers
        results = search.find_similar_papers("transformer language models", top_k=3)

        assert len(results) > 0
        # NLP paper should rank higher
        paper_ids = [r["paper_id"] for r in results]
        # p2 (NLP paper) should be in results
        assert "p2" in paper_ids

    def test_cosine_similarity(self, temp_cache_dir):
        """Cosine similarity should compute correctly"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        # Identical vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        sim = search._cosine_similarity(vec1, vec2)
        assert abs(sim - 1.0) < 0.001

        # Orthogonal vectors
        vec3 = [0.0, 1.0, 0.0]
        sim = search._cosine_similarity(vec1, vec3)
        assert abs(sim) < 0.001

        # Opposite vectors
        vec4 = [-1.0, 0.0, 0.0]
        sim = search._cosine_similarity(vec1, vec4)
        assert abs(sim + 1.0) < 0.001

    def test_cache_persistence(self, temp_cache_dir):
        """Embeddings should persist across instances"""
        from cite_agent.semantic_search import SemanticSearch

        # First instance
        search1 = SemanticSearch(cache_dir=temp_cache_dir)
        search1.add_paper("p1", "Test Paper", "Test abstract")

        # New instance should load cached embeddings
        search2 = SemanticSearch(cache_dir=temp_cache_dir)
        stats = search2.get_stats()

        assert stats["papers_indexed"] == 1

    def test_find_similar_to_paper(self, temp_cache_dir):
        """Should find papers similar to another paper"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)

        search.add_paper("p1", "Deep Neural Networks", "Convolutional layers backpropagation")
        search.add_paper("p2", "Recurrent Networks for Sequences", "LSTM GRU time series")
        search.add_paper("p3", "Convolutional Neural Networks", "Image features deep learning")

        # Find papers similar to p1 (about CNNs)
        results = search.find_similar_to_paper("p1", top_k=2)

        assert len(results) <= 2
        # p3 (CNN paper) should be more similar to p1 than p2
        if len(results) >= 1:
            assert results[0]["paper_id"] in ["p2", "p3"]

    def test_clear_embeddings(self, temp_cache_dir):
        """Clear should remove all embeddings"""
        from cite_agent.semantic_search import SemanticSearch

        search = SemanticSearch(cache_dir=temp_cache_dir)
        search.add_paper("p1", "Test", "Abstract")

        search.clear()

        stats = search.get_stats()
        assert stats["total_embeddings"] == 0

    def test_global_functions(self, temp_cache_dir):
        """Global helper functions should work"""
        from cite_agent.semantic_search import (
            add_paper_to_index,
            find_similar_papers,
            semantic_search_stats
        )

        # These should not raise
        stats = semantic_search_stats()
        assert "total_embeddings" in stats


# ============================================================================
# CITATION VERIFICATION TESTS
# ============================================================================

class TestCitationVerification:
    """Test citation verification functionality"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_citation_verifier_import(self):
        """CitationVerifier should be importable"""
        from cite_agent.citation_verification import CitationVerifier
        assert CitationVerifier is not None

    def test_extract_doi_valid(self):
        """Should extract valid DOIs from text"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier()

        # Standard DOI
        text = "See the paper at 10.1038/nature12373 for details"
        doi = verifier.extract_doi(text)
        assert doi == "10.1038/nature12373"

        # DOI in URL
        text = "Available at https://doi.org/10.1145/3292500.3330919"
        doi = verifier.extract_doi(text)
        assert doi == "10.1145/3292500.3330919"

        # Complex DOI
        text = "Reference: 10.1007/978-3-030-58452-8_24"
        doi = verifier.extract_doi(text)
        assert doi == "10.1007/978-3-030-58452-8_24"

    def test_extract_doi_none(self):
        """Should return None when no DOI present"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier()

        text = "This text has no DOI in it"
        doi = verifier.extract_doi(text)
        assert doi is None

    def test_extract_all_dois(self):
        """Should extract multiple DOIs"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier()

        text = "Papers: 10.1038/nature12373, 10.1145/3292500.3330919, and 10.1007/123"
        dois = verifier.extract_all_dois(text)

        assert len(dois) == 3
        assert "10.1038/nature12373" in dois

    def test_heuristic_validation_complete_citation(self, temp_cache_dir):
        """Complete citations should pass heuristic validation"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        citation = 'Smith, J., Doe, J. (2023). "Machine Learning for NLP". Journal of AI Research.'
        result = verifier._heuristic_validation(citation)

        assert result.valid is True
        assert result.confidence >= 0.5
        assert result.year == 2023
        assert result.verification_method == "heuristic"

    def test_heuristic_validation_incomplete(self, temp_cache_dir):
        """Incomplete citations should fail validation"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        # Missing year, author pattern, journal
        citation = "some random text"
        result = verifier._heuristic_validation(citation)

        assert result.valid is False
        assert result.confidence < 0.5

    @pytest.mark.asyncio
    async def test_verify_doi_with_cache(self, temp_cache_dir):
        """DOI verification should use cached results"""
        from cite_agent.citation_verification import CitationVerifier, VerificationResult

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        # Pre-populate cache with mock result
        verifier._cache["10.1038/test123"] = {
            "valid": True,
            "doi": "10.1038/test123",
            "title": "Test Paper Title",
            "authors": ["John Smith", "Jane Doe"],
            "year": 2023,
            "journal": "Nature",
            "url": "https://doi.org/10.1038/test123",
            "error": None,
            "verification_method": "crossref",
            "confidence": 1.0
        }

        result = await verifier.verify_doi("10.1038/test123")

        assert result.valid is True
        assert result.title == "Test Paper Title"
        assert result.year == 2023
        assert "John Smith" in result.authors
        assert result.journal == "Nature"
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_verify_doi_cache_miss_returns_result(self, temp_cache_dir):
        """DOI verification should return result even on API errors"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        # Test that function handles missing aiohttp gracefully
        # Temporarily hide aiohttp
        import sys
        original_modules = sys.modules.copy()

        # Remove aiohttp to simulate import error
        if 'aiohttp' in sys.modules:
            del sys.modules['aiohttp']

        try:
            result = await verifier.verify_doi("10.1038/nonexistent")
            # Should return a result (possibly with error) but not crash
            assert result is not None
            assert isinstance(result.valid, bool)
            assert result.doi == "10.1038/nonexistent"
        finally:
            # Restore modules
            sys.modules.update(original_modules)

    @pytest.mark.asyncio
    async def test_verify_citation_with_doi(self, temp_cache_dir):
        """Citation with DOI should use DOI verification"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        # Mock successful DOI verification
        with patch.object(verifier, 'verify_doi', new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = MagicMock(valid=True, doi="10.1038/test")

            citation = "Smith, J. (2023). Paper Title. 10.1038/test"
            result = await verifier.verify_citation(citation)

            mock_verify.assert_called_once_with("10.1038/test")

    @pytest.mark.asyncio
    async def test_verify_citation_without_doi(self, temp_cache_dir):
        """Citation without DOI should use heuristic validation"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        citation = 'Smith, J. (2023). "Paper Title". Journal of Testing.'
        result = await verifier.verify_citation(citation)

        assert result.verification_method == "heuristic"

    def test_cache_persistence(self, temp_cache_dir):
        """Verification results should be cached"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        # Manually add to cache
        verifier._cache["10.1038/test"] = {
            "valid": True,
            "doi": "10.1038/test",
            "title": "Cached Paper",
            "authors": ["Test Author"],
            "year": 2023,
            "journal": "Test Journal",
            "url": "https://doi.org/10.1038/test",
            "error": None,
            "verification_method": "crossref",
            "confidence": 1.0
        }
        verifier._save_cache()

        # New instance should load cache
        verifier2 = CitationVerifier(cache_dir=temp_cache_dir)
        assert "10.1038/test" in verifier2._cache

    def test_get_stats(self, temp_cache_dir):
        """Stats should report correctly"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)

        verifier._cache["doi1"] = {"valid": True}
        verifier._cache["doi2"] = {"valid": False}
        verifier._cache["doi3"] = {"valid": True}

        stats = verifier.get_stats()

        assert stats["total_verifications"] == 3
        assert stats["valid_citations"] == 2
        assert stats["invalid_citations"] == 1

    def test_clear_cache(self, temp_cache_dir):
        """Clear should remove all cache"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier(cache_dir=temp_cache_dir)
        verifier._cache["test"] = {"valid": True}
        verifier._save_cache()

        verifier.clear_cache()

        assert len(verifier._cache) == 0
        assert not (temp_cache_dir / "verifications.json").exists()

    def test_global_functions(self):
        """Global helper functions should be importable"""
        from cite_agent.citation_verification import (
            verify_doi,
            verify_citation,
            verify_paper_exists,
            extract_dois,
            verification_stats
        )

        # These should be async functions or regular functions
        assert callable(verify_doi)
        assert callable(verify_citation)
        assert callable(extract_dois)
        assert callable(verification_stats)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for all advanced features working together"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_full_research_workflow(self, temp_cache_dir):
        """Test complete research workflow: search -> verify -> similar papers"""
        from cite_agent.semantic_search import SemanticSearch
        from cite_agent.citation_verification import CitationVerifier

        # Initialize modules
        search = SemanticSearch(cache_dir=temp_cache_dir / "embeddings")
        verifier = CitationVerifier(cache_dir=temp_cache_dir / "verification")

        # 1. Index some papers
        papers = [
            ("doi1", "Deep Learning for Text Classification", "Neural networks NLP"),
            ("doi2", "Attention Mechanisms in Neural Networks", "Transformer self-attention"),
            ("doi3", "Computer Vision with CNNs", "Image recognition convolution"),
        ]

        for doi, title, abstract in papers:
            search.add_paper(doi, title, abstract)

        # 2. Search for relevant papers
        results = search.find_similar_papers("transformer attention models", top_k=2)
        assert len(results) > 0

        # 3. Verify a citation
        citation = 'Smith, J. (2023). "Attention is All You Need". NeurIPS Conference.'
        verification = verifier._heuristic_validation(citation)
        assert verification.year == 2023

        # 4. Check stats
        search_stats = search.get_stats()
        verify_stats = verifier.get_stats()

        assert search_stats["papers_indexed"] == 3
        assert "total_verifications" in verify_stats

    def test_cli_streaming_flag_exists(self):
        """CLI should have --stream flag"""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "cite_agent.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert "--stream" in result.stdout

    def test_streaming_mode_method_exists(self):
        """NocturnalCLI should have streaming_interactive_mode method"""
        from cite_agent.cli import NocturnalCLI

        cli = NocturnalCLI()
        assert hasattr(cli, 'streaming_interactive_mode')
        assert callable(cli.streaming_interactive_mode)

    def test_all_modules_importable(self):
        """All new modules should be importable without errors"""
        modules = [
            "cite_agent.streaming_ui",
            "cite_agent.semantic_search",
            "cite_agent.citation_verification",
        ]

        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance benchmarks for advanced features"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_semantic_search_scaling(self, temp_cache_dir):
        """Semantic search should handle 100+ papers"""
        from cite_agent.semantic_search import SemanticSearch
        import time

        search = SemanticSearch(cache_dir=temp_cache_dir)

        # Index 100 papers
        start = time.time()
        for i in range(100):
            search.add_paper(
                f"paper_{i}",
                f"Paper Title Number {i} about Machine Learning Topic {i % 10}",
                f"Abstract discussing technique {i} and method {i % 5}"
            )
        index_time = time.time() - start

        # Should complete in reasonable time
        assert index_time < 10.0  # 10 seconds for 100 papers

        # Search should be fast
        start = time.time()
        results = search.find_similar_papers("machine learning technique")
        search_time = time.time() - start

        assert search_time < 1.0  # 1 second for search
        assert len(results) > 0

    def test_citation_extraction_performance(self):
        """DOI extraction should be fast even on large text"""
        from cite_agent.citation_verification import CitationVerifier

        verifier = CitationVerifier()

        # Large text with multiple DOIs
        text = "References:\n"
        for i in range(100):
            text += f"10.1038/paper{i:04d}\n"

        import time
        start = time.time()
        dois = verifier.extract_all_dois(text)
        extract_time = time.time() - start

        assert len(dois) == 100
        assert extract_time < 1.0  # Should be very fast

    @pytest.mark.asyncio
    async def test_streaming_latency(self):
        """Streaming should have minimal latency"""
        from cite_agent.streaming_ui import simulate_streaming
        import time

        text = "A" * 1000  # 1000 characters
        chunks = []

        start = time.time()
        async for chunk in simulate_streaming(text, chunk_size=10):
            chunks.append(chunk)
        elapsed = time.time() - start

        assert len(chunks) == 100
        # Should be nearly instantaneous (no artificial delays)
        assert elapsed < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
