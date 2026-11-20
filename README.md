# 漏洞验证指南

VXP（Vulnerability Validation Guide）记录漏洞研究、验证和交付中常见的证据误判，帮助团队把技术结论建立在可复核的证据上。分类定位场景，条目给出判断依据与检查方法；具体验收标准由项目约定。

- 阅读站点：<https://atoz-project.github.io/vxp/>
- 术语表：[GLOSSARY.md](GLOSSARY.md)
- 条目契约：[TEMPLATE.md](TEMPLATE.md)
- 字段表：`_data/entry_record.yml`（检查器与站点共用的唯一 schema）
- 条目文件：`VXP-NNN-短标题.md`。文件顶部的 front matter 是条目记录，保存编号、标题、分类、父条目、状态、版本与日期。

```sh
uv run bin/check-entries
uv run --with pyyaml python -m unittest discover -s tests
```

分类名称、目录、计数和侧栏由站点在构建时从条目记录生成，本文件保留仓库入口与维护说明。新增条目先读 [TEMPLATE.md](TEMPLATE.md)。