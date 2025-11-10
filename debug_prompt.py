#!/usr/bin/env python3
"""
Debug what system prompt is being generated
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent

async def check_prompt():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Check available tools
    tools_data = agent.get_available_tools()
    tools = tools_data.get("tools", {})
    print("=" * 70)
    print("AVAILABLE TOOLS:")
    print("=" * 70)
    for name, info in tools.items():
        print(f"\n{name}:")
        print(f"  Description: {info.get('description', 'N/A')}")
        print(f"  Use when: {info.get('use_when', 'N/A')}")
        print(f"  Methods: {len(info.get('methods', []))} methods")

    # Build a test system prompt
    request_analysis = {"apis": [], "analysis_mode": "quantitative"}
    memory_context = ""
    api_results = {}

    prompt = agent._build_system_prompt(request_analysis, memory_context, api_results)

    print("\n" + "=" * 70)
    print("SYSTEM PROMPT (first 2000 chars):")
    print("=" * 70)
    print(prompt[:2000])
    print("\n[...truncated...]")

    await agent.close()

if __name__ == "__main__":
    asyncio.run(check_prompt())
