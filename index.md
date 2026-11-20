---
layout: default
title: 漏洞验证指南 Wiki
description: VXP（Vulnerability Validation Guide）记录漏洞研究、验证和交付中常见的证据误判。
permalink: /
---

# VXP：漏洞验证指南 Wiki

VXP（Vulnerability Validation Guide）记录漏洞研究、验证和交付中常见的证据误判。分类用于导航，条目用于判断；它不是漏洞类型目录，也不替代具体项目的技术验收。

{%- assign entries = site.pages | where_exp: "p", "p.vxp_id" | sort: "vxp_id" %}
{%- assign main_count = 0 %}
{%- assign child_count = 0 %}
{%- for p in entries %}
  {%- if p.parent %}{% assign child_count = child_count | plus: 1 %}
  {%- else %}{% assign main_count = main_count | plus: 1 %}{% endif %}
{%- endfor %}

<p class="catalog-summary"><span>{{ entries.size }} 个条目</span><span>{{ main_count }} 个主条目 / {{ child_count }} 个子条目</span><span>{{ site.data.categories.size }} 个分类</span></p>

<div class="catalog-tools" data-catalog-tools hidden>
  <label class="visually-hidden" for="catalog-search">搜索条目</label>
  <div class="search-box">
    <svg class="search-icon" width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" stroke-width="1.6"/>
      <path d="m12.6 12.6 4.1 4.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    </svg>
    <input id="catalog-search" type="search" data-catalog-search placeholder="搜索编号、标题或关键词" autocomplete="off" spellcheck="false">
    <kbd aria-hidden="true">/</kbd>
  </div>
  <p class="search-status" data-search-status role="status" aria-live="polite">共 {{ entries.size }} 个条目</p>
</div>

## 结构与使用原则

- **分类（A～F）**：表示失效模式发生的活动，不表示严重程度。
- **主条目（`VXP-NNN`）**：描述一种可独立判断的失效模式。
- **子条目（`VXP-NNN.MMM`）**：仅在存在独立场景、判据或证据要求时设置。
- **原子条目**：没有子条目，直接给出完整检查方法。
- **稳定编号**：已发布的 ID 不复用。重大定义变化时新增条目，并在原条目中说明关系。
- **项目约定**：次数、比例、容差和时限由具体项目确定，不在通用条目中设置统一阈值。

阅读条目时使用统一[模板](TEMPLATE.md)和[术语表](GLOSSARY.md)。参考来源用于支撑技术事实；“必须”“应当”等验收措辞若属于本项目约定，会在条目中明确标注。

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

## 维护规则

1. 新增条目前先检查是否属于现有条目的示例；只有新增独立判据或证据要求时才拆分。
2. 子条目继承父条目的共同规则，正文只写新增内容；父条目保留导航和共同边界。
3. 删除或合并条目时保留旧 ID 的重定向说明，不静默复用编号。
4. 每个事实性技术结论应有可访问的一手来源；无法核验的内容标为未验证。
5. 项目映射应记录条目状态、证据链接、责任人和复核日期。具体项目的私有映射不纳入公开 Wiki。

## 条目元数据与版本

- **条目版本**：采用 `主版本号.次版本号.修订号`，初始公开草案为 `0.1.0`。
- **创建日期**：条目首次建立的日期，发布后不再修改。
- **修改日期**：条目正文、判据、字段或来源发生实质修改的日期；批量修改时必须同步更新。
- **参考来源查询日期**：保留在每条来源后，表示在线资料的访问时间；不得用条目修改日期替代。
- **修订号（PATCH）**：文字、格式或来源说明修正，不改变判据。
- **次版本号（MINOR）**：增加向后兼容的示例、检查方法、量化字段或子条目。
- **主版本号（MAJOR）**：在不改变条目范围的前提下调整判据或字段语义；若失效模式的范围发生根本变化，应新增 ID，而不是覆盖原条目。