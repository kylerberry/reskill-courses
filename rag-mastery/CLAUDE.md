# RAG Mastery Claude Guide

This course is part of `courses-v2`, the Claude-exclusive version of the AI/ML Solutions Architect study curriculum. Challenges are pre-built; Claude should guide the learner through the prescribed workflow rather than generating new files from scratch.

## Startup Protocol (Run Once Per Course)

Before starting the first challenge, verify the environment is ready. Do not skip this — a broken environment derails the learning flow.

### 1. Check Go version

```bash
go version  # must be 1.22+
```

### 2. Confirm the first challenge tests run (all skipped or passing is expected)

```bash
cd 01-rag-ingestion-pipeline
go test ./...
```

You should see a list of skipped or passing tests. If you see compilation errors, fix the environment before continuing.

### 3. Go module hygiene

Each challenge has its own `go.mod`. If you add dependencies while experimenting:

```bash
go mod tidy
```

### Optional: PostgreSQL + pgvector

Some challenges describe production vector stores. Tests use in-memory fakes by default. Install PostgreSQL with pgvector only if you want to run against a real database:

```bash
# macOS
brew install postgresql@16 && brew services start postgresql@16

# Then install pgvector extension
```

## Challenge Workflow (Standard Order)

Every challenge follows this exact sequence — no exceptions:

1. **Cold answer** — Generate a fresh question from the challenge README's problem statement and learning objectives. Require the learner to answer before reading code. Record the generated question and answer in the challenge `STATE.md`.
2. **Red tests** — Have the learner remove skip markers from relevant tests and write assertions until tests fail for the expected missing implementation.
3. **Scaffold + implement** — Guide the learner through `TODO(human)` markers. These mark critical decision points or key learning objectives.
4. **Run and fix** — Run the challenge test suite and iterate. Capture notable discoveries in the challenge `STATE.md`.
5. **Re-grade** — Re-ask the original cold-answer question stored in `STATE.md`, compare the new answer to the original, assign a completion score, and update course `STATE.md`.

## State Management

- Update this course's `STATE.md` when a challenge is completed and scored.
- Update each challenge's `STATE.md` whenever progress changes, the cold answer is captured, or the learner makes a notable discovery.
- Challenge progress uses steps 1–5 matching the standard workflow.
- When all course challenges are completed, provide a congratulatory summary covering the main systems concepts practiced across the course.

## Claude Guidance Rules

- Do not skip the cold answer step.
- Do not inspect or explain implementation files before the cold answer is recorded.
- Do not implement `TODO(human)` sections unless the learner explicitly asks for a solution or implementation.
- Prefer hints, trade-off questions, and small next steps over direct answers.
- Keep explanations concise and tied to the challenge's learning objectives.
