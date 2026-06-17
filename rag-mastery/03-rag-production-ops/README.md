# RAG Production Ops

## Problem Statement

You are hardening a compliance RAG system for production. Retrieval quality matters, but Principal-level design discussions focus on operational boundaries: tenant isolation, access control, hallucination controls, latency, cost, caching, and observability.

## Learning Objectives

1. Compare tenant isolation strategies for pgvector-backed RAG
2. Enforce row-level access control on retrieved chunks
3. Generate structured JSON answers for compliance questionnaire workflows
4. Evaluate groundedness and completeness with LLM-as-judge
5. Track retrieval quality, answer quality, and latency percentiles
6. Design cache invalidation around document updates

## Key Concepts

- **Tenant isolation**: Separate schema, separate table, metadata filter, or row-level security
- **Access control**: Filter by tenant, document ACLs, role, and user entitlement before generation
- **Structured output**: JSON schema reduces questionnaire format drift
- **Grounding**: Answer only from retrieved context and require citations
- **LLM-as-judge**: Score groundedness, completeness, citation support, and refusal correctness
- **Hot query caching**: Cache repeated questionnaire answers, invalidate on source updates
- **Observability**: MRR, NDCG, judge scores, fallback rate, P50/P95/P99 latency

## What You Will Implement

1. **`TenantRegistry.ResolveScope()`** — Decide pgvector namespace/schema/table scope for a tenant.
2. **`AccessPolicy.FilterChunks()`** — Remove chunks the user is not allowed to see.
3. **`AnswerGenerator.GenerateStructured()`** — Produce schema-shaped questionnaire answers with citations.
4. **`LLMJudgeEvaluator.Evaluate()`** — Score groundedness and completeness.
5. **`QueryCache` invalidation** — Invalidate tenant/document answers on document updates.
6. **`MetricsCollector.RecordQuery()`** — Track latency and quality signals.

## How to Run Tests

```bash
go test ./...
```

## Production Trade-Offs

| Strategy | Isolation | Cost | Operational complexity |
|---|---|---|---|
| Separate database per tenant | Strongest | Highest | Highest |
| Schema per tenant | Strong | Medium | Medium |
| Shared table + RLS | Strong if correct | Low | Medium |
| Metadata filter only | Weakest | Lowest | Low |

For interviews: call out that metadata filters are not a security boundary unless enforced below application code, ideally with database RLS or physically separated storage.

## Extension Ideas

- Add OpenTelemetry spans across retrieval, reranking, and generation
- Add Prometheus metrics endpoints
- Add eval fixtures for MRR/NDCG and hallucination rate
- Add cache stampede prevention for repeated questionnaire rows

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
