package retrieval

import (
	"context"
	"errors"
	"sort"
)

type ConfidenceLevel string

const (
	ConfidenceHigh   ConfidenceLevel = "high"
	ConfidenceMedium ConfidenceLevel = "medium"
	ConfidenceLow    ConfidenceLevel = "low"
)

type  struct {
	ID         string
	TenantID   string
	DocumentID string
	ParentID   string
	Text       string
	Metadata   map[string]string
}

type SearchResult struct {
	Chunk       Chunk
	DenseScore  float64
	SparseScore float64
	FusedScore  float64
	RerankScore float64
	Sources     []string
}

type RetrievalResponse struct {
	Results    []SearchResult
	Confidence ConfidenceLevel
	Fallback   bool
}

type QueryEmbedder interface {
	EmbedQuery(ctx context.Context, query string) ([]float32, error)
}

type DenseSearcher interface {
	Search(ctx context.Context, tenantID string, embedding []float32, limit int) ([]SearchResult, error)
}

type SparseSearcher interface {
	Search(ctx context.Context, tenantID, query string, limit int) ([]SearchResult, error)
}

type Reranker interface {
	Rerank(ctx context.Context, query string, results []SearchResult, limit int) ([]SearchResult, error)
}

type HybridRetriever struct {
	Embedder   QueryEmbedder
	Dense      DenseSearcher
	Sparse     SparseSearcher
	Reranker   Reranker
	TopK       int
	RerankTopK int
	RRFK       float64
}

func (r HybridRetriever) Retrieve(ctx context.Context, tenantID, query string) (RetrievalResponse, error) {
	if r.Embedder == nil || r.Dense == nil || r.Sparse == nil || r.Reranker == nil {
		return RetrievalResponse{}, errors.New("embedder, dense searcher, sparse searcher, and reranker are required")
	}

	topK := r.TopK
	if topK == 0 {
		topK = 20
	}
	rerankTopK := r.RerankTopK
	if rerankTopK == 0 {
		rerankTopK = 5
	}

	embedding, err := r.Embedder.EmbedQuery(ctx, query)
	if err != nil {
		return RetrievalResponse{}, err
	}

	// TODO(human): Implement retrieval orchestration with query embedding, dense/sparse concurrency, reranking, and latency-aware error handling.
	denseResults, err := r.Dense.Search(ctx, tenantID, embedding, topK)
	if err != nil {
		return RetrievalResponse{}, err
	}
	sparseResults, err := r.Sparse.Search(ctx, tenantID, query, topK)
	if err != nil {
		return RetrievalResponse{}, err
	}

	fused := r.FuseResults(denseResults, sparseResults)
	reranked, err := r.Reranker.Rerank(ctx, query, fused, rerankTopK)
	if err != nil {
		return RetrievalResponse{}, err
	}
	confidence := AssessConfidence(reranked)
	return RetrievalResponse{Results: reranked, Confidence: confidence, Fallback: confidence == ConfidenceLow}, nil
}

func (r HybridRetriever) FuseResults(denseResults, sparseResults []SearchResult) []SearchResult {
	k := r.RRFK
	if k == 0 {
		k = 60
	}
	merged := map[string]SearchResult{}

	add := func(results []SearchResult, source string) {
		for i, result := range results {
			rank := float64(i + 1)
			current, ok := merged[result.Chunk.ID]
			if !ok {
				current = result
			}
			current.FusedScore += 1 / (k + rank)
			if source == "dense" {
				current.DenseScore = result.DenseScore
			} else {
				current.SparseScore = result.SparseScore
			}
			current.Sources = appendSource(current.Sources, source)
			merged[result.Chunk.ID] = current
		}
	}

	// TODO(human): Implement hybrid result fusion with deduplication, RRF weighting, and compliance-term ranking trade-offs.
	add(denseResults, "dense")
	add(sparseResults, "sparse")

	out := make([]SearchResult, 0, len(merged))
	for _, result := range merged {
		out = append(out, result)
	}
	sort.Slice(out, func(i, j int) bool {
		return out[i].FusedScore > out[j].FusedScore
	})
	return out
}

func AssessConfidence(results []SearchResult) ConfidenceLevel {
	if len(results) == 0 {
		return ConfidenceLow
	}
	top := results[0].RerankScore
	if top >= 0.85 && len(results[0].Sources) > 1 {
		return ConfidenceHigh
	}
	if top >= 0.55 {
		return ConfidenceMedium
	}
	// TODO(human): Calibrate confidence and fallback behavior from score distribution, result count, and citation coverage.
	return ConfidenceLow
}

type PGVectorDenseSearcher struct{}

func (s PGVectorDenseSearcher) Search(ctx context.Context, tenantID string, embedding []float32, limit int) ([]SearchResult, error) {
	// TODO(human): Implement tenant-scoped dense, sparse, and rerank provider adapters with normalized scores.
	return nil, nil
}

type GoNativeSparseSearcher struct{}

func (s GoNativeSparseSearcher) Search(ctx context.Context, tenantID, query string, limit int) ([]SearchResult, error) {
	// Learning objective: sparse search should preserve exact-term matching and tenant isolation.
	return nil, nil
}

type CrossEncoderReranker struct{}

func (r CrossEncoderReranker) Rerank(ctx context.Context, query string, results []SearchResult, limit int) ([]SearchResult, error) {
	if limit > len(results) {
		limit = len(results)
	}
	// Learning objective: reranking improves precision but must fit the retrieval latency budget.
	return results[:limit], nil
}

func appendSource(sources []string, source string) []string {
	for _, existing := range sources {
		if existing == source {
			return sources
		}
	}
	return append(sources, source)
}
