"""Offline checks for the twenty-tool bridge. No network and no Unity editor."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAKE = Path(__file__).resolve().parent / "fake_upstream.py"
BRIDGE_PATH = ROOT / "bridge" / "csharp_game_editor_bridge.py"


def load_bridge():
    spec = importlib.util.spec_from_file_location("csharp_game_editor_bridge", BRIDGE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load_bridge()


class Fake:
    def __init__(self, mode: str = "normal", project: bool = True):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.calls = base / "calls.jsonl"
        self.root = base / "proj"
        (self.root / "Assets" / "Scripts").mkdir(parents=True)
        (self.root / "Assets" / "Scenes").mkdir(parents=True)
        (self.root / "Assets" / "Scripts" / "Player.cs").write_text("class Player {}\n")
        (self.root / "Assets" / "Scenes" / "Main.unity").write_text("scene v1\n")
        env = dict(os.environ)
        env.pop("FAKE_PROJECT_PATH", None)
        if project:
            env["FAKE_PROJECT_PATH"] = str(self.root)
        self.bridge = B.Bridge(argv=[sys.executable, "-I", str(FAKE), str(self.calls), mode], env=env)

    def sent(self, method: str = "tools/call") -> list[dict]:
        if not self.calls.exists():
            return []
        rows = [json.loads(line) for line in self.calls.read_text().splitlines() if line.strip()]
        return [row for row in rows if row["method"] == method]

    def sent_names(self) -> list[str]:
        return [row["name"] for row in self.sent()]

    def close(self):
        self.bridge.shutdown()
        self.tmp.cleanup()


def text(res: dict) -> str:
    return "\n".join(item.get("text", "") for item in res["content"])


def plan_id_of(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("plan_id: "):
            return line.split(": ", 1)[1].strip()
    raise AssertionError("no plan_id in " + body[:240])


def first_sentence(body: str) -> str:
    head = body.split(". ", 1)[0]
    return head if body.startswith(head + ".") and ". " not in head else head + "."


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()
        self.addCleanup(self.fake.close)
        self.asked = []
        self.answer = "accept"
        self.fake.bridge._elicit = self._elicit

    def _elicit(self, message, mid):
        self.asked.append(message)
        return self.answer

    def plan(self, steps, fake=None):
        result = (fake or self.fake).bridge.call("plan_batch", {"steps": steps})
        self.assertFalse(result["isError"], text(result))
        self.assertIn("plan_id: ", text(result), text(result))
        return text(result)

    def changes_sent(self, fake=None) -> list[dict]:
        reads = {"get_loaded_scenes", "get_hierarchy", "get_history"}
        return [row for row in (fake or self.fake).sent()
                if row["name"] not in ("set_active_instance", "read_console", "refresh_unity")
                and not (row["name"] == "execute_code" and "sha256:" in (row["arguments"] or {}).get("code", ""))
                and (row["arguments"] or {}).get("action") not in reads]

    def test_surface_hints_are_honest(self):
        self.assertEqual([tool["name"] for tool in B.T], list(B.TOOL_ORDER))
        self.assertEqual(len(B.T), 22)
        for tool in B.T:
            sentence = first_sentence(tool["description"])
            self.assertLessEqual(len(sentence), 60, tool["name"])
            self.assertFalse(sentence.startswith("Read-only."))
            self.assertLessEqual(len(tool["description"]), 1024)
            hints = tool["annotations"]
            self.assertLessEqual(len(json.dumps(tool, ensure_ascii=False)), B.TOOL_BUDGET, tool["name"])
            if tool["name"] in ("apply_plan", "confirm_risky_plan"):
                self.assertIs(hints["readOnlyHint"], False)
                self.assertIs(hints["destructiveHint"], True)
                self.assertIn("second question", tool["description"])
            elif tool["name"] == "unity_docs":
                # every docs op sends the query to docs.unity3d.com: Hermes asks before each call
                self.assertIs(hints["readOnlyHint"], False)
                self.assertIn("docs.unity3d.com", tool["description"])
            else:
                self.assertIs(hints["readOnlyHint"], True)
                self.assertIs(hints["destructiveHint"], False)
        enums = []
        for tool in B.T:
            if tool["name"] in B.PLAN_TOOLS:
                continue
            enums.extend(op for op in tool["inputSchema"]["properties"]["op"]["enum"] if op != "describe")
        self.assertEqual(len(enums), len(set(enums)))
        self.assertNotIn("apply_text_edits.read", enums)
        self.assertNotIn("script_apply_edits.get_sha", enums)
        for op in B.READ_ALLOW:
            self.assertIn(op, enums + ["describe"])
            for (_bundle, key), spec in B.OPS.items():
                if key != op:
                    continue
                # A listed read reaches no save, delete, write, compile, load, play, or send in upstream's code
                # (the side effect table), except reflection into Unity's own internals. Docs reads send.
                sites = {(row["kind"], row["at"]) for row in spec.get("effects") or []}
                if op.startswith("unity_docs."):
                    self.assertEqual({kind for kind, _at in sites}, {"send"}, op)
                    continue
                for kind, at in sites:
                    self.assertEqual(kind, "reflection", (op, kind, at))
                    self.assertIn(at, B.UNITY_OWN_REFLECTION, (op, at))
        self.assertNotIn("mcpforunity://scene/gameobject/{instance_id}/components", B.READ_ALLOW)
        self.assertNotIn("manage_packages.list_packages", B.READ_ALLOW)
        for op in ("asset_find", "describe", "prefab_info", "read_text", "set_active_instance"):
            self.assertIn(op, B.READ_ALLOW)
        for op in ("validate_script", "unity_docs.lookup", "execute_code.get_history", "component_values",
                   "manage_scene.get_hierarchy"):
            self.assertNotIn(op, B.READ_ALLOW)

    def test_schema_names_each_argument_with_upstream_type_and_text(self):
        obj = B.TOOLS_BY_NAME["unity_object"]["inputSchema"]["properties"]
        args = obj["arguments"]["properties"]
        self.assertIn("search_method", args)
        self.assertEqual(args["search_method"].get("type"), "string")
        script = B.TOOLS_BY_NAME["unity_script"]["inputSchema"]["properties"]
        self.assertIn("overwrite", script["arguments"]["properties"])
        self.assertIn("describe", obj["op"]["enum"])
        # the whole upstream text of one op, and what it does inside, come back from describe (a read)
        full = text(self.fake.bridge.call("unity_object", {"op": "describe",
                                                           "arguments": {"op": "manage_gameobject.create"}}))
        self.assertIn("Performs CRUD operations on GameObjects", full)
        self.assertIn("prefab_path", full)
        self.assertIn("instantiate: PrefabUtility.InstantiatePrefab", full)
        self.assertIn("[only with not save_as_prefab, prefab_path]", full)
        edits = text(self.fake.bridge.call("unity_script", {"op": "describe",
                                                            "arguments": {"op": "apply_text_edits"}}))
        self.assertIn("1-indexed", edits)
        self.assertEqual(self.changes_sent(), [])

    def test_read_runs_without_a_plan(self):
        result = self.fake.bridge.call("unity_asset", {"op": "read_text",
                                                       "arguments": {"path": "Assets/Scripts/Player.cs"}})
        self.assertFalse(result["isError"], text(result))
        self.assertIn("sha256", text(result))
        self.assertNotIn("manage_scene", self.fake.sent_names())
        planned = self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        self.assertIn("changes Unity, so that step was not sent", text(planned))
        self.assertIn("plan_id: ", text(planned))

    def test_a_change_on_a_domain_tool_comes_back_as_a_plan(self):
        for tool, op, args in (
            ("unity_script", "create_script", {"path": "Assets/Scripts/A.cs", "contents": "class A {}"}),
            ("unity_build", "manage_build.scenes", {"scenes": "[]"}),
            ("unity_packages", "manage_packages.embed_package", {"package": "com.unity.ugui"}),
            ("unity_physics", "manage_physics.simulate_step", {}),
        ):
            result = self.fake.bridge.call(tool, {"op": op, "arguments": args})
            self.assertFalse(result["isError"], op + text(result))
            self.assertIn("changes Unity, so that step was not sent", text(result), op)
            self.assertIn("plan_id: ", text(result), op)
        self.assertEqual(self.changes_sent(), [])
        gone = self.fake.bridge.call("unity_script", {"op": "apply_text_edits.read", "arguments": {}})
        self.assertFalse(gone["isError"])
        self.assertIn("unknown op", text(gone))
        self.assertIn("Closest: ", text(gone))

    def test_plan_sends_no_change_and_apply_runs_it_once(self):
        body = self.plan([{"tool": "unity_script", "op": "create_script",
                           "arguments": {"path": "Assets/Scripts/Evi%6C.cs", "contents": "class Evil {}\n"}}])
        self.assertIn("Assets/Scripts/Evil.cs", body)
        self.assertIn("| class Evil {}", body)
        self.assertIn("file: creates Assets/Scripts/Evil.cs", body)
        self.assertIn("refresh_unity, compile request", body)
        self.assertIn("there is no second question", body)
        self.assertIn("state fingerprint: ", body)
        self.assertNotIn("%6C", body)
        self.assertEqual(self.changes_sent(), [])
        self.assertFalse((self.fake.root / "Assets" / "Scripts" / "Evil.cs").exists())
        plan_id = plan_id_of(body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertFalse(done["isError"], text(done))
        self.assertIn("Unity compiled with no errors", text(done))
        self.assertEqual(self.asked, [])
        calls = [row for row in self.fake.sent() if row["name"] == "create_script"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["arguments"], {"path": "Assets/Scripts/Evil.cs", "contents": "class Evil {}\n"})
        refresh = [row for row in self.fake.sent() if row["name"] == "refresh_unity"]
        self.assertEqual(refresh[-1]["arguments"], {"mode": "force", "scope": "all", "compile": "request",
                                                    "wait_for_ready": True})
        again = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertIn("already used plan_id", text(again))
        self.assertEqual(len([row for row in self.fake.sent() if row["name"] == "create_script"]), 1)

    def test_only_the_newest_plan_runs_and_plans_expire(self):
        first = plan_id_of(self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                                       "arguments": {"name": "A"}}]))
        second = plan_id_of(self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                                        "arguments": {"name": "B"}}]))
        stale = self.fake.bridge.call("apply_plan", {"plan_id": first})
        self.assertIn("replaced by a newer plan", text(stale))
        self.assertFalse(self.fake.bridge.call("apply_plan", {"plan_id": second})["isError"])
        names = [row["arguments"].get("name") for row in self.fake.sent() if row["name"] == "manage_gameobject"]
        self.assertEqual(names, ["B"])
        old = plan_id_of(self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                                     "arguments": {"name": "C"}}]))
        self.fake.bridge.plans[old]["created"] -= B.PLAN_TTL + 1
        expired = self.fake.bridge.call("apply_plan", {"plan_id": old})
        self.assertIn("older than 10 minutes", text(expired))

    def test_a_state_change_after_the_plan_runs_nothing(self):
        plan_id = plan_id_of(self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                                         "arguments": {"name": "A"}}]))
        (self.fake.root / "Assets" / "intruder.txt").write_text("x")
        moved = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertIn("changed after the plan (scene objects", text(moved))
        (self.fake.root / "Assets" / "intruder.txt").unlink()
        script = plan_id_of(self.plan([{"tool": "unity_script", "op": "apply_text_edits",
                                        "arguments": {"uri": "Assets/Scripts/Player.cs", "edits": []}}]))
        (self.fake.root / "Assets" / "Scripts" / "Player.cs").write_text("class Player { int x; }\n")
        changed = self.fake.bridge.call("apply_plan", {"plan_id": script})
        self.assertIn("file Assets/Scripts/Player.cs", text(changed))
        self.assertNotIn("apply_text_edits", self.fake.sent_names())
        self.assertNotIn("manage_gameobject", self.fake.sent_names())

    def test_a_short_failure_before_running_keeps_the_plan(self):
        plan_id = plan_id_of(self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                                         "arguments": {"name": "A"}}]))
        real = self.fake.bridge._wait_settled
        self.fake.bridge._wait_settled = lambda limit=B.READY_WAIT: False
        busy = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertIn("The plan is kept", text(busy))
        self.fake.bridge._wait_settled = real
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertFalse(done["isError"], text(done))

    def test_a_risky_plan_shows_its_text_in_the_second_question(self):
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Scripts/Player.cs"}},
                          {"tool": "unity_code", "op": "execute_code.execute", "arguments": {"code": "return 1;"}}])
        self.assertIn("Second question: step 1 deletes; step 2 runs editor code.", body)
        self.answer = "decline"
        refused = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("did not approve the plan in the second question", text(refused))
        self.assertEqual(len(self.asked), 1)
        question = self.asked[0]
        self.assertLessEqual(len(question), B.SECOND_CAP)
        self.assertTrue(question.startswith(f"Unity plan {plan_id_of(body)}: 2 step(s)."), question)
        self.assertIn("DELETES: step 1 deletes Assets/Scripts/Player.cs", question)
        self.assertIn("RUNS EDITOR CODE: step 2 runs this C#: return 1;", question)
        self.assertLess(question.index("DELETES"), question.index("Steps: 1 manage_asset.delete"))
        self.assertNotIn("manage_asset", self.fake.sent_names())
        again = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("unknown or already used", text(again))
        self.answer = "accept"
        body = self.plan([{"tool": "unity_code", "op": "execute_code.execute", "arguments": {"code": "return 2;"}}])
        ran = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(ran["isError"], text(ran))
        self.assertIn("return 2;", self.asked[-1])
        play = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("there is no second question", play)

    def test_a_surface_that_cannot_show_the_question_gets_confirm_risky_plan(self):
        self.answer = "unshown"
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Scripts/Player.cs"}}])
        plan_id = plan_id_of(body)
        early = self.fake.bridge.call("confirm_risky_plan", {"plan_id": plan_id})
        self.assertIn("apply_plan has not asked about it yet", text(early))
        held = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertFalse(held["isError"])
        self.assertIn("call confirm_risky_plan with plan_id " + plan_id, text(held))
        self.assertIn("what the plan deletes", text(held))
        self.assertNotIn("manage_asset", self.fake.sent_names())
        done = self.fake.bridge.call("confirm_risky_plan", {"plan_id": plan_id})
        self.assertFalse(done["isError"], text(done))
        self.assertIn("manage_asset", self.fake.sent_names())
        safe = plan_id_of(self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                                      "arguments": {"name": "A"}}]))
        self.assertIn("has no step that deletes", text(self.fake.bridge.call("confirm_risky_plan", {"plan_id": safe})))
        bridge = self.fake.bridge
        bridge._elicit = B.Bridge._elicit.__get__(bridge)
        bridge.client_caps = {}
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Scenes/Main.unity"}}])
        no_client = bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("confirm_risky_plan", text(no_client))

    def test_batch_is_expanded_step_by_step(self):
        body = self.plan([{"tool": "unity_generate", "op": "batch_execute", "arguments": {"commands": [
            {"tool": "manage_gameobject", "params": {"action": "create", "name": "Box"}},
            {"tool": "manage_scene", "params": {"action": "create", "name": "Fresh", "path": "Assets/Scenes"}},
        ]}}])
        self.assertIn("unity_object manage_gameobject.create (batch_execute item 1 of 2", body)
        self.assertIn("closes Assets/Scenes/Main.unity, and its unsaved changes are lost", body)
        self.assertIn("step 2 loses unsaved work", body)
        nested = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_generate", "op": "batch_execute",
                                                                 "arguments": {"commands": [
                                                                     {"tool": "batch_execute", "params": {}}]}}]})
        self.assertIn("batch inside a batch", text(nested))
        odd = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_generate", "op": "batch_execute",
                                                              "arguments": {"commands": [
                                                                  {"tool": "manage_scene", "params": {
                                                                      "action": "create", "path": "/tmp/x"}}]}}]})
        self.assertIn("batch_execute item 1:", text(odd))
        self.assertIn("outside", text(odd))
        plan_id = plan_id_of(body)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertNotIn("batch_execute", self.fake.sent_names())
        self.assertIn("manage_gameobject", self.fake.sent_names())

    def test_replay_is_sent_as_the_code_shown(self):
        self.fake.close()
        fake = Fake("history_match")
        self.addCleanup(fake.close)
        fake.bridge._elicit = self._elicit
        body = self.plan([{"tool": "unity_code", "op": "execute_code.replay", "arguments": {"index": 0}}], fake)
        self.assertIn("| Debug.Log(1);", body.replace("code: Debug.Log(1);", "| Debug.Log(1);"))
        fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        sent = [row for row in fake.sent() if row["name"] == "execute_code"
                and row["arguments"].get("action") == "execute" and "sha256:" not in row["arguments"]["code"]]
        self.assertEqual(sent[-1]["arguments"]["code"], "Debug.Log(1);")
        cut = Fake("history_prefix")
        self.addCleanup(cut.close)
        refused = cut.bridge.call("plan_batch", {"steps": [{"tool": "unity_code", "op": "execute_code.replay",
                                                            "arguments": {"index": 0}}]})
        self.assertIn("first 500 characters", text(refused))

    def test_plans_follow_their_own_earlier_steps(self):
        body = self.plan([
            {"tool": "unity_scene", "op": "manage_scene.create", "arguments": {"name": "Level", "path": "Assets/Scenes"}},
            {"tool": "unity_object", "op": "manage_gameobject.create", "arguments": {"name": "Box"}},
            {"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
            {"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}},
            {"tool": "unity_object", "op": "manage_gameobject.modify", "arguments": {"target": "Box",
                                                                                     "position": [0, 1, 0]}},
        ])
        self.assertIn("file: writes the open scene over Assets/Scenes/Level.unity (step 1 of this plan makes it)",
                      body)
        self.assertIn("Unity refuses this while in play mode", body)

    def test_scene_plans_name_the_file_and_what_is_lost(self):
        save = self.plan([{"tool": "unity_scene", "op": "manage_scene.save",
                           "arguments": {"path": "Assets/Scenes/Level2.unity"}}])
        self.assertIn("file: creates Assets/Scenes/Level2.unity from the open scene", save)
        self.assertIn("name: Level2", save)
        create = self.plan([{"tool": "unity_scene", "op": "manage_scene.create", "arguments": {"name": "Fresh"}}])
        self.assertIn("file: creates Assets/Scenes/Fresh.unity", create)
        self.assertIn("closes Assets/Scenes/Main.unity, and its unsaved changes are lost", create)
        load = self.plan([{"tool": "unity_scene", "op": "manage_scene.load",
                           "arguments": {"path": "Assets/Scenes/Main.unity"}}])
        self.assertIn("Unity refuses this load", load)
        play = self.plan([{"tool": "unity_editor", "op": "manage_editor.stop", "arguments": {}}])
        self.assertIn("drops every scene change made during play", play)

    def test_bad_paths_quit_and_root_deletes_send_nothing(self):
        cases = [
            ("Assets/Scripts/Evi%6.cs", "percent-encoding"),
            ("Assets/Scripts/Evi%256C.cs", "percent-encoding"),
            ("Assets/Scripts/Evil.json", "path must end with .cs"),
            ("Assets/.hidden/x.cs", "hidden"),
            ("Assets/Scripts/..%2F..%2Ftmp/secret.cs", "outside"),
            ("Assets/%2e%2e/secret.cs", "outside"),
        ]
        for path, phrase in cases:
            result = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script", "op": "create_script",
                                                                     "arguments": {"path": path,
                                                                                   "contents": "class X {}"}}]})
            body = text(result)
            self.assertIn(phrase, body, path)
            self.assertIn("Nothing was sent.", body)
        for menu in ("File/Quit", "File/Exit", "Unity/Quit"):
            quit_result = self.fake.bridge.call("plan_batch", {"steps": [
                {"tool": "unity_editor", "op": "execute_menu_item", "arguments": {"menu_path": menu}}]})
            self.assertIn("Quit is not sent", text(quit_result))
        for secret in ("Assets/credentials.json", "Assets/Config/api_keys.yaml", "Assets/Keys/release.keystore",
                       "Assets/AuthKey_ABC123.p8", "Assets/infra/prod.tfvars"):
            refused = self.fake.bridge.call("plan_batch", {"steps": [
                {"tool": "unity_asset", "op": "manage_asset.delete", "arguments": {"path": secret}}]})
            self.assertIn("key or credential", text(refused), secret)
        root = self.fake.bridge.call("plan_batch", {"steps": [
            {"tool": "unity_asset", "op": "manage_asset.delete", "arguments": {"path": "Assets"}}]})
        self.assertIn("a whole project folder", text(root))
        self.assertEqual(self.changes_sent(), [])

    def test_upstream_file_arguments_are_checked(self):
        outside = self.fake.bridge.call("unity_profiler", {"op": "manage_profiler.memory_compare_snapshots",
                                                           "arguments": {"snapshot_a": "../outside/notes.txt",
                                                                         "snapshot_b": "/etc/hosts"}})
        self.assertFalse(outside["isError"])
        self.assertIn("refused", text(outside))
        self.assertIn("Nothing was sent.", text(outside))
        self.assertNotIn("manage_profiler", self.fake.sent_names())
        spec = B.OPS[("unity_profiler", "manage_profiler.memory_compare_snapshots")]
        self.assertEqual(spec["file_params"], ["snapshot_a", "snapshot_b"])

    def test_build_and_profiler_outputs_go_where_upstream_puts_them(self):
        ok = self.plan([{"tool": "unity_build", "op": "manage_build.build",
                         "arguments": {"target": "StandaloneOSX", "output_path": "Builds/Mac/Game.app"}}])
        self.assertIn("Builds/Mac/Game.app", ok)
        default = self.plan([{"tool": "unity_build", "op": "manage_build.build",
                              "arguments": {"target": "StandaloneOSX"}}])
        self.assertIn("/Builds/<target>/ (upstream's default)", default)
        absolute = self.plan([{"tool": "unity_build", "op": "manage_build.build", "arguments": {
            "target": "StandaloneOSX",
            "output_path": os.path.join(os.path.realpath(self.fake.root), "Builds", "Mac", "Game.app")}}])
        self.assertIn("file: writes", absolute)
        for bad in ("Assets/Builds/Mac", "/tmp/advbuild/Mac", "../Builds/Mac"):
            refused = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_build", "op": "manage_build.build",
                                                                      "arguments": {"target": "StandaloneOSX",
                                                                                    "output_path": bad}}]})
            self.assertIn("refused", text(refused), bad)
        snap = self.plan([{"tool": "unity_profiler", "op": "manage_profiler.memory_take_snapshot", "arguments": {}}])
        self.assertIn("outside the project (upstream's default)", snap)
        self.assertIn("step 1 sends or writes outside the project", snap)

    def test_file_effects_follow_the_upstream_action_not_the_tool_name(self):
        body = self.plan([{"tool": "unity_build", "op": "manage_build.scenes",
                           "arguments": {"scenes": "Assets/Scenes/Main.unity"}}])
        self.assertIn("file: uses Assets/Scenes/Main.unity", body)
        self.assertNotIn("replaces the existing file", body)
        self.assertIn("there is no second question", body)
        def kinds(key: str, send: dict) -> set:
            spec = next(spec for (_bundle, op), spec in B.OPS.items() if op == key)
            return B.step_kinds({"op": key, "spec": spec, "send": send, "paths": []})

        self.assertNotIn("write_file", kinds("generate_image.status", {}))
        self.assertIn("write_file", kinds("create_script", {"path": "Assets/A.cs"}))
        self.assertIn("save_scene", kinds("manage_build.build", {}))
        self.assertIn("save_scene", kinds("run_tests", {"mode": "EditMode"}))
        # prefab_path places the prefab: it is loaded and instantiated, not written, unless save_as_prefab
        placed = kinds("manage_gameobject.create", {"name": "C", "prefab_path": "Assets/P.prefab"})
        self.assertTrue({"load_asset", "instantiate"} <= placed, placed)
        self.assertNotIn("write_file", placed)
        saved = kinds("manage_gameobject.create", {"name": "C", "save_as_prefab": True, "prefab_path": "Assets/P.prefab"})
        self.assertIn("write_file", saved)
        # overwrite on a ScriptableObject reaches upstream's DeleteAsset; without it, it does not
        self.assertIn("delete_file", kinds("manage_scriptable_object.create",
                                           {"type_name": "T", "folder_path": "Assets/D", "asset_name": "A",
                                            "overwrite": True}))
        self.assertNotIn("delete_file", kinds("manage_scriptable_object.create",
                                              {"type_name": "T", "folder_path": "Assets/D", "asset_name": "A"}))

    def test_argument_types_follow_the_upstream_schema(self):
        wrong = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_build", "op": "manage_build.scenes",
                                                                "arguments": {"scenes": ["Assets/Scenes/Main.unity"]}}]})
        self.assertFalse(wrong["isError"])
        self.assertIn("scenes must be string for manage_build (JSON array of scene paths", text(wrong))
        self.assertEqual(self.changes_sent(), [])
        ok = self.plan([{"tool": "unity_build", "op": "manage_build.scenes",
                         "arguments": {"scenes": "[\"Assets/Scenes/Main.unity\"]"}}])
        self.assertIn("manage_build.scenes", ok)

    def test_text_edits_carry_the_files_sha(self):
        body = self.plan([{"tool": "unity_script", "op": "apply_text_edits",
                           "arguments": {"uri": "Assets/Scripts/Player.cs",
                                         "edits": [{"startLine": 1, "startCol": 1, "endLine": 1, "endCol": 1,
                                                    "newText": "// x\n"}]}}])
        sha = B.file_sha(str(self.fake.root / "Assets" / "Scripts" / "Player.cs"))
        self.assertIn("precondition_sha256: " + sha, body)
        wrong = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script", "op": "apply_text_edits",
                                                                "arguments": {"uri": "Assets/Scripts/Player.cs",
                                                                              "precondition_sha256": "0" * 64,
                                                                              "edits": []}}]})
        self.assertIn("changed since that precondition_sha256", text(wrong))

    def test_unknown_op_and_unknown_key_are_guidance(self):
        unknown = self.fake.bridge.call("unity_scene", {"op": "not_an_op", "arguments": {}})
        self.assertFalse(unknown["isError"])
        self.assertIn("unknown op", text(unknown))
        self.assertIn("Ops of unity_scene:", text(unknown))
        extra = self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {"nope": 1}})
        self.assertFalse(extra["isError"])
        self.assertIn("does not take nope; it takes", text(extra))
        self.assertIn("page_size (", text(extra))
        missing = self.fake.bridge.call("not_a_tool", {})
        self.assertIn("unknown tool", text(missing))
        nested = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "apply_plan", "op": "x"}]})
        self.assertIn("cannot contain", text(nested))
        self.assertEqual(self.fake.sent(), [])

    def test_existing_file_and_long_plan(self):
        exists = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script", "op": "create_script",
                                                                 "arguments": {"path": "Assets/Scripts/Player.cs",
                                                                               "contents": "class P {}"}}]})
        self.assertIn("already exists", text(exists))
        replace = self.plan([{"tool": "unity_script", "op": "create_script",
                              "arguments": {"path": "Assets/Scripts/Player.cs", "contents": "class P {}\n",
                                            "overwrite": True}}])
        self.assertIn("file: replaces the whole text of Assets/Scripts/Player.cs (sent as apply_text_edits", replace)
        self.assertIn("step 1 deletes", replace)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(replace)})
        sent = [row for row in self.fake.sent() if row["name"] == "apply_text_edits"]
        edits = sent[-1]["arguments"]["edits"]
        self.assertEqual([edit["newText"] for edit in edits], ["class P {}\n", ""])
        self.assertEqual((edits[0]["endLine"], edits[0]["endCol"], edits[1]["startLine"]), (2, 1, 2))
        (self.fake.root / "Assets" / "Scripts" / "Headed.cs").write_text("// header\nusing UnityEngine;\nclass H {}\n")
        headed = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script", "op": "create_script",
                                                                 "arguments": {"path": "Assets/Scripts/Headed.cs",
                                                                               "contents": "class H {}", "overwrite": True}}]})
        self.assertIn("text above its first using line", text(headed))
        long = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script", "op": "create_script",
                                                               "arguments": {"path": "Assets/Scripts/Big.cs",
                                                                             "contents": "x\n" * 30000}}]})
        self.assertIn("would be cut", text(long))
        self.assertNotIn("create_script", self.fake.sent_names())

    def test_compile_errors_stop_the_plan(self):
        self.fake.close()
        broken = Fake("compile_error")
        self.addCleanup(broken.close)
        plan_id = plan_id_of(self.plan([
            {"tool": "unity_script", "op": "create_script",
             "arguments": {"path": "Assets/Scripts/Coin.cs", "contents": "class Coin { int }\n"}},
            {"tool": "unity_object", "op": "manage_gameobject.create",
             "arguments": {"name": "Coin", "components_to_add": ["Coin"]}},
        ], broken))
        result = broken.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertTrue(result["isError"])
        self.assertIn("error CS1002", text(result))
        self.assertIn("later steps were not sent", text(result))
        self.assertNotIn("manage_gameobject", broken.sent_names())

    def test_several_editors_need_a_choice_and_apply_pins_it(self):
        self.fake.close()
        two = Fake("two_editors")
        self.addCleanup(two.close)
        refused = two.bridge.call("plan_batch", {"steps": [{"tool": "unity_object", "op": "manage_gameobject.create",
                                                           "arguments": {"name": "A"}}]})
        self.assertIn("more than one Unity editor is open (proj@1, other@2)", text(refused))
        chosen = two.bridge.call("unity_editor", {"op": "set_active_instance", "arguments": {"instance": "proj@1"}})
        self.assertFalse(chosen["isError"], text(chosen))
        body = self.plan([{"tool": "unity_object", "op": "manage_gameobject.create", "arguments": {"name": "A"}}], two)
        self.assertIn("Plan for the Unity editor proj@1", body)
        two.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        names = two.sent_names()
        self.assertIn("set_active_instance", names[:names.index("manage_gameobject")])

    def test_failure_replies_name_the_next_step(self):
        zero_plan = self.plan([{"tool": "unity_object", "op": "find_gameobjects",
                                "arguments": {"search_term": "Nobody"}}])
        zero = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(zero_plan)})
        self.assertFalse(zero["isError"], text(zero))
        self.assertIn("0 results", text(zero))
        plan_id = plan_id_of(self.plan([
            {"tool": "unity_object", "op": "manage_components.set_property", "arguments": {
                "component_type": "Rigidbodyy", "property": "mass", "value": 1}},
            {"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}},
        ]))
        stopped = self.fake.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertTrue(stopped["isError"])
        self.assertIn("not found", text(stopped))
        self.assertIn("later steps were not sent", text(stopped))
        self.assertNotIn("manage_editor", self.fake.sent_names())

    def test_component_values_read_runs_bridge_code_only(self):
        body = self.plan([{"tool": "unity_object", "op": "component_values", "arguments": {"path": "Player"}}])
        self.assertIn('p == "Player"', body)
        result = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        if "confirm_risky_plan" in text(result):
            result = self.fake.bridge.call("confirm_risky_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(result["isError"], text(result))
        self.assertIn("m_LocalPosition = (0, 1, 0)", text(result))
        code = [row for row in self.fake.sent() if row["name"] == "execute_code"][-1]["arguments"]["code"]
        self.assertIn('p == "Player"', code)
        self.assertIn("ISerializationCallbackReceiver", code)
        bad = self.fake.bridge.call("unity_object", {"op": "component_values",
                                                     "arguments": {"path": "A", "component": "x;y"}})
        self.assertIn("C# type name", text(bad))

    def test_progress_is_sent_only_with_a_token(self):
        written = []
        self.fake.bridge.write = written.append
        plan_id = plan_id_of(self.plan([{"tool": "unity_script", "op": "create_script",
                                         "arguments": {"path": "Assets/Scripts/P2.cs", "contents": "class P2 {}\n"}}]))
        self.fake.bridge.handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {
            "name": "apply_plan", "arguments": {"plan_id": plan_id}, "_meta": {"progressToken": "tok"}}})
        for _ in range(200):
            if any(msg.get("id") == 7 for msg in written):
                break
            time.sleep(0.05)
        notes = [msg for msg in written if msg.get("method") == "notifications/progress"]
        self.assertTrue(notes)
        self.assertEqual({msg["params"]["progressToken"] for msg in notes}, {"tok"})
        counts = [msg["params"]["progress"] for msg in notes]
        self.assertEqual(counts, sorted(counts))
        written.clear()
        self.fake.bridge.handle({"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {
            "name": "unity_scene", "arguments": {"op": "manage_scene.get_hierarchy"}}})
        for _ in range(200):
            if any(msg.get("id") == 8 for msg in written):
                break
            time.sleep(0.05)
        self.assertEqual([msg for msg in written if msg.get("method") == "notifications/progress"], [])

    def test_elicitation_round_trip_through_handle(self):
        written = []
        bridge = self.fake.bridge
        bridge.write = written.append
        bridge._elicit = B.Bridge._elicit.__get__(bridge)
        bridge.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2025-06-18", "capabilities": {"elicitation": {}}}})
        body = self.plan([{"tool": "unity_code", "op": "execute_code.execute", "arguments": {"code": "return 3;"}}])
        bridge.handle({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {
            "name": "apply_plan", "arguments": {"plan_id": plan_id_of(body)}}})
        request = None
        for _ in range(200):
            request = next((msg for msg in written if msg.get("method") == "elicitation/create"), None)
            if request:
                break
            time.sleep(0.05)
        self.assertIsNotNone(request)
        self.assertTrue(request["params"]["message"].startswith(f"Unity plan {plan_id_of(body)}"))
        self.assertIn("RUNS EDITOR CODE: step 1 runs this C#: return 3;", request["params"]["message"])
        bridge.handle({"jsonrpc": "2.0", "id": request["id"], "result": {"action": "accept", "content": {}}})
        for _ in range(200):
            if any(msg.get("id") == 9 for msg in written):
                break
            time.sleep(0.05)
        reply = next(msg for msg in written if msg.get("id") == 9)
        self.assertFalse(reply["result"]["isError"], json.dumps(reply))
        self.assertIn("return 3;", json.dumps(self.fake.sent()))

    def test_child_env_has_no_home_and_telemetry_is_off(self):
        self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        env = json.loads(Path(str(self.fake.calls) + ".env.json").read_text(encoding="utf-8"))
        self.assertNotIn("HOME", env)
        self.assertEqual(env["DISABLE_TELEMETRY"], "true")
        self.assertEqual(env["UNITY_MCP_DISABLE_TELEMETRY"], "true")
        self.assertEqual(env["FASTMCP_CHECK_FOR_UPDATES"], "off")
        source = BRIDGE_PATH.read_text(encoding="utf-8")
        self.assertIn('["defaults", "read"', source)
        self.assertNotIn("defaults write", source)
        self.assertNotIn('["defaults", "write"', source)

    def test_transport_helpers_fail_closed(self):
        self.assertTrue(B.interpret_transport_pref(1, ""))
        self.assertFalse(B.interpret_transport_pref(0, "0"))
        self.assertTrue(B.interpret_transport_pref(0, "1"))
        self.assertEqual(B.remote_http_refusal("http://127.0.0.1:8080"), "")
        self.assertIn("not this machine", B.remote_http_refusal("http://example.com/mcp"))
        self.assertFalse(B.port_open("http://example.com/mcp"))
        self.assertEqual(B.transport_choice(True, "http://example.com", True)[0], "refuse")
        self.assertEqual(B.transport_choice(True, "http://127.0.0.1:8080", True)[0], "attach")
        self.assertEqual(B.transport_choice(False, "http://127.0.0.1:8080", False)[0], "stdio")
        env = B.child_environment({"HOME": "/tmp/nope", "PATH": "/usr/bin", "SECRET": "no"})
        self.assertNotIn("HOME", env)
        self.assertNotIn("SECRET", env)
        self.assertEqual(env["DISABLE_TELEMETRY"], "true")

    def test_read_retries_once_and_a_change_does_not(self):
        self.fake.close()
        retry = Fake("reconnect")
        self.addCleanup(retry.close)
        read = retry.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        self.assertFalse(read["isError"], text(read))
        self.assertGreaterEqual(retry.sent_names().count("manage_scene"), 2)
        self.assertNotIn("not retried", text(read))

        change = Fake("reconnect")
        self.addCleanup(change.close)
        change.bridge._elicit = self._elicit
        change.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        plan_id = plan_id_of(self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}],
                                       change))
        play = change.bridge.call("apply_plan", {"plan_id": plan_id})
        self.assertFalse(play["isError"], text(play))
        self.assertEqual(
            [row["arguments"].get("action") for row in change.sent() if row["name"] == "manage_editor"], ["play"])

    def test_no_editor_and_a_huge_reply_are_errors(self):
        self.fake.close()
        closed = Fake("normal", project=False)
        self.addCleanup(closed.close)
        result = closed.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        self.assertTrue(result["isError"])
        self.assertIn("No Unity Editor instances found", text(result))
        info = closed.bridge.call("unity_editor", {"op": "mcpforunity://project/info", "arguments": {}})
        self.assertTrue(info["isError"], text(info))

        huge = Fake("big")
        self.addCleanup(huge.close)
        big = huge.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        self.assertTrue(big["isError"])
        self.assertIn("truncated", text(big))
        self.assertLess(len(text(big)), 1000)

    def test_timeout_and_not_offered_messages(self):
        folded = self.fake.bridge._fold_reply({"bridge_error": "timeout"}, False)
        self.assertIn("did not answer in time", text(folded))
        self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        self.fake.bridge.upstream_tools = set()
        missing = self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_active", "arguments": {}})
        self.assertIn("is not offered", text(missing))


if __name__ == "__main__":
    unittest.main()
