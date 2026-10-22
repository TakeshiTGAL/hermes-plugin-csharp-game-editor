"""H7: what a step does inside comes from the side effect table, and "done" is read back from the editor.

Offline, against the fake upstream (tests/fake_upstream.py). The same cases on a real Unity 6000.6.6f1 editor are
in the CLAIMS ledger of the release.
"""

from __future__ import annotations

import json
import os
import unittest

from test_bridge import B, Fake, plan_id_of, text

# Line separator and right-to-left override, made from code points (the install scan rejects them in source).
LS, RLO = chr(0x2028), chr(0x202E)


class SideEffectTest(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()
        self.addCleanup(self.fake.close)
        self.asked: list[str] = []
        self.answer = "accept"
        self.fake.bridge._elicit = self._elicit

    def _elicit(self, message, mid):
        self.asked.append(message)
        return self.answer

    def use(self, mode: str) -> Fake:
        self.fake.close()
        self.fake = Fake(mode)
        self.addCleanup(self.fake.close)
        self.fake.bridge._elicit = self._elicit
        return self.fake

    def plan(self, steps) -> str:
        result = self.fake.bridge.call("plan_batch", {"steps": steps})
        self.assertIn("plan_id: ", text(result), text(result))
        return text(result)

    def test_running_tests_says_it_saves_the_unsaved_scene_and_asks(self):
        # The fake editor's open scene has unsaved changes made before the plan.
        body = self.plan([{"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        self.assertIn("inside: saves scene files to disk (EditorSceneManager.SaveScene, "
                      "Editor/Services/TestRunnerService.cs:569", body)
        self.assertIn("then: upstream saves Assets/Scenes/Main.unity over its file first, because it has unsaved "
                      "changes", body)
        self.assertIn("Second question: step 1 saves unsaved changes over a scene file", body)
        self.assertIn("Play mode and tests run the project's own scripts", body)
        self.answer = "decline"
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("SAVES OVER A FILE: step 1 saves the unsaved changes in Assets/Scenes/Main.unity", self.asked[-1])
        self.assertNotIn("run_tests", self.fake.sent_names())

    def test_tests_after_a_save_in_the_same_plan_need_no_second_question(self):
        body = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                          {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        self.assertIn("then: no open scene has unsaved changes now, so this saves nothing", body)
        self.assertIn("there is no second question", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        first = text(done).splitlines()[0]
        self.assertIn("done. 2 step(s) ran", first)
        self.assertIn("2 passed, 0 failed", first)

    def test_failed_and_empty_test_runs_are_errors(self):
        for mode, phrase in (("tests_bad", "1 of 2 tests failed"), ("tests_zero", "0 tests ran")):
            self.use(mode)
            body = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                              {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
            done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
            self.assertTrue(done["isError"], mode)
            first = text(done).splitlines()[0]
            self.assertIn("FAILED at step 2 of 2 (unity_tests run_tests)", first)
            self.assertIn(phrase if mode == "tests_zero" else "the test run failed", first)

    def test_scriptable_object_overwrite_is_a_delete_and_a_new_name_otherwise(self):
        data = self.fake.root / "Assets" / "Data"
        data.mkdir()
        (data / "Balance.asset").write_text(
            "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!114 &11400000\nMonoBehaviour:\n"
            "  m_Name: Balance\n  speed: 3\n")
        args = {"type_name": "Balance", "folder_path": "Assets/Data", "asset_name": "Balance"}
        replace = self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create",
                              "arguments": dict(args, overwrite=True)}])
        self.assertIn("file: replaces Assets/Data/Balance.asset: upstream removes or overwrites the existing asset "
                      "(AssetDatabase.DeleteAsset, Editor/Tools/ManageScriptableObject.cs:169", replace)
        self.assertIn("step 1 deletes", replace)
        keep = self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create", "arguments": args}])
        self.assertIn("Assets/Data/Balance.asset exists and this step does not replace it, so upstream writes the "
                      "asset under the next free name", keep)
        self.assertIn("there is no second question", keep)

    def test_destroying_the_callers_objects_is_a_delete(self):
        gone = self.plan([{"tool": "unity_object", "op": "manage_gameobject.delete", "arguments": {"target": "Player"}}])
        self.assertIn("Second question: step 1 deletes", gone)
        removed = self.plan([{"tool": "unity_object", "op": "manage_gameobject.modify",
                              "arguments": {"target": "Player", "components_to_remove": ["Rigidbody"]}}])
        self.assertIn("Second question: step 1 deletes", removed)
        made = self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                           "arguments": {"name": "Box", "primitive_type": "Cube", "components_to_add": ["Rigidbody"]}}])
        self.assertIn("there is no second question", made)

    def test_placing_a_prefab_does_not_write_it(self):
        prefabs = self.fake.root / "Assets" / "Prefabs"
        prefabs.mkdir()
        (prefabs / "Coin.prefab").write_text("%YAML 1.1\n")
        body = self.plan([{"tool": "unity_object", "op": "manage_gameobject.create",
                           "arguments": {"name": "Coin4", "prefab_path": "Assets/Prefabs/Coin.prefab"}}])
        self.assertIn("file: loads Assets/Prefabs/Coin.prefab", body)
        self.assertIn("this step does not write it", body)
        self.assertNotIn("file: replaces", body)
        self.assertIn("there is no second question", body)

    def test_a_script_unity_runs_by_itself_is_editor_code(self):
        auto = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Editor/Boot.cs",
            "contents": "using UnityEditor;\n[InitializeOnLoad]\npublic static class Boot { static Boot() {} }\n"}}])
        self.assertIn("Second question: step 1 runs editor code", auto)
        self.assertIn("Unity runs this code by itself in the editor", auto)
        plain = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Tests/Editor/MathTests.cs",
            "contents": "using NUnit.Framework;\npublic class MathTests { [Test] public void Adds() {} }\n"}}])
        self.assertIn("is an editor script", plain)
        self.assertIn("Second question: step 1 runs editor code", plain)

    def test_a_script_changed_after_the_last_compile_is_compiled_before_play(self):
        assemblies = self.fake.root / "Library" / "ScriptAssemblies"
        assemblies.mkdir(parents=True)
        dll = assemblies / "Assembly-CSharp.dll"
        dll.write_bytes(b"old")
        os.utime(dll, (1_700_000_000, 1_700_000_000))
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("before: the plugin asks Unity to compile first, because Assets/Scripts/Player.cs changed on "
                      "disk after the last compile", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        names = [row["name"] for row in self.fake.sent()]
        self.assertLess(names.index("refresh_unity"), names.index("manage_editor"))

    def test_play_that_starts_is_read_back(self):
        # In play, upstream's editor state reports is_playing and is_changing (isPlayingOrWillChangePlaymode) true.
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertIn("Unity is in play mode", text(done).splitlines()[0])
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.stop", "arguments": {}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("Unity left play mode", text(done).splitlines()[0])

    def test_play_that_never_starts_is_an_error(self):
        self.use("no_play")
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("check after: Unity is in play mode", body)
        B.PLAY_WAIT, saved = 1.0, B.PLAY_WAIT
        try:
            done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        finally:
            B.PLAY_WAIT = saved
        self.assertTrue(done["isError"])
        self.assertIn("FAILED at step 1 of 1 (unity_editor manage_editor.play): Unity did not enter play mode",
                      text(done).splitlines()[0])

    def test_a_success_reply_that_changed_nothing_is_an_error(self):
        self.use("no_file_effects")
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Scripts/Player.cs"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"])
        self.assertIn("Assets/Scripts/Player.cs is still on disk", text(done).splitlines()[0])

    def test_play_and_tests_are_refused_while_the_last_compile_has_errors(self):
        self.use("old_error")
        refused = self.fake.bridge.call("plan_batch", {"steps": [
            {"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}]})
        self.assertFalse(refused["isError"])
        self.assertIn("the last compile has errors", text(refused))
        self.assertIn("error CS0103", text(refused))
        fixed = self.plan([{"tool": "unity_script", "op": "apply_text_edits", "arguments": {
            "uri": "Assets/Scripts/Player.cs", "edits": [{"startLine": 1, "startCol": 1, "endLine": 1,
                                                          "endCol": 1, "newText": "// fix\n"}]}},
                           {"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("step 2 of 2: unity_editor manage_editor.play", fixed)

    def test_second_question_is_short_and_escapes_hidden_characters(self):
        for index in range(3):
            (self.fake.root / "Assets" / "Scripts" / f"Old{index}.cs").write_text("class O {}\n")
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": f"Assets/Scripts/Old{index}.cs"}} for index in range(3)]
                         + [{"tool": "unity_code", "op": "execute_code.execute",
                             "arguments": {"code": "Debug.Log(\"a" + LS + "b" + RLO + "c\");\rreturn 1;"}}])
        self.assertIn("\\u2028", body)
        self.assertIn("\\u202e", body)
        self.assertNotIn(LS, body)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        question = self.asked[-1]
        self.assertLessEqual(len(question), B.SECOND_CAP)
        self.assertNotIn(LS, question)
        self.assertNotIn("\r", question)
        self.assertIn("\\r", question)
        self.assertTrue(question.splitlines()[1].startswith("DELETES:"), question)

    def test_a_question_that_does_not_fit_is_not_sent(self):
        names = []
        for index in range(40):
            name = f"Assets/Scripts/AVeryLongScriptNameForTheQuestion{index:02d}.cs"
            (self.fake.root / name).write_text("class O {}\n")
            names.append(name)
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete", "arguments": {"path": name}}
                          for name in names])
        held = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertEqual(self.asked, [])
        self.assertIn("without being cut", text(held))
        self.assertIn("confirm_risky_plan", text(held))
        done = self.fake.bridge.call("confirm_risky_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done)[:400])

    def test_create_asmdef_writes_once_and_compiles(self):
        body = self.plan([{"tool": "unity_script", "op": "create_asmdef", "arguments": {
            "path": "Assets/Tests/EditMode/Game.Tests.EditMode.asmdef", "kind": "editmode_tests",
            "references": ["Game"]}}])
        self.assertIn("\"nunit.framework.dll\"", body)
        self.assertIn("then: the plugin asks Unity to refresh and compile", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        written = json.loads((self.fake.root / "Assets/Tests/EditMode/Game.Tests.EditMode.asmdef").read_text())
        self.assertEqual(written["includePlatforms"], ["Editor"])
        self.assertIn("UnityEngine.TestRunner", written["references"])
        self.assertIn("refresh_unity", self.fake.sent_names())
        again = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script", "op": "create_asmdef",
                                                                "arguments": {"path": "Assets/Tests/EditMode/"
                                                                              "Game.Tests.EditMode.asmdef",
                                                                              "kind": "editmode_tests"}}]})
        self.assertIn("already exists", text(again))
        bad = self.fake.bridge.call("unity_script", {"op": "create_script", "arguments": {
            "path": "Assets/Game.asmdef", "contents": "{}"}})
        self.assertIn("create_script writes C# only", text(bad))

    def test_deleting_a_folder_with_scripts_waits_for_the_compile(self):
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete", "arguments": {"path": "Assets/Scripts"}}])
        self.assertIn("then: the plugin asks Unity to refresh and compile", body)
        # an asset written into a folder that also holds scripts does not change them
        asset = self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create",
                            "arguments": {"type_name": "T", "folder_path": "Assets/Scripts", "asset_name": "Data"}}])
        self.assertNotIn("refresh and compile", asset)

    def test_disk_reads_do_not_ask_unity(self):
        prefabs = self.fake.root / "Assets" / "Prefabs"
        prefabs.mkdir()
        (self.fake.root / "Assets" / "Scripts" / "Coin.cs.meta").write_text("fileFormatVersion: 2\nguid: "
                                                                            + "a" * 32 + "\n")
        (prefabs / "Coin.prefab").write_text(
            "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!1 &100\nGameObject:\n  m_Name: Coin\n"
            "  m_IsActive: 1\n--- !u!4 &200\nTransform:\n  m_GameObject: {fileID: 100}\n  m_Father: {fileID: 0}\n"
            "--- !u!114 &300\nMonoBehaviour:\n  m_GameObject: {fileID: 100}\n  m_Script: {fileID: 11500000, guid: "
            + "a" * 32 + ", type: 3}\n  m_EditorClassIdentifier: \n  value: 5\n")
        info = self.fake.bridge.call("unity_asset", {"op": "prefab_info",
                                                     "arguments": {"path": "Assets/Prefabs/Coin.prefab"}})
        self.assertFalse(info["isError"], text(info))
        self.assertIn("- Coin [Transform, Coin (Assets/Scripts/Coin.cs)]", text(info))
        self.assertIn("value: 5", text(info))
        found = self.fake.bridge.call("unity_asset", {"op": "asset_find", "arguments": {"type": "prefab"}})
        self.assertIn("Assets/Prefabs/Coin.prefab (prefab", text(found))
        self.assertEqual([name for name in self.fake.sent_names() if name not in ("set_active_instance",)], [])

    def test_a_linked_folder_named_with_a_file_name_is_refused(self):
        outside = self.fake.root.parent / "outside"
        outside.mkdir()
        os.symlink(outside, self.fake.root / "Assets" / "Data")
        refused = self.fake.bridge.call("plan_batch", {"steps": [{"tool": "unity_script",
                                                                  "op": "manage_scriptable_object.create",
                                                                  "arguments": {"type_name": "T",
                                                                                "folder_path": "Assets/Data",
                                                                                "asset_name": "Balance"}}]})
        self.assertIn("symbolic link", text(refused))
        read = self.fake.bridge.call("unity_script", {"op": "manage_script.read",
                                                      "arguments": {"name": "Evil", "path": "Assets/Data"}})
        self.assertIn("symbolic link", text(read))
        self.assertNotIn("manage_script", self.fake.sent_names())

    def test_every_listed_read_is_backed_by_the_table(self):
        table = json.loads((B._HERE / "ops_table.json").read_text())
        self.assertIn("editor_autorun", table["unity_rules"])
        run_tests = table["bundles"]["unity_tests"]["ops"]["run_tests"]["effects"]
        self.assertTrue(any(row["kind"] == "save_scene" and "TestRunnerService.cs:569" in row["at"]
                            for row in run_tests))


if __name__ == "__main__":
    unittest.main()
