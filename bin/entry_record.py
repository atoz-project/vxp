"""条目记录模块：字段表、条目解析与 Catalog 派生。

interface：
    catalog = collect(Path("/path/to/repo"))
    catalog.records   # 解析成功的条目
    catalog.schema    # _data/entry_record.yml 的字段表
    catalog.findings  # 读取阶段的问题（schema、分类、front matter）

规则不在这里：bin/entry_rules.py 消费 Catalog。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

SCHEMA_PATH = Path("_data/entry_record.yml")
CATEGORIES_PATH = Path("_data/categories.yml")
ENTRY_GLOB = "VXP-*.md"
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
ID_PATTERN = re.compile(r"VXP-\d{3}(?:\.\d{3})?\Z")
VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+\Z")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
FIELD_TYPES = ("id", "text", "category", "entry_id", "version", "date")
RENDER_MODES = ("title", "meta", "level")


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path} [{self.rule}] {self.message}"


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    type: str
    required: bool
    render: str


@dataclass(frozen=True)
class Level:
    label: str
    child: str
    main: str


@dataclass(frozen=True)
class Schema:
    fields: tuple[Field, ...]
    sections: tuple[str, ...]
    level: Level

    @classmethod
    def empty(cls) -> "Schema":
        return cls((), (), Level("", "", ""))

    def field(self, key: str) -> Field | None:
        return next((field for field in self.fields if field.key == key), None)

    @property
    def keys(self) -> set[str]:
        return {field.key for field in self.fields}


@dataclass(frozen=True)
class Category:
    letter: str
    name: str
    slug: str


@dataclass(frozen=True)
class Record:
    path: Path
    fields: dict
    body: str

    @property
    def id(self) -> str:
        return str(self.fields.get("vxp_id", "")).strip()

    @property
    def is_child(self) -> bool:
        return "." in self.id

    def value(self, key: str) -> str:
        raw = self.fields.get(key)
        return "" if raw is None else str(raw).strip()


@dataclass(frozen=True)
class Catalog:
    root: Path
    schema: Schema
    categories: tuple[Category, ...]
    records: tuple[Record, ...]
    findings: tuple[Finding, ...]

    @property
    def letters(self) -> list[str]:
        return [category.letter for category in self.categories]

    def relative(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.root))


def collect(root: Path) -> Catalog:
    root = root.resolve()
    findings: list[Finding] = []
    schema = load_schema(root, findings)
    categories = load_categories(root, findings)
    records = [
        record
        for path in sorted(root.glob(ENTRY_GLOB))
        if (record := parse_record(root, path, findings)) is not None
    ]
    return Catalog(root, schema, tuple(categories), tuple(records), tuple(findings))


def load_schema(root: Path, findings: list[Finding]) -> Schema:
    path = root / SCHEMA_PATH
    text = read_text(root, path, "schema", "字段表文件不存在", findings)
    if text is None:
        return Schema.empty()
    data = read_yaml(root, path, text, "schema", findings)
    if not isinstance(data, dict):
        if data is not None:
            add(root, findings, path, "schema", "内容必须是映射")
        return Schema.empty()

    raw_fields = data.get("fields")
    if not isinstance(raw_fields, list) or not raw_fields:
        add(root, findings, path, "schema", "fields 必须是非空数组")
        return Schema.empty()

    fields: list[Field] = []
    seen: set[str] = set()
    for index, item in enumerate(raw_fields, start=1):
        if not isinstance(item, dict):
            add(root, findings, path, "schema", f"第 {index} 个字段必须是映射")
            continue
        key = str(item.get("key", "")).strip()
        label = str(item.get("label", "")).strip()
        field_type = str(item.get("type", "")).strip()
        render = str(item.get("render", "meta")).strip()
        if not (key and label and field_type):
            add(root, findings, path, "schema", f"第 {index} 个字段缺少 key/label/type")
            continue
        if key in seen:
            add(root, findings, path, "schema", f"字段 {key} 重复")
        seen.add(key)
        if field_type not in FIELD_TYPES:
            add(root, findings, path, "schema", f"字段 {key} 的 type 不在 {' / '.join(FIELD_TYPES)} 中")
        if render not in RENDER_MODES:
            add(root, findings, path, "schema", f"字段 {key} 的 render 不在 {' / '.join(RENDER_MODES)} 中")
        fields.append(Field(key, label, field_type, bool(item.get("required")), render))

    sections = tuple(str(section).strip() for section in data.get("sections") or () if str(section).strip())
    if not sections:
        add(root, findings, path, "schema", "sections 必须是非空数组")

    raw_level = data.get("level") if isinstance(data.get("level"), dict) else {}
    level = Level(
        str(raw_level.get("label", "")).strip(),
        str(raw_level.get("child", "")).strip(),
        str(raw_level.get("main", "")).strip(),
    )
    if not all((level.label, level.child, level.main)):
        add(root, findings, path, "schema", "level 必须包含 label/child/main")

    if findings:
        return Schema.empty()
    return Schema(tuple(fields), sections, level)


def load_categories(root: Path, findings: list[Finding]) -> list[Category]:
    path = root / CATEGORIES_PATH
    text = read_text(root, path, "categories", "分类数据文件不存在", findings)
    if text is None:
        return []
    data = read_yaml(root, path, text, "categories", findings)
    if data is None:
        return []
    if not isinstance(data, list):
        add(root, findings, path, "categories", "顶层必须是数组")
        return []

    categories: list[Category] = []
    seen_letters: set[str] = set()
    seen_slugs: set[str] = set()
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            add(root, findings, path, "categories", f"第 {index} 项必须是映射")
            continue
        letter = str(item.get("letter", "")).strip()
        name = str(item.get("name", "")).strip()
        slug = str(item.get("slug", "")).strip()
        if not (letter and name and slug):
            add(root, findings, path, "categories", f"第 {index} 项缺少 letter/name/slug")
        if not re.fullmatch(r"[A-Z]", letter):
            add(root, findings, path, "categories", f"letter {letter!r} 不是单个大写字母")
        if letter in seen_letters:
            add(root, findings, path, "categories", f"letter {letter} 重复")
        if slug in seen_slugs:
            add(root, findings, path, "categories", f"slug {slug} 重复")
        seen_letters.add(letter)
        seen_slugs.add(slug)
        categories.append(Category(letter, name, slug))
    return categories


def parse_record(root: Path, path: Path, findings: list[Finding]) -> Record | None:
    text = read_text(root, path, "front-matter", "无法读取文件", findings)
    if text is None:
        return None
    match = FRONT_MATTER.match(text)
    if not match:
        add(root, findings, path, "front-matter", "缺少 front matter（文件必须以 --- 开头）")
        return None
    data = read_yaml(root, path, match.group(1), "front-matter", findings)
    if data is None:
        return None
    if not isinstance(data, dict):
        add(root, findings, path, "front-matter", "front matter 必须是映射")
        return None
    return Record(path.resolve(), data, match.group(2))


def read_text(root: Path, path: Path, rule: str, message: str, findings: list[Finding]) -> str | None:
    if not path.is_file():
        add(root, findings, path, rule, message)
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        add(root, findings, path, rule, f"无法读取：{error}")
        return None


def read_yaml(root: Path, path: Path, text: str, rule: str, findings: list[Finding]) -> object | None:
    try:
        return yaml.safe_load(text)
    except (yaml.YAMLError, ValueError) as error:
        add(root, findings, path, rule, f"YAML 解析失败：{error}")
        return None


def add(root: Path, findings: list[Finding], path: Path, rule: str, message: str) -> None:
    try:
        relative = str(path.resolve().relative_to(root))
    except ValueError:
        relative = str(path)
    findings.append(Finding(relative, rule, message))