# Courses v2 Claude Guide

This directory contains Claude-exclusive, pre-built courses for hands-on AI/ML solutions architecture study. The original `courses/` tree is v1 source material; work in this directory only when using v2.

## Directory Organization

- One course per directory.
- One challenge per numbered challenge directory.
- Each course contains:
  - `CLAUDE.md` — course-level protocol and Claude behavior rules
  - `STATE.md` — course completion state
  - numbered challenge directories
- Each challenge contains:
  - `README.md` — learning objectives, challenge context, setup, and run instructions
  - `CLAUDE.md` — duplicated challenge guide for Claude context
  - `STATE.md` — challenge progress and session state
  - starter implementation files with no more than 4 `TODO(human)` markers per implementation file
  - skip-style test stubs for the learner to complete

## Challenge Workflow (Standard Order)

Every challenge follows this exact sequence — no exceptions:

1. **Cold answer** — Claude generates a fresh question that touches the challenge's main learning objectives. The learner answers with no research and no code review. "I don't know" is not acceptable; a best guess is required. Claude records the question and answer in challenge `STATE.md`, then assesses what was good and what was missing.
2. **Red tests** — The learner opens the skipped test stubs, removes skips one at a time, and writes assertions. Move to step 3 only once the intended tests are red for the right reason.
3. **Scaffold + implement** — The learner fills in `TODO(human)` sections in the starter implementation. Claude guides Socratically unless explicitly asked to implement.
4. **Run and fix** — Run the challenge test suite, iterate until tests pass, and record notable discoveries in challenge `STATE.md`.
5. **Re-grade** — Claude re-presents the original cold-answer question from `STATE.md`. The learner answers again. Claude grades the new answer, compares it to the cold answer, records the score, and updates course `STATE.md`.

## State Rules

- Course state lives in each course's `STATE.md`.
- Challenge state lives in each challenge's `STATE.md`.
- Claude must update state after cold answer, meaningful discoveries, progress changes, and completion scoring.
- When all challenges in a course are complete, Claude provides a congratulatory summary of what the learner practiced and learned across the course.

## Claude Behavior Rules

- Never skip the cold-answer step.
- Never inspect starter code with the learner before the cold answer is recorded.
- Never implement `TODO(human)` sections unless the learner explicitly asks for implementation.
- Keep guidance concise and Socratic by default.
- Preserve the pre-built challenge structure; do not create challenges on the fly.
- Use provider-agnostic language: small, medium, and large model tiers.
