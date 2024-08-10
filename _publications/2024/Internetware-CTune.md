---
title:          "CTuner: Automatic NoSQL Database Tuning with Causal Reinforcement Learning"
date:           2024-06-18 00:00:00 +0800
selected:       false
pub:            >-
                In 15th Asia-Pacific Symposium on Internetware.
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">Internetware'24 (CCF C)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    The rapid development of information technology has necessitated the management of large volumes of data in modern society, leading to the emergence of NoSQL databases (e.g., MongoDB). To meet the huge demand for efficient data management and query, optimizing the performance of these databases has become crucial. Currently, some reinforcement learning-based methods have been used to improve the efficiency of databases by tuning customizable database configurations. However, these methods have two limitations including susceptibility to cold-start effect and low efficiency in configuration search. To address these issues, we propose a novel and effective approach named CTuner for the online performance tuning of NoSQL databases. CTuner skips cold start by Bayesian optimization-based learning, and improves the exploitation strategy of the TD3 model with causal inference. Practical implementation and experimental evaluations on three prominent NoSQL databases show that CTuner can find a better configuration at the same time cost than state-of-the-art approaches, with up to a 27.4% improvement in throughput and up to 13.2% reduction in 95th latency. Moreover, we introduce meta-learning to enhance the adaptability of CTuner and confirm that it is able to reliably improve performance under new environments and workloads.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Genting Mai
  - Zilong He
  - Guangba Yu
  - Zhiming Chen
  - Pengfei Chen

links:
  Paper: https://yuxiaoba.github.io/files/Interware24/ctune.pdf
  Project: https://github.com/IntelligentDDS/Ctuner
  DOI:  https://doi.org/10.1145/3671016.3674809
  BibTex: https://yuxiaoba.github.io/files/Interware24/ctune-bibtex.txt
  # Arxiv:
---