# Multi-Tenant LLM Gateway

## Problem Statement

You are building a multi-tenant LLM gateway — a shared infrastructure layer that sits between your organization's internal applications and multiple upstream LLM providers (e.g., OpenAI, Anthropic, Azure OpenAI). The gateway must handle routing, cost attribution, rate limiting, and prompt caching across tenants.

Design this system to support 50 internal teams, each with different model preferences, budget caps, and latency SLAs.

**Context**: This is a system that many companies are quietly building as AI spend spirals and teams proliferate. The interesting tension is that you are essentially building an "LLM load balancer" that must be intelligent about semantic caching (not just key-value), budget enforcement in real time, and failover between providers with non-equivalent model capabilities.

## Learning Objectives

1. Design multi-model routing with capability-based filtering and tenant preferences
2. Implement semantic caching with capability fingerprinting
3. Build optimistic budget enforcement with spend tracking
4. Reason about failover strategies when providers are degraded or non-equivalent

## Key Concepts

- **Capability-based routing**: Match request requirements (vision, function calling, JSON mode) against model capabilities
- **Semantic caching**: Store responses keyed by embedding similarity to avoid redundant LLM calls
- **Budget enforcement**: Track per-tenant spend with optimistic reservation (accept small overspend for speed)
- **Provider failover**: When the primary provider fails, cascade to secondary providers in preference order — but never silently downgrade capabilities
- **Cost-latency-quality triangle**: Cheaper models may have higher latency or fewer capabilities; the router should expose this tension, not hide it

## What You Will Implement

1. **`SemanticCache._capability_fingerprint()`** — stable, order-independent fingerprint for capability sets
2. **`ProviderRouter.select_candidates()`** — filter and rank eligible models by capability, latency, and tenant preference
3. **`LLMGateway.handle()`** — full orchestration: cache lookup → route → budget check → provider call → spend tracking → cache storage

## How to Run Tests

```bash
python -m pytest test_gateway.py -v
```

## Extension Ideas

- **Dynamic pricing**: Adjust routing based on real-time provider pricing
- **Request deduplication**: In-flight request coalescing for identical prompts
- **A/B testing**: Route a percentage of traffic to a new model and compare metrics
- **Per-team dashboards**: Expose utilization, cost, and latency breakdowns
- **Circuit breaker per provider**: Isolate failures to individual providers without affecting the whole gateway

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
