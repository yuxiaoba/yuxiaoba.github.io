---
title:          "Microscaler: Cost-effective Scaling for Microservice Applications in the Cloud with an Online Learning Approach"
date:           2020-04-06 00:00:00 +0800
selected:       false
pub:            >-
                In IEEE Transaction on Cloud Computing
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">TCC (Impact Factor 5.9)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Recently, the microservice becomes a popular architecture to construct cloud native systems due to its agility. In cloud native systems, autoscaling is a key enabling technique to adapt to workload changes by acquiring or releasing the right amount of computing resources. However, it becomes a challenging problem in microservice applications, since such an application usually comprises a large number of different microservices with complex interactions. When the performance decreases due to an unpredictable workload peak, it is difficult to pinpoint the scaling-needed services which need to scale out and evaluate how many resources they need. In this paper, we present a novel system named Microscaler to automatically identify the scaling-needed services and scale them to meet the Service Level Agreement (SLA) with an optimal cost for microservice applications. Microscaler first collects the quality of service (QoS) metrics in the service mesh enabled microservice infrastructure. Then, it determines under-provisioning or over-provisioning service instances along the service dependency graph with a novel scaling-needed service criterion named service power. The service dependency graph could be obtained by correlating each request flow in the service mesh. By combining an online learning approach and a step-by-step heuristic approach, Microscaler can precisely reach the optimal service scale meeting the SLA requirements. The experimental evaluations in a microservice benchmark show that Microscaler achieves an average 93% precision in scaling-needed service determination and converges to the optimal service scale faster than several state-of-the-art methods. Moreover, Microscaler is lightweight and flexible enough to work in a large-scale microservice system.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Guangba Yu
  - Pengfei Chen†
  - Zibin Zheng
  
links:
  Paper: https://yuxiaoba.github.io/files/TCC/microscaler.pdf
  DOI: https://doi.org/10.1109/TCC.2020.2985352
  BibTex: https://yuxiaoba.github.io/files/TCC/microscaler-bibtex.txt
  # Arxiv:
---
