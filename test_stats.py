#!/usr/bin/env python3
import asyncio
import sys
import pandas as pd
import numpy as np
import os

sys.path.insert(0, '.')
os.environ['NOCTURNAL_DEBUG'] = '1'

import __main__
__main__.research_data = pd.DataFrame({
    'participant_id': range(1, 51),
    'age': np.random.randint(18, 65, 50),
})

print("Created research_data")

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    request = ChatRequest(
        question="Give me descriptive statistics for the research_data",
        conversation_id="test"
    )

    response = await agent.process_request(request)
    print(f"\nRESPONSE:\n{response.response}")

    await agent.close()

asyncio.run(test())
