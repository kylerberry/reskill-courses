# AI / Systems Design  — Hands-On Course Curriculum
A set of intensive, code-first system design courses for engineers building production AI/ML infrastructure. Each course is a structured progression through real-world architectural challenges, guided by Claude as a Socratic tutor.
This curriculum is pre-built, Claude-exclusive challenges designed around a prescribed learning protocol. The courses emphasize reasoning over memorization: you answer questions before seeing code, write failing tests before writing implementations, and re-grade yourself after each challenge to measure what you actually learned.
---
## Course Tracks
| Track | Language | Focus |
|-------|----------|-------|
| [`agentic-systems/`](../agentic-systems/) | Python | Session management, prompt caching, RAG pipelines, LLM gateways |
| [`distributed-systems/`](../distributed-systems/) | Python | Rate limiting, webhook delivery, feature stores, leaderboards |
| [`rag-mastery/`](../rag-mastery/) | Go | Ingestion pipelines, hybrid retrieval, production ops, compliance Q&A |
Each track contains **4 numbered challenges**. Every challenge is a self-contained design + implementation exercise with starter code, skip-style test stubs, and a problem grounded in real production constraints (cost, latency, fault tolerance, scale).
### Example Challenges
- **Agent Session Manager** — Design checkpointing and hierarchical resumption for multi-agent AI workflows where a single failure can waste $10–100 in LLM tokens.
- **Distributed Rate Limiting** — Enforce per-API-key limits across stateless gateway nodes with <5% overshoot and sub-millisecond enforcement latency.
- **RAG Ingestion Pipeline** — Chunk compliance documents, embed them, and store in pgvector with tenant isolation and incremental re-indexing.
- **Prompt Caching System** — Build a Redis-backed prefix cache with content-addressed invalidation and circuit breakers for graceful degradation.
---
## The Learning Protocol
Every challenge follows the **same five-step sequence**, enforced by Claude. No skipping steps. No peeking at code early.
### 1. Cold Answer
Claude generates a fresh question drawn from the challenge's problem statement and learning objectives. You answer it with **no research, no code review, and no "I don't know."** A best guess is required.
Your answer and the question are recorded in the challenge's `STATE.md`. Claude assesses what was strong and what was missing. This becomes the baseline against which your learning is measured.
### 2. Red Tests
You open the skip-style test stubs, remove `pytest.skip` (or equivalent) one test at a time, and write the assertions you expect to pass. The tests should be **red for the right reason** — failing because the implementation is incomplete, not because the test is wrong.
This step forces you to articulate expectations before writing code.
### 3. Scaffold + Implement
You fill in the `TODO(human)` markers in the starter implementation files. These mark critical decision points — the places where architectural trade-offs actually matter.
Claude guides Socratically by default: hints, trade-off questions, and small next steps rather than direct answers. If you explicitly ask for an implementation, Claude will provide it, but the default mode is deliberate struggle.
### 4. Run and Fix
You run the test suite, iterate until tests pass, and record any notable discoveries in `STATE.md`. These can be bugs you caught, assumptions that were wrong, or trade-offs you hadn't considered.
### 5. Re-Grade
Claude re-presents the **exact cold-answer question** from `STATE.md`. You answer again. Claude compares your new answer to the original, assigns a completion score, and updates the course-level `STATE.md`.
The delta between cold and re-grade answers is the measure of learning.
---
## How Claude Is Used
This curriculum is built specifically for Claude's tutoring style. The protocol leverages several characteristics of Claude's output:
**Socratic guidance** — Claude prefers asking "what happens if Redis is partitioned?" over stating "use a Lua script for atomicity." The `CLAUDE.md` files in each course reinforce this: keep explanations concise, tied to learning objectives, and probe with trade-off questions.
**Stateful session tracking** — Claude reads and updates `STATE.md` files after each step. This gives the conversation memory across sessions: the cold answer persists, the re-grade references it directly, and notable discoveries accumulate.
**Structured but not rigid** — The protocol is fixed, but the questions are generated fresh each time. Claude draws from the problem statement and learning objectives, so two runs of the same challenge can surface different angles.
**Provider-agnostic framing** — The curriculum avoids vendor-specific terminology where possible. Model tiers are referred to as small, medium, and large. This keeps the lessons durable as the provider landscape shifts.
### Claude Behavior Rules (from `CLAUDE.md`)
- Never skip the cold-answer step.
- Never inspect starter code with the learner before the cold answer is recorded.
- Never implement `TODO(human)` sections unless explicitly asked.
- Keep guidance concise and Socratic by default.
- Preserve the pre-built challenge structure; do not create new challenges on the fly.
---
## Directory Structure
```
.
├── CLAUDE.md                          # Top-level protocol and behavior rules
├── README.md                          # This file
├── agentic-systems/
│   ├── CLAUDE.md                      # Course-level rules
│   ├── STATE.md                       # Course completion state
│   ├── 01-agent-session-manager/
│   │   ├── README.md                  # Problem, objectives, setup
│   │   ├── CLAUDE.md                  # Challenge guide for Claude
│   │   ├── STATE.md                   # Challenge progress
│   │   ├── session_manager.py         # Starter implementation
│   │   └── test_session_manager.py    # Skip-style test stubs
│   ├── 02-prompt-caching/
│   └── ...
├── distributed-systems/
│   ├── CLAUDE.md
│   ├── STATE.md
│   ├── 01-distributed-rate-limiting/
│   └── ...
└── rag-mastery/
    ├── CLAUDE.md
    ├── STATE.md
    ├── 01-rag-ingestion-pipeline/
    └── ...
```
Each challenge contains at most **4 `TODO(human)` markers** per implementation file. This keeps the scope focused on the architectural decisions that matter rather than boilerplate.
---
## Getting Started
1. Pick a track and open the first challenge directory.
2. Open the challenge's `README.md` to understand the problem.
3. Start a Claude conversation in that directory and let it guide you through the protocol.
4. Do not read the starter implementation files until after your cold answer is recorded.
### Python Tracks
```bash
cd agentic-systems/01-agent-session-manager
python -m venv .venv
source .venv/bin/activate
python -m pip install pytest
python -m pytest -v
```
### Go Track
```bash
cd rag-mastery/01-rag-ingestion-pipeline
go test ./...
```
---
## Philosophy
**Production context over toy problems.** Every challenge includes scale math, cost implications, and failure modes you would actually encounter. The rate limiting challenge targets <5% overshoot. The RAG ingestion pipeline considers 1M vectors at 6GB raw memory. The session manager acknowledges that agent workflows can cost $10–100 per execution.
**Learning is measured, not assumed.** The cold-answer / re-grade cycle is not a gimmick. It forces retrieval practice, which is one of the most reliable ways to build durable understanding. The `STATE.md` files make that measurement explicit and persistent.
**Code is the artifact, reasoning is the goal.** You will write working implementations, but the point is not the code. It is the sequence of decisions you made — and could defend — to get there.
---
## Contributing
These challenges are pre-built and versioned. If you add a new challenge, follow the existing structure:
- `README.md` with problem statement, learning objectives, key concepts, what to implement, run instructions, and extension ideas
- `CLAUDE.md` duplicated from an existing challenge with updated context
- `STATE.md` with the standard progress template
- Starter implementation with no more than 4 `TODO(human)` markers
- Skip-style test stubs for the learner to activate
