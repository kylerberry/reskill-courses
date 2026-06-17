"""
Distributed Rate Limiting — Local Cache + Async Redis Sync

Architecture:
- GatewayNode: stateless node with local request counter and periodic Redis sync
- RedisRateLimitBackend: atomic counter operations via Lua scripts
- Top-level simulate(): runs a multi-node load test and reports overshoot

Success criteria:
  - Overshoot < 5% above configured limit
  - P99 enforcement latency < 1ms (local decision)
  - Graceful handling of Redis unavailability
"""

from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Redis Backend
# ---------------------------------------------------------------------------

# Lua script: atomically increment a key, set TTL only on first write
# Returns [current_count, ttl_remaining]
INCR_WITH_TTL_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


class RedisRateLimitBackend:
    """Redis backend for distributed rate limiting."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            import redis as _redis
            self.client = _redis.Redis(
                host=host, port=port, db=db, decode_responses=True
            )
            self._incr_script = self.client.register_script(INCR_WITH_TTL_SCRIPT)
        except Exception:
            self.client = None
            self._incr_script = None

    def increment_and_get(self, key: str, window_seconds: int) -> tuple[int, int]:
        """Atomically increment counter, returns (count, ttl_seconds)."""
        if self._incr_script is None:
            raise RuntimeError("Redis not available")
        result = self._incr_script(keys=[key], args=[window_seconds])
        return int(result[0]), int(result[1])

    def get_count(self, key: str) -> int:
        """Read current count without incrementing."""
        if self.client is None:
            return 0
        val = self.client.get(key)
        return int(val) if val else 0

    def get_count_and_ttl(self, key: str) -> tuple[int, int]:
        """Returns (count, ttl). Used by nodes to resync local cache."""
        if self.client is None:
            return 0, 0
        pipe = self.client.pipeline()
        pipe.get(key)
        pipe.ttl(key)
        count_raw, ttl = pipe.execute()
        count = int(count_raw) if count_raw else 0
        return count, max(ttl, 0)

    def ping(self) -> bool:
        try:
            return self.client is not None and self.client.ping()
        except Exception:
            return False


def make_window_key(api_key: str, window_seconds: int) -> str:
    """Generate a time-bucketed Redis key for this API key + current window."""
    bucket = int(time.time()) // window_seconds
    return f"rl:{api_key}:{bucket}"


# ---------------------------------------------------------------------------
# Gateway Node
# ---------------------------------------------------------------------------

@dataclass
class LocalEntry:
    """Local cached state for a single API key."""

    local_count: int = 0
    synced_count: int = 0
    window_key: str = ""
    last_sync: float = 0.0
    window_expires_at: float = 0.0


class GatewayNode:
    """Simulated stateless gateway node with local cache and periodic Redis sync."""

    def __init__(
        self,
        node_id: str,
        backend: RedisRateLimitBackend,
        limit: int = 1000,
        window_seconds: int = 60,
        sync_interval: float = 1.0,
        sync_batch_size: int = 50,
    ):
        self.node_id = node_id
        self.backend = backend
        self.limit = limit
        self.window_seconds = window_seconds
        self.sync_interval = sync_interval
        self.sync_batch_size = sync_batch_size

        self._cache: dict[str, LocalEntry] = {}
        self._lock = threading.Lock()

        # Background sync thread
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()

    def allow_request(self, api_key: str) -> bool:
        """
        TODO(human): Implement the allow/deny hot-path logic.

        Hot path: make allow/deny decision using local cache only.
        Must be fast -- no Redis I/O on this path.

        You have access to:
          entry.local_count   -- requests counted locally since last sync
          entry.synced_count  -- last known Redis total for this window
          self.limit          -- the configured request limit
          self.sync_batch_size -- flush threshold

        Your logic should:
          1. Decide allow/deny based on combined local + synced count
          2. Increment local_count if allowed
          3. Trigger a sync if local_count has hit the batch threshold

        Return True to allow, False to deny.
        """
        with self._lock:
            entry = self._get_or_create_entry(api_key)
            # TODO(human): implement allow/deny logic
            pass

    def _get_or_create_entry(self, api_key: str) -> LocalEntry:
        """Get or create local cache entry, resetting if window has rolled."""
        now = time.time()
        current_window_key = make_window_key(api_key, self.window_seconds)

        entry = self._cache.get(api_key)
        if entry is None or entry.window_key != current_window_key:
            entry = LocalEntry(
                window_key=current_window_key,
                last_sync=0.0,
                window_expires_at=now + self.window_seconds,
            )
            self._cache[api_key] = entry

        return entry

    def _flush_key(self, api_key: str):
        """
        TODO(human): Implement Redis flush for a single API key.

        Push local_count delta to Redis and update synced_count.
        Call with lock held.

        Steps:
          1. If entry is None or local_count == 0, return early.
          2. Use backend.increment_and_get or pipeline to flush local_count.
          3. Update entry.synced_count with the new total from Redis.
          4. Reset entry.local_count to 0.
          5. Update entry.last_sync.

        If Redis is unavailable, keep counting locally (fail-open or fail-closed
        depending on your design decision).
        """
        pass

    def _sync_loop(self):
        """Background thread: periodically sync all stale cache entries."""
        while True:
            time.sleep(self.sync_interval)
            with self._lock:
                now = time.time()
                for api_key, entry in list(self._cache.items()):
                    if now - entry.last_sync >= self.sync_interval:
                        self._flush_key(api_key)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def simulate(
    n_nodes: int = 3,
    n_requests: int = 5000,
    limit: int = 1000,
    window_seconds: int = 60,
    sync_interval: float = 0.5,
    sync_batch_size: int = 20,
):
    """Run a local simulation and report overshoot."""
    backend = RedisRateLimitBackend()
    if not backend.ping():
        print("Redis not available -- start Redis locally: redis-server")
        return

    nodes = [
        GatewayNode(
            node_id=f"node-{i}",
            backend=backend,
            limit=limit,
            window_seconds=window_seconds,
            sync_interval=sync_interval,
            sync_batch_size=sync_batch_size,
        )
        for i in range(n_nodes)
    ]

    api_key = "test-key-001"
    allowed = 0
    denied = 0
    lock = threading.Lock()

    def make_request(_):
        nonlocal allowed, denied
        node = random.choice(nodes)
        result = node.allow_request(api_key)
        with lock:
            if result:
                allowed += 1
            else:
                denied += 1

    threads = [
        threading.Thread(target=make_request, args=(i,)) for i in range(n_requests)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    overshoot_pct = max(0, (allowed - limit) / limit * 100)
    print(f"\nResults ({n_nodes} nodes, {n_requests} requests):")
    print(f"  Allowed:  {allowed}")
    print(f"  Denied:   {denied}")
    print(f"  Limit:    {limit}")
    print(f"  Overshoot: {overshoot_pct:.1f}%")
    print(f"  {'PASS' if overshoot_pct <= 5 else 'FAIL'} -- target: <=5% overshoot")


if __name__ == "__main__":
    simulate()
