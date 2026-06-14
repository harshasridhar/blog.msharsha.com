---
title: "The Evolving Stack of AI Engineering"
subtitle: "From crafting sentences to orchestrating networks — how the discipline keeps reinventing itself"
date: 2026-06-14
tags: [ai, engineering, prompt-engineering, context-engineering, harness-engineering, multi-agent, mcp, agentic-ai]
category: AI Engineering
readTime: 5 min
publishDate: 2026-06-15
medium: https://medium,com/@msharsha
cover: ai_engineering_evolution
references:
  - Jason Wei et al., Google. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models | https://arxiv.org/abs/2201.11903
  - Andrej Karpathy. (2025). Context Engineering | https://karpathy.ai
  - Gartner. (2025). Context Engineering is in, Prompt Engineering is out | https://www.gartner.com/en/articles/context-engineering
  - Nelson et al., Stanford. (2023). Lost in the Middle: How Language Models Use Long Contexts | https://arxiv.org/abs/2307.03172
  - Mitchell Hashimoto. (2026). Engineering the Harness | https://mitchellh.com
  - Ryan Lopopolo, OpenAI. (2026). Harness Engineering: Leveraging Codex in an Agent-First World | https://openai.com/engineering
  - LangChain. (2026). Agent = Model + Harness | https://blog.langchain.dev
  - Anthropic. (2024). Model Context Protocol Specification | https://modelcontextprotocol.io
  - Anthropic. (2025). MCP Ecosystem Update — 97M downloads, 10,000+ servers | https://anthropic.com
  - Linux Foundation. (2025). Agentic AI Foundation (AAIF) Announcement | https://linuxfoundation.org
  - Confident AI. (2026). LLM-as-a-Judge: The Complete Guide | https://www.confident-ai.com/blog/why-llm-as-a-judge-is-the-best-llm-evaluation-method
  - Stanford HAI. (2025). AI Index Report 2025 | https://aiindex.stanford.edu
  - Gartner / AetherLink Research. (2026). Multi-Agent Orchestration Enterprise Report | https://www.innoflexion.com/blog/multi-agent-orchestration-enterprise-genai-2026
---

There's a pattern that keeps showing up in how software disciplines mature.

First, the cowboy phase — people figure out what works through trial and error, intuition, and Twitter threads. Then someone names it. Then companies start hiring for it. Then it becomes a formal engineering discipline with papers, tooling, and defined best practices.

AI engineering has been sprinting through this cycle at an unusual pace. In just under four years, we've gone through several distinct eras — each one necessary, each one insufficient on its own. Each one building on the limitations of the previous.

Here's how it happened.

---

## Era 1: Prompt Engineering (2022–2024)

### The moment everything changed

November 30, 2022. ChatGPT goes live.

One million users in five days. A hundred million in two months. Developers who'd never thought about language models in their lives were suddenly asking the same question: *how do I talk to this thing?*

The answer that emerged was prompt engineering — the practice of crafting inputs to coax better outputs from a language model. And in the early days, it felt almost magical. Rephrase your question just right and the model would go from confused to brilliant. Add "think step by step" and accuracy jumped. Frame yourself as an expert and the response shifted register.

A whole ecosystem formed around it. Prompt marketplaces. YouTube channels dedicated to "the perfect ChatGPT prompt." Job listings with "Prompt Engineer" in the title paying six figures. Andrej Karpathy called this moment "Software 3.0" — natural language as the programming language.

### What prompt engineering actually was

At its core, prompt engineering was about the *words* you used in a single interaction. Its main techniques:

- **Zero-shot prompting**: Just ask, with no examples
- **Few-shot prompting**: Give examples to pattern-match from
- **Chain-of-thought**: Ask the model to reason step-by-step before answering
- **Role prompting**: "You are a senior software engineer reviewing code..."
- **Instruction formatting**: Structuring prompts with explicit instructions, constraints, and output formats

These techniques genuinely worked. Chain-of-thought prompting, introduced by researchers at Google in early 2022, showed that reasoning through intermediate steps before answering dramatically improved accuracy. It wasn't a trick — it was tapping into something real about how these models process information.

### Where it ran out of road

Prompt engineering was powerful for single-turn interactions. Ask a question, get an answer. Write a function, get code.

But as soon as developers tried building something more ambitious — agents that could browse the web, assistants with memory, systems that needed to understand a codebase — the limits became clear fast.

Models forgot critical details between turns. They contradicted earlier decisions. They hallucinated information that no prompt phrasing could prevent, because the model simply didn't have the right *information*, not because it didn't have the right *instructions*. You could craft the most beautiful prompt in the world, but if the model's context window lacked the customer's purchase history, no amount of clever wording would produce a correct answer.

The bottleneck wasn't the words. It was the information.

---

## Era 2: Context Engineering (2024–2025)

### Naming the real problem

In June 2025, Andrej Karpathy put words to what engineers had already been experiencing for months:

> "Context engineering is the delicate art and science of filling the context window with just the right information for the next step."

The phrase landed immediately. Within a week, it was everywhere. Gartner analysts formalized it — "context engineering is in, and prompt engineering is out" — and the industry shifted its mental model.

Context engineering wasn't about changing how you *asked*. It was about changing what the model *knew* when it answered.

### What changed

The shift is easier to understand with a concrete example. Imagine asking an AI assistant to debug a failing test.

**Prompt engineering approach**: Carefully worded request. "You are a senior engineer. The following test is failing. Identify the bug and fix it. Think step by step."

**Context engineering approach**: Before the model sees that request, you've already decided: *which files does it need? What's the test output? What's the relevant function? What architectural rules does this codebase follow?* You've curated, structured, and positioned that information deliberately in the context window.

The model's instructions might be identical. The context window it's working with is completely different.

Context engineering formalized into a set of distinct strategies: write (craft explicit instructions), select (choose what information to include), compress (remove token waste), and isolate (keep unrelated context out of the way). Tools like RAG pipelines and MCP made this systematic rather than manual.

### The physics of context windows

Context engineering also confronted something the "just dump everything in" crowd underestimated. Stanford researchers demonstrated what they called the "lost in the middle" problem — LLM performance degrades significantly when relevant information appears in the middle of long contexts. Models perform best when key information appears at the very beginning or end.

A 2025 study found that LLM accuracy drops by 24.2% when relevant information is embedded within longer contexts, even when models attend only to that information. The degradation wasn't random. It was positional.

This meant context engineering wasn't just about *what* you included — it was about *where* you put it and *how* you structured it. The discipline went from "write good prompts" to something much closer to systems design.

### Where context engineering plateaued

Context engineering solved production reliability for a lot of use cases. But it still assumed something that wasn't always true: that the agent would run for one bounded task, then stop.

Real agentic systems don't work that way. They run autonomously for hours. They make hundreds of sequential decisions. They use tools, produce outputs, and feed those outputs back into subsequent calls. They drift. They compound errors. They do things that look correct in isolation and are catastrophically wrong in context.

And once you have an agent running autonomously — truly running, not just answering — a new question emerges: what happens when it makes a mistake?

---

## Era 3: Harness Engineering (2026 — now)

### Mitchell Hashimoto's habit

Mitchell Hashimoto built HashiCorp. He co-created Terraform. He is not someone who casually blogs about things.

In February 2026, he published a post describing a habit he'd developed while building with AI agents. Every time an agent made a mistake, he didn't just fix the mistake. He engineered a permanent solution into the agent's *environment*, so that mistake could structurally never happen again.

He called it "engineering the harness."

OpenAI and Anthropic followed with their own posts expanding on the concept. LangChain condensed the model into a single equation: **Agent = Model + Harness**.

The framing clicked because it named something every engineer building agents had already hit. Prompt engineering optimizes what you ask. Context engineering optimizes what the model knows. Neither addresses what happens when an agent runs autonomously, making decision after decision without supervision.

Harness engineering addresses that.

### What a harness actually is

The harness is everything that wraps the model. Not the model itself — the model is just the reasoning engine. The harness is the infrastructure that governs how it operates:

- **Guides**: System prompts, AGENTS.md files, constraint documents — the standing instructions that direct what the agent knows and can do
- **Sensors**: Evals, validation loops, output parsers, drift detectors — the systems that observe and verify the agent's behavior
- **Data context layer**: The curated, structured information the agent reasons over

A production-grade harness has five layers: tool orchestration, verification loops, context and memory, guardrails, and observability. Miss any one of them and you get an agent that works in demos and fails in production.

### The core insight

Harness engineering treats the LLM differently from how the previous two eras did.

Prompt engineering treats the model as something to be persuaded. Context engineering treats it as something to be informed. Harness engineering treats the model as a *frozen utility* — a reasoning calculator — and moves the responsibility for safety, accuracy, and control entirely into the surrounding infrastructure.

You stop trying to make the model smarter. You start making failures structurally impossible to repeat.

That's the shift. It sounds subtle. In practice, it changes almost everything about how you architect an AI system.

### Why it matters now

The timing isn't coincidental. Enterprise AI adoption hit a wall in 2025. Data consistently showed that 95% of enterprise AI pilots delivered zero measurable ROI. Gartner projected over 40% of agentic AI projects would be canceled by end of 2027 due to unclear business value or inadequate risk controls.

The models weren't the problem. The harnesses were.

At the AI Engineer World's Fair in April 2026, three independent speakers named "agent harness" and "context engineering" as the top engineering priorities — reflecting where the industry's attention had moved after two years of model capability improvements that failed to translate into production reliability.

---

## The through-line so far

Step back and look at the first three eras together.

**Prompt engineering** asked: *how do I phrase this?*
**Context engineering** asked: *what does the model need to know?*
**Harness engineering** asks: *what happens when the model runs on its own?*

Each question only becomes relevant once the previous one is answered. The discipline has been forced to mature by the ambition of what engineers are trying to build. And that ambition keeps growing.

Which brings us to what's emerging next.

---

## What's coming into focus

Harness engineering solved the single-agent reliability problem. The moment you solve that, you immediately face a harder one: what happens when you have dozens of agents running simultaneously, talking to each other?

That's where the frontier is now — not one agent with a good harness, but networks of them.

### Multi-Agent Network Orchestration

A single agent has one context window, one tool set, one task. That's a fine starting point — until the task is too complex for one model to handle, or too slow when serialized end-to-end.

Multi-agent orchestration is the engineering pattern that splits work across a network of specialized agents. A supervisor agent decomposes a task and routes subtasks to specialists. Those specialists run in parallel, return results, and the supervisor aggregates. The patterns — supervisor/worker, peer-to-peer, hierarchical — borrow heavily from distributed systems design.

The failure modes are also distributed-systems problems: infinite loops that quietly run up your API bill, hallucinations that cascade from one agent to the next, context that silently truncates between handoffs. Only about 28% of enterprise multi-agent deployments achieve sustained results. The differentiating factor isn't the models — it's the orchestration architecture and governance.

The question this era asks: *how do you coordinate agents that can't fully see each other?*

### MCP Standardization — The Protocol Layer

Before you can orchestrate a network of agents, they need a common language for connecting to tools and data.

That's what the Model Context Protocol solved. Anthropic introduced MCP in November 2024 as an open standard defining how AI models connect to external tools, data sources, and systems. The problem it addressed was an M×N explosion: M AI models connecting to N external tools required M×N custom integrations. MCP collapsed that to M+N — each side implements the protocol once.

The adoption curve was steep. OpenAI added support in March 2025. Microsoft integrated it into Copilot Studio in July 2025. By December 2025, Anthropic reported over 97 million monthly SDK downloads and more than 10,000 active public MCP servers. Then Anthropic donated MCP to the Linux Foundation — a signal that competing AI companies had agreed on a shared infrastructure layer.

It's now the closest thing AI engineering has to a universal adapter. Think USB-C, but for agents connecting to the world.

### Self-Healing Pipelines & Autonomous Optimization

Once you have networks of agents running over standardized protocols, a new problem surfaces: who watches the watchers?

Traditional monitoring catches failures after they happen. Self-healing pipelines are designed to catch degradation as it happens and respond automatically — rerouting tasks, swapping underperforming agents, adjusting parameters, and flagging edge cases for human review only when the system can't resolve them.

This isn't autonomous AI in the science-fiction sense. It's more like what DevOps did for software deployment: replacing brittle, manual intervention with systematic, automated feedback loops. The harness detects the problem; the pipeline heals it; a human reviews the audit trail later.

The question this era asks: *how do you build systems that maintain themselves?*

### Continuous AI Evaluation (AI-as-a-Judge)

None of the above works without the ability to measure whether agents are actually doing what you want — at scale, in production, continuously.

That's what AI-as-a-Judge addresses. The idea: use one LLM to evaluate the outputs of another, against rubrics you define — correctness, relevance, safety, tone. No annotation team. No waiting weeks. Just a prompt and an API call.

The numbers are compelling. In 2026, an LLM judge agrees with human reviewers about 85% of the time — higher than two humans typically agree with each other on the same task. This has made AI-as-a-Judge the default method for evaluating LLM applications at scale, embedded directly into CI/CD pipelines as an automated quality gate.

The risks are real too. LLM judges have their own biases. They can be gamed. They're not a substitute for human evaluation on safety-critical outputs. But as a continuous signal at scale — something traditional QA never achieved — they've become essential infrastructure for any team shipping production AI.

The question this era asks: *how do you know if the system is working, always?*

---

## The full picture

Every era in AI engineering has asked a harder version of the same underlying question: *how do we make this reliable?*

| Era | Core question | What it unlocked |
|---|---|---|
| Prompt Engineering | How do I phrase this? | Single-turn reliability |
| Context Engineering | What does the model need to know? | Multi-turn, task-specific reliability |
| Harness Engineering | What happens when it runs alone? | Autonomous single-agent reliability |
| Multi-Agent Orchestration | How do agents coordinate? | Scalable parallel execution |
| MCP Standardization | How do agents connect to everything? | Interoperable agent ecosystems |
| Self-Healing Pipelines | How do systems maintain themselves? | Operational resilience at scale |
| Continuous Evaluation | How do we know it's working? | Ongoing quality assurance in production |

These aren't sequential steps where you finish one and move to the next. They're layers. Engineers building production AI systems in 2026 are working across all of them simultaneously.

The engineers who are actually shipping — and keeping things running — aren't specialists in any one layer. They understand the whole stack well enough to know which layer is causing the failure when something breaks.

That's the job now. Not prompt engineering. Not context engineering. The whole stack, end to end.

---

*If you're working through any of these layers — especially orchestration or eval pipelines — I'd love to hear what you're running into. The patterns are still being figured out in real-time.*