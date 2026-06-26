---
title: "Running in Circles, On Purpose"
subtitle: "Loop engineering is the layer above the harness — and the most valuable code you write now is the bit that decides when the agent stops."
description: Loop engineering is the new discipline above prompt, context, and harness engineering — designing what an agent does between tool calls, and when it's allowed to quit.
tags: [Loop Engineering, Agentic AI, AI Engineering]
category: Loop Engineering
readTime: 6 min
publishDate: 2026-06-26
cover: cover-loop-engineering
references:
  - Addy Osmani. (2026). Loop Engineering — Prompt to Self-Correcting | https://addyo.substack.com
  - Adnan Masood. (2026). Loop Engineering — A Guide for Engineers and Practitioners | https://medium.com/@adnanmasood/loop-engineering-a-guide-for-engineers-and-practitioners-893bb65ea943
  - Data Science Dojo. (2026). 10 Loop Engineering Design Patterns for AI Builders | https://datasciencedojo.com/blog/loop-engineering-design-patterns/
  - Ben Dickson. (2026). Demystifying Loop Engineering — Get More From AI Agents, Avoid Loopmaxxing | https://bdtechtalks.com/2026/06/22/ai-loop-engineering/
  - Geoffrey Huntley. (2025). The Ralph Loop | https://ghuntley.com
  - Shunyu Yao et al. (2022). ReAct — Synergizing Reasoning and Acting in Language Models | https://arxiv.org/abs/2210.03629
  - Anthropic. (2026). Claude Code — /loop and /goal Reference | https://docs.anthropic.com
---

A year ago, if a colleague walked into standup and said *I feel like I'm running in circles*, you'd assume they were close to a breakdown.

In 2026, you assume they're an agent.

That's not a punchline — well, it's a little bit of a punchline — it's the whole shift in one sentence. The loop stopped being a sign that something's gone wrong and became the thing you're building. Which means somebody has to engineer it.

That somebody is increasingly being called a loop engineer.

## So what is loop engineering?

The cleanest definition I've seen comes from Addy Osmani and Jonas Steinberger, who put a name on it in June 2026: *stop prompting your agents and start designing the loops that prompt them.*

Loop engineering is the discipline of designing what an agent does **between** model calls — what triggers the next step, who checks the work, and what counts as "done." The model is still doing the reasoning. You're designing the runtime that hands the model the next thing to reason about.

The shift underneath this is subtle but load-bearing. In a single-turn world, the unit of value is the response — did the model produce the right answer? In an agentic world, the unit of value is the **trajectory** — did the four-turn cycle land somewhere correct? If the model writes a buggy function on turn one, that's fine, as long as the loop runs the test on turn two, sees red on turn three, and patches it on turn four.

You stop optimizing the sentence. You start optimizing the path.

## A short lineage

This didn't come out of nowhere. The lineage is real, and short:

- **ReAct (2022)** — the original *reason → act → observe* loop from Yao et al. One model, one cycle, a human watching.
- **AutoGPT (2023)** — gave the loop a goal and let it self-prompt. Promptly became famous for spinning forever doing nothing, which set the field back a year and seeded the "agents are toys" skepticism.
- **The Ralph loop (2025)** — Geoffrey Huntley's bash one-liner that just runs the agent in a `while true` until tests pass. Crude, but the first time the loop itself was treated as the artifact.
- **`/loop` and `/goal` (2026)** — productized inside Claude Code, Codex, and friends. The loop now ships with the tool.

Four years, from "the model talks once" to "the model runs in a `while` loop with a budget."

## Anatomy of a loop

Strip away the marketing and a production loop has four parts. Get any one wrong and the whole thing fails in a different, expensive way.


<figure class="diagram">
  <svg viewBox="0 0 720 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Anatomy of an agent loop: trigger fires, model acts, verifier checks the work, stop rule decides whether to loop or exit">
    <style>
      .node { fill: none; stroke: currentColor; stroke-width: 1.5; }
      .label { font: 600 14px Inter, system-ui, sans-serif; fill: currentColor; }
      .sub { font: 400 12px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.65; }
      .arrow { stroke: currentColor; stroke-width: 1.5; fill: none; marker-end: url(#a); }
      .loop { stroke: currentColor; stroke-width: 1.5; fill: none; marker-end: url(#a); stroke-dasharray: 4 4; opacity: 0.7; }
    </style>
    <defs>
      <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
      </marker>
    </defs>
    <rect class="node" x="20"  y="110" width="140" height="70" rx="8"/>
    <text class="label" x="90"  y="140" text-anchor="middle">Trigger</text>
    <text class="sub"   x="90"  y="160" text-anchor="middle">cron, event, /goal</text>
    <rect class="node" x="200" y="110" width="140" height="70" rx="8"/>
    <text class="label" x="270" y="140" text-anchor="middle">Model + Tools</text>
    <text class="sub"   x="270" y="160" text-anchor="middle">reason, act, observe</text>
    <rect class="node" x="380" y="110" width="140" height="70" rx="8"/>
    <text class="label" x="450" y="140" text-anchor="middle">Verifier</text>
    <text class="sub"   x="450" y="160" text-anchor="middle">tests, evals, gates</text>
    <rect class="node" x="560" y="110" width="140" height="70" rx="8"/>
    <text class="label" x="630" y="140" text-anchor="middle">Stop Rule</text>
    <text class="sub"   x="630" y="160" text-anchor="middle">done? budget? loop?</text>
    <path class="arrow" d="M160,145 L200,145"/>
    <path class="arrow" d="M340,145 L380,145"/>
    <path class="arrow" d="M520,145 L560,145"/>
    <path class="loop"  d="M630,180 Q630,260 270,260 Q200,260 200,200"/>
    <text class="sub" x="445" y="280" text-anchor="middle">loop back with new context until stop rule fires</text>
  </svg>
  <figcaption>A loop is four things: a trigger, a model with tools, a verifier, and a stop rule. The dashed line is where most teams hand-wave.</figcaption>
</figure>

**Trigger** is what kicks the loop off — a cron, an event, a `/goal` command, a webhook from a pull request. The boring part everyone gets right.

**Model + tools** is the agent itself. Prompt engineering and context engineering live in this box. It's a smaller box than people used to think it was.

**Verifier** is the thing that decides whether the last iteration was any good. Tests passing, types resolving, an LLM judge scoring an output, a human approving a diff. We'll come back to this — it's the part that actually matters.

**Stop rule** is the most underrated line of code in your agent. Did we finish? Did we burn the budget? Are we oscillating? Is the verifier saying the same thing it said three turns ago? Without a stop rule, you have a goal-seeking process with no exit — which is just an expensive way to set money on fire.

## The verifier is the bottleneck

If you remember one thing from this post, remember this: **in any loop, the verifier is the bottleneck, not the model.**

This is the part almost every explainer skips. A loop without an external check is just the agent agreeing with itself — and agents are deeply, structurally good at agreeing with themselves. They'll produce a confident summary of why the broken thing is actually fine, declare victory, and exit.

The fix is to make the exit condition come from deterministic software, not from the agent's self-assessment. Tests passing. `tsc` returning zero. A linter clean. An eval scoring above threshold. A second model judging against a rubric. A human clicking approve.

This is also why the Ralph loop worked when AutoGPT didn't. Ralph wasn't smarter. Ralph just had a real verifier — the test suite — and refused to stop until it was green. AutoGPT asked itself if it was done, and itself, predictably, said yes.

Once you internalize this, the rest of loop engineering follows. The verifier defines the stop rule. The stop rule defines the cost. The cost defines whether you can ship.

## Loopmaxxing — the failure mode that funds the discipline

There's a term floating around for the thing that happens when you skip the verifier and trust the loop to "figure it out": **loopmaxxing**. It's the cousin of tokenmaxxing — the lazy belief that if you just throw more iterations at the problem, the agent will eventually get there.

It will not. It will get worse. And it will charge you for the privilege.

| Failure mode | What it looks like | What it costs you |
|---|---|---|
| No-progress drift | Agent edits, reverts, re-edits the same three files | Tokens, no shipped change |
| Oscillation | Two valid-but-incompatible fixes, ping-ponging | Tokens, plus a corrupt diff |
| Comprehension debt | Loop ships changes faster than humans can review | A codebase nobody understands |
| Runaway spend | Loop runs over a weekend on a malformed goal | A finance conversation on Monday |
| False victory | Agent declares done; verifier never ran | A bug in production with a clean PR |

The throughline is the same in every row: the loop didn't fail because the model was dumb. It failed because the engineering around the model wasn't there.

## What this changes about building agents

If you've been reading along since [the AI engineering eras piece](/posts/ai-engineering-evolution.html), you'll recognize the pattern. Each era asked a harder version of the same question.

- Prompt engineering asked *how do I phrase this?*
- Context engineering asked *what does the model need to know?*
- Harness engineering asked *what happens when it runs alone?*
- Loop engineering asks *what does it do next, and when is it allowed to stop?*

In practice, this changes the shape of the codebase. The most senior engineer on the team is no longer the one writing the cleverest prompt. They're the one writing the circuit breaker, the cost cap, the heartbeat schedule, and the supervisor that watches the worker agents. The model is becoming a frozen utility — you don't tune it, you wrap it. And the wrapper now has its own wrapper.

Boris Cherny, who runs Claude Code at Anthropic, put it bluntly earlier this year: his job has shifted away from prompting models toward writing the external execution loops that coordinate them. When the team building the model is spending its time on the loop, that's a signal worth listening to.

## What's next

The honest answer is: loops watching loops.

Single-agent ralph-style loops are already old hat. The next layer is supervisor topologies where one agent's only job is to verify another agent's loop — the verifier is itself an agent, with its own loop, with its own stop rule. Stack a few of these and you've got something that looks suspiciously like a distributed system, with all the joys that entails: cascading failures, byzantine workers, runaway feedback. The good news is we've solved versions of these problems before. The bad news is "we" was Google, in 2010, with a team of fifty.

The loop is also starting to leak out of the agent and into the org chart. Heartbeat loops that wake on a schedule, do a thing, and go back to sleep — those aren't agents in the sci-fi sense, they're cron jobs with judgment. And the line between "cron job with judgment" and "junior employee" is going to get blurry, fast.

* * *

So next time someone tells you they're running in circles, give them a second before you call HR. They might just be shipping.

The loop is the most expensive thing in your system to get wrong now — and the most leveraged thing to get right. Worth engineering on purpose.

---

*If you're building agentic loops in production — especially the verifier and stop-rule side — I'd genuinely like to compare notes. The patterns are still being figured out in real time.*
