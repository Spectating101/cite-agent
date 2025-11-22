import os
os.environ['NOCTURNAL_FUNCTION_CALLING'] = '1'

import asyncio
import tempfile
from pathlib import Path
from cite_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    
    print(f"✅ Agent initialized")
    print(f"   has tool_executor: {hasattr(agent, 'tool_executor')}")
    
    # Load data
    test_csv = Path(tempfile.gettempdir()) / 'fc_test.csv'
    test_csv.write_text('group,value\nA,10\nA,12\nB,8\nB,9\n')
    
    resp1 = await agent.process_request(ChatRequest(
        question=f'Load {test_csv}',
        user_id='test', conversation_id='fc'
    ))
    print(f"\n✅ Load complete: {resp1.tools_used}")
    
    # Check dataset state
    print("\n🔍 STATE AFTER LOAD:")
    print(f"   has tool_executor: {hasattr(agent, 'tool_executor')}")
    if hasattr(agent, 'tool_executor') and agent.tool_executor:
        print(f"   has _data_analyzer: {hasattr(agent.tool_executor, '_data_analyzer')}")
        if hasattr(agent.tool_executor, '_data_analyzer'):
            analyzer = agent.tool_executor._data_analyzer
            print(f"   has current_dataset: {hasattr(analyzer, 'current_dataset')}")
            if hasattr(analyzer, 'current_dataset') and analyzer.current_dataset is not None:
                print(f"   ✅ Dataset loaded: {analyzer.current_dataset.shape}")
    
    # Vague query
    resp2 = await agent.process_request(ChatRequest(
        question='which did better?',
        user_id='test', conversation_id='fc'
    ))
    print(f"\n✅ Compare: {resp2.tools_used}")
    print(f"   Response: {resp2.response[:200]}")
    
    await agent.close()

asyncio.run(test())
