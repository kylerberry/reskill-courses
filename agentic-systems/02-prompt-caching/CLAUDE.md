# Prompt Caching System Design

## Problem Statement

You are building a prompt caching layer for a high-traffic LLM-powered application (e.g., a customer support assistant handling 50,000 requests/hour). Many requests share long system prompts and few-shot examples, but each has a unique user message appended.

Design a caching system that:

1. **Reduces redundant token processing** across requests
2. **Handles cache invalidation** when prompts are updated
3. **Degrades gracefully** when cache hit rates drop

**Context**: Most LLM providers charge per input token and add latency proportional to prompt length — so prefix caching has real cost and UX implications. The interesting tension is between maximizing cache reuse and maintaining correctness when the underlying prompts evolve.

## Learning Objectives

1. **Cost optimization patterns** for LLM applications at scale
2. **Content-addressable caching** and why it matters for prompt versioning
3. **Cache invalidation strategies** and their distributed systems trade-offs
4. **Circuit breaker patterns** for graceful degradation
5. **Real-world ROI calculations** for caching infrastructure

## Key Concepts

- **Distributed Caching**: Redis-backed cache with TTL management
- **Content Addressing**: SHA-256 hashing for version-independent cache keys
- **Cache Invalidation**: The hardest problem in computer science (seriously)
- **Resilience Patterns**: Circuit breakers, fallback strategies, health checks
- **Cost-Latency Trade-offs**: When does caching ROI justify infrastructure cost?

## What You Will Implement

1. **`invalidate_template()`** — Decide how to match and delete cache keys when a prompt is updated. Consider: SCAN patterns, pub/sub coordination, race conditions.
2. **`CircuitBreaker` state machine** — Implement CLOSED → OPEN → HALF_OPEN → CLOSED transitions with proper timing and thresholds.
3. **`handle_request()`** — Orchestrate the full flow: circuit check → cache lookup → LLM call (with or without cache token) → metrics update.

## How to Run Tests

```bash
python -m pytest test_prompt_cache.py -v
```

## Scale Math

- 50k requests/hour = ~14 req/sec
- Average prompt prefix: ~2k tokens
- At 80% hit rate with $10/1M tokens: **~$1,200/day savings**

## Extension Ideas

- **Multi-region caching**: Geographic distribution for global latency reduction
- **Partial prefix matching**: Cache common sub-prefixes (e.g., language-specific intros)
- **Provider-native cache integration**: Use Anthropic `cache_control` or OpenAI automatic caching on top of Redis layer
- **Cost analytics dashboard**: Track savings by template, version, request type, and provider
- **A/B testing integration**: Run multiple prompt versions simultaneously with separate cache namespaces

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
