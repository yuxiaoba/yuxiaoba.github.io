---
title:          "Microscaler: Automatic Scaling for Microservices with an Online Learning Approach"
date:           2019-08-29 00:00:00 +0800
selected:       false
pub:            >-
                In Proceedings of the 2019 IEEE International Conference on Web Services
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICWS'19 (CCF B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Recently, the microservice becomes a popular architecture to construct cloud native systems due to its agility. In cloud native systems, autoscaling is a core enabling technique to adapt to workload changes by scaling out/in. However, it becomes a challenging problem in a microservice system, since such a system usually comprises a large number of different micro services with complex interactions. When bursty and unpredictable workloads arrive, it is difficult to pinpoint the scaling-needed services which need to scale and evaluate how much resource they need. In this paper, we present a novel system named Microscaler to automatically identify the scaling-needed services and scale them to meet the service level agreement (SLA) with an optimal cost for micro-service systems. Microscaler collects the quality of service metrics (QoS) with the help of the service mesh enabled infrastructure. Then, it determines the under-provisioning or over-provisioning services with a novel criterion named service power. By combining an online learning approach and a step-by-step heuristic approach, Microscaler could achieve the optimal service scale satisfying the SLA requirements. The experimental evaluations in a micro-service benchmark show that Microscaler converges to the optimal service scale faster than several state-of-the-art methods.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Guangba Yu
  - Pengfei Chen†
  - Zibin Zheng
links:
  Paper: https://yuxiaoba.github.io/files/ICWS19/microscaler.pdf
  BibTex: https://yuxiaoba.github.io/files/ICWS19/microscaler-bibtex.txt
  DOI: https://doi.org/10.1109/ICWS.2019.00023
  # Arxiv:
---
