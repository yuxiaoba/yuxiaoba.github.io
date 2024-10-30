---
title:          "FaaSConf: QoS-aware Hybrid Resources Configuration for Serverless Workflows"
date:           2024-08-12 00:00:00 +0800
selected:       true
pub:            >-
                In 39th IEEE/ACM International Conference on Automated Software Engineering.
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ASE'24 (CCF A)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    The workflow composition of multiple short-lived functions has emerged as a prominent pattern in Function-as-a-Service (FaaS), exposing a considerable resources configuration challenge compared to individual independent serverless functions. This challenge unfolds in two ways. Firstly, serverless workflows frequently encounter dynamic and concurrent user workloads, increasing the risk of QoS violations. Secondly, the performance of a function can be affected by the resource re-provision of other functions within the workflow. With the popularity of the mode of concurrent processing in one single instance, concurrency limit as a critical configuration parameter imposes restrictions on the capacity of requests per instance. In this study, we present FaaSConf, a QoS-aware hybrid resource configuration approach that uses multi-agent reinforcement learning (MARL) to configure hybrid resources, including hardware resources and concurrency, thereby ensuring end-to-end QoS while minimizing resource costs. To enhance decision-making, we employ an attention technique in MARL to capture the complex performance dependencies between functions. We further propose a safe exploration strategy to mitigate QoS violations, resulting in a safer and efficient configuration exploration. The experimental results demonstrate that FaaSConf outperforms state-of-the-art approaches significantly. On average, it achieves a 26.5% cost reduction while exhibiting robustness to dynamic load changes.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Yilun Wang
  - Pengfei Chen
  - Hui Dou
  - Yiwen Zhang
  - Guangba Yu
  - Zilong He
  - Haiyu Huang

links:
  Paper: https://yuxiaoba.github.io/files/ASE24/FaaSConf.pdf
  Project: https://github.com/wiluen/FaaSConf
  DOI: https://doi.org/10.1145/3691620.3695477
  BibTex: https://yuxiaoba.github.io/files/ASE24/FaaSConf-bibtex.txt
  # Arxiv:
---