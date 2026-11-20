"""VXP 条目记录模块：字段表读取、条目解析、Catalog 派生与规则检查。

interface：
    catalog = collect(Path("/path/to/repo"))
    findings = check(catalog)
    not findings  # => 所有条目满足约定

CLI 在 bin/check-entries，消费同一接口。
"""

from .entry_record import Catalog, Finding, collect
from .entry_rules import check

__all__ = ["Catalog", "Finding", "check", "collect"]