from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("asset_links", ROOT / "scripts/validate_asset_links.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class AssetLineageTests(unittest.TestCase):
    def test_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ref.md").write_text("ref", encoding="utf-8")
            (root / "frame.png").write_bytes(b"image")
            manifest = {"assets": [
                {"id": "base", "designRef": "ref.md"},
                {"id": "walk", "derivedFrom": ["base"], "runtimeEvidence": [{"path": "frame.png"}]},
            ]}
            self.assertEqual(mod.validate(manifest, root), [])

    def test_duplicate_cycle_and_invalid_reference(self):
        with tempfile.TemporaryDirectory() as td:
            manifest = {"assets": [
                {"id": "a", "derivedFrom": ["b"], "designRef": "missing.md"},
                {"id": "b", "derivedFrom": ["a"]},
                {"id": "b", "derivedFrom": ["a"]},
            ]}
            errors = mod.validate(manifest, Path(td))
            self.assertTrue(any("duplicate" in x for x in errors))
            self.assertTrue(any("cycle" in x for x in errors))
            self.assertTrue(any("designRef" in x for x in errors))

    def test_reject_malformed_and_path_escape(self):
        with tempfile.TemporaryDirectory() as td:
            errors = mod.validate({"assets": [{"id": "x", "derivedFrom": [1], "runtimeEvidence": [{"path": "../invalid.png"}]}]}, Path(td))
            self.assertTrue(any("derivedFrom" in x for x in errors))
            self.assertTrue(any("traversal" in x for x in errors))

if __name__ == "__main__":
    unittest.main()
