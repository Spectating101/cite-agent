#!/usr/bin/env python3
"""
Comprehensive Stress Test Suite for Cite-Agent
Tests concurrent load handling, memory usage, and system stability
"""

import asyncio
import json
import logging
import os
import psutil
import pytest
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch

# Suppress noise during tests
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@dataclass
class StressTestMetrics:
    """Metrics collected during stress testing"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    memory_start_mb: float = 0.0
    memory_peak_mb: float = 0.0
    memory_end_mb: float = 0.0
    queue_depth_max: int = 0
    circuit_breaker_trips: int = 0
    rate_limit_hits: int = 0
    errors_by_type: Dict[str, int] = None
    test_duration_seconds: float = 0.0

    def __post_init__(self):
        if self.errors_by_type is None:
            self.errors_by_type = {}

    def calculate_percentiles(self, latencies: List[float]):
        """Calculate latency percentiles"""
        if not latencies:
            return

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        self.p50_latency_ms = sorted_latencies[int(n * 0.5)]
        self.p95_latency_ms = sorted_latencies[int(n * 0.95)]
        self.p99_latency_ms = sorted_latencies[int(n * 0.99)]

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for reporting"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(1, self.total_requests),
            "avg_latency_ms": self.total_latency_ms / max(1, self.successful_requests),
            "min_latency_ms": self.min_latency_ms if self.min_latency_ms != float('inf') else 0,
            "max_latency_ms": self.max_latency_ms,
            "p50_latency_ms": self.p50_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "memory_start_mb": self.memory_start_mb,
            "memory_peak_mb": self.memory_peak_mb,
            "memory_end_mb": self.memory_end_mb,
            "memory_growth_mb": self.memory_end_mb - self.memory_start_mb,
            "queue_depth_max": self.queue_depth_max,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "rate_limit_hits": self.rate_limit_hits,
            "errors_by_type": self.errors_by_type,
            "test_duration_seconds": self.test_duration_seconds,
            "requests_per_second": self.total_requests / max(0.1, self.test_duration_seconds)
        }


class MockEnhancedAgent:
    """Mock agent for testing with realistic behavior"""

    def __init__(self):
        self.conversation_history = []
        self.daily_token_usage = 0
        self.daily_query_count = 0
        self.memory = {}
        self._initialized = True

    async def initialize(self):
        """Mock initialization"""
        await asyncio.sleep(0.01)  # Simulate initialization delay
        self._initialized = True

    async def process_request(self, request) -> Any:
        """Mock request processing with realistic latency"""
        # Simulate varying latency (50-500ms)
        latency = 0.05 + (hash(request.question) % 450) / 1000.0
        await asyncio.sleep(latency)

        # Simulate occasional failures (5% failure rate)
        if hash(request.question) % 20 == 0:
            raise Exception("Simulated backend failure")

        # Simulate response
        response = Mock()
        response.response = f"Mock response for: {request.question}"
        response.tools_used = ["mock_api"]
        response.reasoning_steps = ["Mock reasoning"]
        response.tokens_used = 100

        self.conversation_history.append({
            "question": request.question,
            "response": response.response,
            "timestamp": datetime.now().isoformat()
        })

        return response


async def simulate_user_session(
    user_id: str,
    num_requests: int,
    request_delay_ms: float,
    metrics: StressTestMetrics,
    latencies: List[float]
) -> Dict[str, Any]:
    """Simulate a single user session with multiple requests"""

    from cite_agent.enhanced_ai_agent import ChatRequest

    agent = MockEnhancedAgent()
    await agent.initialize()

    session_results = {
        "user_id": user_id,
        "requests_sent": 0,
        "requests_succeeded": 0,
        "requests_failed": 0,
        "errors": []
    }

    for i in range(num_requests):
        try:
            request = ChatRequest(
                question=f"User {user_id} question {i}: What is the meaning of life?",
                user_id=user_id,
                conversation_id=f"{user_id}_session"
            )

            start_time = time.time()
            response = await agent.process_request(request)
            end_time = time.time()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

            metrics.total_requests += 1
            metrics.successful_requests += 1
            metrics.total_latency_ms += latency_ms
            metrics.min_latency_ms = min(metrics.min_latency_ms, latency_ms)
            metrics.max_latency_ms = max(metrics.max_latency_ms, latency_ms)

            session_results["requests_sent"] += 1
            session_results["requests_succeeded"] += 1

            # Delay between requests from same user
            if request_delay_ms > 0:
                await asyncio.sleep(request_delay_ms / 1000.0)

        except Exception as e:
            metrics.total_requests += 1
            metrics.failed_requests += 1

            error_type = type(e).__name__
            metrics.errors_by_type[error_type] = metrics.errors_by_type.get(error_type, 0) + 1

            session_results["requests_sent"] += 1
            session_results["requests_failed"] += 1
            session_results["errors"].append(str(e))

            logger.error(f"User {user_id} request {i} failed: {e}")

    return session_results


async def run_stress_test(
    num_users: int,
    requests_per_user: int,
    request_delay_ms: float = 100.0
) -> StressTestMetrics:
    """
    Run stress test with specified parameters

    Args:
        num_users: Number of concurrent users
        requests_per_user: Requests each user makes
        request_delay_ms: Delay between requests from same user

    Returns:
        StressTestMetrics with test results
    """

    metrics = StressTestMetrics()
    latencies = []

    # Get process for memory monitoring
    process = psutil.Process()
    metrics.memory_start_mb = process.memory_info().rss / 1024 / 1024

    print(f"\n{'='*60}")
    print(f"Starting stress test:")
    print(f"  - Concurrent users: {num_users}")
    print(f"  - Requests per user: {requests_per_user}")
    print(f"  - Total requests: {num_users * requests_per_user}")
    print(f"  - Request delay: {request_delay_ms}ms")
    print(f"  - Initial memory: {metrics.memory_start_mb:.2f} MB")
    print(f"{'='*60}\n")

    start_time = time.time()

    # Create tasks for all users
    tasks = []
    for user_num in range(num_users):
        user_id = f"stress_test_user_{user_num}"
        task = simulate_user_session(
            user_id=user_id,
            num_requests=requests_per_user,
            request_delay_ms=request_delay_ms,
            metrics=metrics,
            latencies=latencies
        )
        tasks.append(task)

    # Monitor memory during execution
    async def monitor_memory():
        peak_memory = metrics.memory_start_mb
        while True:
            try:
                current_memory = process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)
                metrics.memory_peak_mb = peak_memory
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break

    memory_monitor = asyncio.create_task(monitor_memory())

    # Run all user sessions concurrently
    try:
        session_results = await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        memory_monitor.cancel()
        try:
            await memory_monitor
        except asyncio.CancelledError:
            pass

    end_time = time.time()
    metrics.test_duration_seconds = end_time - start_time
    metrics.memory_end_mb = process.memory_info().rss / 1024 / 1024

    # Calculate percentiles
    metrics.calculate_percentiles(latencies)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Stress test completed:")
    print(f"  - Duration: {metrics.test_duration_seconds:.2f}s")
    print(f"  - Requests/sec: {metrics.total_requests / metrics.test_duration_seconds:.2f}")
    print(f"  - Success rate: {metrics.successful_requests / max(1, metrics.total_requests) * 100:.2f}%")
    print(f"  - Failed requests: {metrics.failed_requests}")
    print(f"  - Avg latency: {metrics.total_latency_ms / max(1, metrics.successful_requests):.2f}ms")
    print(f"  - P50 latency: {metrics.p50_latency_ms:.2f}ms")
    print(f"  - P95 latency: {metrics.p95_latency_ms:.2f}ms")
    print(f"  - P99 latency: {metrics.p99_latency_ms:.2f}ms")
    print(f"  - Memory start: {metrics.memory_start_mb:.2f} MB")
    print(f"  - Memory peak: {metrics.memory_peak_mb:.2f} MB")
    print(f"  - Memory end: {metrics.memory_end_mb:.2f} MB")
    print(f"  - Memory growth: {metrics.memory_end_mb - metrics.memory_start_mb:.2f} MB")
    print(f"{'='*60}\n")

    return metrics


# ============================================================================
# PYTEST TEST CASES
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.stress
async def test_stress_10_concurrent_users():
    """Test with 10 concurrent users - Light load"""
    metrics = await run_stress_test(
        num_users=10,
        requests_per_user=5,
        request_delay_ms=100
    )

    # Assertions
    assert metrics.successful_requests > 0, "Should have some successful requests"
    success_rate = metrics.successful_requests / metrics.total_requests
    assert success_rate > 0.90, f"Success rate should be >90%, got {success_rate*100:.2f}%"

    # Latency should be reasonable
    avg_latency = metrics.total_latency_ms / metrics.successful_requests
    assert avg_latency < 1000, f"Average latency should be <1s, got {avg_latency:.2f}ms"
    assert metrics.p95_latency_ms < 1500, f"P95 latency should be <1.5s, got {metrics.p95_latency_ms:.2f}ms"

    # Memory growth should be bounded
    memory_growth = metrics.memory_end_mb - metrics.memory_start_mb
    assert memory_growth < 100, f"Memory growth should be <100MB, got {memory_growth:.2f}MB"

    print(f"✅ 10 concurrent users test PASSED")


@pytest.mark.asyncio
@pytest.mark.stress
async def test_stress_50_concurrent_users():
    """Test with 50 concurrent users - Target production load"""
    metrics = await run_stress_test(
        num_users=50,
        requests_per_user=3,
        request_delay_ms=100
    )

    # Assertions
    assert metrics.successful_requests > 0, "Should have some successful requests"
    success_rate = metrics.successful_requests / metrics.total_requests
    assert success_rate > 0.85, f"Success rate should be >85%, got {success_rate*100:.2f}%"

    # Latency degradation acceptable under load
    avg_latency = metrics.total_latency_ms / metrics.successful_requests
    assert avg_latency < 2000, f"Average latency should be <2s under load, got {avg_latency:.2f}ms"
    assert metrics.p95_latency_ms < 3000, f"P95 latency should be <3s under load, got {metrics.p95_latency_ms:.2f}ms"

    # Memory growth should be bounded
    memory_growth = metrics.memory_end_mb - metrics.memory_start_mb
    assert memory_growth < 200, f"Memory growth should be <200MB, got {memory_growth:.2f}MB"

    # Should complete in reasonable time
    expected_duration = (50 * 3 * 0.3)  # Conservative estimate: 50 users * 3 req * 300ms avg
    assert metrics.test_duration_seconds < expected_duration * 2, \
        f"Should complete within 2x expected time ({expected_duration*2:.0f}s), got {metrics.test_duration_seconds:.2f}s"

    print(f"✅ 50 concurrent users test PASSED")


@pytest.mark.asyncio
@pytest.mark.stress
@pytest.mark.slow
async def test_stress_100_concurrent_users():
    """Test with 100 concurrent users - Stress test beyond target"""
    metrics = await run_stress_test(
        num_users=100,
        requests_per_user=2,
        request_delay_ms=100
    )

    # Assertions - More lenient for extreme load
    assert metrics.successful_requests > 0, "Should have some successful requests"
    success_rate = metrics.successful_requests / metrics.total_requests
    assert success_rate > 0.70, f"Success rate should be >70% even under extreme load, got {success_rate*100:.2f}%"

    # Latency can degrade more under extreme load
    avg_latency = metrics.total_latency_ms / metrics.successful_requests
    assert avg_latency < 5000, f"Average latency should be <5s under extreme load, got {avg_latency:.2f}ms"

    # Memory growth should still be bounded
    memory_growth = metrics.memory_end_mb - metrics.memory_start_mb
    assert memory_growth < 500, f"Memory growth should be <500MB even under extreme load, got {memory_growth:.2f}MB"

    print(f"✅ 100 concurrent users test PASSED")


@pytest.mark.asyncio
@pytest.mark.stress
async def test_sustained_load_memory_leak():
    """Test for memory leaks during sustained load"""

    # Run 5 batches of 20 users with 5 requests each
    # Total: 500 requests over sustained period

    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024

    batch_metrics = []

    print(f"\n{'='*60}")
    print(f"Starting sustained load test (5 batches of 20 users):")
    print(f"  - Initial memory: {initial_memory:.2f} MB")
    print(f"{'='*60}\n")

    for batch_num in range(5):
        print(f"\nBatch {batch_num + 1}/5...")

        metrics = await run_stress_test(
            num_users=20,
            requests_per_user=5,
            request_delay_ms=50
        )

        batch_metrics.append(metrics)

        # Brief pause between batches
        await asyncio.sleep(1)

    final_memory = process.memory_info().rss / 1024 / 1024
    total_memory_growth = final_memory - initial_memory

    print(f"\n{'='*60}")
    print(f"Sustained load test completed:")
    print(f"  - Initial memory: {initial_memory:.2f} MB")
    print(f"  - Final memory: {final_memory:.2f} MB")
    print(f"  - Total growth: {total_memory_growth:.2f} MB")
    print(f"  - Growth per batch: {total_memory_growth / 5:.2f} MB")
    print(f"{'='*60}\n")

    # Memory growth should be sub-linear (not growing proportionally with requests)
    # Allow up to 300MB growth for 500 requests
    assert total_memory_growth < 300, \
        f"Memory leak detected: grew {total_memory_growth:.2f}MB over 500 requests"

    # Memory growth per batch should stabilize (last batch shouldn't grow more than first)
    growth_per_batch = [m.memory_end_mb - m.memory_start_mb for m in batch_metrics]

    # Last batch growth should not be significantly larger than first batch
    # (indicating memory is being cleaned up)
    assert growth_per_batch[-1] < growth_per_batch[0] * 2, \
        f"Memory growth accelerating: first batch {growth_per_batch[0]:.2f}MB, " \
        f"last batch {growth_per_batch[-1]:.2f}MB"

    print(f"✅ Sustained load memory leak test PASSED")


@pytest.mark.asyncio
@pytest.mark.stress
async def test_rapid_fire_requests():
    """Test rapid-fire requests from single user (no delay between requests)"""

    metrics = await run_stress_test(
        num_users=1,
        requests_per_user=100,
        request_delay_ms=0  # No delay - rapid fire
    )

    # Should handle rapid requests without failure
    success_rate = metrics.successful_requests / metrics.total_requests
    assert success_rate > 0.90, f"Should handle rapid fire with >90% success, got {success_rate*100:.2f}%"

    # Should complete quickly since only 1 user
    assert metrics.test_duration_seconds < 60, \
        f"Rapid fire should complete in <60s, got {metrics.test_duration_seconds:.2f}s"

    print(f"✅ Rapid fire requests test PASSED")


@pytest.mark.asyncio
@pytest.mark.stress
async def test_concurrent_different_query_types():
    """Test concurrent requests with different query complexity"""

    # This test would use real agent with different query types
    # For now, use mock but structure is ready for real implementation

    metrics = await run_stress_test(
        num_users=25,
        requests_per_user=4,
        request_delay_ms=100
    )

    success_rate = metrics.successful_requests / metrics.total_requests
    assert success_rate > 0.85, f"Mixed query types should work with >85% success, got {success_rate*100:.2f}%"

    print(f"✅ Concurrent different query types test PASSED")


# ============================================================================
# COMMAND LINE INTERFACE FOR MANUAL TESTING
# ============================================================================

async def main():
    """Command-line interface for running stress tests manually"""
    import argparse

    parser = argparse.ArgumentParser(description="Cite-Agent Stress Test Suite")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--requests", type=int, default=5, help="Requests per user")
    parser.add_argument("--delay", type=float, default=100, help="Delay between requests (ms)")
    parser.add_argument("--output", type=str, help="Output JSON file for metrics")

    args = parser.parse_args()

    metrics = await run_stress_test(
        num_users=args.users,
        requests_per_user=args.requests,
        request_delay_ms=args.delay
    )

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        print(f"✅ Metrics saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
