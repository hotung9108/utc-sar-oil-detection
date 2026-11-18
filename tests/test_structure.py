"""Acceptance checks for the dataset-first repository migration."""

import ast
import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StructureTests(unittest.TestCase):
    def test_no_active_legacy_imports(self):
        active = list((ROOT / "src").rglob("*.py"))
        active += list((ROOT / "scripts").rglob("*.py"))
        active += [ROOT / "streamlit_app.py"]
        for path in active:
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    names = [item.name for item in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                self.assertFalse(any(n.startswith(("legacy", "src.tv")) for n in names))

    def test_schedule_dependencies_and_owners(self):
        tasks = json.loads(
            (ROOT / "docs/management/refactor_tasks.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(tasks), 15)
        by_id = {t["id"]: t for t in tasks}
        self.assertEqual(len(by_id), 15)
        for t in tasks:
            self.assertIn(t["day"], ["2026-11-13", "2026-11-14", "2026-11-15"])
            self.assertNotEqual(t["name"], t["reviewer"])
            if t["dependency"] != "Không":
                self.assertLess(by_id[t["dependency"]]["day"], t["day"])
        for i in range(1, 6):
            self.assertEqual(sum(t["owner"] == f"TV{i}" for t in tasks), 3)

    def test_archive_is_excluded_from_test_discovery(self):
        config = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertEqual(config["tool"]["pytest"]["ini_options"]["testpaths"], ["tests"])
        self.assertIn("legacy", config["tool"]["ruff"]["extend-exclude"])
        self.assertFalse((ROOT / "app.py").exists())
        self.assertIn("legacy", config["tool"]["pytest"]["ini_options"]["norecursedirs"])

    def test_sos_assignment_owners_and_dependencies(self):
        tasks = json.loads((ROOT / "docs/management/sos_tasks.json").read_text(encoding="utf-8"))
        by_id = {t["id"]: t for t in tasks}
        self.assertEqual(len(by_id), 15)
        for task in tasks:
            self.assertNotEqual(task["name"], task["reviewer"])
            if task["dependency"] != "Không":
                self.assertLess(by_id[task["dependency"]]["day"], task["day"])
        for i in range(1, 6):
            self.assertEqual(sum(t["owner"] == f"TV{i}" for t in tasks), 3)


if __name__ == "__main__":
    unittest.main()
