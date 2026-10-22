# 首页研究概览图

用户明确选择 imagegen 制图；v2 是减少装饰与重复文案后的双语版本；2026-10-21 的 v3-blue 将配色与首页蓝灰主题对齐。

- 中文：assets/images/research/research-map-zh-v3-blue.png
- 英文：assets/images/research/research-map-en-v3-blue.png
- 当前配色提示词：prompt-blue-zh.txt / prompt-blue-en.txt；原版式提示词：prompt-zh.txt / prompt-en.txt；均使用内置 imagegen。
- 01 云系统、02 AI 系统为两条研究主线，03 混沌工程为共同可靠性验证方法。节点、故障标记与箭头是概念示意，不代表某个具体系统实现或实测数据。

首页根据语言选图，图下可打开原尺寸文件，支持浏览器放大。按用户最新要求，不再展示可展开的文字概览；保留图像替代文本和大图入口，手机可点图查看原尺寸。

2026-10-21 增加同名无损 WebP 副本，首页通过 picture 优先加载 WebP，PNG 保留为兼容回退和原尺寸入口。使用 ImageMagick 格式转换，不重新生成图形；已比对解码后像素完全相同。头像采用相同策略，原始照片和高清 PNG 均保留。

后续修改研究方向时，中英文图片与 `_data/locales.yml` 中对应文字必须同批更新，并目视检查图中文字。不要仅改文字版而让图过时，不将生成图当作从数据自动绘制的图表。
