#!/usr/bin/env python3
"""
Real Professor Research Session Test
Tests multi-turn conversation with context retention
"""
import asyncio
import os
os.environ['USE_LOCAL_KEYS'] = 'true'
os.environ['CEREBRAS_API_KEY'] = 'csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj'

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def professor_research_session():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print('\n' + '='*80)
    print('PROFESSOR RESEARCH SESSION - Testing Real Research Workflow')
    print('='*80 + '\n')

    # Turn 1: Literature review on a specific topic
    print('\n--- TURN 1: Initial Literature Review ---')
    print('Query: Find me recent papers on attention mechanisms in transformers, specifically papers that address computational efficiency\n')
    req1 = ChatRequest(
        question='Find me recent papers on attention mechanisms in transformers, specifically papers that address computational efficiency',
        user_id='professor'
    )
    resp1 = await agent.process_request(req1)
    print(f'Response: {resp1.response[:800]}...')
    print(f'Tokens: {resp1.tokens_used}\n')

    # Turn 2: Deep dive on specific paper
    print('\n--- TURN 2: Deep Dive on Specific Finding ---')
    print('Query: Can you tell me more about the Linformer paper? What was their main contribution and how does it compare to standard transformers?\n')
    req2 = ChatRequest(
        question='Can you tell me more about the Linformer paper? What was their main contribution and how does it compare to standard transformers?',
        user_id='professor'
    )
    resp2 = await agent.process_request(req2)
    print(f'Response: {resp2.response[:800]}...')
    print(f'Tokens: {resp2.tokens_used}\n')

    # Turn 3: Related work comparison
    print('\n--- TURN 3: Comparative Analysis ---')
    print('Query: How does Linformer compare to other efficient attention mechanisms like Reformer or Performer in terms of complexity?\n')
    req3 = ChatRequest(
        question='How does Linformer compare to other efficient attention mechanisms like Reformer or Performer in terms of complexity?',
        user_id='professor'
    )
    resp3 = await agent.process_request(req3)
    print(f'Response: {resp3.response[:800]}...')
    print(f'Tokens: {resp3.tokens_used}\n')

    # Turn 4: Research gap identification
    print('\n--- TURN 4: Research Gap Identification ---')
    print('Query: Based on these papers, what are the current limitations or open problems in efficient transformer architectures?\n')
    req4 = ChatRequest(
        question='Based on these papers, what are the current limitations or open problems in efficient transformer architectures?',
        user_id='professor'
    )
    resp4 = await agent.process_request(req4)
    print(f'Response: {resp4.response[:800]}...')
    print(f'Tokens: {resp4.tokens_used}\n')

    # Turn 5: Citation count for impact assessment
    print('\n--- TURN 5: Impact Assessment ---')
    print('Query: Which of these efficient transformer papers has the highest citation count? I need to cite the most influential work\n')
    req5 = ChatRequest(
        question='Which of these efficient transformer papers has the highest citation count? I need to cite the most influential work',
        user_id='professor'
    )
    resp5 = await agent.process_request(req5)
    print(f'Response: {resp5.response[:800]}...')
    print(f'Tokens: {resp5.tokens_used}\n')

    total_tokens = resp1.tokens_used + resp2.tokens_used + resp3.tokens_used + resp4.tokens_used + resp5.tokens_used

    print('\n' + '='*80)
    print('SESSION SUMMARY')
    print('='*80)
    print(f'Total turns: 5')
    print(f'Total tokens: {total_tokens:,}')
    print(f'Average per turn: {total_tokens/5:.0f}')

    # Check context retention
    has_context = 'linformer' in resp3.response.lower() or 'linear' in resp3.response.lower()
    print(f'Context maintained: {"YES" if has_context else "NO - Lost conversation history"}')

    # Check quality markers
    has_real_papers = any(year in resp1.response for year in ['2017', '2018', '2019', '2020', '2021', '2022', '2023'])
    has_citations = 'citation' in resp5.response.lower() or 'cited' in resp5.response.lower()

    print(f'Real papers cited: {"YES" if has_real_papers else "NO - May be hallucinating"}')
    print(f'Citation analysis: {"YES" if has_citations else "NO - Missing impact metrics"}')

    print('\n' + '='*80)

    await agent.close()

if __name__ == '__main__':
    asyncio.run(professor_research_session())
