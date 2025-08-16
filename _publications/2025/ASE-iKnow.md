---
title:          "iKnow: an Intent-Guided Chatbot for Cloud Operations with Retrieval-Augmented Generation"
date:           2025-08-14 00:00:00 +0800
selected:       true
pub:            >-
                In 40th IEEE/ACM International Conference on Automated Software Engineering
pub_pre:        >-
                <span class="badge badge-pill badge-custom badge-success">ASE'25 (CCF A)</span>
# <span class="badge badge-pill badge-custom badge-info">FSE'24</span>
# pub_post:       'Under review.'
# pub_last:       '🏆 <span style="color:red"><b>Best Paper Award</b></span>'
abstract: >-
    Managing complex cloud services requires standard operational documentation, but its sheer volume often hinders cloud engineers from efficient knowledge acquisition. Retrieval-Augmented Generation (RAG) can streamline this process by retrieving relevant knowledge and generating concise, referenced answers. However, deploying a reliable RAG-based chatbot for cloud operation remains a challenge. In this experience paper, we analyze the development and deployment of RAG-based chatbots for operational question answering (OpsQA) at a large-scale cloud vendor. Through an empirical study of 2,000 real-world queries across three operational teams, we identify five unique OpsQA intent types (e.g., symptom analysis and terminology explanation) and their corresponding requirements for a satisfactory answer, which differ from general software engineering queries. Our analysis further uncovers six root causes leading to chatbot failures---over half stem from query issues (i.e., incompleteness, out-of-scope, or invalid queries), while others are from retrieval or generation issues. To address these issues, we propose iKnow, an intent-guided RAG-based chatbot that integrates intent detection, query rewriting tailored to each intent, and missing knowledge detection to enhance answer quality. In internal evaluations, iKnow improves average answer accuracy from 65.8% to 81.3% with only a modest increase in latency. iKnow has been deployed for six months at CloudA, supporting thousands of cloud engineers in daily operations. We discuss lessons learned from real-world deployment, providing valuable insights for future research and practical implementations in similar domains.
# cover:          assets/images/covers/Prism-cover.png
authors:
  - Junjie Huang
  - Yuedong Zhong
  - Guangba Yu†
  - Zihan Jiang
  - Minzhi Yan
  - Wenfei Luan
  - Tianyu Yang
  - Rui Ren
  - Michael Lyu

links:
  Paper: 
  Project: 
  DOI: 
  BibTex: 
---