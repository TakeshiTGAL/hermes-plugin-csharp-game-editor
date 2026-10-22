"""Scene property names stay arguments. They are not file paths and they are not rewritten."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_bridge():
    spec = importlib.util.spec_from_file_location(
        "csharp_game_editor_bridge", ROOT / "bridge" / "csharp_game_editor_bridge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load_bridge()

SCENE_PATHS = (
    "m_LocalPosition.x", "m_LocalPosition.y", "m_LocalPosition.z",
    "m_LocalRotation.x", "m_LocalRotation.y", "m_LocalRotation.z", "m_LocalRotation.w",
    "m_Mass", "m_LinearDamping", "m_CenterOfMass", "m_Position",
)


class PropertyMatchTest(unittest.TestCase):
    def test_property_names_and_object_paths_are_not_files(self):
        self.assertFalse(hasattr(B, "_RECORD_CSHARP"))
        for prop in SCENE_PATHS:
            rewritten, problem = B.rewrite_paths({"property": prop, "name": "Enemy/Eye"})
            self.assertEqual(problem, "")
            self.assertEqual(rewritten["property"], prop)
            self.assertEqual(rewritten["name"], "Enemy/Eye")
        menu, problem = B.rewrite_paths({"menu_path": "File/Exit"})
        self.assertEqual(problem, "")
        self.assertEqual(menu["menu_path"], "File/Exit")
        self.assertIn("file/exit", B.BLOCKED_MENUS)


if __name__ == "__main__":
    unittest.main()
