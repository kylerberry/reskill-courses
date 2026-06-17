# RAG Ingestion Pipeline

## Problem Statement

You are building the ingestion backbone for a compliance document Q&A system. Enterprise customers upload policy documents, security questionnaires, SOC 2 reports, DPAs, and procedure manuals. Your Go pipeline must chunk documents, embed chunks, and store them in pgvector with enough metadata to support accurate retrieval and safe incremental updates.

## Learning Objectives

1. Design chunking strategies for structured compliance documents
2. Model parent-child chunks for retrieval precision plus generation context
3. Batch embeddings behind a provider-agnostic interface
4. Store vector rows in pgvector with tenant and document isolation metadata
5. Re-index changed documents without rebuilding a full corpus

## Key Concepts

- **Fixed-size chunking**: Simple and fast, but can break semantic units mid-sentence
- **Header-aware chunking**: Splits on document structure such as headings and sections
- **Sliding-window overlap**: Preserves context across chunk boundaries at higher storage cost
- **Parent-child chunking**: Index small child chunks, then fetch parent chunks for LLM context
- **Embedding freshness**: Updated documents require stale chunk deletion and replacement
- **pgvector schema**: Store `tenant_id`, `document_id`, `chunk_id`, `parent_id`, metadata, and embedding

## What You Will Implement

1. **`HeaderAwareChunker.Chunk()`** — Split policy text on headers and produce coherent sections.
2. **`ParentChildChunker.Chunk()`** — Create retrievable child chunks linked to larger parent chunks.
3. **`IngestionPipeline.Ingest()`** — Orchestrate hash check, chunking, embedding, stale delete, and upsert.
4. **`PGVectorStore` methods** — Implement tenant-scoped upsert/delete/search SQL with pgvector.

## How to Run Tests

```bash
go test ./...
```

## Scale Math

- 100 tenants x 10k chunks = 1M vectors
- 1536 dimensions x 4 bytes ~= 6KB per vector before index overhead
- 1M vectors ~= 6GB raw vector memory before metadata and HNSW/IVFFlat overhead
- Re-indexing 1 changed 50-chunk document is far cheaper than re-embedding 10k tenant chunks

## Extension Ideas

- Add a `goose` or `tern` migration for the pgvector schema
- Add token-aware chunk sizing with `tiktoken`-style estimates
- Add contextual retrieval by prepending section summaries before embedding
- Add batch retry and rate-limit handling for embedding providers

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
