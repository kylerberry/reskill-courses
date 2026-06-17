# Challenge 9: Global Leaderboard Service

## Problem Statement

Design the global leaderboard service for a competitive mobile game with 50 million monthly active players. Score updates arrive at thousands of writes per second during peak hours, and players expect to see their current global rank and the top-100 list with sub-100ms p99 latency.

## Learning Objectives

- Understand why global sorted sets resist naive horizontal sharding
- Learn write buffering patterns to absorb burst traffic
- Implement cache invalidation strategies for hot read paths
- Explore approximate vs exact rank trade-offs at scale

## Key Concepts

- **Redis Sorted Sets (ZSET)**: `ZADD`, `ZRANK`, `ZREVRANGE`, `ZREVRANK`
- **Write buffering**: Batch score updates to reduce write amplification
- **Cache invalidation**: Score threshold tracking to avoid recomputing top-N on every write
- **Tie-breaking**: Deterministic ordering when scores are equal

## What You Will Implement

1. `LeaderboardService.batch_update()` -- batch score updates with single cache invalidation
2. `LeaderboardService.get_rank()` -- 1-indexed rank with tie-breaking
3. `LeaderboardService.get_top_n()` -- cache-aware top-N retrieval
4. `TopNCache.set()` -- store entries and derive minimum score threshold
5. `TopNCache.should_invalidate()` -- determine if a new score displaces the cached top-N

## How to Run Tests

```bash
pytest test_leaderboard.py -v
```

## Extension Ideas

- **Approximate rank**: Implement probabilistic rank estimation for massive scale
- **Write buffering**: Add an in-memory buffer that flushes to the sorted set periodically
- **Shard-aware leaderboard**: Design a sharding scheme that preserves global order

## v2 Claude Workflow

This is a pre-built v2 challenge. Start with the cold-answer step before reading implementation code. Claude should generate a fresh cold-answer question from the problem statement and learning objectives, then record it in `STATE.md`.

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pytest
```

### Run

```bash
python -m pytest -v
```

Tests begin as skip-style stubs. During the red-tests step, remove skips one test at a time and replace them with assertions that should fail until the corresponding `TODO(human)` implementation is complete.
