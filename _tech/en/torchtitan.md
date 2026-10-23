---
id: torchtitan
title: '2026-10-23 | TorchTitan: Shared Model Code Needs Shared Numerical Evidence'
date: '2026-10-23'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
tags:
- systems-reliability
- self-improvement
- inference-serving
summary: TitanRL connects training and generation to one model definition, while performance
  changes span communication, sharding, memory, and checkpointing.
long_read: true
source_url: https://pytorch.org/blog/torchtitan-update-new-sota-models-performance-at-scale-titanrl/
permalink: /tech/en/torchtitan/
translation_source: assistant
authorship: assistant
published_at: '2026-10-23T08:58:47.180720+08:00'
updated_at: '2026-10-23T08:58:47.180720+08:00'
---
Supporting more models is only part of a training framework's challenge. The harder task is taking them through pretraining, reinforcement learning, and generation without maintaining diverging implementations. This TorchTitan update organizes model definitions, parallel configurations, hardware kernels, and numerical checks into a composable stack. TitanRL makes agreement between training and generation an infrastructure concern.

Original: [TorchTitan Update: New SOTA Models, Performance at Scale, TitanRL](https://pytorch.org/blog/torchtitan-update-new-sota-models-performance-at-scale-titanrl/) · The PyTorch Team at Meta · 2026-10-21; the page also shows an update on 2026-10-22

## One definition across training and generation

New architecture coverage includes Muse Spark Open, Muse Glimmer, Qwen3-VL, Qwen3.5, Kimi K2.7, Kimi K3, and DeepSeek-V4, with full-stack integration and 5D parallelism. Typed Python recipes, model-configuration transforms, and component overrides allow parallel strategies and specialized kernels without separate model forks.

TitanRL extends shared implementation through pretraining, post-training, and generation inside vLLM. Separate trainer and inference implementations can diverge subtly after architecture changes. When rewards change, it becomes difficult to distinguish algorithmic effects from reward design or implementation mismatch. Sharing a definition reduces one maintenance problem while leaving execution paths to be checked.

<a class="note-image-link" href="/assets/images/tech/torchtitan/overview.png" target="_blank" rel="noopener" aria-label="One model definition for pretraining, reinforcement learning, and generation · View original image ↗"><img src="/assets/images/tech/torchtitan/overview.png" alt="One model definition for pretraining, reinforcement learning, and generation" loading="lazy"><span class="note-image-action">View original image ↗</span></a>

*Reading the diagram: one model definition feeds pretraining, TitanRL training, and vLLM generation. Execution can adapt to each workload while model code remains shared.*

Rollouts run asynchronously, and training and generation can scale with different forms of parallelism. Examples use Qwen3.5-35B-A3B base: SWE-Rebench easy with 64K context on 40 GB300 GPUs, and terminal-task training with 128K context on 20 GB300 GPUs. These demonstrate particular long-context and tool-related workloads, not validation of every agent environment.

## Numerical agreement has a defined scope

Batch-invariant mode is a notable correctness feature. In supported on-policy configurations, trainer and generator log probabilities are bitwise identical, with zero difference. Removing that source of batching-related noise can make algorithm comparisons easier to interpret.

The qualifications matter. This concerns a specific quantity under supported configurations; it does not guarantee identical training trajectories across every kernel, precision, parallel combination, or asynchronous strategy. Model definition, execution configuration, and numerical checks should be recorded together. Shared code should not become a reason to skip verification.

GraphTrainer supplies an explicit training graph, with the official article reporting bitwise-matching results between graph and eager paths. It offers another way to express cross-module fusion, graph-level debugging, and heterogeneous-hardware optimization rather than forcing a single execution mode.

## Performance comes from several layers

The update includes local_compile for selective compilation, torch_remat for fine-grained recomputation, Dist-MoE for fused communication and computation, and revised pipeline parallelism. They affect CPU overhead, activation memory, expert communication, and overlap. Faster GEMMs alone may not offset MoE token-dispatch waits, so these layers require coordinated configuration.

On an internal GB300 cluster, the team evaluates DeepSeek V3 671B plus MTP1 with MXFP8 on the MLPerf training workload. PP2 configurations deliver 5,324.21 tokens/s/GPU at 256 GPUs and 5,262.68 at 512 GPUs, with global throughput rising from 1,362,998 to 2,694,493 tokens/s. DP and local-batch settings also change between rows. These are scaling results for the listed configurations, not an unconditional linear-scaling guarantee.

The Muse Spark Open table separates learned routing from forced-balanced routing. At 96K context on 256 GPUs, throughput is 1,500.61 versus 1,839.52 tokens/s/GPU. The gap highlights load balance, but forced balancing changes workload characteristics; its larger number should not stand in for learned-routing performance.

## FlexShard makes placement configurable

FSDP2's usual row or column sharding can be awkward for distributed Muon or blockwise quantization. FlexShard's bucket interface supports placements including Owned and BlockShard: one rank can own a complete parameter, or sharding can align with two-dimensional tiles. These can avoid pre-update gathering or extra communication for quantization scales.

For DeepSeekV3 on 256 H100 GPUs, the article reports up to 79% improvement in optimizer-stage duration. For Llama3 405B on 256 H100 GPUs with blockwise-quantized all-gather, it reports up to 20% improvement in end-to-end training-step time. These are different metrics and workloads. Optimizer-stage savings are not whole-step savings, and the roughly 50% communication-volume reduction depends on the FP8/BF16 comparison.

## Checkpointing determines the cost of resilience

The new torch_checkpointing library reduces save-time synchronization and changes serialization and pluggable storage behavior. On 512 H100 GPUs running DSv3 671B with checkpoint interval 50, average trainer blocking falls from 841.2 ms to 34.1 ms, average checkpoint writing from 384.4 s to 13.1 s, and non-resharding loading from 194.7 s to 79 s.

Separating trainer blocking from complete write duration is useful. Shorter blocking can permit more frequent saves, while backend throughput, concurrent writes, and restore-time resharding still affect outcomes. The published loading numbers are explicitly non-resharding and do not establish performance for every elastic-recovery configuration.

## Restore the measurement hierarchy before comparing

The update mixes operator, training-step, throughput, and checkpoint measurements. A common misreading is to transfer the best result at one level to another. Large optimizer-stage savings can represent a modest fraction of total training, while short save blocking does not mean persistence has finished. Stage-level timing makes the benefiting configurations easier to identify.

Numerics, performance, and recovery also constrain one another. Aggressive kernels or quantization can increase throughput without preserving the loss curve. More frequent checkpoints reduce lost progress after failure but increase storage pressure. Separate module improvements do not determine an arbitrary cluster's optimal save interval or minimum training cost.

Shared model definitions still need execution context. Pretraining parallelism may not suit small-batch rollouts, and replacing a kernel on one path does not establish the same replacement on another. Recipes and component overrides make these differences explicit instead of burying them in model copies. Retaining configurations and numerical checks keeps performance comparisons interpretable.

A practical reading order is to select the model and workload, establish the required parallel and kernel combination, and locate comparable table conditions. Where conditions differ, official results support mechanism feasibility rather than a peak gain that can be inserted directly into a budget.

**Read this update through consistency, communication, and recovery.** Establish shared-model and batch-invariant scope, inspect the model's parallel recipe, and then compare throughput and checkpoint costs under matched hardware, precision, batch, and storage conditions. The progress is a composable infrastructure stack rather than a universal acceleration factor.
