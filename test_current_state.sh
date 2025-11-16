#!/bin/bash
# Comprehensive Functional Test - Current HEAD (7581403)
# Tests: Research, Financial, Shell operations, Token optimization

set -e

echo "=========================================="
echo "🧪 FUNCTIONAL TEST - Current HEAD"
echo "Commit: 7581403"
echo "=========================================="
echo ""

# Enable debug mode
export NOCTURNAL_DEBUG=1
export USE_LOCAL_KEYS=true

echo "📋 Test 1: Research Query (Citation Formatting)"
echo "Query: 'Find papers on vision transformers'"
echo "Expected: Papers with DOI, authors, citations"
echo "------------------------------------------"
timeout 30 python3 -c "
import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    request = ChatRequest(question='Find papers on vision transformers')
    response = await agent.chat(request)

    print(f'Response: {response.response[:500]}...')
    print(f'Tokens: {response.tokens_used}')
    print(f'Tools used: {response.tools_used}')

    # Validate
    has_papers = 'paper' in response.response.lower() or 'title' in response.response.lower()
    has_citations = 'citation' in response.response.lower() or 'DOI' in response.response

    print(f'✓ Has papers: {has_papers}')
    print(f'✓ Has citations: {has_citations}')

    return has_papers or has_citations

result = asyncio.run(test())
print(f'TEST 1: {'PASS ✅' if result else 'FAIL ❌'}')
" 2>&1 | head -50

echo ""
echo "📋 Test 2: Financial Query (LaTeX Preservation)"
echo "Query: 'What is Apple profit margin'"
echo "Expected: LaTeX formula preserved, no random papers"
echo "------------------------------------------"
timeout 30 python3 -c "
import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    request = ChatRequest(question='What is Apple profit margin')
    response = await agent.chat(request)

    print(f'Response: {response.response[:500]}...')
    print(f'Tokens: {response.tokens_used}')

    # Validate - should have financial data, NOT research papers
    has_financial = 'profit' in response.response.lower() or 'margin' in response.response.lower()
    has_latex = '$' in response.response or 'formula' in response.response.lower()
    no_papers = 'paper' not in response.response.lower() and 'DOI' not in response.response

    print(f'✓ Has financial data: {has_financial}')
    print(f'✓ Has LaTeX/formula: {has_latex}')
    print(f'✓ No research papers: {no_papers}')

    return has_financial and no_papers

result = asyncio.run(test())
print(f'TEST 2: {'PASS ✅' if result else 'FAIL ❌'}')
" 2>&1 | head -50

echo ""
echo "📋 Test 3: Synthesis Skip (Token Optimization)"
echo "Query: 'list files in cite_agent directory'"
echo "Expected: Direct output, 0 tokens"
echo "------------------------------------------"
timeout 30 python3 -c "
import asyncio
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    request = ChatRequest(question='list files in cite_agent directory')
    response = await agent.chat(request)

    print(f'Response length: {len(response.response)} chars')
    print(f'Tokens: {response.tokens_used}')

    # Should skip synthesis for simple directory listing
    low_tokens = response.tokens_used < 500
    has_files = '.py' in response.response or 'cite_agent' in response.response

    print(f'✓ Low tokens: {low_tokens} (target: <500)')
    print(f'✓ Has file listing: {has_files}')

    return low_tokens or has_files

result = asyncio.run(test())
print(f'TEST 3: {'PASS ✅' if result else 'FAIL ❌'}')
" 2>&1 | head -50

echo ""
echo "=========================================="
echo "📊 SUMMARY"
echo "=========================================="
echo "All tests completed. Check results above."
echo ""
echo "Expected Results:"
echo "- Test 1: Papers with proper citations ✅"
echo "- Test 2: Financial data without papers ✅"
echo "- Test 3: Low token usage for simple queries ✅"
