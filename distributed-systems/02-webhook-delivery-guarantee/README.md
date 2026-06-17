# Challenge 7: Webhook Delivery Guarantee

## Problem Statement

Design and implement the delivery guarantee layer for a webhook platform that:
- Fans out a single event to thousands of registered subscriber endpoints
- Tracks per-subscriber delivery state independently
- Guarantees at-least-once delivery with configurable retry budgets
- Applies exponential backoff with jitter per subscriber
- Detects slow/unresponsive endpoints and applies circuit-breaking
- Moves permanently failing deliveries to a dead-letter store

## Learning Objectives

- Model at-least-once delivery with idempotency keys
- Design a per-subscriber retry state machine
- Implement exponential backoff with full jitter
- Apply circuit-breaker pattern to prevent hammering degraded endpoints
- Understand trade-offs between retry aggressiveness and endpoint health

## Key Concepts

- **At-least-once delivery**: Ack on confirmed receipt only; retry until success or budget exhausted
- **Idempotency keys**: Subscribers must handle duplicate delivery
- **Exponential backoff with jitter**: `base * 2^attempt + random(0, base)` avoids thundering herd
- **Circuit breaker**: HALF_OPEN -> CLOSED -> OPEN state transitions based on failure rate
- **Dead-letter queue**: Final resting place for deliveries that exhaust their retry budget

## What You Will Implement

1. `ExponentialBackoffWithJitter.delay_seconds()` -- full-jitter exponential backoff
2. `CircuitBreaker.allow_request()`, `record_success()`, `record_failure()` -- state machine
3. `DeliveryStateMachine.record_failure()` -- retry or dead-letter decision
4. `DeadLetterStore.replay()` -- create fresh attempt from dead-letter entry
5. `WebhookDispatcher._deliver_one()` -- single-subscriber delivery with circuit awareness

## How to Run Tests

```bash
pytest test_webhook_delivery.py -v
```

## Extension Ideas

- **Priority queues**: High-priority events get more aggressive retry budgets
- **Delivery analytics**: Track delivery rates and latency per subscriber
- **LLM provider failover**: Adapt circuit breaker to fail over between LLM providers

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
