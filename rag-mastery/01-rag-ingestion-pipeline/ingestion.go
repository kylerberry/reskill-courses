package ingestion

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"strings"
)

type Document struct {
	ID       string
	TenantID string
	Title    string
	Text     string
	Metadata map[string]string
}

type Chunk struct {
	ID         string
	TenantID   string
	DocumentID string
	ParentID   string
	Text       string
	Index      int
	Metadata   map[string]string
}

type SearchResult struct {
	Chunk Chunk
	Score float64
}

type Chunker interface {
	Chunk(ctx context.Context, doc Document) ([]Chunk, error)
}

type Embedder interface {
	Embed(ctx context.Context, texts []string) ([][]float32, error)
}

type VectorStore interface {
	DocumentHash(ctx context.Context, tenantID, documentID string) (string, bool, error)
	DeleteByDocument(ctx context.Context, tenantID, documentID string) error
	UpsertChunks(ctx context.Context, chunks []Chunk, embeddings [][]float32, documentHash string) error
	Search(ctx context.Context, tenantID string, queryEmbedding []float32, limit int) ([]SearchResult, error)
}

type HeaderAwareChunker struct {
	MaxCharacters int
}

func (c HeaderAwareChunker) Chunk(ctx context.Context, doc Document) ([]Chunk, error) {
	if strings.TrimSpace(doc.Text) == "" {
		return nil, nil
	}

	// TODO(human): Implement chunking strategies that preserve section meaning, parent-child provenance, tenant/document metadata, and retrieval context.
	return []Chunk{{
		ID:         doc.ID + ":0",
		TenantID:   doc.TenantID,
		DocumentID: doc.ID,
		Text:       strings.TrimSpace(doc.Text),
		Index:      0,
		Metadata:   doc.Metadata,
	}}, nil
}

type ParentChildChunker struct {
	Parent Chunker
	Child  Chunker
}

func (c ParentChildChunker) Chunk(ctx context.Context, doc Document) ([]Chunk, error) {
	if c.Parent == nil || c.Child == nil {
		return nil, errors.New("parent and child chunkers are required")
	}

	// Learning objective: connect child chunks back to parent context without losing tenant/document isolation.
	return c.Child.Chunk(ctx, doc)
}

type IngestionPipeline struct {
	Chunker  Chunker
	Embedder Embedder
	Store    VectorStore
}

func (p IngestionPipeline) Ingest(ctx context.Context, doc Document) (int, error) {
	if p.Chunker == nil || p.Embedder == nil || p.Store == nil {
		return 0, errors.New("chunker, embedder, and store are required")
	}

	documentHash := hashText(doc.Text)
	storedHash, found, err := p.Store.DocumentHash(ctx, doc.TenantID, doc.ID)
	if err != nil {
		return 0, err
	}
	if found && storedHash == documentHash {
		return 0, nil
	}

	chunks, err := p.Chunker.Chunk(ctx, doc)
	if err != nil {
		return 0, err
	}
	texts := make([]string, 0, len(chunks))
	for _, chunk := range chunks {
		texts = append(texts, chunk.Text)
	}

	// TODO(human): Design ingestion orchestration around provider batching, ordering guarantees, retries, and atomic stale-delete/upsert behavior.
	embeddings, err := p.Embedder.Embed(ctx, texts)
	if err != nil {
		return 0, err
	}
	if len(embeddings) != len(chunks) {
		return 0, errors.New("embedding count does not match chunk count")
	}

	// Learning objective: keep changed-document reindexing atomic so retrieval never sees mixed old/new chunks.
	if err := p.Store.DeleteByDocument(ctx, doc.TenantID, doc.ID); err != nil {
		return 0, err
	}
	if err := p.Store.UpsertChunks(ctx, chunks, embeddings, documentHash); err != nil {
		return 0, err
	}
	return len(chunks), nil
}

type PGVectorStore struct{}

func (s PGVectorStore) DocumentHash(ctx context.Context, tenantID, documentID string) (string, bool, error) {
	// TODO(human): Implement tenant-scoped PGVectorStore methods for freshness, delete, upsert, and search with citation-ready metadata.
	return "", false, nil
}

func (s PGVectorStore) DeleteByDocument(ctx context.Context, tenantID, documentID string) error {
	// Learning objective: delete only tenant/document scoped rows.
	return nil
}

func (s PGVectorStore) UpsertChunks(ctx context.Context, chunks []Chunk, embeddings [][]float32, documentHash string) error {
	// Learning objective: upsert chunks and document hash transactionally while preserving provenance.
	return nil
}

func (s PGVectorStore) Search(ctx context.Context, tenantID string, queryEmbedding []float32, limit int) ([]SearchResult, error) {
	// Learning objective: search tenant-scoped vectors and return citation-ready chunk metadata.
	return nil, nil
}

func hashText(text string) string {
	sum := sha256.Sum256([]byte(text))
	return hex.EncodeToString(sum[:])
}
