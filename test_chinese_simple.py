#!/usr/bin/env python3
"""Simple Chinese test"""
import asyncio
import sys
import pandas as pd
import os

sys.path.insert(0, '.')
os.environ['NOCTURNAL_DEBUG'] = '1'

import __main__
__main__.research_data = pd.DataFrame({'age': [25, 30, 35]})

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    print("\n" + "="*70)
    print("TEST: Chinese query")
    print("="*70)

    request = ChatRequest(
        question="我的工作空間有什麼數據？",  # What data is in my workspace?
        conversation_id="test"
    )

    print(f"Sending query: {request.question}")
    response = await agent.process_request(request)

    print(f"\nResponse: {response.response}")
    print(f"Tools used: {response.tools_used}")

    await agent.close()

asyncio.run(test())
