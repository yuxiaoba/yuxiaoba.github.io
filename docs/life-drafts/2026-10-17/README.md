# 土耳其早餐相册草稿

- 原照片：`.incoming/life/2026-10-17/`，四张；原图不修改、不提交。
- 用户提供：土耳其、新欧洲区、早餐店。未提供城市、店名、价格或口味评价；正文不补写。
- 日期暂沿用上传文件夹 `2026-10-17`；微信文件名是导出时间，不作为拍摄日期。
- 中英文正文及图注由助手整理，英文为助手翻译。
- 食物类别依据照片与 GoTürkiye 资料比对；börek、baklava 为外观判断，浅色那盘类似 su böreği。具体馅料及细分名称未确认，不能写成店家菜单。
- 参考：https://goturkiye.com/gastronomy/turkish-cuisine 、https://goturkiye.com/gastronomy/turkish-breakfast 、https://goturkiye.com/blog/5-borek-recipes-to-try-at-home 。
- `zh.md` / `en.md` 是 `published: false` 草稿。尚未放入正式 Life 集合。
- 预览构建器 `.preview/life-breakfast/build.py` 在隔离快照中生成 `/review/life-breakfast/` 与 `/review/life-breakfast/en/`，使用原比例、去元数据的网页副本；不进入站内搜索。链接可被访问，noindex 不等于访问控制。
- 确认后再把正文复制到 `_kitchen/zh/2026-10-17-turkish-breakfast.md` 和英文对应路径，并把网页副本及相册样式移至正式 assets；不要直接把私人收件箱加入网站。
- 预览为当前构建的附加页面；后续普通重建可能移除它，可用上述构建器恢复，不为草稿增加自动发布任务。

## 用户确认与精简（2026-10-21）

用户确认两盘为牛肉 börek 与水酥皮 börek；浅色层叠盘标为水酥皮，卷状切块盘标为牛肉。移除导语、食物科普、出处及长图注，双语仅保留日期、标题和食物名称。以上确认取代早期馅料未确认的记录。

用户补充：页面明确写“土耳其 · 新欧洲区”，全景图加短图注“红茶”；英文同步为 Türkiye · New European District / Black tea，不额外推断城市。

## 接入 Life（2026-10-21）

用户指出Life没有更新，现已将确认版复制为 `_kitchen/zh/2026-10-17-turkish-breakfast.md` 和英文对应文件，published:true；网页副本位于 `assets/images/kitchen/2026-10-17-turkish-breakfast/`，原图仍留收件箱。后续修改正式集合中的文件，本目录保留审阅草稿来源。页面使用warm布局及photo_album:true加载独立相册CSS，原有collection自动提供列表及中英文互链。

## 动态流更新

确认版现使用life-album布局，照片与地点统一放在正式文章的photos/location字段。Life列表直接展示照片网格及短文字，标题仍保留详情链接；原图和先前草稿保留。后续维护以正式_kitchen文件为准，不再复制本目录旧HTML覆盖它们。
