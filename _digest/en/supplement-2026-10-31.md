---
id: supplement-2026-10-31
title: 2026-10-31 | Supplementary Research Readings
date: '2026-10-31'
lang: en
published: true
layout: article
maintenance: daily-research
translation_source: assistant-authored paired Chinese/English reading notes
source_type: paper
permalink: /digest/en/supplement/2026-10-31/
summary: 35 additional research and technical readings checked against primary sources.
tags:
- agent-reliability
- systems-reliability
---

[Return to the original digest](/digest/en/daily/2026-10-31/)

## JetSpec++: Foresight Parallel Drafting with Self Refinements
{: #reading-arxiv-2610.19792}

JetSpec++ drafts the next block on a second GPU and refines it while verification runs. Qwen3-8B reaches up to 1,361 tokens/s in bf16 for a single request; it hides drafting latency rather than eliminating draft computation.

Limitations: It uses two GPUs. Higher NVFP4 speed is a different precision setting; high batches and larger models need validation, and latency gains are not per-GPU cost gains.

Source: [JetSpec++: Foresight Parallel Drafting with Self Refinements](https://arxiv.org/abs/2610.19792)

## ConfluxServe: Reconciling Resource Utilization and Parallelism Efficiency across Prefill and Decode in LLM Serving
{: #reading-arxiv-2610.37810}

ConfluxServe co-executes prefill and decode within one batch using different parallel strategies across operators. It reports 1.26–1.62× goodput over strongest baselines under TTFT/TBT constraints, addressing utilization without forcing uniform phase parallelism.

Limitations: Goodput depends on SLOs, workload and parallel configuration; it is not a raw-throughput multiplier for every model.

Source: [ConfluxServe: Reconciling Resource Utilization and Parallelism Efficiency across Prefill and Decode in LLM Serving](https://arxiv.org/abs/2610.37810)

## FAD-KV: Adaptive Dictionary KV Caching for Efficient Reasoning Decoding
{: #reading-arxiv-2610.37921}

FAD-KV reduces sparse-coding cost with one-shot Top-n screening and light coefficient refinement, then reuses inactive dictionary atoms to adapt to KV drift without unbounded growth. Its target is a quality–efficiency tradeoff under bounded dictionary memory.

Limitations: Compression is lossy. Append-style baselines can use larger dictionaries, so comparisons must include quality, total cache size and coding cost.

Source: [FAD-KV: Adaptive Dictionary KV Caching for Efficient Reasoning Decoding](https://arxiv.org/abs/2610.37921)

## GAUSS: A Workload-Aware Analytical and Monte-Carlo Simulator for LLM Inference Serving
{: #reading-arxiv-2610.37989}

GAUSS combines prefill/decode latency surfaces, queueing recurrence and Monte Carlo to model TTFT/TBT distributions and explore capacity, segmentation and SRPT. It makes arrival variability and request shapes explicit instead of relying on mean throughput alone.

Limitations: Predictions depend on calibration and queueing assumptions. Broad comparisons with trace methods do not replace independent error validation; the simulator was not run here.

Source: [GAUSS: A Workload-Aware Analytical and Monte-Carlo Simulator for LLM Inference Serving](https://arxiv.org/abs/2610.37989)

## GearUp: DAG-aware Acceleration for Serverless Inference Serving via Slack-guided Pre-loading
{: #reading-arxiv-2610.38196}

GearUp schedules library, weight and CUDA-kernel loading within upstream DAG slack and reuses initialized instances. Two L40S workflows show 64.5% and 75.9% lower median end-to-end latency than SMIless.

Limitations: Benefits depend on slack, loading profiles and reuse. Cold-execution and eager-preload comparisons use different baselines and must remain separate.

Source: [GearUp: DAG-aware Acceleration for Serverless Inference Serving via Slack-guided Pre-loading](https://arxiv.org/abs/2610.38196)

## GAAC: Lossless KV Compression for Bandwidth-Efficient LLM Inference on Personal Devices
{: #reading-arxiv-2610.38210}

GAAC exploits BF16 exponent redundancy for bit-preserving KV compression, reconstructing tiles inside attention rather than decompressing the full cache. Compression is about 1.405–1.407×; Spark end-to-end decode-step gains are 1.04–1.15×.

Limitations: FP8 offers less redundancy. Positional drift can reduce compression and speed even though decoding remains lossless.

Source: [GAAC: Lossless KV Compression for Bandwidth-Efficient LLM Inference on Personal Devices](https://arxiv.org/abs/2610.38210)

## The Endgame of FSDP Communication: Layout-Aware Collectives on Copy Engines, RDMA, and NVSwitch
{: #reading-arxiv-2610.38228}

TIDE folds FSDP2 per-parameter layout placement into collectives, using copy engines, RDMA and NVSwitch to reduce copies and SM interference. On 64 GPUs, step time falls by up to 27.1% versus stock FSDP2 and 6% versus SymmMem.

Limitations: It depends on specific interconnects and NCCL APIs. Maxima from different configurations are not one operating point.

Source: [The Endgame of FSDP Communication: Layout-Aware Collectives on Copy Engines, RDMA, and NVSwitch](https://arxiv.org/abs/2610.38228)

## Detecting Incorrect LLM Explanations for Automated Program Repair
{: #reading-arxiv-2610.38311}

MetaReJ transforms programs to preserve or change bugs, then questions repair explanations and detects contradictions. On 1,756 human-labeled explanations its best MCC is 0.43, motivating evaluation of explanations separately from patches.

Limitations: Contradictions are signals, not proofs. Repeated querying costs resources; relative MCC gains do not imply high absolute accuracy.

Source: [Detecting Incorrect LLM Explanations for Automated Program Repair](https://arxiv.org/abs/2610.38311)

## A Case Study of a Multi-Agent Kernel-Optimization Loop That Learns a New AI Accelerator
{: #reading-arxiv-2610.38329}

This RNGD case builds target knowledge from documentation, microbenchmarks and compiler rules, screening legality before repeated device comparisons. A 12-day run optimizes three decode kernels to 9.293× geometric-mean speedup over official baselines.

Limitations: One chip and one run without ablations cannot attribute component gains. Synthetic inputs and fixed seeds do not validate full-model quality.

Source: [A Case Study of a Multi-Agent Kernel-Optimization Loop That Learns a New AI Accelerator](https://arxiv.org/abs/2610.38329)

## FlatCake: A Flat KVCache Storage Architecture for LLM Serving
{: #reading-arxiv-2610.38355}

FlatCake treats DRAM and SSD as peer KV media with fixed, session-contiguous placement at creation and GDS streaming into a bounded GPU window. Under high load on a Claude Code trace, cache hits remain 94% versus Mooncake’s 64%.

Limitations: It relies on immutable blocks and session reuse. Total-token throughput includes inputs and is not generation speed; storage configuration matters.

Source: [FlatCake: A Flat KVCache Storage Architecture for LLM Serving](https://arxiv.org/abs/2610.38355)

## How Deterministic SAST and AI Security Agents Divide the Work: Coverage, Harness Policy and Cost in Snyk VulnBench 2.0
{: #reading-arxiv-2610.38617}

VulnBench 2.0 requires source and sink localization rather than file mentions. Of 108 vulnerabilities, Snyk finds 89 and one Claude configuration 85; their union reaches 101. Harness exclusions and file selection materially affect coverage.

Limitations: Vendor involvement, sample and grading matter. Valid out-of-reference findings are not false positives, and product configurations are not pure model comparisons.

Source: [How Deterministic SAST and AI Security Agents Divide the Work: Coverage, Harness Policy and Cost in Snyk VulnBench 2.0](https://arxiv.org/abs/2610.38617)

## Slant: Shaping Traffic for Resource-Efficient Microservices
{: #reading-arxiv-2610.38778}

Slant maintains safe hot/cold pod imbalance to expose clearer utilization signals to existing VPA. Three microservice benchmarks report up to 26% lower allocated CPU and 18% lower P99 latency, with conservative fallback under anomalies.

Limitations: It needs service profiles and capacity estimates. Maxima may not coincide and do not justify arbitrary production routing changes.

Source: [Slant: Shaping Traffic for Resource-Efficient Microservices](https://arxiv.org/abs/2610.38778)

## When Relevant Code Is Wrong: Runtime-Aware Context for AI Coding Agents
{: #reading-arxiv-2610.38800}

CASE classifies retrieved artifacts as valid, invalid or unknown using feature flags, deployment configuration and architectural history. Its prototype filters 16 incompatible artifact occurrences across six tasks, 15 artifacts and three deployments.

Limitations: This is feasibility under illustrative application/reference rules, not demonstrated improvement in coding-agent correctness.

Source: [When Relevant Code Is Wrong: Runtime-Aware Context for AI Coding Agents](https://arxiv.org/abs/2610.38800)

## Causal Attention on CPU: A Cache-Aware and Load-Balanced Scheduling Kernel for Prefill
{: #reading-arxiv-2610.38809}

CACPU combines multilevel cache blocking with in-kernel dispatch for causal CPU prefill. Two Intel CPU platforms show up to 2.01× kernel speedup and up to 1.74× better Llama-3.1-8B TTFT after SGLang integration.

Limitations: The desktop lacks AMX and excludes that SGLang baseline; CPU prefill results do not establish replacement of full GPU serving.

Source: [Causal Attention on CPU: A Cache-Aware and Load-Balanced Scheduling Kernel for Prefill](https://arxiv.org/abs/2610.38809)

## CopyLoop: Fast Looped Transformer Decoding via Context Copying and Shallow Screening
{: #reading-arxiv-2610.38822}

CopyLoop proposes token blocks copied from repeated context, screens them at shallow recurrent depth and overlaps deeper verification. Six looped-model checkpoints show substantial decode gains, illustrating how reusable context reduces sequential drafting cost.

Limitations: It depends on context reuse and calibration. Appendix results show output trajectories, length and repetition can change TPS; speed alone does not establish quality or token equivalence.

Source: [CopyLoop: Fast Looped Transformer Decoding via Context Copying and Shallow Screening](https://arxiv.org/abs/2610.38822)

## TableTune: Measured, Self-Correcting Draft-Length Tables for Dynamic Speculative Decoding
{: #reading-arxiv-2610.38968}

TableTune measures batch-size/draft-length combinations on the actual vLLM serving path and updates tables using live acceptance rates, turning draft length from a hand-written constant into a measured, repairable control parameter.

Limitations: The peak 58% repairs mistuning. Comparisons are only against speculative configurations and do not establish universal gains over non-speculative decoding.

Source: [TableTune: Measured, Self-Correcting Draft-Length Tables for Dynamic Speculative Decoding](https://arxiv.org/abs/2610.38968)

## Why Speculative Decoding Works Better Than Predicted on Sparse MoE Models
{: #reading-arxiv-2610.38981}

This study shows that expert bytes alone mispredict fine-grained MoE verification cost: routing overlap, L2 reuse and kernel bandwidth utilization shape low-batch behavior. An IPF model predicts unique expert counts with under 4% error.

Limitations: Expert-count error is not end-to-end latency error. Some analyses isolate target verification and omit actual drafter cost and acceptance.

Source: [Why Speculative Decoding Works Better Than Predicted on Sparse MoE Models](https://arxiv.org/abs/2610.38981)

## Beyond atol and rtol: Sound Test Oracles for Low-Precision GPU Kernels
{: #reading-arxiv-2610.38983}

numoracle derives per-element acceptance regions from precision-annotated references, tracking shared rounding and block quantization rather than fixed atol/rtol. Its RTX PRO 6000 campaign detects 116 of 124 effective mutants.

Limitations: Soundness depends on rounding, hardware, domain and implementation assumptions. Zero observed alarms is not a universal guarantee, and mutants remain undetected.

Source: [Beyond atol and rtol: Sound Test Oracles for Low-Precision GPU Kernels](https://arxiv.org/abs/2610.38983)

## PDScope: Breaking the Prefill-Decode Seesaw for Memory-Bound MoE Inference
{: #reading-arxiv-2610.39216}

PDScope separately optimizes aggressive prefill loading and conservative decode transfers for memory-limited MoE, using expert prediction, cross-layer cost modeling and static-graph pipelines. It reports separate prefill and decode throughput gains.

Limitations: Phase speedups cannot be multiplied. Model, PCIe, CPU and cache capacity determine results; request-level acceleration may differ.

Source: [PDScope: Breaking the Prefill-Decode Seesaw for Memory-Bound MoE Inference](https://arxiv.org/abs/2610.39216)

## AgentHeal: Evaluating Goal-Preserving Resource Recovery of Web Agents under Access Barriers
{: #reading-arxiv-2610.39234}

AgentHeal tests whether agents find legitimate alternatives without weakening the goal after dead links, authentication walls or rate limits. Across nine snapshot-based barrier families, average success falls from 89.4% to 43.7%, exposing look-alikes, futile retries and policy violations.

Limitations: Snapshots/replay omit live-web dynamics. Scoring includes an LLM judge, and deterministic checks cover predefined provenance and action rules.

Source: [AgentHeal: Evaluating Goal-Preserving Resource Recovery of Web Agents under Access Barriers](https://arxiv.org/abs/2610.39234)

## Soei: Structured Observability of Evidence and Intent for Multi-Agent AI Software Engineering
{: #reading-arxiv-2610.39468}

Soei studies 45 coding-agent sessions with an audited classifier, estimating that 23.4% of editing episodes lack independent checks after the final edit and 57.8% of completed todos lack intervening proof. It proposes an event ledger separating acknowledgment, attribution and completion evidence.

Limitations: Classifier errors remain, and missing observed checks do not prove a bad repair. Hash chaining detects tampering, not truth of event content.

Source: [Soei: Structured Observability of Evidence and Intent for Multi-Agent AI Software Engineering](https://arxiv.org/abs/2610.39468)

## Raincheck: Deferred Multimodal Prefill for Efficient Multi-Turn MLLM Inference
{: #reading-arxiv-2610.39562}

Raincheck initially retains selected multimodal tokens, then prefills omitted tokens during decode and scheduling gaps so later questions can access more original information. Across two models it recovers a substantial share of hard-pruning quality loss.

Limitations: Systems measurements use one running request and do not reduce modality encoding. Recovered-loss percentages are not absolute improvements over full-input quality.

Source: [Raincheck: Deferred Multimodal Prefill for Efficient Multi-Turn MLLM Inference](https://arxiv.org/abs/2610.39562)

## The Real Cost of Context: Predicting Compute Time and Energy Consumption in LLM Prefill and Decode Phases
{: #reading-arxiv-2610.39621}

This study fits time and energy by input/output length, finding linear and quadratic prefill terms that output-only accounting misses. Proprietary-API energy is inferred using the energy model paired with the closest local timing fit.

Limitations: Local measurements cover few H100/H200 configurations at batch one with no exact API match. Similar response time does not uniquely identify hardware power.

Source: [The Real Cost of Context: Predicting Compute Time and Energy Consumption in LLM Prefill and Decode Phases](https://arxiv.org/abs/2610.39621)

## InferD: A Honeypot Framework for AI Inference Infrastructure
{: #reading-arxiv-2610.39807}

InferD uses static pools to emulate model inventories, APIs, tool protocols and authorization while never executing attacker-supplied inference or tools. It separates observation of inference-infrastructure threats from the execution risk of realistic emulation.

Limitations: Reasoning probes, repeated responses and timing can expose the facade; the design does not establish production detection effectiveness.

Source: [InferD: A Honeypot Framework for AI Inference Infrastructure](https://arxiv.org/abs/2610.39807)

## KV Cache Quantization for Diffusion Language Models
{: #reading-arxiv-2610.39853}

dLLM-KVQ observes that bidirectional diffusion states change as tokens are revealed, so cache reuse already introduces error before quantization. TRACE builds reveal-matched calibration trajectories and preserves sensitive key entries at higher precision.

Limitations: Both reuse and quantization can be lossy. Evidence concerns specified LLaDA/Dream protocols, not autoregressive exact-cache assumptions.

Source: [KV Cache Quantization for Diffusion Language Models](https://arxiv.org/abs/2610.39853)

## PhOSv1: Efficient Scaling of Model Sleeping on a Single Server for Autoscaling with GPU-Context Deduplication
{: #reading-arxiv-2610.39999}

PhOSv1 shares duplicated CUDA contexts and kernel binaries across sleeping models through a central daemon and API remoting, reducing resident engine overhead while preserving fast wake-up.

Limitations: Reported measurements use one GPU despite an eight-GPU server; isolation and multi-tenant implications of context sharing need separate evaluation.

Source: [PhOSv1: Efficient Scaling of Model Sleeping on a Single Server for Autoscaling with GPU-Context Deduplication](https://arxiv.org/abs/2610.39999)

## Only Accepted Tokens Count: An Energy Accounting of Speculative Decoding Under Latency Targets
{: #reading-arxiv-2610.40287}

This study accounts for speculation energy per accepted output token. Larger batches already amortize weight reads and can make verification compute-bound; with low acceptance, meeting tighter latency targets can increase energy per token.

Limitations: Results depend on model, corpus, batch and measurement scope; GPU energy is not whole-datacenter energy.

Source: [Only Accepted Tokens Count: An Energy Accounting of Speculative Decoding Under Latency Targets](https://arxiv.org/abs/2610.40287)

## DolphinRouting: Cluster-Level Binary Routing for Disaggregated LLM Inference Serving
{: #reading-arxiv-2610.40292}

DolphinRouting clusters requests by raw and cache-adjusted lengths on both worker pools plus output-length information, learning local/remote prefill choices offline and using feature extraction and lookup online.

Limitations: It assumes a given P/D allocation and available features; obtaining output-length information and handling drift affect deployment.

Source: [DolphinRouting: Cluster-Level Binary Routing for Disaggregated LLM Inference Serving](https://arxiv.org/abs/2610.40292)

## Rimuru: Unified Memory Management for Modern LLM Serving via Elastic Expert Offloading
{: #reading-arxiv-2610.40305}

Rimuru shares pages between expert weights and attention states using tensor-specific views, split/merge allocation and MoE kernels that directly access noncontiguous weights, dynamically adjusting memory boundaries.

Limitations: Large ratios arise under specific memory-constrained baselines, not universally; transfer costs and concurrency determine elastic-offload benefits.

Source: [Rimuru: Unified Memory Management for Modern LLM Serving via Elastic Expert Offloading](https://arxiv.org/abs/2610.40305)

## Can We Rely on Language Models to Orchestrate Services across the Edge-Cloud Continuum?
{: #reading-arxiv-2610.40477}

This systematic review of 39 studies connects system constraints, orchestration decisions, LM responsibility, authority and evidence. Most designs use LMs for proposals while downstream components constrain and execute them; successful actuation still differs from verified recovery.

Limitations: Synthesis depends on search scope and source quality; it is not a new production experiment or proof of generally reliable closed-loop orchestration.

Source: [Can We Rely on Language Models to Orchestrate Services across the Edge-Cloud Continuum?](https://arxiv.org/abs/2610.40477)

## DistOptimize: Automatic Optimization of Distributed Protocols
{: #reading-arxiv-2610.39017}

DistOptimize verifies distributed-protocol rewrite rules in Rocq, then uses calibration and ILP search to optimize throughput. AWS experiments report up to 4× throughput with at most 0.3ms added latency, linking optimization to safety constraints.

Limitations: Guarantees concern the formal model and rewrite preconditions, not arbitrary implementation errors; throughput must be compared with machine costs.

Source: [DistOptimize: Automatic Optimization of Distributed Protocols](https://arxiv.org/abs/2610.39017)

## ForgeKernel: Self-Evolving Kernels Catching and Surpassing Experts and Agents
{: #reading-openbmb-forgekernel}

ForgeKernel’s repository describes architecture-first milestones, promotion of accepted kernels to the next reference and shared hardware-probe knowledge. This is a different workflow from the goal-only JustGoal baseline.

Limitations: The README links JustGoal, whose results do not validate the repository’s separate 27-operator claims. Kernels and leaderboard results were not reproduced here.

Source: [ForgeKernel: Self-Evolving Kernels Catching and Surpassing Experts and Agents](https://github.com/OpenBMB/ForgeKernel)

## Radar: open-source Kubernetes UI with built-in MCP server for AI agents
{: #reading-skyhook-radar-k8s-ai-sre-mcp}

Radar exposes shared cluster relationships, events and health to its UI and MCP with a read-only endpoint. In its author-run same-agent 50-fault comparison, mean diagnosis time is 64 seconds versus 191 with raw kubectl.

Limitations: Product authors run the study with an LLM judge. Faults, dates and load differ between studies; cross-table rankings and real-repair claims are unwarranted.

Source: [Radar: open-source Kubernetes UI with built-in MCP server for AI agents](https://github.com/skyhook-io/radar)

## Build a Validated Kubernetes Runtime for NVIDIA Dynamo
{: #reading-nvidia-dynamo-validated-kubernetes-runtime}

AICR validates Dynamo’s drivers, DRA, scheduling, network and monitoring through version-pinned recipes before application deployment. The article favors worker KV events because request-history prediction cannot observe cache eviction.

Limitations: Recipes cover specified platform combinations. Offline checks skip behavior; generating a bundle does not establish runtime correctness.

Source: [Build a Validated Kubernetes Runtime for NVIDIA Dynamo](https://developer.nvidia.com/blog/build-a-validated-kubernetes-runtime-for-nvidia-dynamo/)

## vLLM Day-0 RL：Mistral Large 4 + SkyRL（8×GB200 LoRA RL）
{: #reading-x-vllm-2115985388649242699}

The official vLLM post reports Mistral Large 4 LoRA RL on eight GB200 nodes using NVFP4 QAT, FP8-KV simulation and routing replay, raising AIME 2024 avg@8 from about 64% to 75% after 75 steps.

Limitations: This is eight nodes, not eight GPUs. A social report on one evaluation set does not establish broad generalization or exact train–inference consistency.

Source: [vLLM Day-0 RL：Mistral Large 4 + SkyRL（8×GB200 LoRA RL）](https://x.com/vllm_project/status/2115985388649242699)
