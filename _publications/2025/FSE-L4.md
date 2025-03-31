---
title:          "L4: Diagnosing Large-scale LLM Training Failures via Automated Log Analysis"
date:           2025-03-22 00:00:00 +0800
selected:       true
pub:            >-
                In 33nd ACM International Conference on the Foundations of Software Engineering.
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">FSE'25 (CCF A)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    As Large Language Models (LLMs) show their capabilities across various applications, training customized LLMs has become essential for modern enterprises. However, due to the complexity of LLM training, which requires massive computational resources and extensive training time, failures are inevitable during the training process. These failures result in considerable waste of resource and time, highlighting the critical need for effective and efficient failure diagnosis to reduce the cost of LLM training. In this paper, we present the first empirical study on the failure reports of 428 LLM training failures in our production Platform-X between May 2023 and April 2024. Our study reveals that hardware and user faults are the predominant root causes, and current diagnosis processes rely heavily on training logs. Unfortunately, existing log-based diagnostic methods fall short in handling LLM training logs. Considering the unique features of LLM training, we identify three distinct patterns of LLM training logs: cross-job, spatial, and temporal patterns. We then introduce our Log-based Large-scale LLM training failure diagnosis framework, L4, which can automatically extract failure-indicating information (i.e., log events, nodes, stages, and iterations) from extensive training logs, thereby reducing manual effort and facilitating failure recovery. Experimental results on real-world datasets show that L4 outperforms existing approaches in identifying failure-indicating logs and localizing faulty nodes. Furthermore, L4 has been applied in Platform-X and demonstrated its effectiveness in enabling accurate and efficient failure diagnosis.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zhihan Jiang
  - Junjie Huang
  - Guangba Yu†
  - Zhuangbin Chen
  - Yichen Li
  - Renyi Zhong
  - Cong Feng
  - Yongqiang Yang
  - Michael R. Lyu

links:
  Paper: https://yuxiaoba.github.io/files/FSE25/L4.pdf
  DOI: 
  BibTex: 
  Arxiv: https://arxiv.org/pdf/2503.20263
---