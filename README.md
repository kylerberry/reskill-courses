░█▀▄░█▀▀░█▀▀░█░█░▀█▀░█░░░█░░
░█▀▄░█▀▀░▀▀█░█▀▄░░█░░█░░░█░░
░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀

Hands-on, terminal-first courses for engineers practicing production AI/ML and distributed systems design.

**Reskill** is a response to deskilling: the softening of engineering judgment that can happen when you rely too heavily on AI. These courses use AI to help you build and rebuild your system design and coding reflexes, so you stay sharp instead of outsourcing the hard thinking.

Each course is a sequence of code-backed architecture challenges. You will reason through a production scenario, write tests, implement focused `TODO(human)` sections, run the test suite, and re-grade your understanding at the end.

## Course Tracks

| Track | Language | Challenges |
|---|---:|---|
| `agentic-systems/` | Python | Agent session management, prompt caching, RAG document Q&A, multi-tenant LLM gateway |
| `distributed-systems/` | Python | Distributed rate limiting, webhook delivery guarantees, feature store write paths, global leaderboards |
| `rag-mastery/` | Go | RAG ingestion, hybrid retrieval, production ops, compliance questionnaire QA |

Each track contains 4 numbered challenges. Every challenge includes a problem statement, learning objectives, starter implementation, skip-style tests, and persistent `STATE.md` progress tracking.

## Learning Protocol

Every challenge follows the same loop:

1. **Cold answer** — Answer a generated design question before research or code review.
2. **Red tests** — Unskip/write tests one at a time until they fail for the right reason.
3. **Scaffold + implement** — Fill in the `TODO(human)` sections.
4. **Run and fix** — Run tests, debug, and record notable discoveries.
5. **Re-grade** — Answer the original cold question again and compare your improvement.

Do not inspect starter implementation code before your cold answer is recorded.

## Why the Cold Answer Comes First

The cold answer uses two learning techniques: **Generation Effect** and **Productive Failure**.

Trying to generate an answer—even if you guess wrong—primes your brain to understand and retain the correct information much better than if you had just been told the answer. Your first answer becomes a baseline; the re-grade shows what changed after testing and implementation.

## Getting Started

You will want to use a coding agent like Claude Code or another coding agent and a code-editing IDE open at the same time—VS Code, Windsurf, Zed, Cursor, or similar—so you can inspect files, edit tests/implementation, and keep integrated views visible while the agent guides the workflow.

1. Open this repository in your terminal and agent.
2. Tell your agent something like: **“Do a course”**, **“Start distributed-systems”**, or **“Start rag-mastery challenge 01.”**
3. Follow the agent’s prompts and instructions. It should begin with the cold-answer step.
4. Initialize the course environment and run tests when prompted.
5. Get reskilling!

### Python Tracks

From a Python challenge directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pytest
python -m pytest -v
```

Some tracks also include a `requirements.txt`; if present, install it:

```bash
python -m pip install -r ../requirements.txt
```

### Go Track

From a Go challenge directory:

```bash
go test ./...
```

If dependencies change while experimenting:

```bash
go mod tidy
```

## `/quiz-me` Skill

This repo also includes a project-scoped `quiz-me` skill for review sessions.

Use it when you want short-answer questions based on a course, track, or challenge:

```text
/quiz-me
/quiz-me rag-mastery
/quiz-me rag-mastery 01 02
/quiz-me distributed-systems 04
```

How it works:

- Asks one short-answer question at a time.
- Grades each answer on a 5-point scale.
- Gives brief feedback on what was correct or missing.
- Waits for you to say `next` before generating another question.

## Philosophy

These are not toy exercises. The challenges focus on production trade-offs: latency, cost, failure modes, tenant isolation, correctness, retrieval quality, caching, and operational boundaries.

The code is the artifact. The real goal is being able to explain and defend the design decisions that got you there.

## Roadmap

The biggest opportunity is to make each challenge more adversarial and production-shaped. Future improvements may include:

- Failure-injection tests for partitions, provider failures, stale data, retries, and degraded dependencies.
- Load and latency harnesses that force concrete trade-offs instead of only passing functional tests.
- Written design review prompts where learners defend architecture choices after implementation.
- Explicit trade-off scoring for cost, latency, correctness, operability, and security.
- Postmortem questions after bugs or failed tests to turn debugging into durable learning.

## Requests and Improvements

Have an idea for a new course, a language port, a challenge topic, or another improvement? Open an issue with the request and any relevant context.
