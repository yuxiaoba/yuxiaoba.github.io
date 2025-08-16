---
title:          "DiagConfig: Configuration Diagnosis of Performance Violations
  in Configurable Software Systems"
date:           2023-07-28 00:00:00 +0800
selected:       false
pub:            >-
                In 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">FSE'23 (CCF A)</span>
# pub_post:       'Under review.'
# pub_last:       '<span class="badge badge-pill badge-custom badge-secondary">Conference</span><span class="badge badge-pill badge-custom badge-warning">Poster</span>'
abstract: >-
  Performance degradation due to misconfiguration in software systems that violates SLOs (service-level objectives) is commonplace. Diagnosing and explaining the root causes of such performance violations in configurable software systems is often challenging due to their increasing complexity. Although there are many tools and techniques for diagnosing performance violations, they provide limited evidence to attribute causes of observed performance violations to specific configurations. This is because the configuration is not originally considered in those tools. This paper proposes DiagConfig, specifically designed to conduct configuration diagnosis of performance violations. It leverages static code analysis to track configuration option propagation, identifies performance-sensitive options, detects performance violations, and constructs cause-effect chains that help stakeholders better understand the relationship between configuration and performance violations. Through experimental evaluations with eight real-world open-source software, we demonstrate that DiagConfig effectively identifies performance-sensitive options and constructs cause-effect chains. Specifically, DiagConfig produces fewer false positives than SafeTune (i.e., 5 vs 77) in the identification of performance-sensitive options, and outperforms Unicorn in the diagnosis of performance violations caused by configuration changes, offering more comprehensive results (recall 0.892 vs 0.289).We also show that DiagConfig can accelerate auto-tuning by compressing configuration space.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Zhiming Chen
  - Pengfei Chen†
  - Peipei Wang
  - Guangba Yu
  - Zilong He
  - Genting Mai
links:
  Paper: https://yuxiaoba.github.io/files/FSE23/diagconfig.pdf
  Project: https://github.com/IntelligentDDS/DiagConfig
  DOI: https://doi.org/10.1145/3611643.3616300
  BibTex: https://yuxiaoba.github.io/files/FSE23/diagconfig-bibtex.txt
  # Arxiv:
---
