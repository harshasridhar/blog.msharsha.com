---
title: The Elephant-Goldfish Model Isn't a Model. It's a Review Habit.
subtitle: Google open-sourced a plugin that pairs one AI session that remembers everything with several that remember nothing. The forgetful ones are the point.
description: Google's Elephant-Goldfish Model is a workflow, not a new AI model. Here's how its two memory roles work, how it differs from Spec Kit and OpenSpec, and where it breaks.
tags: [Agentic AI, AI Engineering, Spec Driven Development]
category: Agentic AI
readTime: 10 min
publishDate: 2026-11-03
cover: cover-elephant-goldfish-model-review-habit
references:
  - Google. (2026). Elephant-Goldfish Model: open-source skills for designing and reviewing software with AI agents | https://github.com/google/elephant-goldfish-model
  - Google Open Source Blog. (2026). Introducing the Elephant-Goldfish Model plugin: scaling design-driven AI software development | https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html
  - Help Net Security. (2026). Google open-sources the Elephant-Goldfish Model plugin its engineers use to catch AI coding mistakes | https://www.helpnetsecurity.com/2026/10/26/google-elephant-goldfish-model-plugin/
  - Digital Applied. (2026). Google's Elephant-Goldfish Method for AI Design Reviews | https://www.digitalapplied.com/blog/google-elephant-goldfish-agent-design-review
  - Holland, C. (2026). Elephants Never Forget. That's the Problem. | https://www.hollandtech.net/elephants-never-forget/
  - GitHub. Spec Kit | https://github.com/github/spec-kit
  - Fission AI. OpenSpec | https://github.com/Fission-AI/OpenSpec
---

When Google released the Elephant-Goldfish Model last month, a lot of people read the name and assumed a new model had shipped. Another architecture, another memory trick, another benchmark chart.

It isn't any of that. There are no weights. Nothing was trained. The Elephant-Goldfish Model, or EGM, is a set of skills you install into a coding agent, and what it automates is something engineers have done by hand for decades: hand your design to someone who wasn't in the room and ask them what's missing.

The twist is who it picks for that job. A reviewer with no memory at all.

* * *

## Why the agent that designed it can't review it

Think about the last time you proofread your own writing. You read what you meant, not what's on the page. Your brain supplies the missing word without telling you.

Long AI sessions do the same thing. After an hour of back-and-forth about a feature, the agent has absorbed your constraints, your rejected options, the side comment about the legacy billing service. All of that sits in context, so when it drafts a design, gaps don't register as gaps. The agent can see the answer even though the document doesn't contain it.

Google's own post describes AI velocity as having "silently introduced a potential reliability crisis," where speed without structure means "auto-scaling our mistakes rather than simply writing code faster." The failure they're pointing at isn't a dumb model. It's a smart one, deep in a conversation, quietly filling blanks.

So EGM splits the work by how much each session is allowed to remember. The repo's tagline says it in seven words: *Design with an elephant. Review with a goldfish.*

## The two memory types

The **elephant** is one long-running session that holds the whole project: architecture, history, the decisions and why they were made. It brainstorms with you and drafts the design doc. Under EGM's rules it writes no code.

The **goldfish** is the opposite. Fresh sessions, zero conversation history. A goldfish gets the design document and the relevant source code, and nothing else. If the doc doesn't say it, the goldfish doesn't know it.

You sit above both and make the calls. The project describes the human as the one who arbitrates trade-offs and approves the design before any implementation starts.

<figure class="diagram">
  <svg viewBox="0 0 720 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Elephant drafts a design doc, three goldfish reviewers read only that doc, the human approves, and findings loop back to the elephant">
    <style>
      .node { fill: none; stroke: currentColor; stroke-width: 1.5; }
      .label { font: 600 13px Inter, system-ui, sans-serif; fill: currentColor; }
      .sub { font: 400 11.5px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.7; }
      .arrow { stroke: currentColor; stroke-width: 1.5; fill: none; marker-end: url(#egm1); }
      .dash { stroke: currentColor; stroke-width: 1.5; fill: none; stroke-dasharray: 5 4; marker-end: url(#egm1); }
    </style>
    <defs>
      <marker id="egm1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
      </marker>
    </defs>
    <rect class="node" x="20" y="105" width="120" height="56" rx="8"/>
    <text class="label" x="80" y="130" text-anchor="middle">Elephant</text>
    <text class="sub" x="80" y="148" text-anchor="middle">full context</text>
    <rect class="node" x="190" y="105" width="120" height="56" rx="8"/>
    <text class="label" x="250" y="130" text-anchor="middle">Design doc</text>
    <text class="sub" x="250" y="148" text-anchor="middle">the only handoff</text>
    <rect class="node" x="360" y="30" width="190" height="44" rx="8"/>
    <text class="label" x="455" y="57" text-anchor="middle">Goldfish: explain it back</text>
    <rect class="node" x="360" y="111" width="190" height="44" rx="8"/>
    <text class="label" x="455" y="138" text-anchor="middle">Goldfish: attack it</text>
    <rect class="node" x="360" y="192" width="190" height="44" rx="8"/>
    <text class="label" x="455" y="219" text-anchor="middle">Goldfish: ready to build?</text>
    <rect class="node" x="590" y="105" width="110" height="56" rx="8"/>
    <text class="label" x="645" y="130" text-anchor="middle">You</text>
    <text class="sub" x="645" y="148" text-anchor="middle">approve or revise</text>
    <path class="arrow" d="M140,133 L190,133"/>
    <path class="arrow" d="M310,133 L360,52"/>
    <path class="arrow" d="M310,133 L360,133"/>
    <path class="arrow" d="M310,133 L360,214"/>
    <path class="arrow" d="M550,52 L590,125"/>
    <path class="arrow" d="M550,133 L590,133"/>
    <path class="arrow" d="M550,214 L590,141"/>
    <path class="dash" d="M645,161 L645,258 L80,258 L80,161"/>
    <text class="sub" x="362" y="274" text-anchor="middle">findings go back to the elephant</text>
  </svg>
  <figcaption>The design doc is the only thing that crosses from the elephant's side to the goldfish's side.</figcaption>
</figure>

That last point is the whole mechanism. The document becomes the only channel between the two. Anything that matters has to be written down, or it doesn't survive the trip.

## How it actually runs

Google's post frames the workflow as three phases. The repo ships seven skills: brainstorm, draft, resolve, bootstrap (document an existing codebase), review, review-loop, and a drift report that compares your specs against current code.

The core loop looks like this:

1. **Brainstorm** with the elephant under a strict no-code rule. You explore options and trade-offs, nothing gets built.
2. **Draft** a Markdown design document: problem, technical plan, alternatives considered, and an implementation plan with specific file paths.
3. **Review** with goldfish, which is where it gets interesting.

The review isn't one pass. The repo's `egm-review` skill defines five stages, each handed to fresh subagents:

| Stage | Who | What it checks |
|---|---|---|
| Zoom-out | Zoom-out reviewer | Does the design fit the wider system? |
| Comprehension | Comprehension reviewer | Can a reader with no context explain the design back accurately? |
| Critic review | Design, structural, and style personas | Gaps, edge cases, hidden dependencies, unstated assumptions |
| Zoom-out (again) | Zoom-out reviewer | Does the design still fit after the critic fixes? |
| Implementation readiness | Readiness, codebase-details, and style personas | Are file paths, data structures, and function signatures present and unambiguous? |

The comprehension step is the cheap, clever one. If a reader with no context can't summarize your design correctly, the prose is the problem, and you find out before a single line of code exists.

> The goldfish has no way to be polite about a gap. It can't remember the conversation where you'd have told it.

## Isn't this just spec-driven development?

Fair question. If you've used Spec Kit or OpenSpec, EGM probably sounds familiar. Specs first, code second, human in the loop.

The overlap is real. The difference is what each tool is trying to solve.

| | Spec Kit | OpenSpec | EGM |
|---|---|---|---|
| **Center of gravity** | A guided pipeline: constitution, specify, plan, tasks, implement, converge | A change lifecycle: propose, apply, archive | A review protocol: elephant drafts, goldfish attacks |
| **What a spec is** | An upfront description of what to build | Living specs of current behavior, with each change in its own folder under `changes/` | One Markdown design doc, down to file paths and signatures |
| **Existing codebases** | Built around a feature pipeline; the README also covers bug fixing and assessments | Stated goal: "built for brownfield not just greenfield" | Bootstrap skill documents what exists; drift report checks spec against code |
| **Fresh-context review** | Has a converge step; the docs I read don't describe a zero-context reviewer | None documented as a separate stage | The defining feature |

Spec Kit and OpenSpec mostly answer *where does the spec live, and how does work flow from it?* EGM answers a different question: *how do I know this spec isn't just its author's blind spots, written down?*

A caveat on that table. "Not documented" doesn't mean "doesn't exist." Spec Kit's docs mention clarification, checklist, and consistency-analysis steps that may catch some of the same problems, and I haven't tested them side by side. I also couldn't find any head-to-head comparison that includes EGM, so this one is mine. Treat it as a reading of the READMEs.

If you want a combined setup, one natural fit is OpenSpec's `changes/` folder to hold the proposal and a goldfish review before you hit apply. That's my suggestion. None of the three projects documents it.

## Isn't this just plan mode?

Same question from a different direction. Most coding agents now have a plan-first flow: the agent explores read-only, proposes an approach, you approve it, and then you switch on auto-accept edits and let it run. That's a real step up from prompting straight into code. If you already work this way, you've captured part of what EGM is after.

Here's where the two diverge. This comparison describes typical use of plan mode, so your setup may differ.

| | Plan mode, then auto-accept | EGM |
|---|---|---|
| **Who challenges the plan** | You, reading the agent's proposal | Fresh sessions try to break it first, then you read it |
| **Reviewer's context** | The session that wrote the plan, unless you ask for a separate reviewer | Zero context, by design |
| **Where the plan lives** | A Markdown file. Claude Code, for example, writes it under `~/.claude/plans/` by default (configurable), outside your repo | A Markdown design doc, saved to `docs/designs/` by default or a directory you configure |
| **Who does the building** | The same session, or subagents if you tell it to | Out of scope: you review, approve, then build |
| **Typical level of detail** | Whatever the agent wrote up, often a list of steps | Pushed down to file paths, data structures, signatures by the readiness check |
| **When gaps surface** | When you spot them, or when the code exposes them | At review, before code exists |

The last row is the one that matters. In plan mode, the session that holds all the context writes the plan, and your approval lands when the plan *looks* plausible. A plan that reads well passes. The missing error path or the vague contract between two components only shows up once code exists.

Two things plan mode already does well are worth crediting. The plan is a real file, not something lost in scrollback. And you can tell it to hand the work to subagents, which keeps the main context clean and lets pieces run in parallel. Neither of those, though, puts anyone independent in front of the plan. A subagent that executes it inherits its gaps and finds them the hard way, halfway through building.

You can bolt a reviewer on yourself. Ask plan mode to spawn a subagent to critique the plan before you approve it, and you've done a hand-rolled goldfish. That's worth doing. What EGM adds is that the protocol is already written down: the reviewer personas, the staged checks, the readiness bar. You don't have to remember to ask, or phrase the ask well, every time.

Without that review, the gap surfaces after the build, and auto-accept has already done what it was asked to do. The first moment you look closely is the diff, which is a much bigger and noisier artifact than a paragraph in a design doc. Fixing the gap now means rewriting code, re-reading the diff, and re-running tests. Fixing it in the doc means editing a sentence.

<figure class="diagram">
  <svg viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two timelines: with plan mode a gap is found after the code is written, with EGM the same gap is found at goldfish review before the code is written">
    <style>
      .node { fill: none; stroke: currentColor; stroke-width: 1.5; }
      .label { font: 600 12.5px Inter, system-ui, sans-serif; fill: currentColor; }
      .sub { font: 400 11px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.7; }
      .arrow { stroke: currentColor; stroke-width: 1.5; fill: none; marker-end: url(#egm2); }
    </style>
    <defs>
      <marker id="egm2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
      </marker>
    </defs>
    <text class="label" x="20" y="52">Plan mode,</text>
    <text class="label" x="20" y="69">then auto-accept</text>
    <rect class="node" x="190" y="30" width="110" height="52" rx="8"/>
    <text class="label" x="245" y="54" text-anchor="middle">Plan</text>
    <rect class="node" x="320" y="30" width="110" height="52" rx="8"/>
    <text class="label" x="375" y="54" text-anchor="middle">You approve</text>
    <rect class="node" x="450" y="30" width="110" height="52" rx="8"/>
    <text class="label" x="505" y="54" text-anchor="middle">Code</text>
    <rect class="node" x="580" y="30" width="110" height="52" rx="8"/>
    <text class="label" x="635" y="52" text-anchor="middle">Gap found</text>
    <text class="sub" x="635" y="68" text-anchor="middle">after code exists</text>
    <path class="arrow" d="M300,56 L320,56"/>
    <path class="arrow" d="M430,56 L450,56"/>
    <path class="arrow" d="M560,56 L580,56"/>
    <text class="label" x="20" y="142">EGM</text>
    <rect class="node" x="190" y="120" width="110" height="52" rx="8"/>
    <text class="label" x="245" y="144" text-anchor="middle">Draft</text>
    <rect class="node" x="320" y="120" width="110" height="52" rx="8"/>
    <text class="label" x="375" y="142" text-anchor="middle">Goldfish review</text>
    <text class="sub" x="375" y="158" text-anchor="middle">gap found here</text>
    <rect class="node" x="450" y="120" width="110" height="52" rx="8"/>
    <text class="label" x="505" y="144" text-anchor="middle">You approve</text>
    <rect class="node" x="580" y="120" width="110" height="52" rx="8"/>
    <text class="label" x="635" y="144" text-anchor="middle">Code</text>
    <path class="arrow" d="M300,146 L320,146"/>
    <path class="arrow" d="M430,146 L450,146"/>
    <path class="arrow" d="M560,146 L580,146"/>
  </svg>
  <figcaption>Illustrative: the same gap, caught at different points in the process.</figcaption>
</figure>

Be careful not to oversell this, though. EGM doesn't remove iteration. It moves it earlier and adds some up front: a draft, a review round, a few resolved findings. That trade only pays off when a change is big enough that rework would hurt. For a small fix, plan mode alone is the right amount of process. And I haven't seen measured numbers on how much rework it saves, so treat the benefit as a reasonable argument, not a proven result.

The two also stack. Here's a cheap version that needs no plugin, and it's my suggestion rather than anything the project documents. Let plan mode write its plan file. Point a clean session or a subagent at that file, with none of the surrounding conversation, and ask it to explain the plan back and list what's ambiguous. Fix the plan. Only then approve, turn on auto-accept, and let subagents build. If you want the plan versioned and reviewable by teammates, copy it into your repo first.

## What a goldfish catches

Here's a hypothetical, written for this post, not taken from a real run. Say the elephant's draft contains this paragraph:

```
## Retry policy
Failed webhook deliveries are retried with exponential backoff.
After the retry limit, the event is moved to the dead-letter queue.
Consumers must handle duplicates.
```

To the elephant, that's complete. Twenty minutes earlier you'd both agreed on five attempts with a 30-second base delay, and the dead-letter queue is the one ops already monitors.

A goldfish reads the same paragraph and asks:

- What is "the retry limit"? A number?
- What's the backoff base, and is there a cap or jitter?
- Who drains the dead-letter queue, and how would anyone know it was filling?
- "Consumers must handle duplicates": through what? Is there an idempotency key, and where is it generated?
- The readiness check adds one more: this section names no file, module, or function where retry logic lives.

None of those are exotic. They're what a new teammate would ask in their first week. The elephant couldn't ask them because it had already answered them, in a conversation the document doesn't contain.

## Using both memory types in your own work

You don't need Google's plugin to borrow the idea, though the repo's skills and reviewer personas save a lot of setup. A few habits from how EGM is built:

- **Make the spec the only handoff.** If a fresh agent can't build the right thing from the doc alone, neither can the next person on the team, or you in three months.
- **Run the explain-back test.** Open a clean session, paste the design, and ask for a summary. Compare it to what you meant. This costs almost nothing.
- **Check readiness at the level of paths and signatures.** A design that says "add caching" is a wish. A design that names the file and the function is something you can review.
- **Keep the human gate.** The project is explicit that your judgment sits between review and code.

On when to use the full cycle, the getting-started guidance (as relayed by Digital Applied) is practical. Use it for multi-service changes, shared data models, and migrations that need rollback plans. Skip it for contained bug fixes and exploratory work. A full goldfish review of a one-line fix is process for its own sake, and the Digital Applied write-up flags the overhead too.

Setup notes worth knowing: install the whole repository, not just the skills, because the reviewer personas and document standards load at runtime. Put your artifact-directory config in your project instructions file. And the same write-up suggests trying it by hand, conversationally, on one real feature before you install anything.

## Who is actually using it?

Google's claim, from its open source post, is that "thousands of Googlers use this plugin every day to ship production Google code." Per the same post, it was developed internally for Google engineers first and is now open source under Apache 2.0.

One wrinkle on platforms: Google's launch post and Help Net Security describe Antigravity as the supported environment, with others coming. The repo's README now also lists Claude Code and Codex, with install commands, so the repo has moved ahead of the announcement.

That's Google describing its own usage, and the secondary coverage I read treats it that way. I found no measured numbers on defects caught or time saved, and I won't pretend there are any. The repo also says it isn't an officially supported Google product. For outside developers, the public record so far is mostly setup guidance and early write-ups, not long-run case studies. It's weeks old. Check back in six months.

## Where it breaks

The best critique I found comes from Charlie Holland, and it's worth taking seriously.

His core point: a goldfish can check that a document is complete and coherent. It can't check that it's *right*. "A perfectly coherent document can describe the wrong system," he writes. A design can be, in his words, "built on an assumption that was false on day one," and that assumption lives outside the document, where no goldfish can see it.

He adds a second, harder problem. To argue usefully with an elephant, you have to know when it's wrong about a design decision, not just a fact. His example is a tidy design with a managed queue, a serverless worker, and a vector store. Someone junior sees nothing obviously wrong. Someone experienced knows, as he puts it, that "the queue is fine at today's volume and a disaster at next year's," and that a boring Postgres table the elephant never mentioned would have done the job. His verdict: EGM is "a very good way to record judgement and test it for completeness," but "the judgement has to come from somewhere else."

Two more limits, from the write-ups I read:

- **Shared blind spots.** The Digital Applied write-up makes this point: if the elephant and every goldfish run on the same base model, they share its training and its characteristic mistakes. Fresh context removes conversation bias. It doesn't remove model bias.
- **No automatic security review.** Help Net Security notes that threat reviews aren't built in. You'd need to configure a custom reviewer persona for that.

None of this makes EGM useless. It makes it a tool for catching one specific class of failure: gaps that exist because the author knew too much. That class is bigger than it sounds.

* * *

## The part worth stealing

Strip away the plugin, the personas, the five stages. What's left is a small idea about trust: the thing that produced a document is the worst judge of whether it stands on its own.

Humans learned that long ago. It's why code review exists, and why you give a draft to someone who hasn't been living in it. EGM's contribution is making that reviewer cheap, fresh, and available at 2 a.m., and refusing to let it remember anything.

If you try it, start small. Pick one real design, run the explain-back test, and see what the goldfish asks. The repo is at [github.com/google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model), and Google's announcement is on the [Open Source Blog](https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html). Read both before you take my summary as gospel.
