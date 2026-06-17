package complianceqa

import "testing"

func TestAnswerReturnsCitedStructuredResponse(t *testing.T) {
	// Arrange: wire fake retriever, access controller, generator, and review sink for one tenant-scoped question.
	// Act: call CompliancePipeline.Answer.
	// Assert: the answer is structured, includes citations, and every citation maps to an allowed retrieved chunk.
	t.Skip("TODO(human): implement cited structured response assertion")
}

func TestLowConfidenceRoutesToReviewQueue(t *testing.T) {
	// Arrange: make the generator return an answer below the pipeline confidence threshold.
	// Act: call Answer with a normal-risk question.
	// Assert: NeedsReview becomes true and the draft answer plus evidence are enqueued for human review.
	t.Skip("TODO(human): implement low-confidence review routing assertion")
}

func TestHighRiskQuestionRoutesToReviewQueue(t *testing.T) {
	// Arrange: make the generator return a well-cited high-confidence answer for a high-risk question.
	// Act: call Answer.
	// Assert: high-risk policy still routes the answer to review, independent of confidence score.
	t.Skip("TODO(human): implement high-risk review routing assertion")
}

func TestValidateCitationsRejectsUnretrievedEvidence(t *testing.T) {
	// Arrange: create an answer citing a chunk that was not returned by retrieval/access filtering.
	// Act: call ValidateCitations.
	// Assert: validation fails so the pipeline can route unsupported claims to review.
	t.Skip("TODO(human): implement unretrieved citation rejection assertion")
}

func TestIncrementalIndexerSkipsUnchangedDocument(t *testing.T) {
	// Arrange: fake an index store whose current document version matches the incoming document.
	// Act: call ReindexChanged.
	// Assert: it returns changed=false and does not stage or promote chunks.
	t.Skip("TODO(human): implement unchanged document assertion")
}

func TestLatencyHarnessCalculatesP95(t *testing.T) {
	// Arrange: provide unordered latency samples around the 2s budget.
	// Act: call LatencyHarness.P95.
	// Assert: the percentile calculation matches the chosen method and can be compared to the SLA.
	t.Skip("TODO(human): implement latency harness assertion")
}

