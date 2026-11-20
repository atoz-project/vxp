"""CLI 适配器：把 Catalog 与规则结果渲染成终端输出与退出码。

interface：
    exit_code = main(["--root", "/path/to/repo"])

退出码：0 无问题，1 有问题，2 用法错误（argparse）。
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .entry_record import collect
from .entry_rules import check


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check-entries", description="检查 VXP 条目记录")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="仓库根目录",
    )
    args = parser.parse_args(argv)

    catalog = collect(args.root)
    findings = sorted(
        [*catalog.findings, *check(catalog)],
        key=lambda finding: (finding.path, finding.rule, finding.message),
    )
    if not findings:
        print(f"检查 {len(catalog.records)} 个条目：0 条问题")
        return 0

    for finding in findings:
        print(f"✗ {finding}")
    print(f"检查 {len(catalog.records)} 个条目：{len(findings)} 条问题")
    return 1