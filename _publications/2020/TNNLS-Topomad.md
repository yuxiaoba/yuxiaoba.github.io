---
title:          "A Spatiotemporal Deep Learning Approach for Unsupervised Anomaly Detection in Cloud Systems"
date:           2020-10-16 00:00:00 +0800
selected:       true
pub:            >-
                In IEEE Transactions on Neural Networks and Learning Systems
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-info">TNNLS (Impact Factor 10.4, CCF B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Anomaly detection is a critical task for maintaining the performance of a cloud system. Using data-driven methods to address this issue is the mainstream in recent years. However, due to the lack of labeled data for training in practice, it is necessary to enable an anomaly detection model trained on contaminated data in an unsupervised way. Besides, with the increasing complexity of cloud systems, effectively organizing data collected from a wide range of components of a system and modeling spatiotemporal dependence among them become a challenge. In this article, we propose TopoMAD, a stochastic seq2seq model which can robustly model spatial and temporal dependence among contaminated data. We include system topological information to organize metrics from different components and apply sliding windows over metrics collected continuously to capture the temporal dependence. We extract spatial features with the help of graph neural networks and temporal features with long short-term memory networks. Moreover, we develop our model based on variational auto-encoder, enabling it to work well robustly even when trained on contaminated data. Our approach is validated on the run-time performance data collected from two representative cloud systems, namely, a big data batch processing system and a microservice-based transaction processing system. The experimental results show that TopoMAD outperforms some state-of-the-art methods on these two data sets.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zilong He
  - Pengfei Chen†
  - Xiaoyun Li
  - Yongfeng Wang
  - Guangba Yu
  - Cailin Chen
  - Xinrui Li
  - Zibin Zheng
  
links:
  Paper: https://yuxiaoba.github.io/files/TNNLS/topomd.pdf
  DOI: https://doi.org/10.1109/TNNLS.2020.3027736
  BibTex: https://yuxiaoba.github.io/files/TNNLS/topomd-bibtex.txt
  Project: https://github.com/IntelligentDDS/TopoMAD
  # Arxiv:
---
