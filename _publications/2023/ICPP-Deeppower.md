---
title:          "DeepPower: Deep Reinforcement Learning based Power Management for Latency Critical Applications in Multi-core Systems"
date:           2023-06-16 00:00:00 +0800
selected:       false
pub:            >-
                In 32nd International Conference on Parallel Processing
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICPP'23 (CCF B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Latency-critical (LC) applications are widely deployed in modern datacenters. Effective power management for LC applications can yield significant cost savings. However, it poses a significant challenge in maintaining the desired Service Level Aggrement (SLA) levels. Prior researches have mainly emphasized predicting the service time of request and utilize heuristic algorithms for CPU frequency adjustment. Unfortunately, the control granularity is limited to the request level and manual feature selection is needed. This paper proposes DeepPower, a deep reinforcement learning (DRL) based power management solution for LC applications. DeepPower comprises two key components, a DRL agent for monitoring the system load changes and a thread controller for CPU frequency adjustment. Considering the high overhead of the neural network and the short service time of requests, it is infeasible to employ DRL for direct adjustment of CPU frequency at the request level. Instead, DeepPower proposes a hierarchical control mechanism. That means the DRL agent adjusts the parameter of thread controller with longer intervals, and thread controller adjusts the CPU frequency with shorter intervals.  This control mechanism enables DeepPower to adapt to dynamic workloads and achieves fine-grained frequency adjustments. We evaluate DeepPower with some common LC applications under dynamic workload. The experimental results show that DeepPower saves up to 28.4\% power compared with state-of-the-art methods and reduces the percentage of request timeout.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Jingrun Zhang
  - Guangba Yu
  - Zilong He
  - Liang Ai
  - Pengfei Chen
  
links:
  Paper: https://yuxiaoba.github.io/files/ICPP23/deeppower.pdf
  DOI: https://doi.org/10.1145/3605573. 3605612
  BibTex: https://yuxiaoba.github.io/files/ICPP23/deeppower-bibtex.txt
  # Arxiv:
---
