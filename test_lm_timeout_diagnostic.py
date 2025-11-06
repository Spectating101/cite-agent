#!/usr/bin/env python3
"""
LLM Timeout Diagnostic
Test to understand where time is being spent:
1. Agent initialization time
2. Cerebras API response time
3. Network latency
"""

import asyncio
import time
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test_initialization_time():
    """Measure how long agent initialization takes"""
    print("\n⏱️  TEST 1: Agent Initialization Time")
    print("=" * 70)
    
    os.environ['NOCTURNAL_DEBUG'] = '0'
    
    start = time.time()
    agent = EnhancedNocturnalAgent()
    instantiation_time = time.time() - start
    print(f"  Instantiation: {instantiation_time:.2f}s")
    
    start = time.time()
    try:
        await asyncio.wait_for(agent.initialize(), timeout=20)
        init_time = time.time() - start
        print(f"  Initialization: {init_time:.2f}s ✅")
        return agent, True
    except asyncio.TimeoutError:
        init_time = time.time() - start
        print(f"  Initialization: {init_time:.2f}s ⏱️  TIMEOUT")
        return agent, False

async def test_simple_query(agent):
    """Test a simple query that requires LLM"""
    print("\n⏱️  TEST 2: Simple LLM Query")
    print("=" * 70)
    
    request = ChatRequest(
        question="What is 2+2?",
        user_id="test_user"
    )
    
    start = time.time()
    try:
        response = await asyncio.wait_for(
            agent.process_request(request),
            timeout=30
        )
        elapsed = time.time() - start
        print(f"  Response time: {elapsed:.2f}s ✅")
        print(f"  Response: {response.response[:100]}...")
        print(f"  Tools used: {response.tools_used}")
        return True, elapsed
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        print(f"  Response time: {elapsed:.2f}s ⏱️  TIMEOUT")
        return False, elapsed

async def test_cerebras_directly():
    """Test Cerebras API directly"""
    print("\n⏱️  TEST 3: Cerebras API Direct Call")
    print("=" * 70)
    
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        print("  ❌ CEREBRAS_API_KEY not set")
        return False, 0
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1"
        )
        
        start = time.time()
        response = client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=100,
            temperature=0.3
        )
        elapsed = time.time() - start
        print(f"  API response time: {elapsed:.2f}s ✅")
        print(f"  Response: {response.choices[0].message.content[:100]}...")
        return True, elapsed
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False, 0

async def test_backend_api():
    """Test if backend is working"""
    print("\n⏱️  TEST 4: Backend API Health")
    print("=" * 70)
    
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.get("http://127.0.0.1:8000/", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                elapsed = time.time() - start
                status = resp.status
                text = await resp.text()
                print(f"  Backend response: {elapsed:.2f}s")
                print(f"  Status: {status}")
                print(f"  Response: {text[:100]}...")
                return status == 200, elapsed
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False, 0

async def main():
    print("\n" + "=" * 70)
    print("🔍 LLM TIMEOUT DIAGNOSTIC")
    print("=" * 70)
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test backend first
    backend_ok, backend_time = await test_backend_api()
    
    # Test Cerebras directly
    cerebras_ok, cerebras_time = await test_cerebras_directly()
    
    # Test agent initialization
    agent, init_ok = await test_initialization_time()
    
    if init_ok:
        # Test simple query
        query_ok, query_time = await test_simple_query(agent)
    else:
        query_ok, query_time = False, 0
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(f"Backend health: {'✅ OK' if backend_ok else '❌ FAILED'} ({backend_time:.2f}s)")
    print(f"Cerebras API: {'✅ OK' if cerebras_ok else '❌ FAILED'} ({cerebras_time:.2f}s)")
    print(f"Agent initialization: {'✅ OK' if init_ok else '❌ TIMEOUT'}")
    print(f"Agent LLM query: {'✅ OK' if query_ok else '❌ TIMEOUT'} ({query_time:.2f}s)")
    
    print("\n🎯 FINDINGS:")
    if not backend_ok:
        print("  ❌ Backend not responding - check if it's running")
    if not cerebras_ok:
        print("  ❌ Cerebras API not responding - check API key or network")
    if not init_ok:
        print("  ❌ Agent initialization hangs - likely waiting for Cerebras during init")
    if not query_ok and init_ok:
        print("  ❌ Agent query times out - Cerebras API is slow or not responding")
    
    if backend_ok and cerebras_ok and init_ok and query_ok:
        print("  ✅ All systems operational - timeouts may be due to LLM provider load")

if __name__ == "__main__":
    asyncio.run(main())
