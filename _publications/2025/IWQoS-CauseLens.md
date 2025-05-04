---
title:          "CauseLens: Causality-based Interpretable Root Cause Analysis for Microservice Systems"
date:           2025-05-01 00:00:00 +0800
selected:       false
pub:            >-
                In IEEE/ACM International Symposium on Quality of Service
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">IWQoS'25 (CCF B)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Microservice applications consist of complex API invocation relationships, where a single fault can propagate through multiple paths, leading to widespread failures. The diverse propagation patterns of different faults make efficient and interpretable root cause analysis (RCA) crucial. We propose CauseLens, a causality-based unsupervised RCA framework that improves both accuracy and interpretability. The key insight is that fine-grained causal modeling enhances root cause localization. CauseLens constructs a heterogeneous causal diagram at the operation and entity levels using normal monitoring data (i.e., metrics and traces) and trains a structural causal model. It then integrates reconstruction error and counterfactual analysis to identify root causes while revealing fault propagation paths. Experiments on two microservice datasets demonstrate that CauseLens outperforms state-of-the-art methods in RCA accuracy. 
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Qihan Liu
  - Pengfei Chen†
  - Guangba Yu
  - Yuanhao Lai 
  - Xiaoyun Li

links:
  Paper: 
  Project: 
  DOI: 
  BibTex: 
  Arxiv: 
---