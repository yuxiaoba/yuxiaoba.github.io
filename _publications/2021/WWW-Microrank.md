---
title:          "MicroRank: End-to-End Latency Issue Localization with Extended Spectrum Analysis in Microservice Environments"
date:           2021-04-19 00:00:00 +0800
selected:       true
pub:            >-
                In Proceedings of the Web Conference 2021
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">WWW'21 (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  With the advantages of flexible scalability and fast delivery, microservice has become a popular software architecture in the modern IT industry. However, the explosion in the number of service instances and complex dependencies make the troubleshooting extremely challenging in microservice environments. To help understand and troubleshoot a microservice system, the end-to-end tracing technology has been widely applied to capture the execution path of each request. Nevertheless, the tracing data are not fully leveraged by cloud and application providers when conducting latency issue localization in the microservice environment. This paper proposes a novel system, named MicroRank, which analyzes clues provided by normal and abnormal traces to locate root causes of latency issues. Once a latency issue is detected by the Anomaly Detector in MicroRank, the cause localization procedure is triggered. MicroRank first distinguishs which traces are abnormal. Then, MicroRank’s PageRank Scorer module uses the abnormal and normal trace information as its input and differentials the importance of different traces to extended spectrum techniques . Finally, the spectrum techniques can calculate the ranking list based on the weighted spectrum information from PageRank Scorer to locate root causes more effectively. The experimental evaluations on a widely-used open-source system and a production system show that MicroRank achieves excellent results not only in one root cause situation but also in two issues that happen at the same time. Moreover, MicroRank makes 6% to 22% improvement in recall in localizing root causes compared to current state-of-the-art methods.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Guangba Yu
  - Pengfei Chen†
  - Hongyang Chen
  - Zijie Guan
  - Zicheng Huang
  - Linxiao Jing
  - Tianjun Weng
  - Xinmeng Sun
  - Xiaoyun Li
  
links:
  Paper: https://yuxiaoba.github.io/files/WWW21/microrank.pdf
  Project: https://github.com/IntelligentDDS/MicroRank
  DOI: https://doi.org/10.1145/3442381.3449905
  BibTex: https://yuxiaoba.github.io/files/WWW21/microrank-bibtex.txt
  # Arxiv:
---
