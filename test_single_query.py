#!/usr/bin/env python3
"""Test single query with debug output"""
import asyncio
import sys
import pandas as pd
import numpy as np
import os

sys.path.insert(0, '.')

# Set debug mode
os.environ['NOCTURNAL_DEBUG'] = '1'

# Create test data in __main__
import __main__
__main__.research_data = pd.DataFrame({
    'participant_id': range(1, 51),
    'age': np.random.randint(18, 65, 50),
    'treatment': np.random.choice(['Control', 'Drug'], 50),
    'blood_pressure': np.random.normal(120, 15, 50),
    'heart_rate': np.random.normal(75, 10, 50),
})

print("Created test dataset 'research_data'")

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    question = "What data do I have in my workspace?"
    print(f"\nQUESTION: {question}")
    print("="*70)

    request = ChatRequest(
        question=question,
        conversation_id="test"
    )

    response = await agent.process_request(request)

    print(f"\nRESPONSE:")
    print(response.response)

    await agent.close()

if __name__ == "__main__":
    asyncio.run(test())
