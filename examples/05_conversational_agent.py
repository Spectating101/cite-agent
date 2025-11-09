#!/usr/bin/env python3
"""
Example 5: Conversational AI Agent

This example demonstrates how to:
- Use the agent in conversational mode
- Ask research questions and get AI-powered answers
- Maintain conversation context
- Get cited, verified responses
"""

import asyncio
from cite_agent import EnhancedNocturnalAgent, ChatRequest

async def main():
    """Conversational agent example"""

    # Initialize agent
    print("🚀 Initializing Cite-Agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    conversation_id = "example_conversation_001"
    user_id = "researcher_001"

    print("\n" + "="*60)
    print("💬 Conversational AI Agent - Example Queries")
    print("="*60)
    print()

    # Example queries that demonstrate different capabilities
    example_queries = [
        {
            "question": "What are the recent advances in transformer models for NLP?",
            "description": "Academic Research Query"
        },
        {
            "question": "What is Apple's revenue in the last quarter?",
            "description": "Financial Data Query"
        },
        {
            "question": "Is the boiling point of water 100°C at standard pressure?",
            "description": "Fact-Checking Query"
        },
        {
            "question": "Summarize the key findings from recent papers on climate change",
            "description": "Research Synthesis Query"
        }
    ]

    # Process each query
    for i, query_info in enumerate(example_queries, 1):
        question = query_info["question"]
        description = query_info["description"]

        print(f"[{i}] {description}")
        print(f"Q: {question}")
        print()

        # Create chat request
        request = ChatRequest(
            question=question,
            user_id=user_id,
            conversation_id=conversation_id
        )

        try:
            # Get response from agent
            response = await agent.process_request(request)

            # Display response
            print(f"A: {response.response[:300]}")
            if len(response.response) > 300:
                print("   ... (truncated)")
            print()

            # Show metadata
            if response.tools_used:
                print(f"   🔧 Tools used: {', '.join(response.tools_used)}")

            if response.confidence_score > 0:
                confidence_emoji = "🟢" if response.confidence_score > 0.8 else "🟡" if response.confidence_score > 0.5 else "🔴"
                print(f"   {confidence_emoji} Confidence: {response.confidence_score:.1%}")

            if response.reasoning_steps:
                print(f"   🧠 Reasoning steps: {len(response.reasoning_steps)}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")

        print("\n" + "-"*60 + "\n")

        # Small delay between queries
        if i < len(example_queries):
            await asyncio.sleep(1)

    # Example: Interactive mode simulation
    print("💡 For interactive mode, you can run:")
    print("   cite-agent   # Start interactive CLI")
    print()
    print("   Or in Python:")
    print("   while True:")
    print("       question = input('You: ')")
    print("       request = ChatRequest(question=question, user_id='...', conversation_id='...')")
    print("       response = await agent.process_request(request)")
    print("       print(f'Agent: {response.response}')")
    print()

    # Clean up
    await agent.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
