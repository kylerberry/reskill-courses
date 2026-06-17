# Challenge 6: Distributed Rate Limiting

## Problem Statement

Design a rate limiting service for a multi-tenant public API platform that enforces per-API-key limits (e.g., 1,000 req/min) across a fleet of stateless gateway nodes spread across 3 availability zones -- without sacrificing accuracy or adding unacceptable latency.

## Learning Objectives

- Understand the accuracy vs latency trade-off space in distributed counters
- Implement token bucket and sliding window algorithms in a distributed context
- Design a local-cache + async-sync hybrid architecture
- Reason about failure modes: Redis down, network partition, clock skew

## Key Concepts

- **Token bucket vs sliding window**: Token bucket allows bursts; sliding window is smoother
- **Local approximation**: Each node counts locally and periodically syncs to Redis
- **Redis atomicity**: Lua scripts ensure `INCR` + `EXPIRE` is atomic
- **Overshoot tolerance**: Accept small overrun (e.g., 5%) in exchange for sub-millisecond enforcement latency

## What You Will Implement

1. `GatewayNode.allow_request()` -- hot-path allow/deny using local cache only
2. `GatewayNode._flush_key()` -- push local delta to Redis and update synced_count

## How to Run Tests

```bash
pytest test_rate_limiter.py -v
```

## Extension Ideas

- **Token-based rate limiting**: Rate limit by token consumption rather than request count
- **Per-provider quotas**: Enforce separate limits per upstream LLM provider
- **Cost-aware throttling**: Prioritize cheaper models when rate limits are near exhaustion

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
