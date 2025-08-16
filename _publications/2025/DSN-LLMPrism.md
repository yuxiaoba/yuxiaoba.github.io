---
title:          "LLMPrism: Black-box Performance Diagnosis for Production LLM Training Platforms"
date:           2025-05-01 00:00:00 +0800
selected:       false
pub:            >-
                In 55th Annual IEEE/IFIP International Conference on Dependable Systems and Networks
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">DSN'25 (CCF B)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Large Language Models (LLMs) have brought about revolutionary changes in diverse fields, rendering LLM training of utmost importance for modern enterprises. To meet this demand, multi-tenant large-scale LLM training platforms have been built to offer LLM training services. Nevertheless, due to the complexity and synchronous nature of LLM training process, performance issues occur frequently and can result in substantial resource wastage. The limited visibility from the perspective of platform providers impedes existing profiling methods and poses challenges to the monitoring and diagnosis of the performance of LLM training jobs. For the first time, this paper proposes the utilization of underlying network flow data to reconstruct the training timelines of jobs based on the distinct characteristics in the LLM training procedure. We design LLMPrism, the first black-box performance diagnosis system for LLM training platforms. By progressively recognizing LLM training jobs, identifying their parallelism strategies, and reconstructing the training timelines, LLMPrism achieves non-intrusive, lightweight, and continuous monitoring of LLM training systems. Leveraging this monitoring capability, it further effectively diagnoses potential performance issues.Since Oct. 2024, LLMPrism has been deployed on our large-scale production Platform-X, in which the evaluations and deployment experiences demonstrate that LLMPrism can achieve accurate timeline reconstruction with an error within 0.3% and effectively diagnose various performance issues.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zhihan Jiang
  - Rui Ren
  - Guangba Yu†
  - Yulun Wu
  - Wenwei Gu
  - Yichen Li
  - Yujie Huang
  - Cong Feng
  - Zengyin Yang
  - Yongqiang Yang
  - Michael R. Lyu

links:
  Paper: https://ieeexplore.ieee.org/document/11068334
  # Project: 
  DOI: https://doi.org/10.1109/DSN-S65789.2025.00034
  BibTex: https://yuxiaoba.github.io/files/DSN25/LLMPrim-bibtex.txt
  Arxiv: https://arxiv.org/pdf/2505.00342
---