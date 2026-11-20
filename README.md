# VXP：漏洞验证指南

VXP（Vulnerability Validation Guide）记录漏洞研究、验证和交付中常见的证据误判。分类用于导航，条目用于判断；它不是漏洞类型目录，也不替代具体项目的技术验收。

- 阅读站点：<https://atoz-project.github.io/vxp/>
- 术语表：[GLOSSARY.md](GLOSSARY.md)
- 条目模板：[TEMPLATE.md](TEMPLATE.md)
- 条目文件：`VXP-NNN-短标题.md`。文件顶部的 front matter 是条目记录，保存编号、标题、分类、父条目、状态、版本与日期。
- 检查条目记录：`uv run bin/check-entries`

新增条目时先读 [TEMPLATE.md](TEMPLATE.md)。分类名称、目录、计数和侧栏由站点在构建时从条目记录生成，不在本文件手工维护。