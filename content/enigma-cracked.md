---
title: "ENIGMA Cracked: An 85-Year-Old Nazi Code Just Got Broken"
subtitle: How modern computation and a clever guess finally decrypted a German Army message from 1941.
description: A team of researchers just broke an 85-year-old Enigma-encrypted message using brute-force computation and AI agents. Here's how they did it.
tags: [Cryptography, AI Engineering, History]
category: Cryptography
readTime: 9 min
publishDate: 2026-09-28
cover: cover-enigma-cracked
references:
  - Carter, L. (2026). MVUEH Enigma Solved | https://mvueh-enigma-solved.carterl.chatgpt.site/
  - Turing, A. (1940). Treatise on the Enigma (Prof's Book)
  - Bletchley Park Trust. Enigma Machine History | https://bletchleypark.org.uk
---

On July 10, 1941, a German soldier sat in the town of Rosenow and radioed a question to his commanding unit. He needed to know the route of march. He typed his message into an Enigma machine, cranked through the encryption, and transmitted the ciphertext over the airwaves.

That message sat unbroken for 85 years.

Until last month, when a small team of researchers finally cracked it. Not with a room full of codebreakers. Not with a stolen codebook. With raw computation, a good guess, and a lot of patience.

The decrypted plaintext? "Please specify the route of march. I am in Rosenow, Rosenow. Immediate reply by radio."

A mundane military logistics request. But the story of how it got unlocked is anything but mundane.

## Why this message survived so long

During World War II, Britain's codebreakers at Bletchley Park broke thousands of Enigma messages. They had help: captured codebooks, repeated message formats, lazy operators who reused settings. The system they built around Alan Turing's Bombe machines was extraordinary, but it relied on those operational shortcuts.

This particular message had none of them.

It was encrypted with the standard Army Enigma I machine using Reflector B, but the specific key for that day was never recovered. No codebook. No known-plaintext shortcut from Bletchley's wartime archives. The intercept sat in the records as ciphertext, untouched, for decades.

After the war, most of the interest in Enigma shifted to historical scholarship. The machine's cryptographic strength wasn't enough to resist a modern attack in theory, but nobody had both the computational resources and the motivation to go after a single orphaned message.

That changed in 2026.

## The attack: 4.29 billion guesses

The team's approach was conceptually simple. Brutally expensive, but simple.

They started with a guess. Cryptanalysts call it a "crib," which is a chunk of plaintext you suspect appears somewhere in the message. The researchers guessed that the word "ROSENOW" appeared in the text, because the message was intercepted near that town. Specifically, they guessed the doubled form "ROSENOWROSENOW," which is a common pattern in German military radio messages when emphasizing a location name.

That crib became the anchor for the entire attack.

Here is the logic. The Enigma machine has a known structure: three rotors chosen from a set of five, a reflector, ring settings for each rotor, and a plugboard that swaps pairs of letters. If you know (or guess) a fragment of the plaintext and where it sits in the message, you can test whether a given machine configuration would produce the observed ciphertext at those positions.

The crib was 14 characters long. The full message was 82 characters. That means the crib could sit at 68 different positions within the message. For each position, they had to test every possible rotor configuration.

How many configurations? The rotor order alone gives 60 possibilities (five rotors, pick three, order matters). Each rotor has 26 ring settings and 26 starting positions. The plugboard, with its 10 swapped pairs, adds another enormous factor. When you multiply it all out, the team faced 4.29 billion distinct rotor-and-placement combinations to evaluate.

They split the work into 43,016 batches and ran them in parallel.

<figure class="diagram">
  <svg viewBox="0 0 720 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Attack pipeline: crib placement, rotor enumeration, plugboard filtering, header matching, language verification">
    <style>
      .node { fill: none; stroke: currentColor; stroke-width: 1.5; }
      .label { font: 500 13px Inter, system-ui, sans-serif; fill: currentColor; }
      .sublabel { font: 400 11px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.7; }
      .arrow { stroke: currentColor; stroke-width: 1.5; fill: none; marker-end: url(#arw); }
      .count { font: 600 11px Inter, system-ui, sans-serif; fill: currentColor; }
    </style>
    <defs>
      <marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
      </marker>
    </defs>
    <rect class="node" x="10"  y="60" width="120" height="70" rx="8"/>
    <text class="label" x="70"  y="90" text-anchor="middle">Crib Placement</text>
    <text class="sublabel" x="70" y="110" text-anchor="middle">68 positions</text>
    <rect class="node" x="170" y="60" width="120" height="70" rx="8"/>
    <text class="label" x="230" y="90" text-anchor="middle">Rotor Search</text>
    <text class="sublabel" x="230" y="110" text-anchor="middle">4.29B combos</text>
    <rect class="node" x="330" y="60" width="120" height="70" rx="8"/>
    <text class="label" x="390" y="90" text-anchor="middle">Plugboard Filter</text>
    <text class="sublabel" x="390" y="110" text-anchor="middle">97,337 keys</text>
    <rect class="node" x="490" y="60" width="120" height="70" rx="8"/>
    <text class="label" x="550" y="90" text-anchor="middle">Header Match</text>
    <text class="sublabel" x="550" y="110" text-anchor="middle">923 keys</text>
    <rect class="node" x="490" y="180" width="120" height="70" rx="8"/>
    <text class="label" x="550" y="210" text-anchor="middle">Language Check</text>
    <text class="sublabel" x="550" y="230" text-anchor="middle">Final decrypt</text>
    <path class="arrow" d="M130,95 L170,95"/>
    <path class="arrow" d="M290,95 L330,95"/>
    <path class="arrow" d="M450,95 L490,95"/>
    <path class="arrow" d="M550,130 L550,180"/>
    <text class="count" x="360" y="195" text-anchor="middle">✓ Verified independently</text>
    <text class="count" x="360" y="215" text-anchor="middle">against 14.8M physical keys</text>
  </svg>
  <figcaption>The five-stage attack pipeline that cracked the MVUEH message.</figcaption>
</figure>

## Filtering the noise

Running 4.29 billion combinations doesn't mean you get 4.29 billion answers. Most configurations fail immediately. The crib doesn't line up. The rotor settings produce gibberish at the known positions. Those get thrown out.

What survived the initial pass: 97,337 candidate keys. Still too many to check by hand, but a massive reduction from billions.

The next filter was the message header. Enigma messages started with a short indicator sequence that told the receiving operator which settings to use. The intercepted message had a recorded header. Of those 97,337 candidates, only 923 produced an output consistent with that header.

Now you're in the range where you can actually look at the results. The researchers checked each of those 923 decryptions for whether the output looked like plausible German. Not just random letters, but actual words. Sentence structure. Military vocabulary.

One key produced coherent German text. One.

## The verification nobody expected

Here is the part that makes this more than just a neat computation exercise.

The team didn't stop at finding one answer that looked right. They ran an independent verification pass. Instead of starting from the crib and working forward, they tested 14.8 million physical key configurations against the full message, checking whether any other key could produce the same plaintext.

None did. The solution was unique.

That kind of verification matters because crib-based attacks have a known weakness: if your guessed plaintext is wrong, you can still sometimes find keys that produce plausible-looking output by coincidence. The independent pass ruled that out. The message really does say what they think it says.

## What the message actually said

After all that computation, the decrypted text is almost anticlimactic:

> Please specify the route of march. I am in Rosenow, Rosenow. Immediate reply by radio.

A German soldier, stuck in a small town in what is now Poland, asking for directions. No strategic secrets. No battle plans. Just a guy who needed to know where to go next.

There is something poignant about that. Eighty-five years of cryptographic silence, billions of computations, and the answer is a lost soldier asking for help.

## The human-AI angle

The research was completed across September 14 and 15, 2026, and the team was explicit about one thing: this was not a human team using AI as a calculator. It was a structured collaboration between human researchers and multiple specialist AI agents, each with a defined role, running in parallel under human direction.

The humans brought the domain expertise. They knew which cribs to try, how Enigma's plugboard constraints could prune the search space, and what "plausible German military text" actually looks like. But the interesting part is what happened on the AI side.

### Five agents, five jobs

The team didn't throw one general-purpose model at the problem. They ran five categories of specialist agents simultaneously, each responsible for a different phase of the work:

**Evidence agents** went first. Their job was to examine the source material and record every possible reading of the intercepted message before anyone knew the answer. Think of them as the archivists: capturing raw observations without the bias of hindsight.

**Search agents** built and ran the actual computational experiments. They wrote the programs that tested 4.29 billion rotor configurations across 43,016 batches, with checkpoints that let work resume if anything crashed. These were the workhorses.

**Context agents** compared the findings against historical references. They checked whether the language patterns, military vocabulary, and message structure were consistent with other solved Enigma messages from the same era. If the search agents found a candidate decryption, the context agents asked: "Does this sound like something a German soldier would actually transmit in 1941?"

**Review agents** operated independently from the others. Their entire purpose was to reproduce results from scratch and verify that every part of the declared search space had actually been covered. No gaps. No missed batches. No silent failures in the parallelization.

**A coordinating agent** sat on top, reducing duplicated work across the other four groups and turning disagreements into further verification checks rather than consensus votes.

<figure class="diagram">
  <svg viewBox="0 0 720 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Five specialist AI agents feeding into a coordinating agent, which reports to human researchers">
    <style>
      .anode { fill: none; stroke: currentColor; stroke-width: 1.5; }
      .alabel { font: 500 13px Inter, system-ui, sans-serif; fill: currentColor; }
      .asublabel { font: 400 11px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.7; }
      .aarrow { stroke: currentColor; stroke-width: 1.5; fill: none; marker-end: url(#arw2); }
      .aheader { font: 600 12px Inter, system-ui, sans-serif; fill: currentColor; opacity: 0.5; }
    </style>
    <defs>
      <marker id="arw2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
      </marker>
    </defs>
    <text class="aheader" x="200" y="20" text-anchor="middle">SPECIALIST AGENTS (parallel)</text>
    <rect class="anode" x="10"  y="30"  width="130" height="55" rx="8"/>
    <text class="alabel" x="75"  y="55" text-anchor="middle">Evidence</text>
    <text class="asublabel" x="75" y="72" text-anchor="middle">Record observations</text>
    <rect class="anode" x="10"  y="100" width="130" height="55" rx="8"/>
    <text class="alabel" x="75"  y="125" text-anchor="middle">Search</text>
    <text class="asublabel" x="75" y="142" text-anchor="middle">Run experiments</text>
    <rect class="anode" x="10"  y="170" width="130" height="55" rx="8"/>
    <text class="alabel" x="75"  y="195" text-anchor="middle">Context</text>
    <text class="asublabel" x="75" y="212" text-anchor="middle">Historical matching</text>
    <rect class="anode" x="10"  y="240" width="130" height="55" rx="8"/>
    <text class="alabel" x="75"  y="265" text-anchor="middle">Review</text>
    <text class="asublabel" x="75" y="282" text-anchor="middle">Reproduce results</text>
    <text class="aheader" x="490" y="20" text-anchor="middle">COORDINATION</text>
    <rect class="anode" x="300" y="120" width="150" height="70" rx="8"/>
    <text class="alabel" x="375" y="152" text-anchor="middle">Coordinating</text>
    <text class="asublabel" x="375" y="170" text-anchor="middle">Merge + de-duplicate</text>
    <rect class="anode" x="560" y="120" width="140" height="70" rx="8"/>
    <text class="alabel" x="630" y="148" text-anchor="middle">Human</text>
    <text class="asublabel" x="630" y="165" text-anchor="middle">Domain expertise</text>
    <text class="asublabel" x="630" y="178" text-anchor="middle">Final decisions</text>
    <path class="aarrow" d="M140,57  L300,145"/>
    <path class="aarrow" d="M140,127 L300,150"/>
    <path class="aarrow" d="M140,197 L300,160"/>
    <path class="aarrow" d="M140,267 L300,170"/>
    <path class="aarrow" d="M450,155 L560,155"/>
  </svg>
  <figcaption>The multi-agent architecture: four specialist agent types work in parallel, feeding findings to a coordinating agent that de-duplicates and escalates to human researchers.</figcaption>
</figure>

### Disagreement as a feature, not a bug

Here is the part that makes this architecture worth studying beyond the Enigma result.

When two agents disagreed on a finding, the system didn't resolve it by majority vote. It didn't average the outputs or defer to whichever agent had higher confidence scores. Instead, a disagreement automatically triggered additional verification. The coordinating agent would route the contested result back to the review agents for independent reproduction.

The team accepted results on the basis of reproducible evidence, not agent agreement. That is a meaningful design choice. Most multi-agent setups in 2026 still lean on consensus or confidence thresholds, which means a confidently wrong majority can overrule a correct minority. This team avoided that entirely.

The result was a system where throwing more agents at the problem didn't just add speed. It added rigor. Every parallel workstream was also a parallel check on the others.

## Why it matters beyond history

You might read this and think: cool story, but who cares about a message from 1941?

Fair question. Here is why it matters.

First, it is a real-world proof that modern computation can break ciphers that were considered practically secure for decades. The Enigma machine was never mathematically unbreakable. Everyone knew that. But "theoretically breakable" and "actually broken on a single orphaned message with no cribs, no codebook, and no operational shortcuts" are very different things. This team closed that gap.

Second, the methodology is interesting. Crib-based attacks are old. Parallel computation is old. But combining them with AI-driven language verification to filter candidates is new. The pipeline they built isn't just useful for Enigma. It is a template for attacking any historical cipher where you have partial plaintext guesses and a known machine structure.

Third, and this is the part that sticks with me: there are other unbroken messages out there. Intercepts from WWII that never got decoded because Bletchley Park didn't have the right cribs or the right day's settings. Some of those messages might contain genuinely important historical information. Letters home. Intelligence reports. Orders that shaped battles.

This team just showed that "unbroken" doesn't have to mean "unbreakable." It just means nobody has thrown enough compute at it yet.

* * *

The next time someone tells you that AI is only good for generating marketing copy and chatbot responses, point them at this. A team of humans and AI agents just read mail that was sealed shut in 1941.

Some envelopes just take 85 years to open.
