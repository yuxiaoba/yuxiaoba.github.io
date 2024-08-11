---
title:          "Kmon: An In-kernel Transparent Monitoring System for Microservice Systems with eBPF"
date:           2021-05-29 00:00:00 +0800
selected:       false
pub:            >-
                In Proceedings of 2021 IEEE/ACM International Workshop on Cloud Intelligence
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">CloudIntelligence'21</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Currently, the architecture of software systems is shifting from “monolith” to “microservice” which is an important enabling technology of cloud native systems. Since the advantages of microservice in agility, efficiency, and scaling, it has become the most popular architecture in the industry. However, as the increase of microservice complexity and scale, it becomes challenging to monitor such a large number of microservices. Traditional monitoring techniques such as end-to-end tracing cannot well fit microservice environment, because they need code instrumentation with great effort. Moreover, they cannot explore the fine-grained internal states of microservice instances. To tackle this problem, we propose Kmon, which is an In-kernel transparent monitoring system for microservice systems with extended Berkeley Packet Filter (eBPF). Kmon can provide multiple kinds of run-time information of micrservices such as latency, topology, performance metrics with a low overhead.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Tianjun Weng
  - Wanqi Yang
  - Guangba Yu
  - Pengfei Chen†
  - Jieqi Cui
  - Chuangfu Zhang
  
links:
  Paper: https://yuxiaoba.github.io/files/ICSE21/Kmon.pdf
  Project: https://github.com/IntelligentDDS/Kmon
  DOI: https://doi.org/10.1109/CloudIntelligence52565.2021.00014
  BibTex: https://yuxiaoba.github.io/files/ICSE21/Kmon-bibtex.txt
  # Arxiv:
---
