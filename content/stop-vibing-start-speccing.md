---
title: Stop Vibing. Start Speccing.
subtitle: Vibe coding made it cheap to start building. Spec-Driven Development makes it possible to finish.
description: How Spec-Driven Development gives AI coding agents something real to aim at — turning confident-but-wrong output into shippable software.
tags: [Software Engineering, Agentic AI, Developer Tools]
category: Agentic AI
readTime: 8 min
publishDate: 2026-06-14
medium: https://medium.com/@msharsha
cover: cover-stop-vibing
references:
  - GitHub. (2025). Spec-Kit: Spec-Driven Development | https://github.com/github/spec-kit/blob/main/spec-driven.md
  - Thoughtworks. (2025). Spec-Driven Development: Unpacking One of 2025's Key New Practices | https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices
  - Anthropic. (2025). Claude Code: Best Practices for Agentic Coding | https://www.anthropic.com/engineering
---

There is a moment every developer eventually has with an AI coding agent. You give it a brief, informal prompt. The files start appearing. Routes get wired, migrations get created, components take shape. For a few minutes, you feel like you skipped a full week of work.

Then your designer asks about the edge case you didn't mention. The agent hardcoded something you intended to be configurable. Your data model uses `QuoteSummary` in the frontend and `ProjectEstimate` in the backend. The tests pass, but only because they don't really test anything.

The code was confident. It just wasn't correct.

This is the failure mode that **Spec-Driven Development (SDD)** is designed to prevent — not by slowing agents down, but by giving them something real to aim at before they start swinging.

* * *

## The problem isn't the model

Here is the thing that gets missed in every "vibe coding is dead" hot take: the model isn't the issue. The issue is that AI agents are very good at producing *plausible* output, and plausible is not the same as correct.

When you say "build me a renovation tracker," the agent doesn't stop and ask whether projects can exist without photos, whether estimates should be editable, or what happens when the AI generation fails. It fills in those blanks itself. Quietly. Confidently. Wrong.

> The better the agent gets at execution, the more leverage your instructions carry — and the more expensive misdirection becomes.

There's also the context decay problem. AI agents are stateless. Every new chat window starts fresh. On a large project with multiple developers and multiple sessions, you lose the thread. Why was the data cleaned that way? Why was that approach rejected? The code remembers nothing; neither does the agent.

Andrej Karpathy, who coined the phrase "vibe coding" back in early 2025, said it plainly a year later: the era of vibe coding is already ending. What comes next is what he called **agentic engineering** — orchestrating agents against detailed specifications, with human oversight still firmly in the loop.

SDD is how you do that orchestration.

* * *

## What SDD actually is

Spec-Driven Development is a workflow where every meaningful feature starts as a written artifact *before* it becomes code. Not a 40-page requirements document. Not a frozen spec nobody opens after kickoff. A living source of truth — scoped, readable, and stored in your repository alongside the code it governs.

The mental shift is simple: **the spec is the primary artifact, and code is what gets generated from it.** Think of it the way you think about source files and compiled binaries. You maintain the source. The output follows.

A useful spec addresses seven things: the user problem, the primary user, the happy path, the edge cases, the constraints, what "done" means, and how you'll verify it. Notice what's missing: every implementation detail. The spec constrains the problem space. The agent is creative within it.

* * *

## What a spec actually looks like

Specs are often described in ways that make them sound heavier than they are. Here's a minimal, honest version — the kind you'd actually write for a real feature:

```
# Renovation assistant

## Goal
Help homeowners turn rough renovation ideas into structured
project plans with editable summaries and rough cost ranges.

## Core flow
1. User creates a project (title + description required).
2. User optionally uploads room photos (JPEG, PNG).
3. System generates a structured plan with cost ranges.
4. User can edit generated content before saving.

## Acceptance criteria
- User can create a project with no photos.
- User can upload multiple supported images.
- Tests cover: missing photos, failed uploads, editable estimates.
```

This document is small, but it changes everything about what happens next. The agent isn't inferring the product anymore — it has a contract. A reviewer can challenge the acceptance criteria. A tester can turn edge cases into test cases. A new teammate six months from now can understand why the code exists.

* * *

## The real question

The question isn't whether to write specs — it's at what point in the process you want to do your hard thinking.

Vibe coding defers the thinking. You discover what you actually needed when you see what the agent built. That's fine for a prototype with no future. For anything that has to survive contact with real users, real edge cases, and real teammates, deferring the thinking means you're borrowing against yourself.

SDD front-loads the thinking into a document instead of distributing it across a series of correction prompts. The spec is the map. The agent still does the flying.

> The agents aren't slowing down. Getting better at directing them is the only lever you have.
