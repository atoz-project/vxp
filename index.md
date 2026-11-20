---
layout: default
title: 漏洞验证指南
description: VXP（Vulnerability Validation Guide）记录漏洞研究、验证和交付中常见的证据误判。
permalink: /
---

# 漏洞验证指南

VXP（Vulnerability Validation Guide）记录漏洞研究、验证和交付中常见的证据误判，帮助团队把技术结论建立在可复核的证据上。分类定位场景，条目给出判断依据与检查方法；具体验收标准由项目约定。

{%- assign entries = site.pages | where_exp: "p", "p.vxp_id" | sort: "vxp_id" %}
{%- assign main_count = 0 %}
{%- assign child_count = 0 %}
{%- for p in entries %}
  {%- if p.parent %}{% assign child_count = child_count | plus: 1 %}
  {%- else %}{% assign main_count = main_count | plus: 1 %}{% endif %}
{%- endfor %}

<p class="catalog-summary"><span>{{ entries.size }} 个条目</span><span>{{ main_count }} 个主条目 / {{ child_count }} 个子条目</span><span>{{ site.data.categories.size }} 个分类</span></p>

## 使用方式

分类（A～F）按研究与验证活动组织，帮助你定位场景。主条目描述一种可独立判断的误判；子条目补充独立场景、判据或证据要求；原子条目直接给出完整检查方法。完整定义见[术语表](GLOSSARY.md)，编写与编号规则见[模板](TEMPLATE.md)。

通用条目提供判断框架；次数、比例、容差与时限由具体项目约定，并在条目中明确标注。编号保持稳定，定义变化时新增条目并标注关系。

参考来源用于支撑技术事实；条目中的“必须”“应当”若属于项目约定，会明确标注。

{% for cat in site.data.categories %}
<h2 id="{{ cat.slug }}">{{ cat.letter }}. {{ cat.name }}</h2>

<table>
  <thead>
    <tr><th>ID</th><th>条目</th><th>层级</th></tr>
  </thead>
  <tbody>
    {%- for entry in entries %}{% if entry.category == cat.letter %}
    <tr>
      <td><a href="{{ entry.url | relative_url }}">{{ entry.vxp_id }}</a></td>
      <td>{{ entry.title }}</td>
      <td>{% if entry.parent %}子条目{% else %}{% assign kids = 0 %}{% for p in entries %}{% if p.parent == entry.vxp_id %}{% assign kids = kids | plus: 1 %}{% endif %}{% endfor %}{% if kids > 0 %}主条目{% else %}主条目，无子条目{% endif %}{% endif %}</td>
    </tr>
    {%- endif %}{% endfor %}
  </tbody>
</table>
{% endfor %}

## 编写条目

条目契约、字段、章节骨架与版本规则见[模板](TEMPLATE.md)；字段表的机器可读来源是 `_data/entry_record.yml`。新增或修改条目后运行 `uv run bin/check-entries`。

项目映射记录条目状态、证据链接、责任人和复核日期；私有映射保留在项目内部。
