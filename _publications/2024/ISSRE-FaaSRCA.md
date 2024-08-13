---
title:          "FaaSRCA: Full Lifecycle Root Cause Analysis for Serverless Applications"
date:           2024-06-12 00:00:00 +0800
selected:       true
pub:            >-
                In 39th IEEE/ACM International Conference on Automated Software Engineering.
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ASE'24 (CCF A)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Serverless becomes popular as a novel computing paradigms for cloud native services. However, the complexity and dynamic nature of serverless applications present significant challenges to ensure system availability and performance. There are many root cause analysis (RCA) methods for microservice systems, but they are not suitable for precise modeling serverless applications. This is because: (1) Compared to microservice, serverless applications exhibit a highly dynamic nature. They have short lifecycle and only generate instantaneous pulse-like data, lacking long-term continuous information. (2) Existing methods solely focus on analyzing the running stage and overlook other stages, failing to encompass the entire lifecycle of serverless applications. To address these limitations, we propose FaaSRCA, a full lifecycle root cause analysis method for serverless applications. It integrates multi-modal observability data generated from platform and application side by using Global Call Graph. We train a Graph Attention Network (GAT) based graph auto-encoder to compute reconstruction scores for the nodes in global call graph. Based on the scores, we determine the root cause at the granularity of the lifecycle stage of serverless functions. We conduct experimental evaluations on two serverless benchmarks, the results show that FaaSRCA outperforms other baseline methods with a top-k precision improvement ranging from 21.25% to 81.63%.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Jin Huang
  - Pengfei Chen
  - Guangba Yu
  - Yilun Wang
  - Haiyu Huang
  - Zilong He

links:
  Paper: 
  Project: 
  DOI: 
  BibTex: 
  # Arxiv:
---