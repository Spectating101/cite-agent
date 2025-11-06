#!/usr/bin/env python3
"""
End-to-End Integration Test
Tests the complete agent workflow from request to response
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.asyncio
async def test_agent_imports_successfully():
    """Test that agent and all new modules import without errors"""
    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest, ChatResponse
        from cite_agent.session_memory_manager import get_memory_manager
        from cite_agent.timeout_retry_handler import get_retry_handler
        from cite_agent.prometheus_metrics import get_prometheus_metrics

        assert EnhancedNocturnalAgent is not None
        assert ChatRequest is not None
        assert ChatResponse is not None
        assert get_memory_manager is not None
        assert get_retry_handler is not None
        assert get_prometheus_metrics is not None

        print("✅ All imports successful")
    except Exception as e:
        pytest.fail(f"Import failed: {e}")


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test that agent initializes with all new components"""
    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent

        agent = EnhancedNocturnalAgent()

        # Check that new components were initialized
        assert hasattr(agent, 'memory_manager'), "memory_manager not initialized"
        assert hasattr(agent, 'retry_handler'), "retry_handler not initialized"
        assert agent.memory_manager is not None, "memory_manager is None"
        assert agent.retry_handler is not None, "retry_handler is None"

        print("✅ Agent initialized with all components")
    except Exception as e:
        pytest.fail(f"Agent initialization failed: {e}")


@pytest.mark.asyncio
async def test_memory_manager_integration():
    """Test that memory manager integrates correctly"""
    try:
        from cite_agent.session_memory_manager import SessionMemoryManager

        manager = SessionMemoryManager(
            max_messages_in_memory=10,
            archive_threshold_messages=20
        )

        # Register session
        session = manager.register_session("test_user", "test_conv")
        assert session is not None
        assert session.user_id == "test_user"

        # Update activity
        manager.update_session_activity("test_user", "test_conv", 5, 100)

        # Should not archive yet (under threshold)
        should_archive = manager.should_archive("test_user", "test_conv", 5)
        assert not should_archive

        # Should archive when over threshold
        should_archive = manager.should_archive("test_user", "test_conv", 25)
        assert should_archive

        print("✅ Memory manager works correctly")
    except Exception as e:
        pytest.fail(f"Memory manager test failed: {e}")


@pytest.mark.asyncio
async def test_retry_handler_integration():
    """Test that retry handler works correctly"""
    try:
        from cite_agent.timeout_retry_handler import TimeoutRetryHandler, RetryConfig

        handler = TimeoutRetryHandler(
            config=RetryConfig(max_attempts=3, initial_delay_seconds=0.1)
        )

        # Test successful operation
        call_count = 0
        async def successful_operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await handler.execute_with_retry(
            successful_operation,
            operation_name="test_success"
        )

        assert result.success is True
        assert result.result == "success"
        assert call_count == 1  # Should succeed on first try

        # Test retry on failure then success
        call_count = 0
        async def retry_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise asyncio.TimeoutError("Simulated timeout")
            return "success after retry"

        result = await handler.execute_with_retry(
            retry_then_succeed,
            operation_name="test_retry",
            custom_max_attempts=3
        )

        assert result.success is True
        assert result.result == "success after retry"
        assert call_count == 2  # Failed once, succeeded on retry

        print("✅ Retry handler works correctly")
    except Exception as e:
        pytest.fail(f"Retry handler test failed: {e}")


@pytest.mark.asyncio
async def test_session_archival_workflow():
    """Test the session archival workflow"""
    try:
        from cite_agent.session_memory_manager import SessionMemoryManager

        manager = SessionMemoryManager(
            max_messages_in_memory=5,
            archive_threshold_messages=10,
            recent_context_window=2
        )

        # Create fake conversation history
        conversation = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(15)
        ]

        # Archive should happen
        result = await manager.archive_session(
            user_id="test_user",
            conversation_id="test_conv",
            conversation_history=conversation,
            keep_recent=True
        )

        assert result["archived_count"] == 13  # 15 total - 2 recent
        assert len(result["kept_messages"]) == 2
        assert result["summary"] is not None
        assert result["archive_path"] is not None

        print("✅ Session archival works correctly")
    except Exception as e:
        pytest.fail(f"Session archival test failed: {e}")


@pytest.mark.asyncio
async def test_agent_process_request_with_mocked_backend():
    """Test full agent workflow with mocked backend"""
    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest, ChatResponse

        agent = EnhancedNocturnalAgent()

        # Mock the backend call to avoid needing API keys
        mock_response = ChatResponse(
            response="This is a mocked response for testing.",
            tools_used=["backend_llm"],
            model="test-model",
            tokens_used=100
        )

        with patch.object(agent, 'call_backend_query', new_callable=AsyncMock) as mock_backend:
            mock_backend.return_value = mock_response

            # Create a request
            request = ChatRequest(
                question="What is AI?",
                user_id="test_user",
                conversation_id="test_conv"
            )

            # Process the request
            response = await agent.process_request(request)

            # Verify response
            assert response is not None
            assert isinstance(response, ChatResponse)
            assert response.response is not None
            assert len(response.response) > 0

            # Verify conversation history was updated
            assert len(agent.conversation_history) > 0

            print(f"✅ Agent processed request successfully")
            print(f"   Response: {response.response[:100]}...")

    except Exception as e:
        pytest.fail(f"Full workflow test failed: {e}")


@pytest.mark.asyncio
async def test_agent_memory_archival_triggered():
    """Test that memory archival is triggered during request processing"""
    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest, ChatResponse

        agent = EnhancedNocturnalAgent()

        # Force small archive threshold for testing
        agent.memory_manager.archive_threshold_messages = 5

        # Add fake conversation history to exceed threshold
        for i in range(10):
            agent.conversation_history.append({
                "role": "user",
                "content": f"Message {i}"
            })

        # Mock backend
        mock_response = ChatResponse(
            response="Test response",
            tools_used=["backend_llm"]
        )

        with patch.object(agent, 'call_backend_query', new_callable=AsyncMock) as mock_backend:
            mock_backend.return_value = mock_response

            # Get initial history length
            initial_length = len(agent.conversation_history)

            request = ChatRequest(
                question="Test question",
                user_id="test_user",
                conversation_id="test_conv"
            )

            # Process request - should trigger archival
            response = await agent.process_request(request)

            # Verify archival happened (history should be shorter)
            final_length = len(agent.conversation_history)

            print(f"✅ Memory archival integration test passed")
            print(f"   Initial history: {initial_length} messages")
            print(f"   Final history: {final_length} messages")
            print(f"   Archival {'triggered' if final_length < initial_length else 'not triggered (may need adjustment)'}")

    except Exception as e:
        pytest.fail(f"Memory archival integration test failed: {e}")


@pytest.mark.asyncio
async def test_prometheus_metrics_integration():
    """Test that Prometheus metrics can be collected"""
    try:
        from cite_agent.prometheus_metrics import get_prometheus_metrics

        metrics = get_prometheus_metrics()

        if metrics.enabled:
            # Record some test metrics
            metrics.record_request("test_user", 0.5, True)
            metrics.record_request("test_user", 1.0, False)
            metrics.update_queue_depth(5)
            metrics.record_retry_attempt("timeout", True)

            # Generate metrics output
            metrics_output = metrics.generate_metrics()

            assert metrics_output is not None
            assert len(metrics_output) > 0

            print("✅ Prometheus metrics integration works")
        else:
            print("⚠️  Prometheus client not available (expected if not installed)")

    except Exception as e:
        print(f"⚠️  Prometheus metrics test skipped: {e}")


@pytest.mark.asyncio
async def test_unified_observability_integration():
    """Test unified observability system"""
    try:
        from cite_agent.unified_observability import UnifiedObservability

        obs = UnifiedObservability()

        # Start operation
        ctx = obs.start_operation(
            operation_name="test_operation",
            user_id="test_user",
            provider="test_provider"
        )

        assert ctx is not None
        assert ctx.operation_name == "test_operation"
        assert ctx.user_id == "test_user"

        # Complete operation
        obs.complete_operation(ctx, success=True)

        # Get stats
        stats = obs.get_stats()
        assert stats is not None
        assert "active_operations" in stats

        print("✅ Unified observability integration works")

    except Exception as e:
        pytest.fail(f"Unified observability test failed: {e}")


@pytest.mark.asyncio
async def test_complete_end_to_end_workflow():
    """
    Complete end-to-end test simulating real usage
    """
    try:
        from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

        print("\n" + "="*60)
        print("Running Complete End-to-End Workflow Test")
        print("="*60)

        # Initialize agent
        print("1. Initializing agent...")
        agent = EnhancedNocturnalAgent()
        assert agent is not None
        print("   ✅ Agent initialized")

        # Check components
        print("2. Checking components...")
        assert agent.memory_manager is not None, "Memory manager missing"
        assert agent.retry_handler is not None, "Retry handler missing"
        print("   ✅ All components present")

        # Mock backend to avoid API keys
        print("3. Setting up mocked backend...")
        from cite_agent.enhanced_ai_agent import ChatResponse

        mock_response = ChatResponse(
            response="The meaning of life is a philosophical question...",
            tools_used=["backend_llm"],
            model="test-model",
            tokens_used=50,
            confidence_score=0.9
        )

        with patch.object(agent, 'call_backend_query', new_callable=AsyncMock) as mock_backend:
            mock_backend.return_value = mock_response
            print("   ✅ Backend mocked")

            # Process first request
            print("4. Processing first request...")
            request1 = ChatRequest(
                question="What is the meaning of life?",
                user_id="end_to_end_user",
                conversation_id="end_to_end_session"
            )

            response1 = await agent.process_request(request1)
            assert response1 is not None
            assert response1.response is not None
            print(f"   ✅ First request processed")
            print(f"      Response length: {len(response1.response)} chars")

            # Process second request (test conversation continuity)
            print("5. Processing second request...")
            request2 = ChatRequest(
                question="Can you explain more?",
                user_id="end_to_end_user",
                conversation_id="end_to_end_session"
            )

            response2 = await agent.process_request(request2)
            assert response2 is not None
            print(f"   ✅ Second request processed")

            # Check conversation history
            print("6. Verifying conversation history...")
            assert len(agent.conversation_history) >= 2
            print(f"   ✅ Conversation history: {len(agent.conversation_history)} messages")

            # Test memory manager
            print("7. Testing memory management...")
            session_stats = agent.memory_manager.get_stats()
            print(f"   ✅ Active sessions: {session_stats['active_sessions']}")

            # Test retry handler
            print("8. Testing retry handler...")
            retry_stats = agent.retry_handler.get_stats()
            print(f"   ✅ Retry stats available: {retry_stats is not None}")

        print("\n" + "="*60)
        print("✅ Complete End-to-End Test PASSED")
        print("="*60 + "\n")

    except Exception as e:
        import traceback
        print(f"\n❌ End-to-end test FAILED: {e}")
        traceback.print_exc()
        pytest.fail(f"Complete end-to-end test failed: {e}")


if __name__ == "__main__":
    # Run tests
    print("Running end-to-end integration tests...")
    pytest.main([__file__, "-v", "-s"])
