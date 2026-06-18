---
title: "Google's Open Knowledge Format Is Almost Nothing. That's the Point."
subtitle: "OKF v0.1 is a folder of markdown files. The bet is that minimalism beats every metadata standard that came before it."
description: Google released the Open Knowledge Format last week. It's deliberately tiny — markdown files in a folder. Here's why that asceticism might be the smartest part.
tags: [AI Engineering, Agentic AI, Specs, Open Source]
category: AI Engineering
readTime: 7 min
publishDate: 2026-06-18
cover: cover-open-knowledge-format-the-folder-bet
references:
  - Sam McVeety and Amir Hormati, Google Cloud. (2026). How the Open Knowledge Format can improve data sharing | https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
  - Search Engine Journal. (2026). Google Cloud Announces The Open Knowledge Format | https://www.searchenginejournal.com/google-cloud-announces-the-open-knowledge-format/579253/
  - Marc Bara. (2026). Google's New Format for Agent Context — A Standard, or Just a Folder? | https://medium.com/@marc.bara.iniesta/googles-new-format-for-agent-context-a-standard-or-just-a-folder-82fb21d92041
  - MarkTechPost. (2026). Google Cloud Introduces Open Knowledge Format (OKF) — A Vendor-Neutral Markdown Spec | https://www.marktechpost.com/2026/06/16/google-cloud-introduces-open-knowledge-format-okf-a-vendor-neutral-markdown-spec-for-giving-ai-agents-curated-context/
  - Andrej Karpathy. (2025). The LLM Wiki pattern (X/Twitter thread referenced by OKF authors) | https://twitter.com/karpathy
  - innFactory. (2026). Open Knowledge Format — The Open Standard That Frees AI Knowledge From Silos | https://innfactory.ai/en/blog/open-knowledge-format-okf-standard-for-ai-knowledge/
---

A new specification dropped from Google Cloud last week. The whole thing fits on one page.

It's called the Open Knowledge Format. Sam McVeety and Amir Hormati — tech leads on Google's Data Analytics and BigQuery teams — published v0.1 on June 12. The spec is a directory of markdown files with YAML frontmatter. There is no SDK. There is no runtime. There is no database. There isn't even a required schema beyond one field called `type`.

You could read the entire specification on your phone in two minutes. You could write a compliant bundle in a text editor.

And that's already provoking the right argument: **is this a standard, or just a folder with a logo?**

I think it's both. I also think the asceticism is the most interesting design decision in the spec — and the one most likely to be misread as laziness.

## The context-assembly tax

Every team building AI agents pays a tax nobody talks about.

The model is brilliant in the abstract. The product needs it to be brilliant about your business — your tables, your metrics, your runbooks, your weird Tuesday-night incident from 2023 that everyone still references in retros. None of that is in the model's weights. All of it has to be assembled, shaped, and shoved into a context window before the model can be useful.

So engineers go shopping. Snowflake's catalog has the schemas. Confluence has the runbooks. The dbt repo has the metric definitions. Slack has the tribal knowledge. Code comments have half of it. The other half lives in three senior engineers' heads.

Every agent builder writes the same boring scaffolding to glue these together. Every catalog vendor invents a slightly different graph schema. Every team rebuilds the same M×N integration matrix from scratch.

This is the context-assembly tax. It compounds, silently, on every AI project you ship.

OKF's pitch is straightforward: agree on a folder format, write knowledge once, let any agent consume it. Boring. Familiar. Probably right.

## What OKF actually is

A bundle is a directory. Each markdown file is a *concept* — a table, a dataset, a metric, an API, a runbook. The YAML frontmatter carries a small set of structured fields. The body is freeform markdown. Concepts reference each other with regular markdown links.

That's the entire format.


<figure class="diagram">
  <svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="An OKF bundle shown as a directory of markdown files on the left and a graph of linked concepts on the right">
    <style>
      .node { fill: none; stroke: currentColor; stroke-width: 1.5; }
      .label { font: 500 13px Inter, system-ui, sans-serif; fill: currentColor; }
      .mono { font: 500 12px ui-monospace, SFMono-Regular, Menlo, monospace; fill: currentColor; }
      .small { font: 400 11px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.7; }
      .arrow { stroke: currentColor; stroke-width: 1.3; fill: none; marker-end: url(#arr); }
      .dashed { stroke: currentColor; stroke-width: 1.2; fill: none; stroke-dasharray: 4 3; }
      .divider { stroke: currentColor; stroke-width: 1; opacity: 0.25; }
    </style>
    <defs>
      <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
      </marker>
    </defs>

    <text class="small" x="20" y="28">Filesystem view</text>
    <text class="mono" x="20" y="58">sales/</text>
    <text class="mono" x="20" y="80">├── index.md</text>
    <text class="mono" x="20" y="102">├── datasets/</text>
    <text class="mono" x="20" y="124">│   └── orders_db.md</text>
    <text class="mono" x="20" y="146">├── tables/</text>
    <text class="mono" x="20" y="168">│   ├── orders.md</text>
    <text class="mono" x="20" y="190">│   └── customers.md</text>
    <text class="mono" x="20" y="212">├── metrics/</text>
    <text class="mono" x="20" y="234">│   └── gross_revenue.md</text>
    <text class="mono" x="20" y="256">└── runbooks/</text>
    <text class="mono" x="20" y="278">    └── refund_flow.md</text>

    <line class="divider" x1="320" y1="20" x2="320" y2="340"/>

    <text class="small" x="360" y="28">Graph view (markdown links)</text>

    <rect class="node" x="360" y="50" width="130" height="42" rx="6"/>
    <text class="label" x="425" y="76" text-anchor="middle">orders</text>

    <rect class="node" x="550" y="50" width="130" height="42" rx="6"/>
    <text class="label" x="615" y="76" text-anchor="middle">customers</text>

    <rect class="node" x="360" y="160" width="130" height="42" rx="6"/>
    <text class="label" x="425" y="186" text-anchor="middle">gross_revenue</text>

    <rect class="node" x="550" y="160" width="130" height="42" rx="6"/>
    <text class="label" x="615" y="186" text-anchor="middle">orders_db</text>

    <rect class="node" x="455" y="270" width="130" height="42" rx="6"/>
    <text class="label" x="520" y="296" text-anchor="middle">refund_flow</text>

    <path class="arrow" d="M490,71 L550,71"/>
    <path class="arrow" d="M425,160 L425,92"/>
    <path class="arrow" d="M615,160 L615,92"/>
    <path class="dashed" d="M455,291 Q380,200 405,92"/>
    <path class="dashed" d="M585,291 Q660,200 635,92"/>
  </svg>
  <figcaption>An OKF bundle is a directory on disk and a graph in practice. Markdown links cut across the filesystem hierarchy.</figcaption>
</figure>

The directory tree on the left is what `ls` shows you. The graph on the right is what the links inside those files create. The bundle is both at the same time — and that duality is the entire point.

The required frontmatter field is `type`. Optional ones include `title`, `description`, `resource`, `tags`, and `timestamp`. There are no registered vocabularies. There is no canonical list of allowed types. If you want a `metric` concept and your vendor wants a `kpi` concept, you each just write it.

Google shipped three reference bundles alongside the spec — [GA4 e-commerce](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset), [Stack Overflow](https://console.cloud.google.com/bigquery?ws=!1m4!1m3!3m2!1sbigquery-public-data!2sstackoverflow), and [Bitcoin datasets](https://cloud.google.com/blog/topics/public-datasets/bitcoin-in-bigquery-blockchain-analytics-on-public-data) — plus an [enrichment agent](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/toolbox/mdcode/demo) that walks a BigQuery dataset and drafts OKF files for every table, and a static HTML visualizer that renders any bundle as an interactive graph. All from a single self-contained file. No backend. No install. The [reference implementation lives on GitHub](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf).

The whole thing reads like someone read every previous metadata standard, listed everything that killed adoption, and removed it.

## The asceticism gamble

There's a pattern in successful infrastructure specs that nobody likes to admit. The minimal ones win.

`robots.txt` is a text file with two verbs. It runs the world's crawler etiquette layer. `JSON` is curly braces and strings. It runs every API on the planet. Markdown itself is glorified plaintext, and it now ships docs for nearly every open-source project in existence. `AGENTS.md` and `CLAUDE.md` — convention files that have no committee, no schema, no enforcement — are now the de facto way agents read project context.

Heavy specs die in conference rooms. Light specs spread because the cost of *trying* them is roughly zero.

OKF is making the same bet. The frontmatter is minimal because every required field is a fight nobody wants to have until they have to. The vocabulary is open because the moment you ship a canonical list of types, every team with a slightly-different concept invents a fork. The body is freeform markdown because the moment you mandate structure inside the body, you're rebuilding XML schema and you've already lost.

> OKF specifies the minimum necessary for interoperability and leaves the rest to producers.

This is the design choice that makes me think OKF has a real chance.

Compare it to the alternatives. OpenLineage tries to be a complete lineage schema and most teams adopt 10% of it. Schema.org's enterprise extensions exist mostly as polite fiction. Every major catalog vendor — Atlan, Collibra, Alation, DataHub — has its own knowledge model, and none of them are portable.

OKF doesn't try to win the schema war. It tries to make the schema war happen one optional field at a time.

## The semantic gap

Here's where it gets honest, and where the critics have a real point.

There's a useful distinction between **structural interoperability** and **semantic interoperability**. Structural means we agree on the file layout — that's what OKF v0.1 nails. Semantic means we agree on what the content *means* — that, OKF deliberately punts on.

Two teams can both ship perfectly valid OKF bundles. One team's `orders` table represents completed transactions. The other team's `orders` represents shopping carts. An agent that consumes both will happily compute a metric across them and produce a number that is precisely, syntactically, and uselessly wrong.

A `type: metric` field tells you something is a metric. It does not tell you what the metric measures, how it's defined, whether it's revenue-recognized, or whether the denominator excludes returns. That's the semantic layer — and v0.1 has nothing to say about it.

The Google team knows this. The post explicitly calls v0.1 "a starting point, not a finished standard." Closing the semantic gap is what later versions are for — registered types, link vocabularies, declared profiles, maybe even shared ontologies for common domains.

Until then, OKF is **a shared way to store context, not yet a shared way to make sense of it.**

This is fine. It might even be necessary. The instinct to specify everything at once is what killed the previous generation of metadata standards. The instinct to ship something nearly-empty and let conventions accrete around it is what built every working web standard since the early 2000s. Google is making that bet explicitly, in public, and naming the limitation in the announcement itself. That's unusually mature for a vendor-led format proposal.

The risk is real, though. Conventions only accrete in public if the producer/consumer ecosystem actually shows up. If OKF v0.2 is decided in a Google repo with three contributors, the asceticism stops being a feature and starts being a vacuum. The first six months of community PRs matter more than the spec.

## Where it might actually matter

Forget the standard-or-folder argument for a second. Here are the places I expect OKF to land first, ranked by how soon you'd feel it in your work.

**Data warehouse documentation as agent fuel.** Right now, every team with a BigQuery, Snowflake, or Redshift warehouse has the same problem: the schemas live in one place, the column-level docs live in dbt YAML files, the metric definitions live somewhere else, and the runbooks live in Notion. An LLM agent asked "why did revenue dip last week?" has to assemble all of it from scratch. An OKF bundle is exactly the shape of artifact you'd hand that agent.

**Cross-vendor migration.** Catalog migrations today are nightmarish — every vendor has its own model, and you re-document everything by hand. An OKF export becomes a portable intermediate. Atlan exports OKF, Collibra imports OKF, the bundle stays version-controlled in git in between. This is the use case where the format's lack of opinion is a feature, not a bug.

**Onboarding handoffs between agents.** Multi-agent systems share context through prompts and tool calls today. An OKF bundle could become the shared substrate — a researcher agent populates it, a writer agent consumes it, an evaluator agent diffs across runs. The directory itself becomes the working memory.

**Open data sharing with semantics.** The Bitcoin sample bundle is more interesting than it looks. Public dataset providers have always shipped raw data with PDFs of documentation. Shipping an OKF bundle instead means the dataset arrives with a graph of typed, linked, machine-readable context. Agents can navigate the docs the way they currently navigate code.

**Replacing internal wikis for AI consumption.** This is the boldest claim, and the one I'd bet on hardest. Your Confluence space is a text dump that pretends to be structured. An OKF bundle in a git repo is structured-enough, diffable, reviewable, and consumable by both humans and agents. The maintenance burden is similar. The downstream utility is dramatically higher.

* * *

## The bet, named clearly

The Open Knowledge Format is a folder. That is not a criticism — it is, I think, the smartest thing about it.

The history of working infrastructure standards is the history of formats that did the absolute minimum required to be useful and let everything else be a convention. The history of failed standards is the history of formats that tried to specify the world on day one.

Google is betting that *naming the file format* and shipping the reference tooling is enough to bootstrap an ecosystem. They might be right. They might be wrong. Either way, the experiment is cheap enough for any of us to run on our own data this weekend — and that, too, is the point.

The interesting question isn't whether OKF v0.1 is a real standard. It's whether the next year of community PRs will let it become one.

I'd read the original announcement before the takes pile up on top of it. It's the rare big-vendor format proposal that says, plainly, *this is the starting point, not the finished thing*. That posture is worth taking seriously.

[Read Google's announcement →](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
