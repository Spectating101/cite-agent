#!/usr/bin/env python3
"""
End-to-end conversation test with actual LLM calls.
Tests if the LLM intelligently selects tools and reasons about results.

This uses LOCAL source code, not pip installed version.
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Use LOCAL source code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable function calling mode
os.environ["NOCTURNAL_FUNCTION_CALLING"] = "1"
os.environ["NOCTURNAL_DEBUG"] = "1"

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


async def run_conversation_tests():
    """Run comprehensive conversation tests with actual LLM."""

    print("=" * 70)
    print("CITE-AGENT END-TO-END LLM CONVERSATION TEST")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 70)

    # Initialize agent
    print("\n🚀 Initializing agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    print(f"✅ Agent initialized")
    print(f"   LLM Provider: {getattr(agent, 'llm_provider', 'unknown')}")
    print(f"   Model: gpt-oss-120b")

    # Track all interactions
    conversation_log = []

    test_cases = [
        # Test 1: Simple file listing (should call list_directory)
        {
            "name": "Simple File Listing",
            "query": "what files are here?",
            "expected_tool": "list_directory",
            "description": "Should call list_directory() to show files"
        },

        # Test 2: Conversational (should use chat tool or respond directly)
        {
            "name": "Conversational Query",
            "query": "thanks for that",
            "expected_tool": "chat",
            "description": "Should respond conversationally without file ops"
        },

        # Test 3: Fuzzy query (the real intelligence test)
        {
            "name": "Fuzzy Query - Find Data",
            "query": "I think there's some CSV data around here somewhere, can you check?",
            "expected_tool": "list_directory",
            "description": "Should browse and identify CSV files intelligently"
        },

        # Test 4: Data analysis request
        {
            "name": "Load Dataset",
            "query": "load the data/test_stats.csv file",
            "expected_tool": "load_dataset",
            "description": "Should load CSV and compute statistics"
        },

        # Test 5: Statistics query (should use already loaded data)
        {
            "name": "Statistics Query",
            "query": "what's the mean spread?",
            "expected_tool": "analyze_data",  # Should use loaded data
            "description": "Should report statistics from loaded data"
        },

        # Test 6: Academic research
        {
            "name": "Academic Paper Search",
            "query": "find papers on transformer neural networks",
            "expected_tool": "search_papers",
            "description": "Should search academic databases"
        },
    ]

    print("\n" + "=" * 70)
    print("RUNNING CONVERSATION TESTS")
    print("=" * 70)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['description']}")
        print()

        try:
            request = ChatRequest(
                question=test['query'],
                user_id="test_user",
                conversation_id="test_session"
            )

            response = await agent.process_request(request)

            # Log the interaction
            interaction = {
                "test_name": test['name'],
                "query": test['query'],
                "response": response.response,
                "tools_used": response.tools_used,
                "tokens_used": response.tokens_used,
                "confidence": response.confidence_score,
                "timestamp": response.timestamp
            }
            conversation_log.append(interaction)

            # Display results
            print(f"📥 Response ({len(response.response)} chars):")
            print("-" * 50)
            # Truncate very long responses
            if len(response.response) > 1000:
                print(response.response[:1000])
                print(f"\n... [truncated, {len(response.response)} chars total]")
            else:
                print(response.response)
            print("-" * 50)

            print(f"\n📊 Metrics:")
            print(f"   Tools used: {response.tools_used}")
            print(f"   Tokens used: {response.tokens_used}")
            print(f"   Confidence: {response.confidence_score}")

            # Check if expected tool was called
            if test['expected_tool']:
                if test['expected_tool'] in response.tools_used:
                    print(f"   ✅ Expected tool '{test['expected_tool']}' was called")
                else:
                    print(f"   ⚠️  Expected tool '{test['expected_tool']}' NOT called")
                    print(f"      Got: {response.tools_used}")

            # Check for errors
            if response.error_message:
                print(f"   ❌ Error: {response.error_message}")

            # Brief pause between queries
            await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

            conversation_log.append({
                "test_name": test['name'],
                "query": test['query'],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    # Save conversation log
    print("\n" + "=" * 70)
    print("SAVING CONVERSATION LOG")
    print("=" * 70)

    log_file = "conversation_test_results.json"
    with open(log_file, "w") as f:
        json.dump(conversation_log, f, indent=2, default=str)
    print(f"✅ Saved to {log_file}")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    successful = sum(1 for log in conversation_log if "error" not in log)
    print(f"Tests run: {len(test_cases)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(test_cases) - successful}")

    total_tokens = sum(log.get("tokens_used", 0) for log in conversation_log)
    print(f"Total tokens used: {total_tokens}")
    print(f"Estimated cost: ${total_tokens * 0.60 / 1_000_000:.6f}")

    # Check key behaviors
    print("\n📋 Key Behaviors:")

    # Did it call tools?
    tools_called = set()
    for log in conversation_log:
        tools_called.update(log.get("tools_used", []))
    print(f"   Tools called: {', '.join(tools_called) if tools_called else 'NONE'}")

    # Did it reason about results?
    for log in conversation_log:
        if "load_dataset" in log.get("tools_used", []):
            if "mean" in log.get("response", "").lower() or "spread" in log.get("response", "").lower():
                print("   ✅ LLM reasoned about data statistics")
            else:
                print("   ⚠️  LLM loaded data but may not have reported stats")

    # Cleanup
    await agent.close()
    print("\n✅ Agent closed")

    return conversation_log


if __name__ == "__main__":
    print("Starting end-to-end LLM conversation test...")
    print("This will make REAL API calls and use tokens.\n")

    try:
        results = asyncio.run(run_conversation_tests())
        print("\n✅ Test complete. Check conversation_test_results.json for full log.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
