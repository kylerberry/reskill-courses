# Agentic Systems Claude Guide

This course is part of `courses-v2`, the Claude-exclusive version of the AI/ML Solutions Architect study curriculum. Challenges are pre-built; Claude should guide the learner through the prescribed workflow rather than generating new files from scratch.

## Startup Protocol (Run Once Per Course)

Before starting the first challenge, verify the environment is ready. Do not skip this — a broken environment derails the learning flow.

### 1. Check Python version

```bash
python --version  # must be 3.10+
```

### 2. Create and activate a virtual environment

From the course root (`agentic-systems/`):

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Verify pytest works

```bash
python -m pytest --version
```

### 5. Confirm the first challenge tests run (all skipped is expected)

```bash
cd 01-agent-session-manager
python -m pytest -v
```

You should see a list of skipped tests. If you see import errors or pytest crashes, fix the environment before continuing.

### Optional: Redis

Some challenges reference Redis for optional simulation. If Redis is unavailable, tests use in-memory fakes. Install Redis locally only if you want to run the simulation scripts:

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server && sudo service redis-server start
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
