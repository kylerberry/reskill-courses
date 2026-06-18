---
name: quiz-me
description: Quiz the learner on completed course or challenge objectives using short-answer questions. Accept optional course/challenge focus; if no state exists, fall back to README learning objectives and key concepts. Use when the user invokes /quiz-me or asks to be quizzed on course understanding.
---

# Quiz Me

Use this skill when the user wants short-answer quizzing on one or more courses or challenges in this repository.

## Invocation

The user may invoke this as:

- `/quiz-me`
- `/quiz-me rag-mastery`
- `/quiz-me rag-mastery 01 02`
- `/quiz-me 01-rag-ingestion-pipeline`
- Natural language such as “quiz me on courses 01 and 02”.

If the scope is ambiguous, ask one concise clarification question. Otherwise proceed.

## Scope Resolution

1. Identify the requested course, courses, challenge, or challenges.
2. If no scope is provided, choose from available completed or in-progress challenges in the current project.
3. Prefer course/challenge `STATE.md` files for targeting:
   - Completed challenges
   - Re-grade answers
   - Notable discoveries
   - Scores or weak areas
4. If state is missing, empty, stale, or says “not started,” fall back to each challenge `README.md`:
   - Problem statement
   - Learning objectives
   - Key concepts
   - What You Will Implement
   - Scale, latency, safety, or operational notes

## Quiz Loop

Run a one-question-at-a-time loop:

1. Ask exactly one short-answer question.
2. Keep the question focused on one concept or tradeoff.
3. Ask for a 2–5 sentence answer unless another format is better.
4. Wait for the user’s answer.
5. Grade the answer immediately.
6. Provide brief feedback:
   - Score using `N/5`
   - What was correct
   - What was missing or imprecise
   - One concise model-answer improvement when useful
7. The user can optionally ask questions for clarification or deeper understanding.
8. Wait for explicit user confirmation before continuing.
   - Treat `next`, `continue`, `another`, or similar as confirmation.
9. Generate a new question only after confirmation.

## Question Design

Prefer applied, short-answer questions over trivia. Mix question types across the session:

- Explain a design tradeoff.
- Compare two approaches.
- Diagnose a failure mode.
- Explain why a workflow step matters.
- Interpret a scoring, confidence, scale, or latency implication.
- Ask what metadata or isolation boundary is needed and why.
- Ask how intermediate results are combined and returned to the application/user, such as fusion, deduplication, reranking, confidence, and fallback behavior.

Avoid asking the same concept repeatedly unless the learner struggled with it.
When a concept has important adjacent mechanisms, either ask about those mechanisms explicitly or save them for a follow-up question. Do not expect the learner to cover unstated implementation details.

## Grading Rubric

Grade on a 5-point scale:

- `5/5`: Correct, complete, and uses relevant terminology or implications.
- `4/5`: Mostly correct with one minor omission or imprecision.
- `3/5`: Partially correct but misses an important mechanism, tradeoff, or consequence.
- `2/5`: Shows limited understanding; includes significant gaps or confusion.
- `1/5`: Mostly incorrect but attempts an answer.
- `0/5`: No meaningful answer.

Be direct but encouraging. Do not over-explain; keep feedback concise. Grade against the question actually asked, not against every related concept in the course objective. Mention adjacent missing concepts as optional follow-up, not as score penalties, unless the question explicitly asked for them.

## State Awareness

When course rules require state updates and the quiz is part of the official course workflow, update the relevant `STATE.md` after re-grade or meaningful progress. If this is an informal review quiz, do not modify state unless the user asks.

If state says a challenge is incomplete but the user says they completed it, mention the mismatch once and continue using README objectives as the source of truth.

## Response Style

Keep responses short. Use this structure:

```markdown
### Question X — <Course or Challenge Topic>

<Question>

Answer in 2–5 sentences.
```

For grading:

```markdown
**Grade: N/5**

<Brief assessment.>

Say **“next”** when ready.
```
