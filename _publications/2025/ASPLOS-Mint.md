---
title:          "Mint: Cost-Efficient Tracing with All Requests Collection via Commonality and Variability Analysiss"
date:           2025-01-02 00:00:00 +0800
selected:       true
pub:            >-
                In 30th ACM International Conference on Architectural Support for Programming Languages and Operating Systems.
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ASPLOS'25 (CCF A)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Distributed traces contain valuable information but are often massive in volume, posing a core challenge in tracing framework design: balancing the tradeoff between preserving essential trace information and reducing trace volume. To address this tradeoff, previous approaches typically used a '1 or 0' sampling strategy: retaining sampled traces while completely discarding unsampled ones. However, based on an empirical study on real-world production traces, we discover that the '1 or 0' strategy actually fails to effectively balance this tradeoff. To achieve a more balanced outcome, we shift the strategy from the '1 or 0' paradigm to the 'commonality + variability' paradigm. The core of 'commonality + variability' paradigm is to first parse traces into common patterns and variable parameters, then aggregate the patterns and filter the parameters. We propose a cost-efficient tracing framework, Mint, which implements the 'commonality + variability' paradigm on the agent side to enable all requests capturing. Our experiments show that Mint can capture all traces and retain more trace information while optimizing trace storage (reduced to an average of 2.7%) and network overhead (reduced to an average of 4.2%). Moreover, experiments also demonstrate that Mint is lightweight enough for production use.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Haiyu Huang
  - Cheng Chen
  - Kunyi Chen
  - Pengfei Chen†
  - Guangba Yu
  - Zilong He
  - Yilun Wang
  - Huxing Zhang
  - Qi Zhou

links:
  Paper: https://yuxiaoba.github.io/files/ASPLOS25/Mint.pdf
  DOI: https://doi.org/10.1145/3669940.3707287
  BibTex: https://yuxiaoba.github.io/files/ASPLOS25/mint-bibtex.txt
  Arxiv: https://arxiv.org/pdf/2411.04605
---