---
id: supplement-2026-11-04
title: 2026-11-04 | Supplementary Research Readings
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English reading notes
source_type: paper
permalink: /digest/en/supplement/2026-11-04/
summary: 63 additional research and technical readings checked against primary sources.
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
---

[Return to the original digest](/digest/en/daily/2026-11-04/)

## ParetoSaddler: Pareto-Guided Optimization of Agent Harnesses for Quality and Cost
{: #reading-arxiv-2611.02079}

ParetoSaddler retains intermediate quality/cost progress using Bayesian-bootstrap Pareto support rather than pruning with the final deployment preference, then selects deployment candidates separately. Two domain-disjoint benchmarks improve quality and per-task cost.

Limitations: Repeated evaluation increases search cost. Bootstrap captures run variation on fixed tasks, not task-sampling uncertainty or total optimization expenditure.

Source: [ParetoSaddler: Pareto-Guided Optimization of Agent Harnesses for Quality and Cost](https://arxiv.org/abs/2611.02079)

## WebHarbor: Docking Real Websites for Evolving GUI Agent Environments
{: #reading-arxiv-2611.03634}

WebHarbor reconstructs 153 executable website environments and 3,518 tasks, expanding workflows through human–agent audits and covering post-login actions under deterministic control. It reduces evaluation drift from live websites.

Limitations: Reconstruction is not full equivalence; dynamic maps and similar behavior use surrogates. Training covers one 4B model, and graders can miss errors.

Source: [WebHarbor: Docking Real Websites for Evolving GUI Agent Environments](https://arxiv.org/abs/2611.03634)

## TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with TLA+ Proof System
{: #reading-arxiv-2611.02849}

TLAPS-Bench provides machine-checked proof development for 265 targets from 95 TLA+ specifications. Evaluation uses 70 targets from 12 specifications; the best configuration proves 31 under pass@3.

Limitations: This is not single-run success across all 265 targets. Proofs concern formal specifications/properties, not complete implementation correctness.

Source: [TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with TLA+ Proof System](https://arxiv.org/abs/2611.02849)

## An Agentic OS Kernel for Flexible and Enhanced Semantics
{: #reading-arxiv-2611.00002}

IntentOS accepts intents through isyscall, composes micro-syscalls through LLM planning and caches checked execution plans. Cache hits bypass inference, targeting redundant operations imposed by rigid interfaces.

Limitations: Roughly thirty intents and four kernel versions do not prove arbitrary composition safe. PDF dating conflicts with the arXiv identifier; no first-publication date is inferred.

Source: [An Agentic OS Kernel for Flexible and Enhanced Semantics](https://arxiv.org/abs/2611.00002)

## SpecGuardBench: Can Coding Agents Construct Reliable Validation Harnesses from Natural Language Specifications?
{: #reading-arxiv-2610.16870}

SpecGuardBench includes violating and valid alternative implementations to test specification-faithful harnesses. No agent exceeds 63% faithfulness across 291 tasks; a key failure is treating reference implementation details as requirements.

Limitations: Faithfulness is tested against retained benchmark implementations, not every possible program; reference code can induce overfitted checks.

Source: [SpecGuardBench: Can Coding Agents Construct Reliable Validation Harnesses from Natural Language Specifications?](https://arxiv.org/abs/2610.16870)

## Don't Guess, Just Ask: Evaluating Interactive Requirement Clarification for Repository-Level Software Development
{: #reading-arxiv-2610.13022}

ReqClarifyBench uses 341 repository-level tasks and simulated user personas to evaluate clarification of vague intent. More effective clarification does not necessarily yield better requirements documents, and coding harnesses add no further document-quality gain.

Limitations: LLM user simulation does not represent all real interactions; document quality, downstream code outcomes and persona distribution need separate interpretation.

Source: [Don't Guess, Just Ask: Evaluating Interactive Requirement Clarification for Repository-Level Software Development](https://arxiv.org/abs/2610.13022)

## LARK: Lean-Assisted Reasoning for LLM-Generated GPU Kernels
{: #reading-arxiv-2611.02028}

LARK uses Lean to verify segmentation and functional/memory equivalence against references, concentrating human trust in operator semantics. It verifies nine sampled library kernels and finds a race in another; the appendix explicitly uses pinned-kernel verify-only runs.

Limitations: Exact-arithmetic guarantees do not establish floating-point equivalence. Semantics remain trusted; results cannot be relabeled as measured full-generation-pipeline success.

Source: [LARK: Lean-Assisted Reasoning for LLM-Generated GPU Kernels](https://arxiv.org/abs/2611.02028)

## Ask, Don't Equip: Question-Driven Coding Agents for Deep Kernel Optimization
{: #reading-arxiv-2611.03517}

KernelSeek uses questions within a minimal validation harness to redirect optimization hypotheses, later collecting them into a reusable bank. Hopper and Blackwell attention kernels each pass 182 tested scenarios, with human messages and tool traces released.

Limitations: Gains following questions are observational, not randomized causal evidence. Human effort matters, and finite tests do not prove all-input correctness.

Source: [Ask, Don't Equip: Question-Driven Coding Agents for Deep Kernel Optimization](https://arxiv.org/abs/2611.03517)

## SpecPilot: Autonomous Algorithm Discovery and Systems Optimization for Speculative Decoding
{: #reading-arxiv-2611.02501}

SpecPilot uses cost ceilings to locate deployment bottlenecks, with agents exploring and integrating optimizations and token-forcing checks against stock outputs. Results emphasize different mechanisms for single-request and batched serving.

Limitations: The 10.87× figure is relative to AR, not stock. Finite output checks do not prove distribution equivalence for every input; search cost also matters.

Source: [SpecPilot: Autonomous Algorithm Discovery and Systems Optimization for Speculative Decoding](https://arxiv.org/abs/2611.02501)

## SpecOPD: Branch-Parallel On-Policy Distillation for Speculative Decoding
{: #reading-arxiv-2611.02846}

SpecOPD samples fresh drafter branches after reference anchors, sharing trunk computation while preserving branch histories. Its 16.09× supervised-token throughput combines faster updates and more supervision per update; the peak 3.56× AR inference gain is a separate metric.

Limitations: Native configurations differ and exclude offline reference preparation. Supervision throughput is not equal-quality training acceleration; gains vary by architecture and task.

Source: [SpecOPD: Branch-Parallel On-Policy Distillation for Speculative Decoding](https://arxiv.org/abs/2611.02846)

## AgentPRO: Coordinating Compiler Optimizations for LLM Agent Workflows
{: #reading-arxiv-2611.00628}

AgentPRO separates tool execution dependencies from observations needed for generation, merging compatible regions and removing redundant context with runtime guards. It completes 110 of 115 tasks while reducing mean tokens by 41.85%.

Limitations: The cohort is selected for baseline success, so baseline perfection is by construction. There is one attempt per task, and component time is not total user latency.

Source: [AgentPRO: Coordinating Compiler Optimizations for LLM Agent Workflows](https://arxiv.org/abs/2611.00628)

## SNAPPerf: Software-Aware Tabular Foundation Model for Retraining-Free Performance Prediction of Configurable Systems
{: #reading-arxiv-2611.00944}

SNAPPerf pretrains on synthetic configurable systems and uses a few new measurements as context without per-system retraining. Across 12 real systems, error averages 38% below the prior baseline at matched measurement budgets.

Limitations: No retraining does not mean no measurements. Immediate use after every version change remains a vision; error and sample savings depend on system and budget.

Source: [SNAPPerf: Software-Aware Tabular Foundation Model for Retraining-Free Performance Prediction of Configurable Systems](https://arxiv.org/abs/2611.00944)

## Agent Stack for ML Training Lifecycle: Generation, Validation, and Optimization
{: #reading-arxiv-2611.00384}

LinkedIn’s AutoTorch uses executable checks for model generation/migration; AutoResearch uses external experiment orchestration. Of 115 workflows, 92 complete training and 77 meet quality requirements; 28 of a separate 100 optimization pipelines improve.

Limitations: The roughly 4× migration speedup is a team estimate, not randomized evidence. Training completion and quality success have different denominators.

Source: [Agent Stack for ML Training Lifecycle: Generation, Validation, and Optimization](https://arxiv.org/abs/2611.00384)

## Characterizing and Predicting the Longest CI Builds in Machine Learning Projects
{: #reading-arxiv-2611.00667}

In the studied ML projects, the longest 18% of builds consume 80.30% of build time and 39.09% fail. Recent history and workflow structure help predict long builds; chronological XGBoost evaluation reaches F1 .775.

Limitations: Thresholds are dataset-specific and associations are not causal; findings do not justify removing tests or canceling builds by predicted failure.

Source: [Characterizing and Predicting the Longest CI Builds in Machine Learning Projects](https://arxiv.org/abs/2611.00667)

## Understanding GPU Megakernels: Why Residency Can Mislead
{: #reading-arxiv-2611.00495}

This megakernel study reconstructs separate kernels with the same operator code while controlling launch, prefetch and memory ordering. PDL lowers TK decode-step latency by 5.7%; resident CTAs do not imply useful capacity in the bottleneck resource.

Limitations: Evidence centers on two implementations and H100; it does not establish universal megakernel inferiority, and ordering-mismatched comparisons are invalid.

Source: [Understanding GPU Megakernels: Why Residency Can Mislead](https://arxiv.org/abs/2611.00495)

## Weights That Stay: On-Chip Megakernels for Serial Heads in Speculative Decoding
{: #reading-arxiv-2611.00506}

Weights That Stay retains projection shards on chip across the serial draft walk with GPU-side token/state advancement. Head execution accelerates up to 11.6×, while full SGLang throughput improves at most 12.3%.

Limitations: B200 tests only the head; end-to-end serving uses H100. Head speedup is not whole-model acceleration.

Source: [Weights That Stay: On-Chip Megakernels for Serial Heads in Speculative Decoding](https://arxiv.org/abs/2611.00506)

## Rethinking KV Cache Eviction for Agentic LLM Serving
{: #reading-arxiv-2611.00391}

Penelope preserves shared prefixes and private suffixes, recomputing missing segments rather than evicting costly late-history tokens first. It co-designs eviction, recomputation and GPU/CPU management rather than introducing holes into unchanged prefix-cache logic.

Limitations: It needs the corresponding correctness/indexing implementation. GPU-only and two-tier maxima use different conditions and cannot be combined.

Source: [Rethinking KV Cache Eviction for Agentic LLM Serving](https://arxiv.org/abs/2611.00391)

## Fairway: Load-Aware KV Cache Reuse for LLM Prefill Scheduling
{: #reading-arxiv-2611.02082}

Fairway uses virtual Fast/Fair lanes to balance KV reuse and normalized waiting time, favoring cheap hits in short queues while protecting expensive requests under congestion. It jointly targets median TTFT and starvation.

Limitations: Each request generates one token to isolate prefill. Tail-latency ratios do not establish full multi-turn agent completion gains.

Source: [Fairway: Load-Aware KV Cache Reuse for LLM Prefill Scheduling](https://arxiv.org/abs/2611.02082)

## LADS: Lease-Aware Delivery Scheduling of Tool Results for Language Model Agents
{: #reading-arxiv-2611.00881}

LADS schedules tool-result delivery using prefix-lease ownership and estimated resumption delay, freeing extra cache protection when requests resume. It reduces complete-workflow waiting under bursty, constrained return paths.

Limitations: Benefits depend on delivery bandwidth, concurrency and lease conditions; controlled bursts and web replay do not cover every agent network.

Source: [LADS: Lease-Aware Delivery Scheduling of Tool Results for Language Model Agents](https://arxiv.org/abs/2611.00881)

## When Shards Fly: Cross-Tensor In-Flight Conversion for Low-Latency, Low-Memory Weight Updates in Disaggregated RL
{: #reading-arxiv-2611.00646}

ShardFly compiles cross-tensor shard plans and fuses conversion, quantization, transfer and in-place writes in a persistent kernel, forwarding transformed bytes across replicas. Large update-only speedups yield 5.49–6.71% end-to-end GRPO response-throughput gains.

Limitations: It targets synchronous in-place updates with plan reuse under stable configurations; the peak 27.92× update gain is not training acceleration.

Source: [When Shards Fly: Cross-Tensor In-Flight Conversion for Low-Latency, Low-Memory Weight Updates in Disaggregated RL](https://arxiv.org/abs/2611.00646)

## Introducing Cluster Efficiency to LLM Serving: Pooling Economical Accelerators over Fast Interconnects
{: #reading-arxiv-2611.02975}

This study evaluates economical accelerators at cluster scale: fast links let Blackhole Galaxy reach 1.07–2.24× reference tokens per dollar under a three-year acquisition-plus-electricity model; slower-link emulation removes the advantage.

Limitations: The cost model is not full TCO and TCP-class links are emulated; throughput must be interpreted with latency, precision and software coverage.

Source: [Introducing Cluster Efficiency to LLM Serving: Pooling Economical Accelerators over Fast Interconnects](https://arxiv.org/abs/2611.02975)

## LoRAForge: Co-Designing Post-Hoc Compression and Execution for Efficient Multi-LoRA Serving
{: #reading-arxiv-2611.01256}

LoRAForge connects batched factor construction to rank-specialized serving. Across 85 adapters, a spectral allocation retains about 7.7% of parameters with fleet-average score loss at most 1.2 points.

Limitations: Compression is lossy and fleet means hide per-adapter regressions; factor construction, runtime and allocation-policy gains need separate accounting.

Source: [LoRAForge: Co-Designing Post-Hoc Compression and Execution for Efficient Multi-LoRA Serving](https://arxiv.org/abs/2611.01256)

## Scute: Exact Batched Serving for PEFT Adapters Beyond LoRA
{: #reading-arxiv-2611.01089}

Scute expresses DoRA, IA3, VeRA, OFT and other adapters through a six-slot normal form in modified batched LoRA kernels, avoiding approximate LoRA conversion and allowing mixed-method batches.

Limitations: Exact representation is not bitwise floating-point identity; measured error is normalized by adapter effect, and mixed methods still add overhead versus LoRA-only serving.

Source: [Scute: Exact Batched Serving for PEFT Adapters Beyond LoRA](https://arxiv.org/abs/2611.01089)

## Inference First, Training Underneath: Layer-Granular LoRA Co-Serving with LayerLoom
{: #reading-arxiv-2611.00652}

LayerLoom schedules LoRA backward at layer granularity using inference latency slack, maintaining a staggered microbatch wavefront with host-offloaded activation state so bursty inference takes priority over training.

Limitations: Evidence uses one 4090, model and rank-16 down_proj setting; SLO percentage-point gains depend on chosen thresholds, not a universal latency ratio.

Source: [Inference First, Training Underneath: Layer-Granular LoRA Co-Serving with LayerLoom](https://arxiv.org/abs/2611.00652)

## Jet-QSparse: Accelerating Agentic LLM Inference with 4-Bit Sparse Attention
{: #reading-arxiv-2611.01022}

Jet-QSparse scans keys in FP4 and aggregates selected value blocks at higher precision. Its 128-block quality setting must be distinguished from the 64-block peak 1.94× decode speedup; they are not one operating point.

Limitations: No detected quality loss is not losslessness. Smaller budgets regress; applicability depends on Blackwell and tested models/contexts.

Source: [Jet-QSparse: Accelerating Agentic LLM Inference with 4-Bit Sparse Attention](https://arxiv.org/abs/2611.01022)

## PagedMoE: Cross-Precision Expert Caching for Token-Level Dynamic Precision in SSD-Resident MoE Inference
{: #reading-arxiv-2611.03173}

PagedMoE represents precision levels as refinable bitplane prefixes, fetching only missing bits and executing compact states directly. Experts execute on CPU; cross-precision sharing is 1.33× faster than independent objects for identical dynamic-precision requests.

Limitations: The 2.5-bit figure is average lossy expert precision; near-INT4 quality is not universal equivalence, and experts do not execute on GPU.

Source: [PagedMoE: Cross-Precision Expert Caching for Token-Level Dynamic Precision in SSD-Resident MoE Inference](https://arxiv.org/abs/2611.03173)

## Apto: Self-Adaptive CPU-GPU Hybrid MoE Inference on Shared PCs
{: #reading-arxiv-2611.01859}

Apto lets CPU and GPU claim experts from opposite queue ends, adapting partitioning to actual progress, with affinity ordering and cancellable tail racing. It targets changing CPU contention on shared PCs rather than fixed offline splits.

Limitations: Gains depend on contention, core limits and models; larger contended-load ratios do not establish equal standalone performance on every PC.

Source: [Apto: Self-Adaptive CPU-GPU Hybrid MoE Inference on Shared PCs](https://arxiv.org/abs/2611.01859)

## Layer-wise CPU-GPU Scheduling for LLM Inference on Memory-Limited Consumer GPUs
{: #reading-arxiv-2611.01393}

This scheduler computes selected layers on CPU while asynchronously transferring the next GPU layer, hiding PCIe traffic when CPU work is cheaper than weight movement. Consumer-desktop OPT-30B tests outperform Accelerate and ZeRO-Inference.

Limitations: Outputs are only 32 tokens and evaluation emphasizes performance. Avoiding compression does not validate exact CPU/GPU numerical agreement or comprehensive quality.

Source: [Layer-wise CPU-GPU Scheduling for LLM Inference on Memory-Limited Consumer GPUs](https://arxiv.org/abs/2611.01393)

## Accelerating LLM Decoding with In-DRAM Parallelism
{: #reading-arxiv-2611.02401}

PUD-LLM reformulates projections through residual state to pack cross-layer work into DRAM parallelism, approximating corrections with fewer bit-serial steps. Performance simulations reach 1.41× the PUD baseline.

Limitations: These are performance simulations, not end-to-end silicon measurements. Approximate corrections trade quality for efficiency and are not lossless GPU replacements.

Source: [Accelerating LLM Decoding with In-DRAM Parallelism](https://arxiv.org/abs/2611.02401)

## RankLane: Efficient MoE Prefill on Accelerators with Ranked Expert Capacities
{: #reading-arxiv-2611.00421}

RankLane assigns experts by current load rank to fixed-capacity lanes, preserving compiled shapes and device ownership while rerunning overflowing chunks at full capacity. It reduces MoE padding on static-plan accelerators.

Limitations: Results concern batch-one prefill on a four-SoC card. Calibration and recovery are required; prefill ratios do not generalize to decoding.

Source: [RankLane: Efficient MoE Prefill on Accelerators with Ranked Expert Capacities](https://arxiv.org/abs/2611.00421)

## Sonar-MoE: In-Backward Expert Updates for Memory-Efficient Mixture-of-Experts Training
{: #reading-arxiv-2611.03577}

Sonar-MoE updates each batched expert tensor during backward and immediately frees its gradients, lowering peak memory by 19–22%. Batched updates avoid per-expert hook overhead.

Limitations: Bitwise agreement is with baselines without expert-gradient clipping. Global clipping and multi-step accumulation cannot directly preserve their original semantics.

Source: [Sonar-MoE: In-Backward Expert Updates for Memory-Efficient Mixture-of-Experts Training](https://arxiv.org/abs/2611.03577)

## Accelerating LLM Pretraining with Zeroth-Order Curvature on Idle Serving Compute
{: #reading-arxiv-2611.02688}

ZO-Curv uses idle forward-only devices for curvature estimation alongside first-order pretraining rather than direct noisy zeroth-order gradients. A 770M experiment reaches the specified AdamW validation loss in 3.9 rather than 7.5 hours.

Limitations: It uses additional compute, so this is not halved cost at equal resources. Model scale and available idle capacity limit deployment extrapolation.

Source: [Accelerating LLM Pretraining with Zeroth-Order Curvature on Idle Serving Compute](https://arxiv.org/abs/2611.02688)

## FlyWheel: Attention Kernels Built for the TPU
{: #reading-arxiv-2611.01426}

FlyWheel restructures softmax and linear attention for TPU, reducing vector work, reusing matrix operands and overlapping independent computation. Peak kernel ratios exceed the up-to-1.56× prefill-throughput gain after vLLM integration.

Limitations: Chip/TensorCore counts differ on v6e and v7x. Prefill gains are not universal request speedups; numerical approximations still require quality checks.

Source: [FlyWheel: Attention Kernels Built for the TPU](https://arxiv.org/abs/2611.01426)

## Multi-Turn Semantic Caching for Low-Cost LLM Serving
{: #reading-arxiv-2611.01077}

This multi-turn semantic cache learns reuse risk from judge feedback and balances avoided generation cost against unacceptable answers. Structured tutoring/ticketing benefit, while only about 1–2% of open-chat follow-ups are safely reusable.

Limitations: Judges and recurring-state assumptions matter. Latency gains are estimated and do not cover all open chat; semantic similarity alone does not establish valid reuse.

Source: [Multi-Turn Semantic Caching for Low-Cost LLM Serving](https://arxiv.org/abs/2611.01077)

## Seeing What Matters, Verifying What Pays: Load-Adaptive Speculative Decoding for Vision-Language Models
{: #reading-arxiv-2611.01617}

Uni-LaSpec selects a few visual tokens using previous verifier attention and switches between tree and truncated-linear verification by GPU load. Eight visual tokens retain at least 98.6% of full-image draft acceptance, not an image-quality score.

Limitations: There are exceptions to the 123/144 fixed-strategy matches. Peak throughput uses greedy single-concurrency decoding, separate from burst-latency results.

Source: [Seeing What Matters, Verifying What Pays: Load-Adaptive Speculative Decoding for Vision-Language Models](https://arxiv.org/abs/2611.01617)

## FactorSpec: Serving Exact Relational Constraints as Speculative Drafts
{: #reading-arxiv-2611.02297}

FactorSpec compiles JSON Schema and field relations into an exact-feasibility factor graph, drafts constraint-determined tokens and computes masks asynchronously. It optimizes decoding and valid-record production together.

Limitations: The peak 13.9× is valid records per GPU-second; decoding peaks at 1.43×. Guarantees cover expressible relations and the implemented constraint model.

Source: [FactorSpec: Serving Exact Relational Constraints as Speculative Drafts](https://arxiv.org/abs/2611.02297)

## Who Schedules Agent Memory? A Sidecar Approach to Long-Horizon Tasks
{: #reading-arxiv-2611.00779}

MemSidecar offers event-triggered Hooks and independent predictive Foresight retrieval, reducing main-agent memory-scheduling work. Prefetched results are delivered only when matching actual requests and still valid.

Limitations: The extra predictor has cost. Modes and benchmarks require separate comparisons; a prefetch hit does not prove memory content correct.

Source: [Who Schedules Agent Memory? A Sidecar Approach to Long-Horizon Tasks](https://arxiv.org/abs/2611.00779)

## Capacity Planning for Resource-Constrained Clinical LLM Serving
{: #reading-arxiv-2611.01152}

This four-GPU study fixes hardware and workloads while varying model mix and routing. Fleet composition causes larger observed shifts in latency and long-context coverage than tested routing changes; capacity-aware routing manages demand within provisioned limits.

Limitations: These are descriptive systems results across 24 configurations. Long-context coverage is not clinical correctness or evidence for clinical deployment.

Source: [Capacity Planning for Resource-Constrained Clinical LLM Serving](https://arxiv.org/abs/2611.01152)

## TRIAGE: Reliability- and Load-Conditioned Escalation for Two-Tier LLM Serving with a Semantic Evidence Judge
{: #reading-arxiv-2611.01174}

This TRIAGE study retains its failed claim: preregistered corruption detection reaches only AUROC .571; semantic-judge improvements are post hoc. The actual 7B→32B quality gap is small, so the allocator declines escalation—the main end-to-end result is null.

Limitations: It differs from the published miniTE training controller with the same name. API savings depend on price ratios and do not transfer to open-model pairs or become preregistered evidence.

Source: [TRIAGE: Reliability- and Load-Conditioned Escalation for Two-Tier LLM Serving with a Semantic Evidence Judge](https://arxiv.org/abs/2611.01174)

## STLT: A Novel System for Energy-Aware Distributed Inference in the Edge-Cloud-Space Continuum
{: #reading-arxiv-2611.01233}

STLT filters favorable DNN split points offline, then cheaply selects satellite/ground execution using current energy and environmental state, accounting for computation and downlink together.

Limitations: Real telemetry is not in-orbit execution validation; decision-module energy and total-system energy reductions have different scopes.

Source: [STLT: A Novel System for Energy-Aware Distributed Inference in the Edge-Cloud-Space Continuum](https://arxiv.org/abs/2611.01233)

## Parallelism-Aligned Pruning and Round-Aware Context Reuse for On-Device Multimodal Agents
{: #reading-arxiv-2611.02601}

PARC prunes attention heads to shapes divisible across seven cores and separates persistent text from transient image KV. A parameter-matched control attributes most speedup to core alignment rather than parameter reduction alone.

Limitations: Task recovery training is required and old images leave persistent cache. No regression on 2,062 actions does not establish preserved semantics for every old-image-dependent task.

Source: [Parallelism-Aligned Pruning and Round-Aware Context Reuse for On-Device Multimodal Agents](https://arxiv.org/abs/2611.02601)

## A Self-Exploring and Self-Evolving Paradigm for Adaptive Edge AI Development
{: #reading-arxiv-2611.01377}

SE2 lets agents dynamically choose retrieval, reasoning, coding and testing, with continued model adaptation. Beyond augmented IoTBench, generated programs run on laptops, Jetson Nano and Raspberry Pi under changes such as missing modalities.

Limitations: Code-embedding similarity is not functional correctness. Model tuning and workflow changes interact; tested cases do not cover arbitrary unseen edge tasks.

Source: [A Self-Exploring and Self-Evolving Paradigm for Adaptive Edge AI Development](https://arxiv.org/abs/2611.01377)

## Action Verification through Conjecture and Refutation for Language Model Agents
{: #reading-arxiv-2611.02950}

BlackSwan predicts an action’s effect, formulates testable suspicions and tries to refute them through observations or non-mutating actions before committing. AppWorld and WebShop experiments show improved action-task outcomes.

Limitations: Failure to find a counterexample is not proof of safety. Tests add cost and simulated applications/shopping do not cover all real side effects.

Source: [Action Verification through Conjecture and Refutation for Language Model Agents](https://arxiv.org/abs/2611.02950)

## When AI Agents Act on Our Behalf: A Taxonomy of Human-Agent Interaction Failure
{: #reading-arxiv-2611.00291}

This study derives 12 interaction failures from 695 documented incidents in two public repositories, examining when users can observe, stop and undo agent actions. All modes occur at both autonomy levels; autonomy changes their form and intervention window.

Limitations: Public incidents have reporting/selection bias; they cannot establish incidence rates or universal causal primacy of configuration over model capability.

Source: [When AI Agents Act on Our Behalf: A Taxonomy of Human-Agent Interaction Failure](https://arxiv.org/abs/2611.00291)

## CUA-Master: Scaling Computer-use Agents through Open-World Recursive Improvements
{: #reading-arxiv-2611.03126}

CUA-Master mines workflows from instructional videos, converts them to reusable task primitives and expands data using model-weakness feedback. Snapshot rollback reduces recollection after failure, linking open-world sources with controlled task generation.

Limitations: Recursive training and VM infrastructure are costly. OSWorld-Verified and 2.0 measure different settings; one leaderboard score cannot summarize generalization.

Source: [CUA-Master: Scaling Computer-use Agents through Open-World Recursive Improvements](https://arxiv.org/abs/2611.03126)

## NorthCUA Technical Report: Turbocharging Computer-Use Agents through Experience at Scale
{: #reading-arxiv-2611.02102}

NorthCUA connects task generation, execution records, evidence-linked outcome checks and staged learning, preserving verified milestones from unfinished tasks. Collection judges can inspect workspaces; benchmark evaluation uses independent scorers.

Limitations: Open-ended judges depend on calibration and predicate coverage. New software/interfaces remain difficult; illustrative evidence chains do not establish aggregate error rates.

Source: [NorthCUA Technical Report: Turbocharging Computer-Use Agents through Experience at Scale](https://arxiv.org/abs/2611.02102)

## MemU-Bench: Benchmarking GUI Agents on Long-Horizon User Interactions
{: #reading-arxiv-2611.00191}

MemU-Bench builds 118 vague mobile tasks from 29 user histories, using SPL to distinguish context recovery from exhaustive search. With AppMem, the GPT configuration rises from 15.7% to 66.9% SPL—51.2 percentage points.

Limitations: Only 44.9% of tasks are entirely rule-scored; the rest require an LLM judge. Low temperature does not ensure correctness or fully deterministic backend validation.

Source: [MemU-Bench: Benchmarking GUI Agents on Long-Horizon User Interactions](https://arxiv.org/abs/2611.00191)

## Coati: Host-Grounded Execution for Installable Mobile GUI Agents
{: #reading-arxiv-2611.02644}

Coati records host-side action effects and cross-app state, marking unauditable completion claims unverified through VerifyLoop. Same-model AndroidWorld evaluation reaches 86.5%, with separate real-phone fast-execution tests.

Limitations: AndroidWorld uses an Android 13 emulator, not 116 real-phone tasks. Fewer reasoning calls do not establish fully local inference or no network dependence.

Source: [Coati: Host-Grounded Execution for Installable Mobile GUI Agents](https://arxiv.org/abs/2611.02644)

## Optimize the Harness, Not the Model: Fitting a Minimal Agent to a Self-Hostable LLM for Investigative Analysis
{: #reading-arxiv-2611.03434}

CLEO starts with a minimal harness, retaining tools, guardrails and memory policies that help expert-validated investigative tasks. In one domain its held-out pass rate is 83.8%, close to the strongest out-of-box SDK baseline.

Limitations: The LLM judge is spot-checked rather than systematically validated. A hundredfold smaller codebase does not prove equal reductions in attack risk or maintenance cost.

Source: [Optimize the Harness, Not the Model: Fitting a Minimal Agent to a Self-Hostable LLM for Investigative Analysis](https://arxiv.org/abs/2611.03434)

## Latent Harness: Compiling Agent Behaviors into Post-Block Activation Shifts
{: #reading-arxiv-2611.01415}

Latent Harness distills external behavior into low-rank post-block shifts on frozen models, removing repeated harness text while exposing strength, phase and mixing controls. Eight of ten preregistered settings recover the original gains.

Limitations: Training and adapter execution still cost resources. Only five transfer pairs are positive; shifts cannot replace dynamic permissions or arbitrary harness controls.

Source: [Latent Harness: Compiling Agent Behaviors into Post-Block Activation Shifts](https://arxiv.org/abs/2611.01415)

## Causality-Based Fault Localization
{: #reading-arxiv-2611.01292}

SoftReX ranks fault locations through actual causal responsibility and mutation distance, penalizing broken passing tests. Better ranking on the same mutants and fewer evaluations through structured generation are separate contributions.

Limitations: Causality is relative to the program model, tests and mutation space. Ranking is not repair correctness; 2.6× fewer mutants is not total debugging acceleration.

Source: [Causality-Based Fault Localization](https://arxiv.org/abs/2611.01292)

## VerusWeave: A Benchmark for Proof Repair in Concurrent Verus Programs
{: #reading-arxiv-2611.00287}

VerusWeave removes proof annotations from four projects while preserving executable code and specifications, checking repairs with Verus and a change checker. Success falls from 75–85% on 75 focused tasks to 29–47% on 17 module variants.

Limitations: Tasks derive from existing proofs and samples are small. They do not represent proving arbitrary concurrent programs from scratch; verifier and specification remain trusted.

Source: [VerusWeave: A Benchmark for Proof Repair in Concurrent Verus Programs](https://arxiv.org/abs/2611.00287)

## Stop Handcrafting Your Engine! GenDB-V: Towards AI-Generated and Formally Verified Database Systems
{: #reading-arxiv-2611.02779}

GenDB-V fixes implementation-independent SQLSpec targets before jointly searching code and proofs, checking them in isolation. Template-specialized implementations and a general engine for a supported SQL subset are evaluated separately; the latter gains 1.27–3.4×.

Limitations: Template gains of 22–61.3× are not full-database acceleration. Guarantees depend on SQLSpec, verification and the supported subset, not every SQL feature.

Source: [Stop Handcrafting Your Engine! GenDB-V: Towards AI-Generated and Formally Verified Database Systems](https://arxiv.org/abs/2611.02779)

## AdapBench: Adaptive Early-Stopping and Prioritization for Efficient Microbenchmarking in Cloud-based CI/CD
{: #reading-arxiv-2611.01255}

AdapBench prioritizes microbenchmarks near statistical decisions and stops once enough evidence accumulates. Recorded-data replay saves 42% aggregate Java duration at matched detection/false-positive rates and 85% on Go.

Limitations: The prototype replays data rather than demonstrating a new live CI deployment. Zero observed Go false positives is not zero risk; matched 90% detection retains misses.

Source: [AdapBench: Adaptive Early-Stopping and Prioritization for Efficient Microbenchmarking in Cloud-based CI/CD](https://arxiv.org/abs/2611.01255)

## Progress on provable inference for large language models
{: #reading-anthropic-provable-inference}

FlashProve addresses which committed model performed a computation, rather than whether its answer is correct. A provider commits to hidden weights and produces a zkSNARK that anyone holding the commitment, input and result can check without the weights. It hides weights and expert choices, not architecture. Proving that approved inference occurred does not prove that the server performed no other work.

The implementation proves after the fact. Finished text is recomputed through a parallel, prefill-like path; work scales with the MoE experts actually used. Segmented host-to-device streaming lets one H100 work with substantial host memory. Evaluation uses 4-bit Llama 4 Maverick and integer arithmetic. Each request contains a 1,024-token window, but each proof checks one token. Proving 24 requests takes about 223 seconds: the quoted 110 tokens/s counts contextual processing, not 110 newly generated tokens proved each second. A proof is about 18.78MB and takes about 17 seconds to check on 24 CPU threads. Offline commitment takes around 39 minutes and has a request-count lifetime.

The trust boundary matters. Lean formalizes top-level properties in the random-oracle model and supplies an executable verifier connected to the soundness theorem. The everyday C++ verifier agrees in tests but lacks that formal guarantee. Correspondence between the prover implementation and formal protocol still requires auditing, particularly for zero knowledge. Humans must also assess whether the formal statements express the intended claims.

The authors report roughly 72–94× GPU-time overhead relative to FP8 vLLM. This is neither zero-overhead online attestation nor a same-numerics kernel comparison. Useful follow-up questions include sampled post-hoc verification, commitment lifecycle management and the interval between proof arrival and irreversible external actions. The repository explicitly describes an unmaintained research artifact. No proof generation, Lean build or independent cryptographic audit was performed here.

Limitations: Proofs concern declared quantization, arithmetic and protocol, not original floating-point models, factual correctness or unchecked response tokens. Overhead, post-hoc delay and implementation correspondence remain deployment limits.

Source: [Progress on provable inference for large language models](https://www.anthropic.com/research/provable-inference)

Implementation and documentation: [FlashProve](https://github.com/anthropics/FlashProve).

## Honeycomb Introduces AI SRE Agents That Go Beyond Incidents
{: #reading-honeycomb-ai-sre-agents}

Honeycomb distinguishes personal assistance from team goal agents, linking findings to queries, traces or deploys and separating confirmation from hypothesis. Personal actions require instructions; teams configure autonomous permissions.

Limitations: The release gives no diagnostic-accuracy or recovery benchmark, and survey methods are incomplete. Capabilities are not validated SRE outcomes.

Source: [Honeycomb Introduces AI SRE Agents That Go Beyond Incidents](https://honeycomb.io/blog/honeycomb-introduces-ai-sre-agents)

## Pika H3 Flex in FastVideo: 7x Faster, and Near Real Time in 4-bit
{: #reading-haoailab-pika-h3-flex}

FastVideo optimizes Pika H3 Flex attention, small-operation fusion and VAE decoding, with NVFP4 QAD variants. The headline 7× compares optimized four-GPU execution with a one-GPU reference; the matched four-GPU ratio is at most 4.58×.

Limitations: Timings are warm medians with resident models, excluding loading. Precision and decoder also change; near-real-time 480p results do not generalize to higher resolutions.

Source: [Pika H3 Flex in FastVideo: 7x Faster, and Near Real Time in 4-bit](https://haoailab.com/blogs/pika-h3-flex/)

## Scaling NVIDIA TensorRT Performance Optimization Beyond a Single Build Route with the Global Performance Tuner, Part 1
{: #reading-nvidia-tensorrt-global-performance-tuner-1}

TensorRT Global Performance Tuner treats graph transforms, fusion, kernels, layout and quantization as interacting build routes, searching acceptable engines under end-to-end accuracy constraints rather than selecting operators independently.

Limitations: Part 1 mainly establishes the framework; tuner gains were not tested here. Candidate space and accuracy-check coverage bound the result.

Source: [Scaling NVIDIA TensorRT Performance Optimization Beyond a Single Build Route with the Global Performance Tuner, Part 1](https://developer.nvidia.com/blog/scaling-nvidia-tensorrt-performance-optimization-beyond-a-single-build-route-with-the-global-performance-tuner-part-1/)

## open-flapping-airplanes: reproducing the flapping airplanes megakernel
{: #reading-github-open-flapping-airplanes}

open-flapping-airplanes independently reconstructs a persistent GPU kernel from a demo, co-running training, serving and Doom. B200 training of a 162.4M model takes 48.1 seconds, beating eager baselines but trailing CUDA-Graph Megatron’s 43.1 seconds.

Limitations: It is not reproduction from original source or production-scale LLM validation. Workloads receive fixed SM shares; concurrency is not free shared capacity.

Source: [open-flapping-airplanes: reproducing the flapping airplanes megakernel](https://github.com/Bobliuuu/open-flapping-airplanes)

## Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights
{: #reading-weight-space-programming}

The Qwen3.5-0.8B weight-space editing case changes about 0.016% of weights, reducing reasoning loops and raising MATH-500 from 7.9% to 48.1%. It removes an obstacle to existing ability; a non-looping Gemma control shows no established math gain.

Limitations: It still uses controlled forward feedback, not universal zero-data optimization. Raw-weight-only sycophancy detection fails; future capability speculation is not evidence.

Source: [Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://rikiyat.github.io/blog/weight-space-programming/)

## F3 Lightning: How Meta Accelerates Ads ML Features to Production at Scale
{: #reading-meta-f3-lightning}

F3 Lightning separates per-feature release from shared execution, preventing one invalid definition from blocking all updates. Stable computation IDs, shared plans and buffers retain common work; Meta reports roughly 3.6× faster production release for comparable features.

Limitations: The 3.6× figure is release lead time, not inference throughput. Compute parity is comparison-specific, not zero engineering cost or universal feature isolation.

Source: [F3 Lightning: How Meta Accelerates Ads ML Features to Production at Scale](https://engineering.fb.com/2026/11/03/ml-applications/f3-lightning-how-meta-accelerates-ads-ml-features-to-production/)

## Trace linkage: connect the dots between your app traces and database queries
{: #reading-grafana-trace-linkage}

Grafana trace linkage matches SQL samples through sqlcommenter trace/span IDs, falling back to normalized query text and database context. The fallback supplies query history, not a definitive record of that execution.

Limitations: Alloy polling can miss short queries, so exact matching is best-effort. SQL comments can affect database caches; linkage is not root-cause proof.

Source: [Trace linkage: connect the dots between your app traces and database queries](https://grafana.com/blog/trace-linkage-connect-the-dots-between-your-app-traces-and-database-queries/)

## Agents make decisions at runtime—your security controls should too
{: #reading-datadog-runtime-security-ai-agents}

Datadog AI Guard places checks at prompt, output and tool boundaries inside the agent loop, combining session, dependency and policy context for blocking/sanitization and trace-linked investigation.

Limitations: The article provides no attack recall, false-positive or inline-overhead benchmark. Blocking capability does not replace independent adversarial evaluation.

Source: [Agents make decisions at runtime—your security controls should too](https://www.datadoghq.com/blog/runtime-security-for-ai-agents/)
