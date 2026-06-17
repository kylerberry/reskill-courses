# Distributed Systems Design Claude Guide

This course is part of `courses-v2`, the Claude-exclusive version of the AI/ML Solutions Architect study curriculum. Challenges are pre-built; Claude should guide the learner through the prescribed workflow rather than generating new files from scratch.

## Course Environment

Primary language: **Python**.

Use Python 3.10+ from the challenge directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pytest
python -m pytest -v
```

Some challenges use optional local infrastructure such as Redis. If an import or service is unavailable, use the tests and README context to decide whether to fake that dependency while learning.

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
