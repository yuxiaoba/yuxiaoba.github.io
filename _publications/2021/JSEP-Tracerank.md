---
title:          "TraceRank: Abnormal Service Localization with Dis-Aggregated End-to-End Tracing Data in Cloud Native Systems"
date:           2021-12-07 00:00:00 +0800
selected:       false
pub:            >-
                In Journal of Software Evolution and Process 
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">JSEP (CCF B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Modern cloud native applications are generally built with a microservice architecture. To tackle various performance problems among a large number of services and machines, an end-to-end tracing tool is always equipped in these systems to track the execution path of every single request. However, it is nontrivial to conduct root cause analysis of anomalies with such a large volume of tracing data. This paper proposes a novel system named TraceRank to identify and locate abnormal services causing performance problems with dis-aggregated end-to-end traces. TraceRank mainly includes an anomaly detection module and a root cause analysis module. The root cause analysis procedure is triggered when an anomaly is detected. To fully leverage the information provided by the tracing data, both the spectrum analysis and the PageRank-based random walk methods are introduced to pinpoint abnormal services. The experiments in TrainTicket and Bookinfo microservice benchmarks and a real-world system show that TraceRank can locate root causes with 90% in Precision and 86% in Recall. TraceRank has up to 10% improvement compared with several state-of-the-art approaches in both Precision and Recall. Finally, TraceRank has good scalability and a low overhead to adapt to large-scale microservice systems.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Guangba Yu
  - Zicheng Huang
  - Pengfei Chen†
  - 
links:
  Paper: https://yuxiaoba.github.io/files/JSEP/tracerank.pdf
  DOI: https://doi.org/10.1002/smr.2413
  BibTex: https://yuxiaoba.github.io/files/JSEP/tracerank-bibtex.txt
  # Arxiv:
---
