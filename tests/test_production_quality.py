#!/usr/bin/env python3
"""
Production Quality Testing Framework
Tests for Cursor/Claude-level sophistication

This test suite measures:
1. Response quality (clarity, structure, completeness)
2. Error handling (graceful, user-friendly)
3. Formatting (scannable, consistent)
4. Intelligence (context awareness, anticipation)
5. Sophistication (reasoning, reflection)
"""

import asyncio
import re
from typing import Dict, Any, List
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


class QualityMetrics:
    """Measures response quality across multiple dimensions"""

    @staticmethod
    def assess_response_quality(response: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive quality assessment

        Returns:
        {
            'overall_score': 0.0-1.0,
            'clarity_score': 0.0-1.0,
            'structure_score': 0.0-1.0,
            'completeness_score': 0.0-1.0,
            'issues': [],
            'strengths': []
        }
        """
        issues = []
        strengths = []
        scores = {}

        # 1. Clarity - Is it easy to understand?
        clarity_score = QualityMetrics._assess_clarity(response, issues, strengths)
        scores['clarity'] = clarity_score

        # 2. Structure - Is it scannable and well-formatted?
        structure_score = QualityMetrics._assess_structure(response, issues, strengths)
        scores['structure'] = structure_score

        # 3. Completeness - Does it answer the question?
        completeness_score = QualityMetrics._assess_completeness(response, query, issues, strengths)
        scores['completeness'] = completeness_score

        # 4. Conciseness - Right amount of info?
        conciseness_score = QualityMetrics._assess_conciseness(response, query, issues, strengths)
        scores['conciseness'] = conciseness_score

        # 5. No technical errors exposed
        error_score = QualityMetrics._assess_error_handling(response, issues, strengths)
        scores['error_handling'] = error_score

        # Calculate overall score (weighted average)
        weights = {
            'clarity': 0.25,
            'structure': 0.20,
            'completeness': 0.30,
            'conciseness': 0.15,
            'error_handling': 0.10
        }

        overall_score = sum(scores[k] * weights[k] for k in weights)

        return {
            'overall_score': overall_score,
            'clarity_score': clarity_score,
            'structure_score': structure_score,
            'completeness_score': completeness_score,
            'conciseness_score': conciseness_score,
            'error_handling_score': error_score,
            'issues': issues,
            'strengths': strengths,
            'grade': QualityMetrics._score_to_grade(overall_score)
        }

    @staticmethod
    def _assess_clarity(response: str, issues: List[str], strengths: List[str]) -> float:
        """Score: Is the response clear and understandable?"""
        score = 1.0

        # Check for unclear phrases
        unclear_phrases = [
            'might be', 'could be', 'possibly', 'perhaps', 'maybe',
            'I think', 'I believe', 'seems like'
        ]
        unclear_count = sum(1 for phrase in unclear_phrases if phrase in response.lower())
        if unclear_count > 3:
            score -= 0.2
            issues.append(f"Too many uncertain phrases ({unclear_count})")

        # Check for jargon without explanation
        jargon = ['TLS_error', 'upstream', 'CERTIFICATE_VERIFY_FAILED', 'stack trace']
        jargon_count = sum(1 for term in jargon if term in response)
        if jargon_count > 0:
            score -= 0.4
            issues.append(f"Contains technical jargon without explanation")

        # Positive: Clear structure with headers/bullets
        if '•' in response or '- ' in response:
            strengths.append("Uses bullets for clarity")
            score += 0.1

        return min(1.0, max(0.0, score))

    @staticmethod
    def _assess_structure(response: str, issues: List[str], strengths: List[str]) -> float:
        """Score: Is the response well-structured and scannable?"""
        score = 0.5  # Start neutral

        # Positive: Uses formatting
        if '**' in response or '__' in response:
            score += 0.2
            strengths.append("Uses bold for emphasis")

        if '\n\n' in response:
            score += 0.1
            strengths.append("Uses paragraphs for readability")

        # Bullets or numbered lists
        if ('•' in response or '- ' in response or
            re.search(r'^\d+\.', response, re.MULTILINE)):
            score += 0.2
            strengths.append("Uses lists for structure")

        # Negative: Wall of text
        lines = response.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        if max_line_length > 200:
            score -= 0.2
            issues.append("Has very long lines (hard to scan)")

        # Negative: No structure at all
        if '\n' not in response and len(response) > 100:
            score -= 0.3
            issues.append("Wall of text with no structure")

        return min(1.0, max(0.0, score))

    @staticmethod
    def _assess_completeness(response: str, query: str, issues: List[str], strengths: List[str]) -> float:
        """Score: Does it answer the actual question?"""
        score = 0.7  # Assume mostly complete by default

        # Check if response is too short for complex query
        query_words = len(query.split())
        response_words = len(response.split())

        if query_words > 10 and response_words < 20:
            score -= 0.3
            issues.append("Response too brief for complex query")

        # Check for deflection phrases
        deflections = [
            "I don't have access",
            "I can't help with that",
            "I'm not sure",
            "Could you clarify",
            "I don't understand"
        ]

        has_deflection = any(phrase.lower() in response.lower() for phrase in deflections)
        if has_deflection and len(response.split()) < 30:
            score -= 0.2
            issues.append("Deflects without attempting to help")

        # Positive: Provides specific information
        has_specifics = (
            any(char.isdigit() for char in response) or  # Numbers/data
            '/' in response or  # Paths
            '.' in response  # File extensions or URLs
        )
        if has_specifics:
            score += 0.1
            strengths.append("Provides specific information")

        return min(1.0, max(0.0, score))

    @staticmethod
    def _assess_conciseness(response: str, query: str, issues: List[str], strengths: List[str]) -> float:
        """Score: Right amount of information?"""
        score = 1.0

        response_words = len(response.split())
        query_words = len(query.split())

        # Simple query shouldn't get essay response
        if query_words < 5 and response_words > 200:
            score -= 0.3
            issues.append("Too verbose for simple query")

        # Complex query needs detail
        if query_words > 15 and response_words < 50:
            score -= 0.2
            issues.append("Too brief for complex query")

        # Check for filler phrases
        fillers = [
            "Let me check", "I'll look into", "I'm going to",
            "First, let me", "Before I", "I should mention"
        ]
        filler_count = sum(1 for phrase in fillers if phrase.lower() in response.lower())
        if filler_count > 2:
            score -= 0.2
            issues.append("Too many filler phrases")

        return min(1.0, max(0.0, score))

    @staticmethod
    def _assess_error_handling(response: str, issues: List[str], strengths: List[str]) -> float:
        """Score: Graceful error handling (no technical exposure)?"""
        score = 1.0

        # Check for technical error messages
        error_indicators = [
            'ERROR:', 'Exception', 'Traceback', 'stack trace',
            'TLS_error', 'CERTIFICATE_VERIFY_FAILED',
            'upstream connect error', 'failed with status',
            '⚠️ I couldn\'t finish', 'language model call failed'
        ]

        for indicator in error_indicators:
            if indicator.lower() in response.lower():
                score = 0.0
                issues.append(f"Exposes technical error: {indicator}")
                break

        if score == 1.0:
            strengths.append("No technical errors exposed")

        return score

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'


async def test_graceful_error_handling():
    """Test: Errors should be user-friendly, never technical"""
    agent = EnhancedNocturnalAgent()

    # Force an error condition by using invalid API setup
    test_cases = [
        ChatRequest(
            question="Search for papers on quantum computing",
            user_id="test_user"
        ),
        ChatRequest(
            question="Get Tesla revenue",
            user_id="test_user"
        )
    ]

    for request in test_cases:
        response = await agent.process_request(request)

        # Check: No technical errors exposed
        technical_errors = [
            'TLS_error', 'CERTIFICATE_VERIFY_FAILED', 'upstream',
            'Exception', 'Traceback', 'stack trace'
        ]

        for error in technical_errors:
            assert error not in response.response, \
                f"FAIL: Technical error exposed: {error}"

        # Check: Response should be friendly
        assert len(response.response) > 0, "FAIL: Empty response"
        assert response.response[0].isupper(), "FAIL: Should start with capital"

        print(f"✓ Graceful error handling for: {request.question[:50]}")


async def test_response_formatting():
    """Test: Responses should be well-formatted and scannable"""
    agent = EnhancedNocturnalAgent()

    test_cases = [
        (
            "List Python files in this directory",
            ['file', 'python', '.py']  # Expected content
        ),
        (
            "What's the current directory?",
            ['directory', 'current']
        ),
        (
            "Find files with test in the name",
            ['test', 'file']
        )
    ]

    for query, expected_content in test_cases:
        request = ChatRequest(question=query, user_id="test_user")
        response = await agent.process_request(request)

        # Assess quality
        quality = QualityMetrics.assess_response_quality(
            response.response, query, {}
        )

        print(f"\nQuery: {query}")
        print(f"Response: {response.response[:200]}...")
        print(f"Quality Score: {quality['overall_score']:.2f} (Grade: {quality['grade']})")
        print(f"Issues: {quality['issues']}")
        print(f"Strengths: {quality['strengths']}")

        # Should score at least C (0.7+)
        assert quality['overall_score'] >= 0.7, \
            f"FAIL: Quality too low ({quality['overall_score']:.2f})\nIssues: {quality['issues']}"

        print(f"✓ Quality check passed for: {query}")



async def test_response_completeness():
    """Test: Responses should actually answer the question"""
    agent = EnhancedNocturnalAgent()

    test_cases = [
        (
            "What Python files are in this directory?",
            lambda r: '.py' in r.lower() or 'python' in r.lower()
        ),
        (
            "Where am I?",
            lambda r: '/' in r  # Should contain a path
        ),
        (
            "List test files",
            lambda r: 'test' in r.lower()
        )
    ]

    for query, check_fn in test_cases:
        request = ChatRequest(question=query, user_id="test_user")
        response = await agent.process_request(request)

        # Check completeness
        assert check_fn(response.response), \
            f"FAIL: Response doesn't answer '{query}'\nGot: {response.response[:200]}"

        # Check it's not just an error message
        assert len(response.response.split()) >= 5, \
            f"FAIL: Response too brief for '{query}'"

        print(f"✓ Completeness check passed for: {query}")



async def test_no_technical_jargon():
    """Test: No technical jargon in user-facing responses"""
    agent = EnhancedNocturnalAgent()

    test_cases = [
        "Hey there",
        "Thanks!",
        "What files are here?",
        "Where am I?"
    ]

    for query in test_cases:
        request = ChatRequest(question=query, user_id="test_user")
        response = await agent.process_request(request)

        # Check for technical terms that shouldn't be in responses
        forbidden_terms = [
            'api_results', 'shell_info', 'execution_results',
            'tokens_used', 'confidence_score', 'reasoning_steps',
            'LLM', 'prompt', 'embedding', 'vector'
        ]

        for term in forbidden_terms:
            assert term not in response.response, \
                f"FAIL: Technical term '{term}' in response to '{query}'"

        print(f"✓ No jargon in response to: {query}")



async def test_consistency_across_runs():
    """Test: Same query should get consistent quality"""
    agent = EnhancedNocturnalAgent()

    query = "List files in current directory"

    # Run same query 3 times
    responses = []
    qualities = []

    for i in range(3):
        request = ChatRequest(question=query, user_id=f"test_user_{i}")
        response = await agent.process_request(request)

        quality = QualityMetrics.assess_response_quality(
            response.response, query, {}
        )

        responses.append(response.response)
        qualities.append(quality['overall_score'])

        print(f"Run {i+1}: Quality = {quality['overall_score']:.2f}")

    # Check variance
    avg_quality = sum(qualities) / len(qualities)
    variance = sum((q - avg_quality) ** 2 for q in qualities) / len(qualities)
    std_dev = variance ** 0.5

    print(f"\nAverage Quality: {avg_quality:.2f}")
    print(f"Standard Deviation: {std_dev:.2f}")

    # Variance should be low (< 0.15)
    assert std_dev < 0.15, \
        f"FAIL: Too much variance in quality ({std_dev:.2f})"

    # Average should be good (>= 0.7)
    assert avg_quality >= 0.7, \
        f"FAIL: Average quality too low ({avg_quality:.2f})"

    print("✓ Consistency check passed")


def run_quality_assessment():
    """Run comprehensive quality assessment"""
    print("=" * 80)
    print("PRODUCTION QUALITY ASSESSMENT")
    print("=" * 80)

    # Run all tests
    asyncio.run(test_graceful_error_handling())
    asyncio.run(test_response_formatting())
    asyncio.run(test_response_completeness())
    asyncio.run(test_no_technical_jargon())
    asyncio.run(test_consistency_across_runs())

    print("\n" + "=" * 80)
    print("QUALITY ASSESSMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_quality_assessment()
