"""
Scaffolded tests for Distributed Rate Limiting.

Fill in the assertions during the red-tests step.
"""

import pytest
from rate_limiter import GatewayNode, RedisRateLimitBackend, make_window_key


class FakeRedisBackend:
    """In-memory Redis substitute for unit testing."""

    def __init__(self):
        self._counts: dict[str, int] = {}
        self._ttls: dict[str, int] = {}
        self.available = True

    def ping(self) -> bool:
        return self.available

    def increment_and_get(self, key: str, window_seconds: int) -> tuple[int, int]:
        self._counts[key] = self._counts.get(key, 0) + 1
        if key not in self._ttls:
            self._ttls[key] = window_seconds
        return self._counts[key], self._ttls[key]

    def get_count(self, key: str) -> int:
        return self._counts.get(key, 0)

    def get_count_and_ttl(self, key: str) -> tuple[int, int]:
        return self._counts.get(key, 0), self._ttls.get(key, 0)


@pytest.fixture
def backend():
    return FakeRedisBackend()


@pytest.fixture
def node(backend):
    return GatewayNode(
        node_id="node-test",
        backend=backend,
        limit=10,
        window_seconds=60,
        sync_interval=0.1,
        sync_batch_size=3,
    )


# ---------------------------------------------------------------------------
# Basic allow/deny
# ---------------------------------------------------------------------------

class TestAllowDeny:
    def test_allow_when_under_limit(self, node):
        pytest.skip("TODO(human): Assert that allow_request returns True when under limit")

    def test_deny_when_over_limit(self, node):
        pytest.skip("TODO(human): Assert that allow_request returns False when limit exceeded")

    def test_local_count_increments_on_allow(self, node):
        pytest.skip("TODO(human): Assert that local_count increases after allowed request")


# ---------------------------------------------------------------------------
# Sync behavior
# ---------------------------------------------------------------------------

class TestSync:
    def test_flush_pushes_local_count_to_redis(self, node, backend):
        pytest.skip("TODO(human): Assert that _flush_key updates Redis and resets local_count")

    def test_sync_happens_on_batch_threshold(self, node, backend):
        pytest.skip("TODO(human): Assert that local_count hitting sync_batch_size triggers flush")


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_redis_unavailable_graceful(self, node, backend):
        pytest.skip("TODO(human): Assert that node handles Redis being down without crashing")

    def test_window_rollover_resets_counts(self, node, backend):
        pytest.skip("TODO(human): Assert that a new time window resets local counters")


# ---------------------------------------------------------------------------
# Multi-node simulation
# ---------------------------------------------------------------------------

class TestMultiNode:
    def test_overshoot_within_tolerance(self, backend):
        pytest.skip("TODO(human): Simulate multiple nodes and assert overshoot <= 5%")

    def test_p99_latency_under_1ms(self, backend):
        pytest.skip("TODO(human): Measure allow_request latency and assert < 1ms")
