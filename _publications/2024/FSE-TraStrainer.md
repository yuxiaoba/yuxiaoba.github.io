---
title:          "TraStrainer: Adaptive Sampling for Distributed Traces with System Runtime State"
date:           2023-07-28 00:00:00 +0800
selected:       true
pub:            >-
                In 32nd ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">FSE'24 (CCF A)</span>
pub_last:       '🏆 <span style="color:red"><b>Distinguish Paper Award</b></span>'
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Distributed tracing has been widely adopted in many microservice systems and plays an important role in monitoring and analyzing the system. However, trace data often come in large volumes, incurring substantial computational and storage costs. To reduce the quantity of traces, trace sampling has become a prominent topic of discussion, and several methods have been proposed in prior work. To attain higher-quality sampling outcomes, biased sampling has gained more attention compared to random sampling. Previous biased sampling methods primarily considered the importance of traces based on diversity, aiming to sample more edge-case traces and fewer common-case traces. However, we contend that relying solely on trace diversity for sampling is insufficient, system runtime state is another crucial factor that needs to be considered, especially in cases of system failures. In this study, we introduce TraStrainer, an online sampler that takes into account both system runtime state and trace diversity. TraStrainer employs an interpretable and automated encoding method to represent traces as vectors. Simultaneously, it adaptively determines sampling preferences by analyzing system runtime metrics. When sampling, it combines the results of system-bias and diversity-bias through a dynamic voting mechanism. Experimental results demonstrate that TraStrainer can achieve higher quality sampling results and significantly improve the performance of downstream root cause analysis (RCA) tasks. It has led to an average increase of 32.63\% in Top-1 RCA accuracy compared to four baselines in two datasets.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Haiyu Huang
  - Xiaoyu Zhang
  - Pengfei Chen
  - Zilong He
  - Zhiming Chen
  - Guangba Yu
  - Hongyang Chen
  - Chen Sun
links:
  Paper: https://yuxiaoba.github.io/files/FSE24/trastrainer.pdf
  Project: https://github.com/IntelligentDDS/TraStrainer
  DOI: https://doi.org/10.1145/3643748
  BibTex: https://yuxiaoba.github.io/files/FSE24/trastrainer-bibtex.txt
  # Arxiv:
---
