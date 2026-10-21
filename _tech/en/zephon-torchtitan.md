---
id: "zephon-torchtitan"
title: "2026-10-16 | Zephon: Preserving Training Batches When GPU Counts Change"
date: "2026-10-16"
lang: "en"
published: true
layout: "article"
maintenance: "daily-research"
source_type: "tech"
tags: ["systems-reliability"]
summary: "How accumulators, logical lanes, and flush/replay make online data loading elastically deterministic, without promising bitwise identical training arithmetic."
authoring_source: "assistant"
translation_source: "assistant-authored paired Chinese/English editorial notes"
long_read: true
source_url: "https://pytorch.org/blog/bringing-elastically-deterministic-data-loading-to-torchtitan-with-zephon/"
permalink: "/tech/en/zephon-torchtitan/"
---

**Josh Wills, Maximilian Böther, Ties Robroek and the Zephon team · Official PyTorch technical article**  
Original: [Bringing Elastically Deterministic Data Loading to TorchTitan with Zephon](https://pytorch.org/blog/bringing-elastically-deterministic-data-loading-to-torchtitan-with-zephon/)

## A new data recipe can accidentally mean a new data order

Mixtures, filters, tokenization, and packing directly influence training. Offline preparation requires scanning a corpus and producing another copy before an experiment starts; unsuccessful recipes still incur storage costs. Moving preparation into training can use node CPUs and avoid disposable copies, but introduces a reproducibility problem: processing is stateful, and GPU counts may change through scheduling or fault recovery.

Many loaders partition samples by physical rank. Changing the rank count can change which samples enter tokenization, packing, and mixing together, altering global training batches. A data-recipe ablation may then also compare a different training sequence. Zephon aims to preserve global batches during online stateful processing so physical parallelism primarily changes processing speed.

## Separate the recipe from execution

The example uses Dataset, WorkSource, and Pipeline. Dataset describes raw data; WorkSource chooses mixing and order; Pipeline converts samples into training tensors through tokenization, packing, shuffling, and batching. Separating curriculum planning from processing means changing a recipe need not rewrite operators, making experimental changes easier to identify.

The example's 0.5/0.5 mixture is a token ratio, not a sample ratio. Unequal document lengths mean equal sample counts do not yield equal training tokens. TokenEstimation samples token-to-byte ratios and adjusts planning toward the target mixture. It is an estimator, not a guarantee of exactly half the tokens in every short window.

Each operator can use its own parallelism, assigning more workers to expensive tokenization rather than imposing one configuration on the whole chain. To keep tuning from changing outputs, Zephon separates order-sensitive decisions from expensive computation.

## Accumulators decide; workers compute

Each operator has a single-threaded accumulator that sees records in order and makes stateful decisions such as packing. A stateless function distributes expensive work among workers. Work groups are numbered before dispatch; completion can be out of order, but results are reordered before reaching the next operator. More tokenization workers therefore need not change the document order seen by packing.

This does not make dependent processing arbitrarily parallel. Ordered decisions remain, with parallelizable heavy work around them. Benefits depend on the relative cost of these parts and on reordering, buffering, and process communication. The article's full vision-language pipeline includes image decoding, tokenization, packing, and batching. The authors report keeping pace with Google Grain, the fastest loader they tested, while offering stronger elastic determinism, not universal superiority on every workload.

The comparison with existing loaders centers on state constraints. The article says Mosaic Streaming and Google Grain preserve batches across GPU counts when sample order is indexable ahead of time, excluding online packing in that setting. Megatron-Energon's corresponding capability requires the total loader-worker count across GPUs to remain fixed. Zephon keeps ordered decisions within logical streams so worker counts can change independently. This comparison concerns the modes described by the source, not an assertion that those systems lack other determinism capabilities.

## Logical lanes carry the state

Zephon next partitions data into a fixed number of logical lanes rather than binding it directly to GPUs. Each lane owns an ordered sample stream and packing or shuffling state. When physical data-parallel ranks change, lanes are reassigned while logical streams remain intact, preserving global batches. Accumulators provide within-lane determinism; lanes extend it across resource changes.

The trade-off is choosing lane count in advance. It should be a common multiple of planned data-parallel sizes: 32 lanes can cover 8, 16, and 32 GPUs, but not arbitrary counts. TorchTitan integration also checks that lanes divide evenly among replicas and that each global optimizer-step batch divides evenly among lanes. Failing at launch makes misconfiguration easier to diagnose than silently changing data hours later.

More lanes are not always better. More lanes per GPU increase work rebuilt at restoration. Reserving an excessive logical scale for hypothetical expansion adds recovery overhead, so the choice should reflect actual resource configurations.

## Small checkpoints exchange serialization for replay

Online packing and shuffle buffers can be large. Serializing all of them increases checkpoint cost. Zephon periodically passes a flush sentinel through the pipeline, making stateful operators emit retained content and reset. A checkpoint records only input chunks still in progress. Restoration replays from the latest flush to rebuild state, then discards outputs the training loop already consumed.

The authors report checkpoints of a few MiB, achieved by trading recomputation for smaller storage. This is not zero-time recovery and does not establish that flushing is free for packing or throughput. Actual recovery needs evaluation under the target recipe, lane count, and data-access costs. Zephon state is checkpointed alongside the TorchTitan model and retains progress for every lane.

## Data identity differs from arithmetic identity

The authors train a 1B model in TorchTitan on sixteen GPUs, checkpoint at step 150, and resume on eight, thirty-two, and sixty-four GPUs alongside the original run. Standard-loader loss curves diverge. Zephon's curves overlap, and every global batch's SHA-256 matches the baseline. Batch hashes verify input content, not bitwise identity of the entire training process.

Another experiment trains from scratch for 20B tokens on 8, 16, 32, and 64 GPUs. With the standard loader, DCLM Core v1 scores vary by up to 0.82 points and FineWeb evaluation scores by 0.64 points; Zephon reduces the spreads to 0.05 and 0.011 points. The article describes the former spreads as roughly four times the relevant data-curation thresholds. Resource counts can therefore confound small apparent recipe improvements, within the particular model and conditions tested.

The source figures use official interactive embeds. No suitable, verified static original was obtained for this batch, so reconstructed curves are not substituted. The original article provides recovery-loss, downstream-evaluation, and throughput views.

## What must remain fixed

Elastic restoration keeps data, tokenizer, seed, mixture recipe, context length, and global batch size fixed. Processing parallelism and similar performance settings can change. GPU counts can still alter floating-point reduction order, so identical input does not imply bitwise identical weights or losses. For automated experimentation, this removes one confound before investigating numerical noise and model quality.

The article also reports that the Python 3.14t thread runner samples vision-language data about 3.7× faster than the process runner on standard Python. This is not a 3.7× training speedup. A configurable dynamic-curriculum component remains in development. **Read the combination of lanes, flush/replay, and TorchTitan configuration checks first.** It connects resource elasticity to data reproducibility, while the economics of online preparation still depend on CPU work, I/O, recovery replay, and GPU stalls.
