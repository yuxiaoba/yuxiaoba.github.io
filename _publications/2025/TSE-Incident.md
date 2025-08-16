---
title:          ""Subgraphs as First-Class Citizens in Incident Management for Large-Scale Online Systems An Evolution-AwareFramework"
date:           2025-07-29 00:00:00 +0800
selected:       true
pub:            >-
                In IEEE Transactions Software Engineering 
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">TSE (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  With the ever-increasing scale and complexity of modern online systems, incidents are becoming inevitable, which seriously decreases the system availability and user satisfaction. To enhance incident management, many machine learning based techniques are proposed to automate incident detection and diagnosis. However, previous studies have mostly ignored the impact of evolution on the practicality of an incident management framework. Specifically, (1) The scale of modern online systems is continually evolving, but most state-of-the-art techniques are overly dependent on a continuous modelling of the entire system, and thus are less practical for online systems evolved to tens of thousands of services; (2) The volume of telemetry data is massively growing, while the number of incident records for learning is scarce and slowly generated (sometimes from zero), but prior techniques usually neglect this extreme imbalance in data volume evolution, and cannot support the life-cycle evolution (i.e., cold start and continual learning) of their developed models; (3) Prior techniques usually require operators to manually select a set of telemetry as inputs for incident diagnosis, but ignore how to automatically evolve this selection to continually improve diagnosis performance. These gaps stem from the unawareness of evolution, including the evolution of the target online system and the evolution of the built incident management models. To fill these gaps, we propose an evolution-aware incident management framework GEM. Specifically, considering the evolution of system scale and data volume, GEM continually refines the enormous real-time collected telemetry data into individual compact yet expressive graph-based representations, namely issue impact subgraphs, and treat them as the first-class citizens in incident management. Centered around these subgraphs, we design a couple of lifelong learning based graph analysis techniques to learn and evolve models for incident detection and diagnosis.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zilong He
  - Pengfei Chen†
  - Yu Luo
  - Qiuyu Yan
  - Hongyang Chen
  - Guangba Yu
  - Fangyuan Lo
  - Xiaoyun Li
  - Zibin Zheng
  
links:
  Paper: https://yuxiaoba.github.io/files/TSE/GEM.pdf
  DOI: https://doi.org/10.1109/TSE.2025.3590221
  BibTex: https://yuxiaoba.github.io/files/TSE/GEM-bibtex.txt
  # Arxiv:
---
