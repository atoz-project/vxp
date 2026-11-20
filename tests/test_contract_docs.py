import re
import unittest

import yaml

from support import REPO

from entry_record import collect


class ContractDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = collect(REPO).schema
        cls.template = (REPO / "TEMPLATE.md").read_text(encoding="utf-8")

    def test_front_matter_sample_covers_every_field(self):
        block = re.search(r"```yaml\n(.*?)```", self.template, re.S)
        self.assertIsNotNone(block)
        sample = "\n".join(line for line in block.group(1).splitlines() if line.strip() != "---")
        self.assertEqual(set(yaml.safe_load(sample)), self.schema.keys)

    def test_field_table_covers_every_field(self):
        lines = self.template.splitlines()
        start = lines.index("| 字段 | 标签 | 必填 | 类型 |") + 2
        rows = {}
        for line in lines[start:]:
            if not line.startswith("| `"):
                break
            cells = line.split("|")
            rows[cells[1].strip().strip("`")] = cells[2].strip()
        self.assertEqual(set(rows), self.schema.keys)
        for field in self.schema.fields:
            self.assertEqual(rows[field.key], field.label)

    def test_section_headings_follow_schema_order(self):
        positions = [self.template.index(f"## {section}") for section in self.schema.sections]
        self.assertEqual(positions, sorted(positions))

    def test_index_links_to_the_contract(self):
        index = (REPO / "index.md").read_text(encoding="utf-8")
        self.assertIn("[模板](TEMPLATE.md)", index)
        self.assertNotIn("## 条目元数据与版本", index)
        self.assertNotIn("## 维护规则", index)


if __name__ == "__main__":
    unittest.main()