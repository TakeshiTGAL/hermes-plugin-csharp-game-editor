"""The second question, rendered by Hermes v0.22.2's own chat adapters, is not cut.

Runs with the Hermes v0.22.2 source and its venv (the adapters import their platform libraries):

    HERMES_SRC=<hermes-agent v0.22.2 checkout> <v0.22.2 venv>/bin/python -m pytest tests/test_gateway_render.py

Skipped when HERMES_SRC is not set. The question goes to Hermes as an MCP elicitation; Hermes hands its message to
the platform adapter's exec-approval card (_format_exec_approval) with the elicitation schema summary as the
reason (tools/mcp_tool_sampling.py, tools/approval_prompt.py).
"""

from __future__ import annotations

import html
import os
import sys
import tempfile
import unittest

from test_bridge import B, Fake, plan_id_of, text

SRC = os.environ.get("HERMES_SRC", "")


@unittest.skipUnless(SRC and os.path.isdir(SRC), "HERMES_SRC (Hermes v0.22.2 source) is not set")
class GatewayRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, SRC)
        cls.home = tempfile.TemporaryDirectory()
        os.environ["HERMES_HOME"] = cls.home.name
        from tools.mcp_tool_sampling import _format_elicitation_schema_summary
        cls.reason = _format_elicitation_schema_summary({"type": "object", "properties": {}}, "csharp-game-editor")
        cls.adapters = {}
        from plugins.platforms.telegram.adapter import TelegramAdapter
        from plugins.platforms.slack.adapter import SlackAdapter
        from plugins.platforms.discord.adapter import DiscordAdapter
        for name, cls_ in (("telegram", TelegramAdapter), ("slack", SlackAdapter), ("discord", DiscordAdapter)):
            adapter = object.__new__(cls_)
            adapter.config = None
            cls.adapters[name] = adapter

    @classmethod
    def tearDownClass(cls):
        cls.home.cleanup()

    def question(self, steps_count: int, code: str) -> str:
        fake = Fake()
        self.addCleanup(fake.close)
        asked = []
        fake.bridge._elicit = lambda message, mid: (asked.append(message), "decline")[1]
        names = []
        for index in range(steps_count):
            name = f"Assets/Scripts/Generated/EnemyWaveController{index:02d}.cs"
            path = fake.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("class E {}\n")
            names.append(name)
        steps = [{"tool": "unity_asset", "op": "manage_asset.delete", "arguments": {"path": name}} for name in names]
        steps.append({"tool": "unity_code", "op": "execute_code.execute", "arguments": {"code": code}})
        body = text(fake.bridge.call("plan_batch", {"steps": steps}))
        held = fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        return asked[0] if asked else "", text(held)

    def rendered_whole(self, question: str) -> dict:
        out = {}
        for name, adapter in self.adapters.items():
            shown = adapter._format_exec_approval(question, self.reason, False)
            plain = html.unescape(shown) if name == "telegram" else shown
            out[name] = (all(line in plain for line in question.splitlines()), len(shown),
                         adapter._exec_approval_cmd_budget(self.reason, False))
        return out

    def test_the_largest_question_that_is_sent_shows_whole_everywhere(self):
        worst = 'File.Delete("ab"); return 1;'
        sent = 0
        for count in range(1, 40):
            question, held = self.question(count, worst)
            if not question:
                self.assertIn("confirm_risky_plan", held)
                self.assertIn("without being cut", held)
                break
            sent = count
            self.assertLessEqual(len(question), B.SECOND_CAP)
            self.assertIn('File.Delete("ab")', question)
            for name, (whole, size, budget) in self.rendered_whole(question).items():
                self.assertTrue(whole, f"{name} cut the question at {count} steps (budget {budget}, size {size})")
        self.assertGreater(sent, 3)
        print(f"\nlargest question sent: {sent} deletes + 1 code step; then confirm_risky_plan")

    def test_ampersands_are_not_cut_on_telegram_and_long_code_is_not_silently_cut(self):
        ampersands = "&" * 40
        fake = Fake()
        self.addCleanup(fake.close)
        asked = []
        fake.bridge._elicit = lambda message, mid: (asked.append(message), "decline")[1]
        steps = []
        for index in range(17):
            name = f"Assets/Scripts/{ampersands}File{index:02d}.cs"
            path = fake.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("class E {}\n")
            steps.append({"tool": "unity_asset", "op": "manage_asset.delete", "arguments": {"path": name}})
        body = text(fake.bridge.call("plan_batch", {"steps": steps}))
        held = text(fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)}))
        if asked:
            whole, size, budget = self.rendered_whole(asked[0])["telegram"]
            self.assertTrue(whole, f"telegram cut an ampersand question (budget {budget}, size {size})")
            for index in range(17):
                self.assertIn(f"{ampersands}File{index:02d}.cs", asked[0])
        else:
            self.assertIn("without being cut", held)
            self.assertIn("confirm_risky_plan", held)
        long_code = 'File.Delete("a&b"); ' * 80
        question, held = self.question(1, long_code)
        if question:
            self.assertEqual(question.count('File.Delete("a&b")'), 80)
            whole, size, budget = self.rendered_whole(question)["telegram"]
            self.assertTrue(whole, f"telegram cut the code (budget {budget}, size {size})")
        else:
            self.assertIn("without being cut", held)
            self.assertIn("confirm_risky_plan", held)
            self.assertNotIn('File.Delete("a&b")', held)

    def test_the_whole_plan_text_would_be_cut(self):
        # 0.5.0 sent the whole plan text as the question; the same plan is cut by Discord and Slack.
        fake = Fake()
        self.addCleanup(fake.close)
        steps = [{"tool": "unity_code", "op": "execute_code.execute", "arguments": {"code": "return 1;\n" * 200}}]
        body = text(fake.bridge.call("plan_batch", {"steps": steps}))
        cut = {name: whole for name, (whole, _size, _budget) in self.rendered_whole(body).items()}
        self.assertFalse(cut["discord"])
        self.assertFalse(cut["slack"])


if __name__ == "__main__":
    unittest.main()
