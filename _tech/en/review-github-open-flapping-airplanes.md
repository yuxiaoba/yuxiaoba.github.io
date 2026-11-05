---
id: review-github-open-flapping-airplanes
title: '2026-11-04 | open-flapping-airplanes: reproducing the flapping airplanes megakernel'
date: '2026-11-04'
lang: en
published: true
layout: article
maintenance: daily-research
source_type: tech
source_url: https://github.com/Bobliuuu/open-flapping-airplanes
tags:
- agent-reliability
- self-improvement
- observability
- inference-serving
- systems-reliability
translation_source: assistant-created bilingual notes
permalink: /tech/en/review-github-open-flapping-airplanes/
---

open-flapping-airplanes independently reconstructs a persistent GPU kernel from a demo, co-running training, serving and Doom. B200 training of a 162.4M model takes 48.1 seconds, beating eager baselines but trailing CUDA-Graph Megatron’s 43.1 seconds.

It is not reproduction from original source or production-scale LLM validation. Workloads receive fixed SM shares; concurrency is not free shared capacity.

[open-flapping-airplanes: reproducing the flapping airplanes megakernel](https://github.com/Bobliuuu/open-flapping-airplanes)
