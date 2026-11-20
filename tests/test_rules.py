import unittest

from support import BODY, entry, filename, repo

from entry_record import collect
from entry_rules import check


def findings_for(entries=None, **kwargs):
    with repo(entries, **kwargs) as root:
        return check(collect(root))


def rules_for(entries=None, **kwargs):
    return [finding.rule for finding in findings_for(entries, **kwargs)]


class FieldRuleTests(unittest.TestCase):
    def test_missing_required_field(self):
        self.assertIn("field:version", rules_for({filename(): entry(omit=("version",))}))

    def test_unknown_field(self):
        self.assertIn("field:unknown", rules_for({filename(): entry(extra="categroy: A")}))

    def test_invalid_version(self):
        self.assertIn("field:version", rules_for({filename(): entry(version="1.0")}))

    def test_invalid_date_format(self):
        self.assertIn("field:created", rules_for({filename(): entry(created="2026/11/01")}))

    def test_unparseable_date(self):
        findings = findings_for({filename(): entry(created='"2026-13-01"')})
        self.assertEqual([(f.rule, f.message) for f in findings], [("field:created", "日期 '2026-13-01' 无法解析")])

    def test_updated_before_created(self):
        self.assertIn("field:updated", rules_for({filename(): entry(created="2026-11-02")}))

    def test_category_not_allowed(self):
        self.assertIn("field:category", rules_for({filename(): entry(category="Z")}))

    def test_vxp_id_must_match_filename(self):
        self.assertIn("field:vxp_id", rules_for({"VXP-002-测试条目.md": entry(id="VXP-001")}))

    def test_title_must_not_repeat_id(self):
        self.assertIn("field:title", rules_for({filename(): entry(title="VXP-001 测试")}))


class BodyRuleTests(unittest.TestCase):
    def test_missing_section(self):
        body = BODY.replace("## 参考来源\n\n本项目约定。\n", "")
        self.assertIn("body:sections", rules_for({filename(): entry(body=body)}))

    def test_wrong_section_order(self):
        body = BODY.replace("## 示例\n\n示例。\n", "").replace(
            "## 识别方法\n\n- 检查一。\n", "## 识别方法\n\n- 检查一。\n\n## 示例\n\n示例。\n"
        )
        findings = findings_for({filename(): entry(body=body)})
        self.assertEqual([f.rule for f in findings], ["body:sections"])

    def test_h1_in_body(self):
        self.assertIn("body:h1", rules_for({filename(): entry(body="# 标题\n\n" + BODY)}))

    def test_metadata_in_body(self):
        body = BODY.replace("把甲误认为乙。", "- 状态：草案\n\n把甲误认为乙。")
        self.assertIn("body:metadata", rules_for({filename(): entry(body=body)}))

    def test_parent_link_in_body_is_allowed(self):
        body = BODY.replace("无子条目。", "- 父条目：[VXP-001](VXP-001-测试条目.md)")
        self.assertEqual(rules_for({filename(): entry(body=body)}), [])


class ParentRuleTests(unittest.TestCase):
    def test_child_requires_parent(self):
        child = {filename("VXP-001.001"): entry(id="VXP-001.001")}
        self.assertIn("parent:missing", rules_for(child))

    def test_unknown_parent(self):
        child = {filename("VXP-001.001"): entry(id="VXP-001.001", parent="VXP-999")}
        self.assertIn("parent:unknown", rules_for(child))

    def test_parent_must_be_main(self):
        entries = {
            filename("VXP-001"): entry(),
            filename("VXP-001.001"): entry(id="VXP-001.001", parent="VXP-001", title="子一"),
            filename("VXP-001.002"): entry(id="VXP-001.002", parent="VXP-001.001", title="子二"),
        }
        self.assertIn("parent:not-main", rules_for(entries))

    def test_parent_must_match_id_prefix(self):
        entries = {
            filename("VXP-001"): entry(),
            filename("VXP-002"): entry(id="VXP-002", title="另一条"),
            filename("VXP-001.001"): entry(id="VXP-001.001", parent="VXP-002", title="子一"),
        }
        self.assertIn("parent:mismatch", rules_for(entries))

    def test_child_category_must_match_parent(self):
        entries = {
            filename("VXP-001"): entry(),
            filename("VXP-001.001"): entry(id="VXP-001.001", parent="VXP-001", category="B", title="子一"),
        }
        self.assertIn("parent:category", rules_for(entries))

    def test_main_must_not_have_parent(self):
        entries = {
            filename("VXP-001"): entry(),
            filename("VXP-002"): entry(id="VXP-002", parent="VXP-001", title="另一条"),
        }
        self.assertIn("parent:unexpected", rules_for(entries))

    def test_valid_child_has_no_findings(self):
        entries = {
            filename("VXP-001"): entry(),
            filename("VXP-001.001"): entry(id="VXP-001.001", parent="VXP-001", title="子一"),
        }
        self.assertEqual(rules_for(entries), [])


class UniquenessRuleTests(unittest.TestCase):
    def test_duplicate_id(self):
        entries = {
            "VXP-001-甲.md": entry(title="甲"),
            "VXP-001-乙.md": entry(title="乙"),
        }
        self.assertIn("unique:id", rules_for(entries))

    def test_duplicate_title(self):
        entries = {
            filename("VXP-001"): entry(title="同题"),
            filename("VXP-002"): entry(id="VXP-002", title="同题"),
        }
        self.assertIn("unique:title", rules_for(entries))


if __name__ == "__main__":
    unittest.main()