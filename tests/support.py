"""测试夹具：临时仓库、条目文本与 schema 副本。"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

REPO = Path(__file__).resolve().parents[1]

DATA = REPO / "_data"

BODY = """## 定义

把甲误认为乙。

## 示例

示例。

## 识别方法

- 检查一。

## 预防与验收要求

- 必须一。

## 验收证据与量化字段

| 字段 | 含义 | 单位/取值 |
|---|---|---|
| `example_field` | 示例 | 计数 |

## 边界与关联

无子条目。

## 参考来源

本项目约定。
"""


def entry(
    id: str = "VXP-001",
    title: str = "测试条目",
    category: str = "A",
    parent: str | None = None,
    status: str = "草案",
    version: str = "0.1.0",
    created: str = "2026-11-01",
    updated: str = "2026-11-01",
    body: str | None = None,
    extra: str = "",
    omit: tuple[str, ...] = (),
) -> str:
    fields = [
        ("vxp_id", id),
        ("title", f"'{title}'"),
        ("category", category),
        ("parent", parent),
        ("status", status),
        ("version", version),
        ("created", created),
        ("updated", updated),
    ]
    lines = [f"{key}: {value}" for key, value in fields if key not in omit and value is not None]
    if extra:
        lines.append(extra)
    return "---\n" + "\n".join(lines) + "\n---\n" + (BODY if body is None else body)


def filename(id: str = "VXP-001", slug: str = "测试条目") -> str:
    return f"{id}-{slug}.md"


@contextmanager
def repo(
    entries: dict[str, str] | None = None,
    *,
    schema: str | None = None,
    categories: str | None = None,
    include_schema: bool = True,
    include_categories: bool = True,
):
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        data = root / "_data"
        data.mkdir()
        if include_schema:
            (data / "entry_record.yml").write_text(
                schema if schema is not None else (DATA / "entry_record.yml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        if include_categories:
            (data / "categories.yml").write_text(
                categories if categories is not None else (DATA / "categories.yml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        entry_dir = root / "entries"
        entry_dir.mkdir()
        for name, text in (entries or {filename(): entry()}).items():
            (entry_dir / name).write_text(text, encoding="utf-8")
        yield root