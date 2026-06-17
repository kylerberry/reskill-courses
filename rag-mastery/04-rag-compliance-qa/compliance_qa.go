package complianceqa

import (
	"context"
	"errors"
	"sort"
	"time"
)

type Document struct {
	ID       string
	TenantID string
	Text     string
	Version  string
}

type Chunk struct {
	ID         string
	TenantID   string
	DocumentID string
	ParentID   string
	Text       string
	Score      float64
}

type Question struct {
	ID       string
	TenantID string
	UserID   string
	Text     string
	HighRisk bool
}

type Citation struct {
	DocumentID string `json:"document_id"`
	ChunkID    string `json:"chunk_id"`
	Excerpt    string `json:"excerpt"`
}

type Answer struct {
	QuestionID  string     `json:"question_id"`
	Text        string     `json:"text"`
	Confidence  float64    `json:"confidence"`
	Citations   []Citation `json:"citations"`
	NeedsReview bool       `json:"needs_review"`
}

type Retriever interface {
	Retrieve(ctx context.Context, question Question) ([]Chunk, error)
}

type Generator interface {
	Generate(ctx context.Context, question Question, context string) (Answer, error)
}

type AccessController interface {
	Filter(ctx context.Context, question Question, chunks []Chunk) ([]Chunk, error)
}

type ReviewSink interface {
	Enqueue(ctx context.Context, item ReviewItem) error
}

type CompliancePipeline struct {
	Retriever     Retriever
	Generator     Generator
	Access        AccessController
	Reviews       ReviewSink
	MinConfidence float64
}

func (p CompliancePipeline) Answer(ctx context.Context, question Question) (Answer, error) {
	if p.Retriever == nil || p.Generator == nil || p.Access == nil || p.Reviews == nil {
		return Answer{}, errors.New("retriever, generator, access controller, and review sink are required")
	}

	chunks, err := p.Retriever.Retrieve(ctx, question)
	if err != nil {
		return Answer{}, err
	}
	allowedChunks, err := p.Access.Filter(ctx, question, chunks)
	if err != nil {
		return Answer{}, err
	}
	contextBlock := BuildContext(allowedChunks)
	answer, err := p.Generator.Generate(ctx, question, contextBlock)
	if err != nil {
		return Answer{}, err
	}
	if err := ValidateCitations(answer, allowedChunks); err != nil {
		answer.NeedsReview = true
	}

	threshold := p.MinConfidence
	if threshold == 0 {
		threshold = 0.7
	}
	if question.HighRisk || answer.Confidence < threshold || answer.NeedsReview {
		// TODO(human): Implement review routing so low confidence, invalid citations, and high-risk questions fail closed without blocking safe answers.
		answer.NeedsReview = true
		if err := p.Reviews.Enqueue(ctx, ReviewItem{Question: question, Draft: answer, Evidence: allowedChunks}); err != nil {
			return Answer{}, err
		}
	}
	return answer, nil
}

func BuildContext(chunks []Chunk) string {
	// TODO(human): Select compact cross-document context that preserves source labels, parent-child provenance, and token budget.
	context := ""
	for _, chunk := range chunks {
		context += "[" + chunk.DocumentID + ":" + chunk.ID + "]\n" + chunk.Text + "\n\n"
	}
	return context
}

func ValidateCitations(answer Answer, chunks []Chunk) error {
	available := map[string]bool{}
	for _, chunk := range chunks {
		available[chunk.DocumentID+":"+chunk.ID] = true
	}
	for _, citation := range answer.Citations {
		if !available[citation.DocumentID+":"+citation.ChunkID] {
			return errors.New("citation does not map to retrieved evidence")
		}
	}
	// TODO(human): Enforce citation policy so non-refusal answers cite retrieved chunks and never cite unretrieved text.
	return nil
}

type ReviewItem struct {
	Question  Question
	Draft     Answer
	Evidence  []Chunk
	CreatedAt time.Time
}

type ReviewQueue struct {
	Items []ReviewItem
}

func (q *ReviewQueue) Enqueue(ctx context.Context, item ReviewItem) error {
	item.CreatedAt = time.Now()
	q.Items = append(q.Items, item)
	return nil
}

type IndexStore interface {
	DocumentVersion(ctx context.Context, tenantID, documentID string) (string, bool, error)
	StageChunks(ctx context.Context, document Document) error
	PromoteStagedChunks(ctx context.Context, tenantID, documentID, version string) error
}

type IncrementalIndexer struct {
	Store IndexStore
}

func (i IncrementalIndexer) ReindexChanged(ctx context.Context, document Document) (bool, error) {
	if i.Store == nil {
		return false, errors.New("index store is required")
	}
	currentVersion, found, err := i.Store.DocumentVersion(ctx, document.TenantID, document.ID)
	if err != nil {
		return false, err
	}
	if found && currentVersion == document.Version {
		return false, nil
	}
	// TODO(human): Implement zero-downtime corpus refresh with staging, validation, and atomic promotion.
	if err := i.Store.StageChunks(ctx, document); err != nil {
		return false, err
	}
	if err := i.Store.PromoteStagedChunks(ctx, document.TenantID, document.ID, document.Version); err != nil {
		return false, err
	}
	return true, nil
}

type LatencyHarness struct {
	Samples []time.Duration
}

func (h LatencyHarness) P95() time.Duration {
	if len(h.Samples) == 0 {
		return 0
	}
	samples := append([]time.Duration(nil), h.Samples...)
	sort.Slice(samples, func(i, j int) bool { return samples[i] < samples[j] })
	idx := int(float64(len(samples)-1) * 0.95)
	// Learning objective: align percentile math with the production metrics backend before comparing to a 2s SLA.
	return samples[idx]
}
