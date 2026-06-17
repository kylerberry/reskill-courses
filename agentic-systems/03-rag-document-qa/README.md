# RAG Document Q&A

## Problem Statement

You are building an LLM-powered document Q&A service for enterprise customers. Each tenant uploads large document corpora (thousands of PDFs, hundreds of pages each) and queries them in natural language. The system must:

- Return answers with citations within **2 seconds at P95**
- Support **per-customer data isolation**
- Scale to **hundreds of concurrent enterprise tenants**

The interesting tension: it is not just "use a vector database." You must make real trade-offs around chunking strategy, embedding freshness, multi-tenant isolation at the index level, and what happens when retrieval confidence is low or a question spans many documents.

## Learning Objectives

1. Design a document ingestion pipeline with a principled chunking strategy
2. Implement multi-tenant isolation without blowing up infrastructure costs
3. Build a retrieval pipeline that meets a hard latency SLA under concurrent load
4. Handle retrieval uncertainty gracefully (low confidence, cross-document queries)

## Key Concepts

- **RAG (Retrieval-Augmented Generation)**: Retrieve relevant chunks -> pass to LLM as context -> generate grounded answer
- **Chunking strategy**: Fixed-size vs semantic vs document-structure-aware — each has cost/quality trade-offs
- **Embedding freshness**: When a document is updated, which embeddings go stale and how do you re-index efficiently?
- **Multi-tenant isolation**: Separate vector indexes vs metadata filtering on a shared index — cost vs latency vs security
- **Hybrid search**: Combining dense (vector) + sparse (BM25/keyword) retrieval for better recall
- **Reranking**: A second-pass model to re-score retrieved chunks before passing to LLM
- **Confidence scoring**: How do you know when retrieval failed? What is the fallback?

## What You Will Implement

1. **`chunk_document()`** — Decide how to split text into chunks. Consider: fixed-size windowing, overlap, sentence boundaries, page spans.
2. **`fuse_results()`** — Merge vector and keyword search results into a single ranked list. Consider: Reciprocal Rank Fusion, deduplication, score normalization.
3. **`assess_confidence()`** — Decide whether retrieval results are trustworthy enough to generate an answer. Consider: score thresholds, result count, score spread.

## How to Run Tests

```bash
python -m pytest test_rag_pipeline.py -v
```

## Scale Math

- 100 tenants x avg 10k chunks = 1M vectors total
- At 1536 dimensions (OpenAI ada-002): ~6GB RAM for flat index
- With namespaces: single Pinecone pod, query isolated by namespace
- P95 budget breakdown (target 2s):
  - Query embed: ~50ms
  - Vector search: ~100ms
  - Rerank: ~200ms
  - LLM generation: ~1200ms
  - Network/overhead: ~450ms

## Extension Ideas

- **Semantic chunking**: Use NLP to split at sentence/paragraph boundaries
- **Hierarchical chunks**: Store parent summaries alongside child chunks
- **Embedding refresh pipeline**: Detect updated documents and re-index only changed chunks
- **Cross-encoder reranking**: Integrate Cohere Rerank or local cross-encoder
- **Query rewriting**: Expand queries with synonyms or decompose complex questions

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
