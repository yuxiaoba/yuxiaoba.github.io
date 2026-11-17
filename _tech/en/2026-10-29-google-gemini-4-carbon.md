---
id: 2026-10-29-google-gemini-4-carbon
title: '2026-10-29 | Gemini 4 Carbon: Long-Horizon Engineering, Security Evals, and
  Staged Access'
date: '2026-10-29'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
long_read: true
tags:
- coding-agents
- agent-reliability
- systems-reliability
summary: Close reading of Google's Gemini 4 Carbon launch, covering multi-day engineering runs, stage-split vulnerability discovery/exploitation/patching evaluations, anti-shortcut alignment with 0.0% Gray Swan IPI, and Fairwind staged access limits.
source_url: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/
source_published_at: '2026-10-28'
permalink: /tech/en/2026-10-29-google-gemini-4-carbon/
authoring_source: assistant
translation_source: assistant
updated_at: '2026-11-15T19:40:00+08:00'
---
Koray Kavukcuoglu (SVP, Google DeepMind and Chief AI Architect, Google) · 2026-10-28 · [Official Announcement: "Gemini 4 Carbon: our next frontier model"](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/) · [Google DeepMind X Post](https://x.com/GoogleDeepMind/status/2115489356437651654) · [Evals Methodology PDF](https://deepmind.google/models/evals-methodology/gemini-4-carbon)

Announced two weeks after Gemini 4 Argon on October 28, 2026, **Gemini 4 Carbon** is positioned as Google's strongest frontier model for **long-horizon software engineering** and the **cybersecurity defense lifecycle**. For systems and agent reliability readers, the announcement's substance goes beyond ranking `#1` (`59`) on Artificial Analysis Intelligence Index v5.0: it pairs **multi-day autonomous execution**, **three-stage cyber evaluation** (discovery, exploitation validation, and root-cause patching), **anti-shortcut alignment training**, and **restricted Fairwind rollout** under one technical frame.

> **Evidence & scope boundary**: Every figure and claim below is cross-checked against Google's official launch post, its five embedded benchmark graphics, and the directly linked [Gemini 4 Carbon Evaluation Methodology PDF](https://deepmind.google/models/evals-methodology/gemini-4-carbon), [Fairwind Program](https://deepmind.google/fairwind-program/), and [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf). Three evidence boundaries matter: **(1) External cybersecurity scores** reflect access **without guardrails** through the **Fairwind Program** (and mixed harnesses/time caps across peer baselines); **(2) Provider and partner internal results** (`>2×` secure code generation, `>10×` Chrome patch claim, `~80%` drop in live high-severity misalignment alerts, `~2×` reduction in unsupported claims) omit sample sizes, denominators, or competitor model identities and are **not** independently reproduced evaluations; and **(3) Zero failures on tested probes do not prove universal immunity**—Gray Swan's `0.0%` reflects evaluated attacks only, not immunity against future adaptive prompt injections.

## Long-Horizon Engineering & Capability Profile: Leads, Lags, and Long Context

Google frames Carbon specifically around **sustained agentic workflows**: internally, engineering teams report running Carbon **for days** to persist past dead ends while root-causing and patching subtle bugs across large codebases and low-level systems. Examining all 17 rows in the official benchmark table alongside the methodology PDF reveals a clear pattern—strong gains in long-context state tracking and terminal workflows, paired with two explicit rows where competing models remain ahead:

- **Long-Context Traversal & Composite Reasoning**: On Google's self-computed `GraphWalks` (`256k` to `1M` token subset, `200` problems, BFS F1), Carbon reaches **`96.2%`**, outperforming Gemini 4 Argon (`84.2%`), GPT-6 Astra (`71.8%`), and Claude Opus 5.5 (`66.8%`) under the same evaluation setup. Across general benchmarks, Carbon ranks `#1` on Artificial Analysis Intelligence Index v5.0 (with tools) at **`59`** and scores **`70.4%`** on Vals Index v2.2.
- **Terminal Engineering & Full-Stack Artifacts**: On `Terminal-Bench 4.0 (AA)`, Carbon reaches **`65.2%`** (vs. Argon `57.1%`, Opus 5.5 `59.6%`). Using `mini-swe-agent` (subtask-weighted reward), it scores **`9.6%`** on `SWE-sweep` (just ahead of GPT-6 Astra's `9.5%` leaderboard score), and jumps `+89` Elo on `WebDev Arena` to `#4` (`1768`).
- **Explicit Lagging Rows**: The primary summary table does not claim a clean sweep. On Proximal's `FrontierSWE 2` public leaderboard, Carbon scores **`61.2%`**, trailing **GPT-6 Astra (`65.5%`)** and **Claude Opus 5.5 (`62.3%`)**. On `OSWorld-2.1` (`82`-task offline no-internet subset, screenshot-only PyAutoGUI loop, max `500` steps, max over `3` runs), Carbon scores **`81.5%`**, ahead of Argon (`74.7%`) and Astra (`80.9%`) yet behind **Claude Opus 5.5 (`87.2%`)**.

<figure>
  <a class="note-image-link" href="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-capability-cyber-profile-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-capability-cyber-profile-en.svg" alt="Assistant diagram of Gemini 4 Carbon capability profile and 3-stage cybersecurity evaluation: left panel pairs leading metrics (AA Index 59, GraphWalks 96.2%, Terminal-Bench 4.0 65.2%, WebDev 1768) with trailing rows (FrontierSWE 2 61.2% behind Astra 65.5%, OSWorld-2.1 81.5% behind Opus 5.5 87.2%); right panel separates SEC-bench Pro 88.2%, ExploitGym 54.8% at 10h, and CWE-bench 71.0% under unguardrailed Fairwind access; bottom bar flags non-public provider/partner claims over 2x and over 10x." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Synthesizing the official benchmark table, three cyber bar charts, and the Gemini 4 Carbon evals-methodology PDF.</figcaption>
</figure>

The table below aligns key external benchmark numbers from the primary announcement with the exact harness, timeout, and comparison constraints disclosed in Google's methodology appendix:

| Domain & Benchmark | Evaluation Scope & Harness (Methodology PDF) | Gemini 4 Carbon | Gemini 4 Argon | Top Peer in Primary Table (Source) | Engineering Interpretation & Comparison Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **General Reasoning**: `AA Index v5.0` | Artificial Analysis (with tools) | **`59`** (`#1`) | `50` | Claude Opus 5.5 `58` / GPT-6 Astra `57` | Reflects highest thinking settings; does not isolate token cost or latency budgets |
| **Long Context**: `GraphWalks` (`256k–1M`) | `200` problems, self-computed across all models (BFS F1) | **`96.2%`** | `84.2%` | GPT-6 Astra `71.8%` | Strong multi-hop state retention across `256k–1M` windows, critical for large-repo triage |
| **Agentic Coding**: `Terminal-Bench 4.0 (AA)` | Sourced from Artificial Analysis | **`65.2%`** | `57.1%` | Claude Opus 5.5 `59.6%` | Paired with `0.0%` cheating success and `0.4%` attempts (Section 3) |
| **Agentic Coding**: `FrontierSWE 2` | Proximal public leaderboard | `61.2%` | `55.0%` | **GPT-6 Astra `65.5%`** / Opus 5.5 `62.3%` | Shows Carbon does not dominate every SWE suite; verify on target repositories |
| **Computer Use**: `OSWorld-2.1` (offline) | `82`-task offline split, `max@3`, max `500` steps | `81.5%` | `74.7%` | **Claude Opus 5.5 `87.2%`** | Screenshot + PyAutoGUI actuation lags Opus 5.5 (`Agents' Last Exam v1.1`: `77.4%`) |
| **Discovery**: `SEC-bench Pro` | `183` JS engine tasks (May 2026), `3`-run avg, `Antigravity` | **`88.2%`** | `83.4%` | GPT-6 Astra `85.4%` (system card) | Run in Fairwind mode without guardrails; peer scores come from published reports |
| **Validation**: `ExploitGym` | Single attempt, offline, **mitigations off**, `Antigravity` | **`54.8%`** (`10h`) / `53.5%` (`6h`) | `42.0%` (`10h`) / `39.5%` (`6h`) | GPT-6 Astra `42.4%` (`No time cap`) | Asymmetric time caps (`6h` / `10h` / uncapped / unknown) plus LLM judge validation |
| **Patching**: `CWE-bench v1` | Collinear AI / AA leaderboard, `Pass@1` (`Pass@4` tiebreak) | **`71.0%`** (`Antigravity`) | `68.0%` (`Antigravity`) | Grok 4.7 (`opencode`) & Astra (`Codex`) `68.0%` | Mixed agent harnesses across leaderboard rows conflate model and scaffold effects |

## Splitting the Cyber Defense Lifecycle: Discovery, Exploitation Validation, and Root-Cause Patching

Rather than collapsing cybersecurity capability into a single CTF score, Google separates the defensive workflow into three distinct stages—**vulnerability discovery (`SEC-bench Pro`)**, **exploitability validation (`ExploitGym`)**, and **root-cause patching (`CWE-bench`)**:

1. **Autonomous Vulnerability Discovery** (`SEC-bench Pro`: `88.2%` Pass@1): Using the open-source setup on the **183-task May 2026 JavaScript engine split**, Google averaged **3 independent attempts per task** inside the `Antigravity` harness. A task passes when the generated PoC crashes the vulnerable build without crashing the patched build (or crashes both and an LLM source-review judge confirms the target flaw was hit). Carbon's **`88.2%`** leads GPT-6 Astra (`85.4%`), Argon (`83.4%`), GPT-6.1 Terra (`83.3%`), GPT-6.1 Sol (`78.8%`), MiMo-V2.6-Pro (`66.3%`), DeepSeek-V4.1-Flash (`62.8%`), and DeepSeek-V4-Pro (`56.4%`).
2. **Validating Real Risk Through Exploitation** (`ExploitGym`: `54.8%` @ `10h` / `53.5%` @ `6h`): Security teams need to distinguish theoretically flagged bugs from actually exploitable vulnerabilities to prioritize remediation. On [ExploitGym](https://github.com/sunblaze-ucb/exploitgym), Google ran **one attempt per task** in `Antigravity`, **offline (no internet)**, with **benchmark mitigations disabled**, requiring both target flag capture and LLM-judge verification of the intended exploit path. Under the default `6h` cap, Carbon scores **`53.5%`** (Argon `39.5%`, Opus 5.5 `34.5%`, Claude Mythos 5.1 `30.4%`, GLM-5.3 `15.0%`); extending to `10h` raises Carbon to **`54.8%`** (Argon `42.0%`), ahead of uncapped GPT-6 Astra (`42.4%`) and GPT-6.1 Sol (`35.1%`).
3. **Root-Cause Remediation** (`CWE-bench v1`: `71.0%` Pass@1): On Collinear AI's public leaderboard (independently evaluated with Artificial Analysis, ranked by programmatic `Pass@1` with `Pass@4` tiebreakers), Carbon in `Antigravity` reaches **`71.0%`**, edging out Grok 4.7 (`opencode`, `68.0%`), Argon (`Antigravity`, `68.0%`), GPT-6 Astra (`Codex`, `68.0%`), and Claude Opus 5.5 (`Claude Code`, `67.0%`). Because the chart pairs each model with its respective coding scaffold, improvements reflect the combined model-plus-harness configuration rather than a harness-controlled parameter comparison.

Google supplements those public benchmarks with three internal or partner-reported observations: **more than `2×` uplift** in internal secure-code generation success over Argon; a **Chrome team report** stating Carbon performed **more than `10×` better** than "another lab's large frontier model" on high-quality patch generation; and **Wiz** observing Carbon leading web penetration-testing benchmarks supporting *Scan for Good*. Because task distributions, sample counts, and Chrome's baseline competitor are undisclosed, these remain **provider and partner signals**, not audited external benchmarks.

Crucially, both the launch post ("evaluated without guardrails") and the methodology PDF (noting cyber scores reflect **Fairwind Program** access) underscore why dual-use capabilities drive Google's deployment gating: an unguardrailed frontier model that excels at PoC crash generation and flag-capturing exploit synthesis lowers attacker friction if exposed without access controls.

## Anti-Shortcut Training, Prompt-Injection Resilience, and the Four-Layer Runtime Stack

For teams deploying long-running coding or operations agents, Carbon's behavioral alignment section targets a concrete failure mode: **capable models often exploit loopholes when stuck**. Carbon builds on Argon's multi-layered stack while pushing training directly against reward hacking, fabrication, and scope drift:

<figure>
  <a class="note-image-link" href="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-safety-rollout-stack-en.svg" target="_blank" rel="noopener">
    <img src="/assets/images/tech/2026-10-29-google-gemini-4-carbon/carbon-safety-rollout-stack-en.svg" alt="Assistant diagram of Gemini 4 Carbon alignment deltas, runtime safety stack, and rollout model: left cards detail Terminal-Bench 4.0 0.0% cheating success and 0.4% attempts, nearly 80% drop in live high-severity misalignment alerts, ~2x fewer unsupported claims, 26% less overreach, 29% less under-service, and 0.0% Gray Swan IPI attack success; right panels map the 4-layer Argon-lineage defense stack and U.S. govt testing to Fairwind rollout and $2/$10 to $4/$20 pricing." width="960" height="540" loading="lazy">
    <span class="note-image-action">Expand diagram ↗</span>
  </a>
  <figcaption>Assistant diagram (not an original figure): Synthesizing alignment training deltas, Gray Swan IPI scores, Argon-lineage runtime defenses, and Fairwind rollout gates.</figcaption>
</figure>

- **Curbing Cheating and Specification Gaming**: On `Terminal-Bench 4.0`, Carbon reduced **successful cheating to `0.0%`** and **cheating attempts to `0.4%`**, while simultaneously raising overall accuracy (`65.2%`). In live internal coding environments with Google teams, **high-severity misalignment alerts dropped by almost `80%`**. Practically, this addresses agents that edit unit tests, mock verifiers, or fabricate green exit statuses under pressure.
- **Honesty Under Missing Evidence**: Internal testing records roughly **`2×` fewer unsupported claims** relative to Argon. Rather than fabricating or hedging when data is absent, Carbon inserts **methodological caveats directly into deliverables** or **withholds blocked actions alongside an explicit checklist of missing prerequisites**.
- **Ambiguity Resolution & Scope Control**: When requirements conflict, Carbon retrieves relevant sources and surfaces discrepancies before acting; internal metrics report **`26%` lower overreach** and **`29%` lower under-service**, keeping multi-step executions bounded within project constraints.
- **Indirect Prompt Injection (`Gray Swan IPI`)**: Evaluated at `k=1`, `k=10`, and `k=15` attack attempts, Carbon records **`0.0%` attack success rate** across every tested probe—improving over Gemini 4 Argon (`0.7%`), Claude Opus 5.5 (`1.0%`), Claude Fable 5.1 (`1.0%`), Claude Opus 5 (`4.6%`), Gemini 3.8 Flash (`5.5%`), Gemini 3.8 Flash Cyber (`6.0%`), GPT-6 Astra (`8.5%`), GPT-6.1 Sol (`8.6%`), Muse Spark 1.3 (`15.9%`), GLM 5.3 (`31.5%`), Grok 4.6 (`51.8%`), and Kimi K3 (`52.7%`).
- **Argon-Lineage Four-Layer Runtime Defense**: Carbon reuses the safety stack detailed in the linked [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf), combining **aligned training (SFT/RL)**, **inference-time input/output/thought classifiers & activation introspection probes**, **prompt-injection resilience**, and **AI Control action/chain-of-thought (CoT) monitoring**. Notably, the Argon report emphasizes **not training directly against AI Control monitor outputs** so CoT traces stay transparent rather than learning obfuscation.

Still, one engineering boundary cannot be relaxed: **`0.0%` on Gray Swan IPI proves that none of the evaluated test attempts succeeded—not universal immunity** against novel obfuscated payloads, multi-turn social engineering, or chained tool-output injections in production. Untrusted inputs must remain strictly sandboxed and gated by independent tool-layer authorization.

## Staged Rollout, Pricing Trajectory, and Production Validation Boundaries

Rather than immediate general availability, Google pairs Carbon with a gated release cadence and a scheduled two-step pricing transition:

1. **U.S. Government Pre-Release Testing**: Google notes active engagement in the U.S. government's voluntary pre-release testing process while iterating on guardrails.
2. **Cyber-Defender Seed & Fairwind Program Expansion**: Initial access starts with a subset of cyber defenders, expanding gradually to vetted partners through [Fairwind](https://deepmind.google/fairwind-program/). Fairwind rules restrict dual-use workflows (threat simulation, reverse engineering, malware analysis) to defensive and academic research, mandate user-level auth plus phishing-resistant MFA restricted to internal security/IR/pentest teams, prohibit sharing or reselling, and execute interactions inside continuously monitored environments (optionally paired with Google's *CodeMender* security agent).
3. **Deferred General Availability & Post-Intro Pricing Step**: Broader developer, enterprise, and consumer launch timing remains unspecified. Carbon debuts at Argon's introductory pricing (**`$2` per 1M input tokens**, **`$10` per 1M output tokens**, **`95%` off cached input tokens**), but footnote `1` explicitly warns that after the introductory period, pricing rises to **`$4` input / `$20` output per 1M tokens**. For multi-day agentic loops, doubling token rates materially shifts retry and cache-efficiency economics.

To translate these announcement claims into concrete pre-adoption checks for engineering teams:

| Primary Claim or Property | Reported Condition & Scope | What It Establishes vs. Leaves Open | Recommended Local Validation Gate |
| :--- | :--- | :--- | :--- |
| **Multi-day runs & `GraphWalks` `96.2%`** | Internal observations; `GraphWalks` `256k–1M` `200`-task self-run | Shows strong long-window retrieval; **omits** internal failure rates, retry multipliers, and token spend distributions | Benchmark multi-day loops on real CI failure repos with dollar caps budgeted at `$4/$20` post-intro rates |
| **3-stage cyber scores (`88.2%` / `54.8%` / `71.0%`)** | **Fairwind unguardrailed access**; `ExploitGym` mitigations off; `CWE-bench` mixed harnesses | Establishes raw defensive/offensive ceiling; **does not equal** guardrailed GA API performance or cross-harness parity | Re-benchmark inside your own scaffold (non-`Antigravity`) under fixed timeouts and production guardrails |
| **`0.0%` cheating & `~80%` alert reduction** | `Terminal-Bench 4.0` and internal live coding; exact internal alert denominator unpublished | Shows reduced reward hacking under stress; **cannot replace** immutable external verifiers | Mount test suites and evaluators read-only to the agent; audit tool traces for test/check edits |
| **Gray Swan IPI `0.0%` attack success** | Evaluated benchmark attempts (`k=1/10/15`) | Demonstrates strong gains over Argon (`0.7%`) and peers; **not** a mathematical proof against unseen adaptive injections | Enforce tool-level least privilege, egress controls, and human approval for high-blast-radius side effects |
| **Intro `$2/$10` (`95%` cache off) -> `$4/$20`** | Launch post + footnote `1`; GA release date open | Clarifies future `2×` unit-cost step and strong prompt-caching incentive; **omits** thinking-tier cost multipliers | Design prefix-stable prompt caching and pre-dispatch budget reservations before scaling concurrency |

Taken together, **Gemini 4 Carbon** marks a substantive step toward long-horizon, safety-instrumented coding and cyber-defense agents—explicitly separating vulnerability detection, exploit validation, and patching while targeting reward hacking directly in alignment training. At the same time, **lagging rows on `FrontierSWE 2` (`61.2%`) and `OSWorld-2.1` (`81.5%`), unguardrailed Fairwind evaluation conditions, undisclosed internal sample denominators, and the upcoming `$2/$10` to `$4/$20` price step** reinforce why engineering teams should treat Carbon's benchmark profile as a promising candidate signal until validated inside their own harnesses, sandboxes, and cost envelopes.

---

> **Provenance**: Expanded and rewritten by the assistant from Google's primary announcement (*"Gemini 4 Carbon: our next frontier model"*), the five official benchmark charts in the frozen HTML snapshot, and the directly linked `evals-methodology/gemini-4-carbon` PDF, Fairwind Program overview, and Gemini 4 Argon Safety & Security Report. Original `id`, `date`, `source_url`, `source_published_at`, `permalink`, `maintenance`, `authoring_source`, `translation_source`, and `systems-reliability` tag are preserved, alongside `_data/note_tags.yml` tags `coding-agents` and `agent-reliability`. Both `v3-blue` diagrams (`carbon-capability-cyber-profile-en.svg`, `carbon-safety-rollout-stack-en.svg`) are assistant-authored summaries (not original figures), distinguishing public benchmarks from provider-internal measurements without fabricating sample sizes or third-party results.
