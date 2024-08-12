---
title:          "MicroFI: Non-Intrusive and Prioritized Request-Level Fault Injection for Microservice Applications"
date:           2024-02-07 00:00:00 +0800
selected:       true
pub:            >-
                In IEEE Transactions on Dependable and Secure Computing
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">TDSC (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Microservice is a widely-adopted architecture for constructing cloud-native applications. To test application resiliency, chaos engineering is widely used to inject faults proactively in applications. However, the searching space formed by possible injection locations is huge due to the scale and complexity of the application. Although some methods are proposed to effectively explore injection space, they cannot prioritize high-impact injection solutions. Additionally, the blast radius of faults injected by existing methods is typically full of uncertainty, causing faults of multiple application functions. Although some tools are designed to conduct request-level injection, they require instrumentation on application code. To tackle these problems, this paper presents MicroFI, a non-intrusive fault injection framework, aiming to efficiently test different application functions with request-level injection. Request-level injection limits the blast radius to specified requests without any source code modification. Additionally, MicroFI leverages historical injection results and parallel technique to accelerate the searching. Moreover, An enhanced PageRank is used to measure the impact of faults and prioritize high-impact faults that fail more functions. Evaluations on three microservice applications show that MicroFI precisely injects faults and reduces up to 91% redundant faults on average. Additionally, by employing prioritization, MicroFI reduces an average of 47.3% injection budgets to cover all high-impact faults.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Hongyang Chen
  - Pengfei Chen†
  - Guangba Yu
  - Xiaoyun Li
  - Zilong He
  - Huxing Zhang
  
links:
  Paper: https://yuxiaoba.github.io/files/TDSC/microfi.pdf
  DOI: https://doi.org/10.1109/TDSC.2024.3363902
  BibTex: https://yuxiaoba.github.io/files/TDSC/microfi-bibtex.txt
  # Arxiv:
---
