---
date: '2026-11-26'
published: true
layout: article
maintenance: daily-research
translation_source: assistant
id: pytorch-vllm-singapore-meetup-2026-11-25
title: 2026-11-26 | Why pipeline parallelism can help vLLM prefill long agent prompts
lang: en
source_type: tech
long_read: true
source_url: https://pytorch.org/blog/vllm-singapore-meetup-faster-prefill-agent-written-kernels-and-the-road-to-vera-rubin/
tags:
- inference-serving
permalink: /tech/en/pytorch-vllm-singapore-meetup-2026-11-25/
summary: Prefill layout on GB300, dispatch on SM12x and video-session cache lifetime
  explain three vLLM performance results.
published_at: '2026-11-26T08:45:51.058767+08:00'
updated_at: '2026-11-26T08:45:51.058767+08:00'
---
An agent request carrying about 100,000 input tokens still has roughly 5,000 new tokens to process even with a 95% prefix hit. Reports at the November 13 Singapore vLLM meetup examine what happens when those fresh tokens must fit a first-token deadline. Model partitioning, queued microbatch sizes and the hardware carrying activations all change the result.

## Fewer collectives introduce pipeline bubbles

Thien Tran compared two-stage pipeline parallelism with TEP2 plus sequence parallelism for MiniMax-M3.1-Flash on two GB300s. Placing stages on separate devices removes collectives that compete with compute, delivering up to 1.37 times the maximum throughput of the comparison layout. But each microbatch still traverses both stages, leaving one idle during fill and drain. Equal layer counts do not guarantee balanced stage times.

The team balanced stages by measured duration and capped the work per step to shorten fill and drain. Moving activation transfers to copy engines lowered median time to first token by 13%–20% near saturation. With fixed step sizes the comparison layout still won at a tight 0.75-second target. A scheduler that sizes microbatches from the queue put PP2 ahead from roughly a 0.5-second target in the reported tests. A throughput comparison therefore needs its first-token constraint alongside its hardware.

## A fast kernel must actually receive the workload

Jie Fang discussed SM12x workstation hardware connected by PCIe Gen5 without NVLink. On the DeepSeek path, a one-line dispatch correction routed work to the intended implementation and lifted throughput 17.7%. A separate change preferring W4A4 for NVFP4 linear layers yielded 23.8%. The percentages belong to separate changes. TP2 × PP2 instead of TP4 gave 1.37 times the prefill throughput on this platform. That ratio happens to match the GB300 case, though the hardware, layouts and baselines all differ.

Backend support alone says little about deployment performance. Which implementation actually receives the operation, where activations cross a link and how closely accesses approach measured memory bandwidth determine whether a new kernel changes user-visible latency.

## Interactive video keeps a cache beyond one request

The vLLM-Omni report approaches engine selection through state lifetime. An ordinary diffusion request can release its state on completion. An interactive world model needs history from earlier video chunks. Its AR-Diffusion engine reuses the paged KV manager, generates one chunk at a time and keeps the required state throughout the session. On LingBot-World 2.0 with a single session across four H200s, Ulysses sequence parallelism reduced one block from 2,397 to 725 milliseconds.

For 12-frame chunks, the main implementation was reported to be 1.9 times as fast as the September version while preserving quality. Enabling all optional optimizations yielded 22.5 fps and a 2.75-fold speedup. The quality statement belongs to the first configuration. The latter measures single-session interactivity and leaves multi-user capacity open. Across the talks, the figures become interpretable once the reader knows when work becomes ready, how long its state must survive and whether the measurement covers a kernel, a request or a session.


Ebba Simpson · 2026-11-25 · [vLLM Singapore Meetup: Faster Prefill, Agent-Written Kernels and the Road to Vera Rubin](https://pytorch.org/blog/vllm-singapore-meetup-faster-prefill-agent-written-kernels-and-the-road-to-vera-rubin/)
