# RAG Compliance QA

## Problem Statement

You are building a standalone compliance questionnaire assistant in Go. It ingests customer compliance documents, retrieves relevant evidence, generates structured answers with citations, and routes uncertain or high-risk answers to human review. The system must enforce tenant isolation and target a 2s P95 answer latency.

## Learning Objectives

1. Explain the full source-docs-to-response RAG pipeline verbally
2. Integrate ingestion, hybrid retrieval, reranking, generation, and review routing
3. Handle cross-document answers with reliable citations
4. Support zero-downtime incremental re-indexing for updated compliance docs
5. Reason about latency, cost, tenant isolation, access control, and observability

## Core Pipeline

```text
[Source Docs] -> Chunking -> Embedding -> pgvector
                                             |
[User Query] -> Query Embedding -> Dense Search -> Retrieved Chunks
                          |       -> Sparse BM25  -> Fusion/Rerank
                          |                         |
                          +-------------------------v
                                  LLM + Prompt -> Structured Response + Citations
                                                   |
                                                   v
                                        Confidence / HITL Review
```

## What You Will Implement

1. **`CompliancePipeline.Answer()`** — End-to-end query path with tenant isolation, retrieval, generation, and review routing.
2. **`BuildContext()`** — Select cross-document context while preserving citation provenance.
3. **`ValidateCitations()`** — Ensure every answer citation maps to retrieved evidence.
4. **`ReviewQueue.Enqueue()`** — Route low-confidence or high-risk answers to human review.
5. **`IncrementalIndexer.ReindexChanged()`** — Swap updated document chunks without downtime.
6. **`LatencyHarness.P95()`** — Measure whether the system fits a 2s P95 budget.

## How to Run Tests

```bash
go test ./...
```

## Whiteboard Talking Points

- Start with ingestion: parse docs, chunk by structure, embed, upsert into pgvector
- Explain parent-child: retrieve precise child chunks, feed parent context to the model
- Explain hybrid retrieval: dense semantic search + sparse exact-token search + RRF
- Explain reranking: higher precision on top candidates within latency budget
- Explain confidence: threshold weak evidence, missing citations, and low coverage
- Explain HITL: route uncertain/high-stakes answers to review instead of hallucinating
- Explain isolation: tenant-scoped SQL/RLS and access-control filtering before generation
- Explain freshness: hash changed docs, re-index only dirty documents, atomically swap chunks
- Explain observability: MRR/NDCG, judge scores, fallback rate, P95/P99 latency, cost per answer

## Extension Ideas

- Add an HTTP API with `/ingest`, `/query`, and `/review` endpoints
- Add synthetic eval fixtures for questionnaire rows
- Add local embeddings and reranking for offline practice
- Add a load generator that simulates many tenants and hot query caching

## v2 Claude Workflow

This is a pre-built v2 challenge. Start with the cold-answer step before reading implementation code. Claude should generate a fresh cold-answer question from the problem statement and learning objectives, then record it in `STATE.md`.

### Setup

```bash
go test ./...
```

If you add dependencies while experimenting, run:

```bash
go mod tidy
```

Tests begin as skip-style stubs. During the red-tests step, remove skips one test at a time and replace them with assertions that should fail until the corresponding `TODO(human)` implementation is complete.
