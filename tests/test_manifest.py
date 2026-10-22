"""Offline checks for the package files. Standard library only."""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Words that must not appear in the published tree (split so this file does not match itself).
# Compared without case. The lower-case folder name below is compared as written, because the
# publisher's name is spelled with capitals in the author field and the license.
CASE_SENSITIVE = ("takeshi" + "tgal",)
INTERNAL = (
    "ship" + "/",
    ".har" + "ness",
    "this " + "book",
    "この" + "本",
    "関" + "門",
    "監査" + "役",
    "執行" + "部",
    "作り" + "手",
    "試験" + "台",
    "cursor-" + "agent",
    "sessions-" + "kit",
    "fixtures/" + "proj",
    "build/" + "p",
    "game" + "jam",
)


def _load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def _skill_text() -> str:
    return (ROOT / "skills" / "csharp-game-editor" / "SKILL.md").read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        raise AssertionError("skill frontmatter missing")
    return text.split("---\n", 2)[1]


class ManifestTest(unittest.TestCase):
    def test_mcp_runs_the_bridge_on_pinned_upstream(self):
        server = _load("mcp.json")["mcpServers"]["csharp-game-editor"]
        self.assertEqual(server["type"], "stdio")
        self.assertEqual(server["command"], "uvx")
        args = server["args"]
        self.assertEqual(args[-5:], ["--from", "mcpforunityserver==10.3.0", "python", "-I",
                                     "${PLUGIN_ROOT}/bridge/csharp_game_editor_bridge.py"])
        self.assertEqual(args[args.index("--exclude-newer") + 1], "2026-10-05T00:00:00Z")
        for flag in ("--isolated", "--no-config", "--no-env-file", "--no-sources", "--no-build"):
            self.assertIn(flag, args)
        self.assertEqual(server["env"], {"DISABLE_TELEMETRY": "true", "UNITY_MCP_DISABLE_TELEMETRY": "true",
                                         "FASTMCP_CHECK_FOR_UPDATES": "off", "UNITY_MCP_LOG_DIR": "${PLUGIN_DATA}/logs"})
        self.assertEqual(server["cwd"], "${PLUGIN_DATA}/work")
        self.assertTrue((ROOT / "bridge" / "csharp_game_editor_bridge.py").is_file())
        self.assertTrue((ROOT / "bridge" / "upstream_schemas.json").is_file())

    def test_plugin_trust_and_app(self):
        plugin = _load("plugin.json")
        self.assertEqual(plugin["name"], "csharp-game-editor")
        self.assertEqual(plugin["version"], "0.6.0")
        self.assertEqual(plugin["license"], "MIT")
        server = plugin["extensions"]["com.nousresearch.hermes"]["servers"]["csharp-game-editor"]
        self.assertEqual(server["trust"], "untrusted")
        self.assertEqual(list(server["app"]), ["darwin"])
        darwin = server["app"]["darwin"]
        self.assertEqual(darwin["presence"], "bundle")
        self.assertEqual(darwin["location"], ["/Applications/Unity/Hub/Editor/*/Unity.app"])
        self.assertEqual(darwin["version"]["kind"], "plist")
        # Unity's Info.plist version is "Unity version 6000.6.6f1" (and "6000.6.6f1"); Hermes compares dotted
        # numbers only, so a min_version would hide the tools on every Mac.
        self.assertEqual(server["requires"], {"app": False})
        self.assertNotIn("python_dependencies", plugin)
        project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertNotIn("mcp>=", project)
        self.assertIn("dependencies = []", project)

    def test_bridge_uses_only_the_standard_library(self):
        import ast
        import sys
        tree = ast.parse((ROOT / "bridge" / "csharp_game_editor_bridge.py").read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names.add(node.module.split(".")[0])
        if not hasattr(sys, "stdlib_module_names"):
            self.skipTest("Python 3.10+ is needed for sys.stdlib_module_names")
        stdlib = set(sys.stdlib_module_names) | {"__future__"}
        self.assertEqual(names - stdlib, set())

    def test_skill_frontmatter_and_sections(self):
        text = _skill_text()
        body = _frontmatter(text)
        self.assertNotIn("requires_toolsets", body)
        self.assertNotIn("requires_tools", body)
        desc = ""
        for line in body.splitlines():
            if line.startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip('"')
        self.assertLessEqual(len(desc), 1024)
        self.assertIn("Unity", desc[:60])
        for heading in ("## When to use", "## Search", "## Procedure", "## Approval", "## When a call fails",
                        "## Limits"):
            self.assertIn(heading, text)
        self.assertIn("Configure", text.split("## Limits", 1)[1])
        self.assertIn("tool_search", text.split("## Search", 1)[1])

    def test_skill_names_every_tool(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("b", ROOT / "bridge" / "csharp_game_editor_bridge.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        text = _skill_text()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for tool in module.T:
            self.assertIn("`" + tool["name"] + "`", text, tool["name"])
            self.assertIn("`" + tool["name"] + "`", readme, tool["name"])

    def test_public_tree_has_no_internal_words(self):
        hits = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            if path.suffix not in {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt"} and path.name != "LICENSE":
                continue
            raw = path.read_text(encoding="utf-8", errors="ignore")
            text = raw.lower()
            for word in INTERNAL:
                if word.lower() in text:
                    hits.append(path.name + ":" + word)
            for word in CASE_SENSITIVE:
                if word in raw:
                    hits.append(path.name + ":" + word)
        self.assertEqual(hits, [])

    def test_no_local_paths(self):
        hits = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if re.search("/Us" + "ers/|/private/" + "tmp|/home/[a-z]", text):
                hits.append(path.name)
        self.assertEqual(hits, [])

    def test_hermes_source_when_present(self):
        src = os.environ.get("HERMES_SRC")
        if not src:
            self.skipTest("HERMES_SRC is not set")
        agent = Path(src) / "hermes_cli" / "agent_plugins.py"
        if not agent.is_file():
            self.skipTest("agent_plugins.py is not in HERMES_SRC")
        text = agent.read_text(encoding="utf-8", errors="replace")
        self.assertIn("_server_trust", text)
        self.assertIn("untrusted", text)


if __name__ == "__main__":
    unittest.main()


class SourceTextTest(unittest.TestCase):
    def test_no_hidden_characters_in_the_plugin_files(self):
        """Hermes' install scan blocks a community plugin whose files carry bidi or zero-width characters (0.6.0's
        first build did, in a regex literal). Escapes in source are fine; the raw characters are not."""
        root = Path(__file__).resolve().parents[1]
        hidden = set(range(0x200B, 0x2010)) | set(range(0x2028, 0x202F)) | set(range(0x2060, 0x2070)) \
            | {0x061C, 0xFEFF} | set(range(0x80, 0xA0))
        found = []
        for path in root.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or ".pytest_cache" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            found += [f"{path.relative_to(root)}:{hex(ord(ch))}" for ch in text if ord(ch) in hidden]
        self.assertEqual(found, [])
