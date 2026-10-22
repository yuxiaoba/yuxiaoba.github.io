# Life 照片维护：文件夹交接

用户选择目录拷贝方式，不搭建网页上传服务，不新增 HTTPS、数据库或 CMS。

收件目录：`/home/GB-Project/yuxiaoba.github.io/.incoming/life/`。

每次记录一个文件夹，放 JPG / JPEG / PNG / WebP / HEIC 原照片，可选 `说明.txt`（日期、地点、文字、封面偏好）。用户不必写 YAML。手机照片先导出到电脑，再沿用已有 SSH/SFTP 上传；电脑照片直接拷贝。`.part` 文件夹用于上传中状态，完整上传后改成最终名称。

用户告知上传完成后，助手读取该组照片和说明，整理页面：列表使用统一比例封面、正文保持照片比例；生成适合网页的图片副本，去除 GPS 等 EXIF 元数据，原图仍保留在收件箱。根据用户真实文字准备中英文 Markdown；不从照片推断口味、消费体验或虚构个人故事。材料不完整时可保持纯相册，必要信息再询问。

初稿 `published: false`，审阅完成后才转公开内容；不设置新的定时自动发布。此目录由 `.incoming/` 的 Git 忽略与 Jekyll 排除保护。仅正式确认的网页副本和文章进入 `_kitchen/` 与 `assets/images/kitchen/`。

## 动态流展示（2026-10-21）

Life入口按日期倒序直接展示一条条动态：短标题／文字、照片网格、地点，无需阅读全文。四张照片使用2×2布局，单张保留原比例，点图在原生dialog中按完整比例查看，支持前后切换、键盘与Escape关闭；无JavaScript仍可打开图片链接。原相册详情URL与双语配对保留。

照片信息统一保存在文章frontmatter的photos列表（src、可选webp、width、height、alt、caption），location记录用户提供的地点。列表与life-album布局共用这份清单，不再手写两套照片HTML。用户上传流程仍是照片文件夹加可选说明，字段由助手整理；旧的普通Markdown图片文章兼容首图回退。图片原件不进入公开目录。
