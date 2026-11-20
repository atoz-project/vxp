import unittest

from support import entry, filename, repo

from vxp_check import collect


class CollectTests(unittest.TestCase):
    def test_valid_repo_has_no_findings(self):
        with repo() as root:
            catalog = collect(root)
        self.assertEqual(catalog.findings, ())
        self.assertEqual(len(catalog.records), 1)
        self.assertEqual(catalog.letters, ["A", "B", "C", "D", "E", "F"])

    def test_schema_comes_from_data_file(self):
        with repo() as root:
            catalog = collect(root)
        self.assertEqual([field.key for field in catalog.schema.fields][:3], ["vxp_id", "title", "category"])
        self.assertEqual(catalog.schema.sections[0], "定义")
        self.assertEqual(catalog.schema.level.child, "子条目")
        self.assertEqual(catalog.schema.field("parent").required, False)

    def test_missing_schema_reports_finding(self):
        with repo(include_schema=False) as root:
            catalog = collect(root)
        self.assertEqual([finding.rule for finding in catalog.findings], ["schema"])

    def test_invalid_schema_reports_finding(self):
        with repo(schema="fields:\n  - key: vxp_id\n    label: 编号\n    type: nope\n") as root:
            catalog = collect(root)
        self.assertIn("schema", [finding.rule for finding in catalog.findings])
        self.assertEqual(catalog.schema.fields, ())

    def test_missing_front_matter_reports_finding(self):
        with repo({filename(): "# 没有 front matter\n"}) as root:
            catalog = collect(root)
        self.assertIn("front-matter", [finding.rule for finding in catalog.findings])
        self.assertEqual(catalog.records, ())

    def test_missing_entry_dir_reports_finding(self):
        with repo() as root:
            for path in (root / "entries").iterdir():
                path.unlink()
            (root / "entries").rmdir()
            catalog = collect(root)
        self.assertEqual([finding.rule for finding in catalog.findings], ["entries"])
        self.assertEqual(catalog.records, ())

    def test_child_record_is_derived_from_id(self):
        with repo({filename("VXP-001.001"): entry(id="VXP-001.001", parent="VXP-001")}) as root:
            catalog = collect(root)
        self.assertTrue(catalog.records[0].is_child)
        self.assertEqual(catalog.records[0].value("parent"), "VXP-001")

    def test_duplicate_category_letter_reports_finding(self):
        categories = "- letter: A\n  name: 甲\n  slug: a\n- letter: A\n  name: 乙\n  slug: b\n"
        with repo(categories=categories) as root:
            catalog = collect(root)
        self.assertIn("categories", [finding.rule for finding in catalog.findings])


if __name__ == "__main__":
    unittest.main()