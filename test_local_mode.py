#!/usr/bin/env python3
"""
Test agent in local-only mode (no backend auth required)
"""
import asyncio
import sys
import os

sys.path.insert(0, '/home/user/cite-agent')
os.chdir('/home/user/cite-agent')

# Force local mode
os.environ['USE_LOCAL_KEYS'] = '1'

async def test_local_mode():
    """Test agent without backend authentication"""
    print("\n" + "="*70)
    print("LOCAL MODE TEST - No Backend Authentication")
    print("="*70 + "\n")

    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

        print("📦 Initializing agent in LOCAL mode...")
        agent = EnhancedNocturnalAgent()
        await agent.initialize()
        print(f"✅ Agent initialized")
        print(f"   Auth token: {agent.auth_token}")
        print(f"   Use local keys: {hasattr(agent, 'use_local_keys') and agent.use_local_keys}")
        print()

        # Simple shell-only tests
        tests = [
            "what directory am I in?",
            "list files in current directory",
            "show me Python files here",
        ]

        for i, question in enumerate(tests, 1):
            print(f"\n{'='*70}")
            print(f"TEST {i}/{len(tests)}: {question}")
            print('='*70)

            request = ChatRequest(
                question=question,
                user_id="local_test",
                conversation_id="local_session"
            )

            try:
                response = await agent.process_request(request)

                print(f"\n📝 Response ({len(response.response)} chars):")
                print(response.response[:400])
                if len(response.response) > 400:
                    print("...")

                print(f"\n📊 Metadata:")
                print(f"   Tools used: {response.tools_used}")
                print(f"   Confidence: {response.confidence_score}")
                print(f"   Error: {response.error_message}")

            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                import traceback
                traceback.print_exc()

        await agent.close()
        return True

    except Exception as e:
        print(f"\n❌ FATAL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_local_mode())
    sys.exit(0 if success else 1)
