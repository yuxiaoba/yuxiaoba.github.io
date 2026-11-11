# 技术专题维护

技术专题与逐日更新分开：现阶段入口在 Tech Notes 顶部，索引为 /topics/、/zh/topics/，顶栏不增加栏目。

## 文件

保存在 _tech/zh/topics/<slug>.md 和 _tech/en/topics/<slug>.md。复用文章模板、长文目录、收藏和全文检索；搜索类型仍为 tech，主题标签仍使用 _data/note_tags.yml 的既有词表。

最少字段：
- title、date（首次创建日期）、updated_at（最后实质修订日期）、lang
- published: true/false、topic_guide: true、long_read: true
- permalink: /tech/<lang>/topics/<slug>/
- summary、tags、authoring_source: assistant、translation_source: assistant

只更新日期不能代替内容修订。双语在同批完成，相同相对路径；准备中的稿用 published: false。未翻译的专题不会出现在另一语言的列表或搜索，切换时返回目标语言专题索引并提示缺失译文。

## 内容规则

用共同问题、机制对照和证据边界串联论文/报告，不复制日更全文，不将不同任务的数字拼成排名。有实质内容的表格即可，无需装饰图。先核对主源全文及必要的关联论文，机制判断与个人推论分开写。只有完整可读的已发布文章才能成为站内入口；否则链接原始论文。

专题不会混入按月 Tech Notes 归档或首页最新技术笔记。每日任务不会自动重写专题；新增来源改变路线、证据或关键分歧时，再作成对修订并更新日期。发布仍走既有构建、资源、双语、草稿排除和手机验证流程。

专题里的背景引用不作为“日更已完成阅读”的去重依据；相应来源仍可在每日论文集或单篇技术笔记里完整解读。
