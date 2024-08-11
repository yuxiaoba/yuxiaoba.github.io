---
title:          "A Learning-based Dynamic Load Balancing Approach for Microservice Systems in Multi-cloud Environment"
date:           2020-12-02 00:00:00 +0800
selected:       false
pub:            >-
                In Proceedings of IEEE 26th International Conference on Parallel and Distributed Systems
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICPADS'20 (CCF C, CORE B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Multi-cloud environment has become common since companies manage to prevent cloud vendor lock-in for security and cost concerns. Meanwhile, the microservice architecture is often considered for its flexibility. Combining multi-cloud with microservice, the problem of routing requests among all possible microservice instances in multi-cloud environment arises. This paper presents a learning-based approach to route requests in order to balance the load. In our approach, the performance of microservice is modeled explicitly through machine learning models. The model can derive the response time from request volume, route decision, and other cloud metrics. Then the balanced route decision is obtained from optimizing the model with Bayesian Optimization. With this approach, the request route decision can adjust to dynamic runtime metrics instead of remaining static for all different circumstances. Explicit performance modeling avoids searching on an actual microservice system which is time-consuming. Experiments show that our approach reduces average response time by 10% at least.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Jieqi Cui
  - Pengfei Chen†
  - Guangba Yu
links:
  Paper: https://yuxiaoba.github.io/files/ICPADS20/load.pdf
  DOI: https://doi.org/10.1109/ICPADS51040.2020.00052
  BibTex: https://yuxiaoba.github.io/files/ICPADS20/load-bibtex.txt
  # Arxiv:
---
