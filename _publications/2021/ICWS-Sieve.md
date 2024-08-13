---
title:          "Sieve: Attention-based Sampling of End-to-End Trace Data in Distributed Microservice Systems"
date:           2021-11-15 00:00:00 +0800
selected:       false
pub:            >-
                In Proceeidings of 2021 IEEE International Conference on Web Services
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICWS'21 (CCF B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  End-to-end tracing plays an important role in understanding and monitoring distributed microservice systems. The trace data are valuable to help find out the anomalous or erroneous behavior of the system. However, the volume of trace data is huge leading to a heavy burden on analyzing and storing them. To reduce the volume of trace data, the sampling technique is widely adopted. However, existing uniform sampling approaches are unable to capture uncommon traces that are more interesting and informative. To tackle this problem, we design and implement Sieve, an online sampler that aims to bias sampling towards uncommon traces by taking advantage of the attention mechanism. The evaluation results on the trace datasets collected from real-world and experimental microservice systems show that Sieve is effective to increase sampling probabilities of the structurally and temporally uncommon traces and reduce the storage space to a large extent by taking a low sampling rate.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zicheng Huang
  - Pengfei Chen†
  - Guangba Yu
  - Hongyang Chen
  - Zibin Zheng
  
links:
  Paper: https://yuxiaoba.github.io/files/ICWS21/sieve.pdf
  Project: https://github.com/IntelligentDDS/Sieve
  DOI: https://doi.org/10.1109/ICWS53863.2021.00063
  Slides: https://yuxiaoba.github.io/files/ICWS21/sieve-slides.pdf
  BibTex: https://yuxiaoba.github.io/files/ICWS21/sieve-bibtex.txt
  # Arxiv:
---
