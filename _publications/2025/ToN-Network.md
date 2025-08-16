---
title:          "NetScope: Fault Localization in Programmable Networking Systems With Low-Cost In-Band Network Telemetry and In-Network Detection"
date:           2025-07-29 00:00:00 +0800
selected:       true
pub:            >-
                In IEEE Transactions on Networking 
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">ToN (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Recently, Software Defined Networking (SDN) has gained widespread adoption as a network infrastructure. Although the openness and programmability of SDN facilitate large complex network construction, diagnosing faults in datacenter-scale network remains challenging. Previous network diagnosis tools pose significant overhead in fine-grained telemetry and typically lack automated fine-grained fault diagnosis capabilities. Although on-demand monitoring methods have been proposed to reduce telemetry overhead, they struggle with effectively setting fixed thresholds, which requires expert experience. This paper presents NetScope, a lightweight system for real-time anomaly detection with self-adaptive thresholds and automatic root cause localization in programmable networking systems. NetScope estimates latency medians for each Flow (i.e., a pair of source and sink switches) within the switch using the proposed per-Flow quantile sketch and calculates the threshold accordingly for anomaly detection. Upon detecting anomalies, NetScope collects aggregated packet-level telemetry on demand and generates a ranked list of fine-grained fault culprits at multiple levels, including port-level, Flow-level, and switch-level. Extensive experiments demonstrate the effectiveness and efficiency of NetScope in anomaly detection and fault localization. Specifically, NetScope achieves a 32%~116% relative improvement in anomaly detection and 6%~197% improvement in root cause analysis compared with other baselines without causing any network bandwidth in anomaly detection while consuming 64.2% less telemetry bandwidth for localization.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Hongyang Chen
  - Benran Wang
  - Guangba Yu
  - Zilong He
  - Pengfei Chen†
  - Chen Sun
  - Zibin Zheng
  
links:
  Paper: https://yuxiaoba.github.io/files/ToN/NetScope.pdf
  DOI: https://doi.org/10.1109/TON.2025.3590034
  BibTex: https://yuxiaoba.github.io/files/ToN/NetScope-bibtex.txt
  # Arxiv:
---
