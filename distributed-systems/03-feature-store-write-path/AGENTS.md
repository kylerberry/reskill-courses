# Challenge 8: Feature Store Write Path — Temporal Consistency

## Problem Statement

Design the write path for an online feature store that receives updates from two sources:
- A **batch pipeline** that rewrites all features for an entity once per hour
- A **streaming pipeline** that pushes individual feature-value updates with sub-minute lag

Ensure model inference always reads a temporally consistent snapshot -- not a mix of fresh streaming and stale batch values.

## Learning Objectives

- Understand event-time vs processing-time in ML feature systems
- Implement conflict resolution using event timestamps
- Design atomic multi-feature writes with partial-write visibility control
- Reason about write ordering in dual-pipeline architectures

## Key Concepts

- **Event-time semantics**: Use the timestamp embedded in the event, not wall-clock arrival time
- **Conflict resolution**: Newer event_time always wins, regardless of which pipeline delivers it
- **Snapshot isolation**: Reads see a consistent point-in-time view
- **Atomic batch commits**: All features in a batch become visible together, or not at all

## What You Will Implement

1. `FeatureStore.__init__()` -- design internal data structures for committed and in-flight state
2. `FeatureStore.stream_write()` -- streaming write with event_time conflict resolution
3. `FeatureStore.get_features()` -- read consistent snapshot, never see uncommitted batch writes
4. `BatchWriteContext.__enter__()` -- register batch as in-progress
5. `BatchWriteContext.__exit__()` -- commit atomically with conflict resolution and rollback on error

## How to Run Tests

```bash
pytest test_feature_store.py -v
```

## Extension Ideas

- **Write-ahead logging**: Persist batch writes to a WAL before committing
- **Compaction**: Archive old event times to reduce memory footprint
- **Multi-entity transactions**: Commit batch writes across multiple entities atomically

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
