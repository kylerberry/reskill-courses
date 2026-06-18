# Agent Session Manager

## Problem Statement

You are building a session management system for multi-agent AI applications that handle long-running, expensive tasks (e.g., research agents that spawn multiple sub-agents for data gathering, analysis, and synthesis). These agents can fail mid-execution due to rate limits, API errors, or deployment issues.

Design a session management system that:

1. **Enables resumable sessions** — Recover from failures without losing expensive progress
2. **Tracks hierarchical agent relationships** — Parent agents spawn child agents with cascading resumption
3. **Implements flexible checkpointing** — Balance between fine-grained (every tool call) and coarse-grained (phase boundaries)
4. **Provides real-time observability** — Event stream for monitoring agent progress

**Context**: Multi-agent workflows can cost $10–100 per execution in LLM tokens. A failure at 80% completion wastes most of that cost. The interesting tension is between checkpoint granularity (storage cost, write latency) and recovery precision (how much work must be re-done on resume).

## Learning Objectives

1. **State persistence patterns** for long-running AI workflows
2. **Checkpoint strategies** and their trade-offs (fine vs coarse-grained)
3. **Hierarchical resumption** — cascading recovery across parent/child agents
4. **Event-driven observability** for distributed agent systems
5. **Storage layer abstractions** — when to use SQLite vs PostgreSQL vs DynamoDB

## Key Concepts

- **Session Lifecycle**: `initializing → running → paused / completed / failed / cancelled`
- **Checkpoint Contents**: Tool calls, artifacts, context, sub-agents, progress
- **Resumption Strategy**: Return latest checkpoint + pending work (incomplete tool calls, non-terminal sub-agents)
- **Cacheability Flags**: Mark tool calls as cacheable (safe to skip on resume) vs non-cacheable (must re-run)
- **Storage Abstraction**: Interface-based design allows swapping SQLite → PostgreSQL → DynamoDB

## What You Will Implement

1. **`Checkpoint` dataclass** — Decide what fields are needed to fully capture agent state at a point in time.
2. **`Session` dataclass** — Decide how sessions relate to checkpoints. Store all checkpoints or only the latest?
3. **`resume_session()`** — The critical method. Reconstruct agent state, identify pending tool calls, and cascade to sub-agents.

## How to Run Tests

```bash
python -m pytest test_session_manager.py -v
```

## Extension Ideas

- **Distributed tracing**: Integrate OpenTelemetry spans for cross-service agent tracking
- **Checkpoint compression**: Use zstd/gzip to reduce storage for large context
- **Multi-region resilience**: Replicate checkpoints across regions for disaster recovery
- **Time-travel debugging**: Replay agent execution from any historical checkpoint
- **Cost attribution**: Track token usage and cost per session/sub-agent (per provider)
- **Partial resume**: Resume from mid-checkpoint (skip completed sub-tasks within a phase)

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
