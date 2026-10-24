---
id: anthropic-formal-verification
title: '2026-10-23 | Turning Fuzz Tests into Proofs: Claude Scales Binary Verification'
date: '2026-10-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- coding-agents
- systems-reliability
summary: Anthropic and Theorem turn existing fuzz tests into binary-level specifications,
  obtaining proofs for 239 entry points across 123 libraries. Trusted components,
  patch constraints, and proof reuse determine what this progress means.
long_read: true
source_url: https://www.anthropic.com/research/formal-verification
permalink: /tech/en/anthropic-formal-verification/
organization: Anthropic / Theorem
translation_source: assistant
editorial_status: source-checked
published_at: '2026-10-24T12:04:05.025845+08:00'
updated_at: '2026-10-24T12:04:05.025845+08:00'
---
Having an agent submit machine-checkable proofs alongside code is moving from small programs toward real dependencies. The notable advance in this collaboration between Anthropic and Theorem is the use of existing fuzz tests as the starting point for specifications, with Claude constructing proofs about compiled programs. For systems reliability, this can turn some instances of “testing has found no problem” into guarantees with explicit assumptions and scope.

**Original:** [LLMs are making formal software verification feasible at a much larger scale](https://www.anthropic.com/research/formal-verification)  
**Authors:** Keane Lucas, Aengus Lynch, Luna Tong, and colleagues; Anthropic Frontier Red Team in collaboration with Theorem. **First published:** 2026-10-22.

## Deriving a provable target from a test entry point

Formal verification starts with a difficult specification problem. A parser may follow a format standard, but describing every aspect of a complex application's correct behavior is much harder. This project uses existing OSS-Fuzz entry points, treating test failures, failed assertions, and detectable memory errors as crashes, then proving that an entry point cannot trigger those behaviors within a specified input range. Domain knowledge already encoded by maintainers can therefore become part of a theorem.

The pipeline compiles the library, test driver, and AddressSanitizer (ASan) into a RISC-V executable. Theorem's instruction and Linux process semantics then support specification generation. Claude constructs a Rocq proof, which the Rocq kernel checks. Where testing executes many samples, the proof quantifies over every input within its bounds. The guarantee still depends on the correctness of the machine model, theorem statement, and checker.

<a class="note-image-link" href="/assets/images/tech/anthropic-formal-verification/pipeline.png" target="_blank" rel="noopener" aria-label="From test source code to a binary proof checked by Rocq · View original image ↗"><img src="/assets/images/tech/anthropic-formal-verification/pipeline.png" alt="Source compiles into a RISC-V program; machine semantics and the desired property generate a specification; Claude writes a proof checked by the Rocq kernel. Blue boxes identify trusted components and green boxes show conditional proof results." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Follow the arrows through compilation, specification generation, and proof checking. The blue boxes below define the assumptions behind the green conclusions. The original diagram labels the bound in MB; the technical appendix specifies inputs smaller than 64 MiB.*

Working at the binary level directly addresses compiled artifacts, avoiding another potential behavioral mismatch from a separately written source interpreter. The cost is that the proof must also handle runtime initialization, allocation, and the test driver. The authors report obtaining proofs for 239 entry points across 123 libraries over several weeks, after patching discovered bugs, with approximately 180 million lines of checked Rocq proofs. This establishes the scale of completed work; it does not establish a success rate across OSS-Fuzz as a whole.

## Connecting the ASan build to the ordinary program

The [technical appendix](https://www-cdn.anthropic.com/files/4zrzovbb/website/6867eadf760258fa8b42a504600cd3c036d16358.pdf) explains how the guarantee connects an instrumented build with an ordinary build. The authors separately prove that neither binary encounters faults, aborts, or unmodeled behavior. They also prove that, for all inputs smaller than 64 MiB and all memory layouts, the binaries have matching read/write event sequences, exit behavior, and final filesystem states.

Behavioral equivalence alone is insufficient. Under the trace definition used here, a crash and a silent infinite loop can leave the same finite trace. The ordinary binary therefore needs its own crash-freedom proof. Crash freedom should not be extended into a universal termination guarantee, nor should equivalence imply equal performance. This detail illustrates why specification design matters: an informal claim of safety must be decomposed into propositions that the checker actually verifies.

## Proof obstacles can expose bugs that testing misses

A proof must handle arbitrary inputs satisfying its premises, including conditions that random mutation may rarely reach. The authors describe a counter underflow causing an out-of-bounds write in decompression code on an approximately 20 MB input with a rare layout. Another image-decoder issue required a 64 MB input and more than 2 GB of memory. The article notes that fuzzing inputs are typically capped at 1 MB, helping explain why long testing campaigns can miss such cases.

An agent can patch a program, regenerate the specification for the new binary, and resume proving it. However, a patch changes the object being verified: deleting functionality could make crash freedom easier to establish. The team therefore penalized patches, encouraged proofs describing which inputs had changed behavior, and logged and audited modifications. For coding agents, the engineering implication is that acceptance criteria must constrain both safety and preservation of functionality. A proof checker does not decide whether a change respects product intent.

Guarantees can also extend beyond memory errors. If a test expresses an encode-decode check through assertions, proving that the failing branches are unreachable can establish the corresponding functional property. The exact coverage still depends on the checks the entry point expresses.

## Scaling costs involve both generation and reuse

The appendix reports roughly one billion lines of Rocq generated across attempts, of which approximately 180 million belonged to successful proofs. A typical completed proof has about 600,000 lines, with more than half emitted by tools the agents wrote. Checking one proof takes 30 minutes to several hours of CPU time. Proof size is therefore neither a direct measure of model-written reasoning nor a substitute for computational cost.

The authors compare models on 36 reduced tasks. Inputs are limited to 64 bytes, much of the runtime is replaced, and a simplified mini-ASan is used; the programs contain only 283–2,491 instructions. Each task receives three independent single-agent attempts, each with a five-million-token budget, and success is counted when the first attempt finishes. The authors report that Opus 5.5 needs approximately 40% fewer tokens than Opus 5 to complete half the tasks. This supports a generation-efficiency improvement on reduced tasks; it cannot directly establish the same cost reduction for real dependency libraries.

<a class="note-image-link" href="/assets/images/tech/anthropic-formal-verification/token-budget.png" target="_blank" rel="noopener" aria-label="Token budgets and completion rates for 36 reduced verification tasks · View original image ↗"><img src="/assets/images/tech/anthropic-formal-verification/token-budget.png" alt="Token budget per agent on the horizontal axis and share of 36 tasks completed on the vertical axis, comparing Opus 5.5, Fable 5.1, and Opus 5." loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Compare horizontal budgets at the same completion rate. This measures tokens needed to generate proofs, not program execution performance or the average cost of verifying a complete library.*

A shared-workspace experiment also reports a 17% token saving. The engineering motivation is clear: different programs carry common components such as startup code and ASan, so reusing proofs can reduce repeated work. Nevertheless, the expert assessment notes that current proofs still expand many register, address, and branch details explicitly. More complex programs may require modular structures such as function contracts and memory abstractions; simply accumulating longer proofs may not continue to scale.

## Watch how closely the guarantees approach deployment

The main results currently concern single-threaded, statically linked RISC-V Linux binaries using musl and a fixed memory budget. They do not directly cover common x86/ARM deployments, dynamically linked glibc, or concurrent execution. ASan also misses some memory-safety problems, the proven entry points do not cover entire libraries, and callers can still misuse them.

This work increases the scale of machine-checkable guarantees for real code. Its practical value also depends on whether specifications capture requirements, patches preserve functionality, and machine models match deployed environments. Read the article's workflow and limitations first, then the appendix's equivalence definition and expert assessment. The [released proof repository](https://github.com/theorem-labs/oss-verify-proofs) helps illustrate the deliverables. The next developments to watch are more accurate deployment semantics, composable proof components, and the cost of maintaining proofs after code changes.
