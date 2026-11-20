"""条目记录的检查规则：每条规则消费 Catalog，返回 Finding。

规则按对象分组，互不读取可变状态：
    check_fields / check_body / check_parents / check_uniqueness

interface：
    findings = check(collect(Path("/path/to/repo")))
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from entry_record import (
    DATE_PATTERN,
    ID_PATTERN,
    VERSION_PATTERN,
    Catalog,
    Field,
    Finding,
    Record,
)

HEADING = re.compile(r"## (.+)\Z")


def check(catalog: Catalog) -> list[Finding]:
    if not catalog.schema.fields:
        return []
    findings: list[Finding] = []
    for rule in (check_fields, check_body, check_parents, check_uniqueness):
        findings.extend(rule(catalog))
    return sorted(findings, key=lambda finding: (finding.path, finding.rule, finding.message))


def check_fields(catalog: Catalog) -> list[Finding]:
    findings: list[Finding] = []
    for record in catalog.records:
        dates: dict[str, date] = {}
        for field in catalog.schema.fields:
            raw = record.fields.get(field.key)
            text = record.value(field.key)
            if not text:
                if field.required:
                    findings.append(Finding(catalog.relative(record.path), f"field:{field.key}", "缺少必填字段"))
                continue
            parsed = check_type(catalog, record, field, raw, findings)
            if parsed is not None:
                dates[field.key] = parsed

        unknown = sorted(set(record.fields) - catalog.schema.keys)
        if unknown:
            findings.append(
                Finding(catalog.relative(record.path), "field:unknown", f"字段 {', '.join(unknown)} 不在条目记录字段表中")
            )

        check_filename(catalog, record, findings)
        check_title(catalog, record, findings)

        created, updated = dates.get("created"), dates.get("updated")
        if created and updated and updated < created:
            findings.append(Finding(catalog.relative(record.path), "field:updated", "修改日期早于创建日期"))
    return findings


def check_type(
    catalog: Catalog,
    record: Record,
    field: Field,
    raw: object,
    findings: list[Finding],
) -> date | None:
    path = catalog.relative(record.path)
    text = record.value(field.key)

    if field.type == "date":
        parsed = as_date(raw)
        if parsed is None:
            message = "日期格式应为 YYYY-MM-DD"
            if isinstance(raw, str) and DATE_PATTERN.fullmatch(text):
                message = f"日期 {text!r} 无法解析"
            findings.append(Finding(path, f"field:{field.key}", message))
        return parsed

    if field.type == "id" and not ID_PATTERN.fullmatch(text):
        findings.append(Finding(path, f"field:{field.key}", "编号格式应为 VXP-NNN 或 VXP-NNN.MMM"))
    elif field.type == "entry_id" and not ID_PATTERN.fullmatch(text):
        findings.append(Finding(path, f"field:{field.key}", "父条目编号格式应为 VXP-NNN"))
    elif field.type == "version" and not VERSION_PATTERN.fullmatch(text):
        findings.append(Finding(path, f"field:{field.key}", "版本格式应为 MAJOR.MINOR.PATCH"))
    elif field.type == "category" and text not in catalog.letters:
        allowed = ", ".join(catalog.letters)
        findings.append(Finding(path, f"field:{field.key}", f"分类 {text!r} 不在 {allowed} 中"))
    return None


def check_filename(catalog: Catalog, record: Record, findings: list[Finding]) -> None:
    path = catalog.relative(record.path)
    match = re.match(r"VXP-\d{3}(?:\.\d{3})?", record.path.name)
    if match is None:
        findings.append(Finding(path, "filename", "文件名必须以 VXP-NNN 或 VXP-NNN.MMM 开头"))
        return
    if record.id != match.group(0):
        findings.append(Finding(path, "field:vxp_id", f"vxp_id {record.id!r} 与文件名 {match.group(0)} 不一致"))


def check_title(catalog: Catalog, record: Record, findings: list[Finding]) -> None:
    title = record.value("title")
    if re.match(r"VXP-\d", title):
        findings.append(Finding(catalog.relative(record.path), "field:title", "标题不应重复编号"))
    if "\n" in title:
        findings.append(Finding(catalog.relative(record.path), "field:title", "标题不应包含换行"))


def check_body(catalog: Catalog) -> list[Finding]:
    findings: list[Finding] = []
    sections = list(catalog.schema.sections)
    metadata_labels = [field.label for field in catalog.schema.fields if field.render == "meta"]
    metadata_labels.append(catalog.schema.level.label)

    for record in catalog.records:
        path = catalog.relative(record.path)
        body = record.body
        if not body.lstrip().startswith("## 定义"):
            findings.append(Finding(path, "body:start", "正文必须从「## 定义」开始"))

        found: list[str] = []
        for line in outside_fences(body):
            if line.startswith("# "):
                findings.append(Finding(path, "body:h1", "正文不应包含 H1；标题由条目记录生成"))
            if any(line.startswith(f"- {label}：") for label in metadata_labels):
                findings.append(Finding(path, "body:metadata", "元数据已移入 front matter，正文不应重复"))
            heading = HEADING.fullmatch(line)
            if heading:
                found.append(heading.group(1))

        missing = [section for section in sections if section not in found]
        extra = [section for section in found if section not in sections]
        if missing or extra:
            parts = []
            if missing:
                parts.append(f"缺少 {'、'.join(missing)}")
            if extra:
                parts.append(f"多出 {'、'.join(extra)}")
            findings.append(Finding(path, "body:sections", "；".join(parts)))
        elif found != sections:
            findings.append(Finding(path, "body:sections", f"章节顺序应为 {' / '.join(sections)}"))
    return findings


def check_parents(catalog: Catalog) -> list[Finding]:
    findings: list[Finding] = []
    by_id = {record.id: record for record in catalog.records if record.id}

    for record in catalog.records:
        path = catalog.relative(record.path)
        parent = record.value("parent")

        if record.is_child:
            if not parent:
                findings.append(Finding(path, "parent:missing", "子条目必须填写 parent"))
                continue
            parent_record = by_id.get(parent)
            if parent_record is None:
                findings.append(Finding(path, "parent:unknown", f"父条目 {parent} 不存在"))
                continue
            if "." in parent:
                findings.append(Finding(path, "parent:not-main", f"父条目 {parent} 自身是子条目"))
            expected = record.id.split(".")[0]
            if parent != expected:
                findings.append(Finding(path, "parent:mismatch", f"parent 应为 {expected}，实际为 {parent}"))
            if record.value("category") != parent_record.value("category"):
                findings.append(Finding(path, "parent:category", "子条目的分类必须与父条目一致"))
        elif parent:
            findings.append(Finding(path, "parent:unexpected", "主条目不应填写 parent"))
    return findings


def check_uniqueness(catalog: Catalog) -> list[Finding]:
    findings: list[Finding] = []
    ids: dict[str, Path] = {}
    titles: dict[str, Path] = {}

    for record in catalog.records:
        if record.id:
            if record.id in ids:
                findings.append(
                    Finding(
                        catalog.relative(record.path),
                        "unique:id",
                        f"编号 {record.id} 与 {catalog.relative(ids[record.id])} 重复",
                    )
                )
            else:
                ids[record.id] = record.path

        title = record.value("title")
        if not title:
            continue
        if title in titles:
            findings.append(
                Finding(
                    catalog.relative(record.path),
                    "unique:title",
                    f"标题 {title!r} 与 {catalog.relative(titles[title])} 重复",
                )
            )
        else:
            titles[title] = record.path
    return findings


def outside_fences(body: str):
    in_fence = False
    for line in body.splitlines():
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line


def as_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and DATE_PATTERN.fullmatch(value.strip()):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None