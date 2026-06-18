# RAG Retrieval System

## Problem Statement

You are building the retrieval layer for compliance Q&A. Users ask natural-language questions that often contain exact legal and security terms: SOC 2, GDPR Article 28, DPA, subprocessors, retention period, encryption at rest. Your Go retriever must combine pgvector dense retrieval with Go-native sparse BM25 retrieval, rerank the candidates, and return a confidence level that controls whether generation is safe.

## Learning Objectives

1. Compare dense, sparse, and hybrid retrieval for compliance documents
2. Implement Reciprocal Rank Fusion (RRF) for combining ranked lists
3. Deduplicate results across dense and sparse sources
4. Add a reranking interface for cross-encoder-style precision improvement
5. Convert retrieval scores into confidence and fallback decisions

## Key Concepts

- **Dense retrieval**: Embedding similarity via pgvector, good for semantic matches
- **Sparse retrieval**: BM25/inverted index via a Go-native library such as Bluge or Bleve
- **Hybrid retrieval**: Combines semantic and exact-token signals
- **RRF**: `score += 1 / (k + rank)` for each ranked list containing the chunk
- **Reranking**: More expensive second-pass scoring on top candidates
- **Confidence scoring**: Uses top score, result count, score spread, and citation coverage

## What You Will Implement

1. **`HybridRetriever.FuseResults()`** — Merge dense and sparse result lists with RRF.
2. **`HybridRetriever.Retrieve()`** — Embed query, run dense + sparse search, fuse, rerank, and score confidence.
3. **`AssessConfidence()`** — Decide high/medium/low confidence from reranked results.
4. **`BlugeSparseSearcher`** — Implement Go-native sparse indexing/querying using Bluge or Bleve.

## How to Run Tests

```bash
go test ./...
```

## Latency Budget

Target P95 for retrieval before generation: ~400ms.

- Query embedding: ~50ms
- Dense pgvector search: ~75ms
- Sparse BM25 search: ~50ms
- Fusion/deduplication: ~5ms
- Reranking top 20: ~200ms
- Margin: ~20ms

## Extension Ideas

- Add query rewriting for synonyms and acronym expansion
- Add multi-query retrieval for broad cross-document questions
- Add MRR/NDCG evaluation fixtures
- Add per-tenant sparse indexes and compare with metadata filtering

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
