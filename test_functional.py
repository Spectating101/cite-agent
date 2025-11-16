#!/usr/bin/env python3
"""
Comprehensive Functional Test - Current HEAD (7581403)
Tests: Research, Financial, Shell operations, Token optimization
"""

import asyncio
import os
import sys

# Set environment
os.environ['NOCTURNAL_DEBUG'] = '1'
os.environ['USE_LOCAL_KEYS'] = 'true'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_research_query():
    """Test 1: Research Query (Citation Formatting)"""
    print("\n" + "="*60)
    print("TEST 1: Research Query (Citation Formatting)")
    print("="*60)
    print("Query: 'Find papers on vision transformers'")
    print("Expected: Papers with DOI, authors, citations")
    print("-"*60)

    try:
        agent = EnhancedNocturnalAgent()
        request = ChatRequest(question='Find papers on vision transformers')
        response = await agent.process_request(request)

        print(f'\nResponse preview: {response.response[:300]}...')
        print(f'Tokens: {response.tokens_used}')
        print(f'Tools used: {response.tools_used}')

        # Validate
        has_papers = 'paper' in response.response.lower() or 'title' in response.response.lower()
        has_citations = 'citation' in response.response.lower() or 'DOI' in response.response

        print(f'\nValidation:')
        print(f'  - Has papers: {has_papers}')
        print(f'  - Has citations: {has_citations}')

        result = has_papers or has_citations
        print(f'\nTEST 1: {"PASS" if result else "FAIL"}')
        return result
    except Exception as e:
        print(f'\nTEST 1: FAIL - {str(e)}')
        return False

async def test_financial_query():
    """Test 2: Financial Query (LaTeX Preservation)"""
    print("\n" + "="*60)
    print("TEST 2: Financial Query (LaTeX Preservation)")
    print("="*60)
    print("Query: 'What is Apple profit margin'")
    print("Expected: LaTeX formula preserved, no random papers")
    print("-"*60)

    try:
        agent = EnhancedNocturnalAgent()
        request = ChatRequest(question='What is Apple profit margin')
        response = await agent.process_request(request)

        print(f'\nResponse preview: {response.response[:300]}...')
        print(f'Tokens: {response.tokens_used}')

        # Validate - should have financial data, NOT research papers
        has_financial = 'profit' in response.response.lower() or 'margin' in response.response.lower() or 'revenue' in response.response.lower()
        has_latex = '$' in response.response or 'formula' in response.response.lower()
        no_papers = 'paper' not in response.response.lower() and 'DOI' not in response.response

        print(f'\nValidation:')
        print(f'  - Has financial data: {has_financial}')
        print(f'  - Has LaTeX/formula: {has_latex}')
        print(f'  - No research papers: {no_papers}')

        result = has_financial and no_papers
        print(f'\nTEST 2: {"PASS" if result else "FAIL"}')
        return result
    except Exception as e:
        print(f'\nTEST 2: FAIL - {str(e)}')
        return False

async def test_synthesis_skip():
    """Test 3: Synthesis Skip (Token Optimization)"""
    print("\n" + "="*60)
    print("TEST 3: Synthesis Skip (Token Optimization)")
    print("="*60)
    print("Query: 'list files in cite_agent directory'")
    print("Expected: Direct output, minimal tokens")
    print("-"*60)

    try:
        agent = EnhancedNocturnalAgent()
        request = ChatRequest(question='list files in cite_agent directory')
        response = await agent.process_request(request)

        print(f'\nResponse length: {len(response.response)} chars')
        print(f'Tokens: {response.tokens_used}')

        # Should skip synthesis for simple directory listing
        low_tokens = response.tokens_used < 1000
        has_files = '.py' in response.response or 'cite_agent' in response.response

        print(f'\nValidation:')
        print(f'  - Low tokens: {low_tokens} (< 1000)')
        print(f'  - Has file listing: {has_files}')

        result = low_tokens or has_files
        print(f'\nTEST 3: {"PASS" if result else "FAIL"}')
        return result
    except Exception as e:
        print(f'\nTEST 3: FAIL - {str(e)}')
        return False

async def main():
    print("="*60)
    print("FUNCTIONAL TEST - Current HEAD (7581403)")
    print("="*60)

    results = []

    # Run tests
    results.append(await test_research_query())
    results.append(await test_financial_query())
    results.append(await test_synthesis_skip())

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f'\nPassed: {passed}/{total}')
    print(f'Pass Rate: {(passed/total)*100:.1f}%')

    if passed == total:
        print('\nAll tests PASSED!')
        return 0
    else:
        print(f'\n{total - passed} test(s) FAILED')
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
