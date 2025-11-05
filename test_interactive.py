#!/usr/bin/env python3
"""
Interactive agent test - simulates real user conversation
"""
import asyncio
import sys
import os

sys.path.insert(0, '/home/user/cite-agent')
os.chdir('/home/user/cite-agent')

async def test_interactive_conversation():
    """Test a real conversation flow"""
    print("\n" + "="*70)
    print("INTERACTIVE AGENT TEST - Real Conversation Simulation")
    print("="*70 + "\n")

    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

        # Initialize agent
        print("📦 Initializing agent...")
        agent = EnhancedNocturnalAgent()
        await agent.initialize()
        print("✅ Agent initialized\n")

        # Test conversation sequence
        conversations = [
            "where am I right now?",
            "what files are in this directory?",
            "can you list the Python files here?",
            "what's in the cite_agent folder?",
        ]

        print("Starting conversation simulation...\n")
        print("-" * 70)

        for i, question in enumerate(conversations, 1):
            print(f"\n👤 USER (Question {i}/4): {question}")
            print("-" * 70)

            request = ChatRequest(
                question=question,
                user_id="test_user",
                conversation_id="test_session"
            )

            try:
                print("🤖 Agent thinking...")
                response = await agent.process_request(request)

                print(f"\n🤖 AGENT RESPONSE:")
                print(response.response[:300] + "..." if len(response.response) > 300 else response.response)
                print(f"\n📊 Tools used: {response.tools_used}")
                print(f"📊 Conversation history size: {len(agent.conversation_history)}")

            except Exception as e:
                print(f"\n❌ ERROR during request: {e}")
                import traceback
                traceback.print_exc()

            print("-" * 70)

        # Check final state
        print("\n" + "="*70)
        print("FINAL STATE CHECK")
        print("="*70)
        print(f"Conversation history entries: {len(agent.conversation_history)}")
        print(f"Shell session alive: {agent.shell_session.poll() is None if agent.shell_session else False}")

        # Check for repetition
        print("\n" + "="*70)
        print("REPETITION CHECK")
        print("="*70)

        # Check if "pwd" or "ls" appeared multiple times in history
        pwd_count = sum(1 for msg in agent.conversation_history if 'pwd' in str(msg).lower())
        ls_count = sum(1 for msg in agent.conversation_history if 'ls' in str(msg).lower() or 'list' in str(msg).lower())

        print(f"'pwd' mentions in history: {pwd_count}")
        print(f"'ls' mentions in history: {ls_count}")

        if pwd_count > 4 or ls_count > 4:
            print("⚠️  WARNING: Possible command repetition detected!")
        else:
            print("✅ No obvious repetition detected")

        await agent.close()

        return True

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_interactive_conversation())
    sys.exit(0 if success else 1)
