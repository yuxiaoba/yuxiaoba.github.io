---
title:          "MicroSketch: Lightweight and Adaptive Sketch based Performance Issue Detection and Localization in Microservice Systems"
date:           2022-09-03 00:00:00 +0800
selected:       false
pub:            >-
                In 20th International Conference on Service-Oriented Computing
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ICSOC'22 (CCF B)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  With the rapid growth of microservice systems in cloud-native environments, end-to-end traces have become essential data to help diagnose performance issues. However, existing trace-based anomalydetection and root cause analysis (RCA) still suffer from practical issues due to either the massive volume or frequent system changes. In this study, we propose a lightweight and adaptive trace-based anomaly detection and RCA approach, named MicroSketch, which leverages Sketch based features and Robust Random Cut Forest (RRCForest) to rendertrace analysis more effective and efficient. In addition,MicroSketchis an unsupervised approach that is able to adapt to changes in microservicesystems without any human intervention. We evaluated MicroSketch on a widely-used open-source system and a production system. The results demonstrate the efficiency and effectiveness of MicroSketch. MicroSketch significantly outperforms start-of-the-art approaches, with an average of 40.9% improvement in F1 score on anomaly detection and 25.0% improvement in Recall of Top-1 on RCA. In particular, MicroSketch is at least 60x faster than other methods in terms of diagnosis time.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Xiaoyun Li
  - Guangba Yu
  - Pengfei Chen†
  - Hongyang Chen
  - Zhekang Chen
links:
  Paper: https://yuxiaoba.github.io/files/ICSOC22/microsketch.pdf
  DOI: https://doi.org/10.1007/978-3-031-20984-0_15
  BibTex: https://yuxiaoba.github.io/files/ICSOC22/microsketch-bibtex.txt
  # Arxiv:
---
