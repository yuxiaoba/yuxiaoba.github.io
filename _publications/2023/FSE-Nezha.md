---
title:          "Nezha: Interpretable Fine-Grained Root Causes Analysis for Microservices on Multi-Modal Observability Data"
date:           2023-07-28 00:00:00 +0800
selected:       true
pub:            >-
                In 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">FSE'23</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Root cause analysis (RCA) in large-scale microservice systems is a critical and challenging task. To understand and localize root causes of unexpected faults, modern observability tools collect and preserve multi-modal observability data, including metrics, traces, and logs. Since system faults may manifest as anomalies in different data sources, existing RCA approaches that rely on single-modal data are constrained in the granularity and interpretability of root causes. In this study, we present Nezha, an interpretable and fine-grained RCA approach that pinpoints root causes at the code region and resource type level by incorporative analysis of multi-modal data. Nezha transforms heterogeneous multi-modal data into a homogeneous event representation and extracts event patterns by constructing and mining event graphs. The core idea of Nezha is to compare event patterns in the fault-free phase with those in the fault-suffering phase to localize root causes in an interpretable way. Practical implementation and experimental evaluations on two microservice applications show that Nezha achieves a high top1 accuracy (87.5%) on average at the code region and resource type level and outperforms state-of-the-art approaches by a large margin. Two ablation studies further confirm the contributions of incorporating multi-modal data.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Guangba Yu
  - Pengfei Chen†
  - Yufeng Li
  - Hongyang Chen
  - Xiaoyun Li
  - Zibin Zheng
links:
  Paper: https://yuxiaoba.github.io/files/FSE23/nezha.pdf
  Project: https://github.com/IntelligentDDS/Nezha
  Slides: https://yuxiaoba.github.io/files/FSE23/nezha-slides.pdf
  DOI: https://doi.org/10.1145/3611643.3616249
  BibTex: https://yuxiaoba.github.io/files/FSE23/nezha-bibtex.txt
  # Arxiv:
---
