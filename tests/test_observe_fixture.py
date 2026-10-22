"""One adversarial fixture for the observe-and-restore bridge.

Each row is a case from the architecture note or from the 0.5.0 audit: an unsaved scene a test run would save,
a ScriptableObject overwrite, InitializeOnLoad, play that does not start, a gateway question that would be cut,
U+2028, a file the plan did not name, a BOM, and a prefab that cannot be parsed.
"""

from __future__ import annotations

import os
import unittest

from test_bridge import B, Fake, plan_id_of, text

LS = chr(0x2028)


class ObserveFixture(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()
        self.addCleanup(self.fake.close)
        self.asked: list[str] = []
        self.fake.bridge._elicit = self._elicit

    def _elicit(self, message, mid):
        self.asked.append(message)
        return "accept"

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

    def test_disk_read_does_not_create_a_marker(self):
        marker = self.fake.root / "Assets" / "marker.txt"
        before = {path.name for path in (self.fake.root / "Assets").rglob("*") if path.is_file()}
        result = self.fake.bridge.call("unity_asset", {"op": "read_text",
                                                       "arguments": {"path": "Assets/Scripts/Player.cs"}})
        self.assertFalse(result["isError"], text(result))
        after = {path.name for path in (self.fake.root / "Assets").rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(marker.exists())
        self.assertNotIn("execute_code", self.fake.sent_names())

    def test_editor_read_is_a_plan_and_sends_nothing_until_apply(self):
        planned = self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        self.assertIn("changes Unity, so that step was not sent", text(planned))
        self.assertNotIn("execute_code", self.fake.sent_names())
        self.assertIn("plan_id: ", text(planned))

    def test_a_file_the_plan_did_not_name_is_put_back(self):
        self.use("surprise")
        body = self.plan([{"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        self.assertIn("disk sha256", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("surprise.txt", text(done))
        self.assertIn("put back", text(done))
        self.assertFalse((self.fake.root / "Assets" / "surprise.txt").exists())
        self.assertIn("# saved by tests", (self.fake.root / "Assets" / "Scenes" / "Main.unity").read_text())

    def test_scriptable_object_overwrite_names_both_sides_or_has_no_plan(self):
        data = self.fake.root / "Assets" / "Data"
        data.mkdir()
        (data / "Balance.asset").write_text(
            "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!114 &11400000\nMonoBehaviour:\n"
            "  m_Name: Balance\n  speed: 3\n")
        body = self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create", "arguments": {
            "type_name": "Balance", "folder_path": "Assets/Data", "asset_name": "Balance", "overwrite": True}}])
        self.assertIn("disk Assets/Data/Balance.asset speed=3", body)
        self.assertIn("editor Assets/Data/Balance.asset: not read while the plan is made", body)
        self.assertNotIn("editor Assets/Data/Balance.asset speed=3", body)
        self.assertNotIn("execute_code", self.fake.sent_names())
        (data / "Garbage.asset").write_text("not yaml\n")
        refused = self.fake.bridge.call("plan_batch", {"steps": [{
            "tool": "unity_script", "op": "manage_scriptable_object.create",
            "arguments": {"type_name": "Garbage", "folder_path": "Assets/Data", "asset_name": "Garbage",
                          "overwrite": True}}]})
        self.assertNotIn("plan_id: ", text(refused))
        self.assertIn("not a text asset", text(refused))
        self.assertIn("No plan", text(refused))

    def test_initialize_on_load_is_in_the_second_question_and_a_marker_is_put_back(self):
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Editor/Boot.cs",
            "contents": "using UnityEditor;\n[InitializeOnLoad]\npublic class Boot { static Boot() {} }\n"}}])
        self.assertIn("Second question:", body)
        self.assertIn("InitializeOnLoad", body)
        self.use("surprise")
        # The marker stands in for an editor script that writes a file when the domain reloads.
        saved = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                           {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(saved)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("put back", text(done))
        self.assertFalse((self.fake.root / "Assets" / "surprise.txt").exists())

    def test_play_that_does_not_advance_frames_is_not_success(self):
        self.use("play_frozen")
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("frame count advances", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("frame count did not advance", text(done))
        self.assertIn("Entered play mode.", text(done))

    def test_play_that_never_starts_is_not_success(self):
        self.use("no_play")
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        B.PLAY_WAIT, saved = 0.6, B.PLAY_WAIT
        try:
            done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        finally:
            B.PLAY_WAIT = saved
        self.assertTrue(done["isError"])
        self.assertIn("did not enter play mode", text(done))

    def test_hidden_line_separator_is_escaped_and_the_question_fits(self):
        body = self.plan([{"tool": "unity_code", "op": "execute_code.execute",
                           "arguments": {"code": "return 1;" + LS}}])
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(self.asked, text(self.fake.bridge.call("plan_batch", {"steps": []})))
        question = self.asked[-1]
        self.assertLessEqual(len(question), B.SECOND_CAP)
        self.assertNotIn(LS, question)
        self.assertIn("\\u2028", question)

    def test_a_result_file_overrides_an_upstream_success_word(self):
        self.use("tests_lie")
        body = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                          {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("test rows failed", text(done))
        self.assertIn("summary said 0", text(done))

    def test_a_run_with_no_result_file_is_not_success(self):
        self.use("no_results")
        body = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                          {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("did not return one row per test to count", text(done))

    def test_bom_and_an_unparsed_prefab_are_refused(self):
        prefab = self.fake.root / "Assets" / "Coin.prefab"
        prefab.write_bytes(b"\xef\xbb\xbf%YAML 1.1\n")
        bom = self.fake.bridge.call("unity_asset", {"op": "prefab_info",
                                                    "arguments": {"path": "Assets/Coin.prefab"}})
        self.assertTrue(bom["isError"])
        self.assertIn("byte-order mark", text(bom))
        prefab.write_text("%YAML 1.1\n--- !u!1001 &1\nPrefabInstance:\n", encoding="utf-8")
        nested = self.fake.bridge.call("unity_asset", {"op": "prefab_info",
                                                       "arguments": {"path": "Assets/Coin.prefab"}})
        self.assertTrue(nested["isError"])
        self.assertIn("not interpreted", text(nested))
        prefab.write_text("%YAML 1.1\n--- !u!1 &1 stripped\nGameObject:\n  m_Name: Coin\n", encoding="utf-8")
        stripped = self.fake.bridge.call("unity_asset", {"op": "prefab_info",
                                                         "arguments": {"path": "Assets/Coin.prefab"}})
        self.assertTrue(stripped["isError"])

    def test_an_audio_meta_the_plan_did_not_name_is_put_back(self):
        audio = self.fake.root / "Assets" / "Audio"
        audio.mkdir()
        meta = audio / "Loop.wav.meta"
        meta.write_text("loopTime: 0\n")
        self.use("audio_loop")
        # use() makes a new project, so write the meta there.
        audio = self.fake.root / "Assets" / "Audio"
        audio.mkdir()
        meta = audio / "Loop.wav.meta"
        meta.write_text("loopTime: 0\n")
        body = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                          {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertEqual(meta.read_text(), "loopTime: 0\n")

    def test_planning_sends_no_execute_code(self):
        self.fake.bridge.call("unity_scene", {"op": "manage_scene.get_hierarchy", "arguments": {}})
        data = self.fake.root / "Assets" / "Data"
        data.mkdir()
        (data / "Balance.asset").write_text(
            "%YAML 1.1\n--- !u!114 &1\nMonoBehaviour:\n  speed: 3\n")
        self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create", "arguments": {
            "type_name": "Balance", "folder_path": "Assets/Data", "asset_name": "Balance", "overwrite": True}}])
        script = self.fake.root / "Assets" / "Scripts" / "Player.cs"
        script.write_text("class Player { int OLD_BODY_TOKEN = 1; }\n")
        self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Player.cs", "contents": "class Player { int n = 2; }\n", "overwrite": True}}])
        self.assertNotIn("execute_code", self.fake.sent_names())

    def test_script_overwrite_names_the_old_text_or_has_no_plan(self):
        script = self.fake.root / "Assets" / "Scripts" / "Player.cs"
        script.write_text("class Player { int OLD_BODY_TOKEN = 1; }\n")
        result = self.fake.bridge.call("plan_batch", {"steps": [{
            "tool": "unity_script", "op": "create_script",
            "arguments": {"path": "Assets/Scripts/Player.cs", "contents": "class Player { int n = 2; }\n",
                          "overwrite": True}}]})
        body = text(result)
        if "plan_id: " in body:
            self.assertIn("OLD_BODY_TOKEN", body)
        else:
            self.assertIn("no plan", body)
        self.assertNotIn("execute_code", self.fake.sent_names())

    def test_a_build_with_no_output_is_not_success(self):
        self.use("build_lie")
        body = self.plan([{"tool": "unity_build", "op": "manage_build.build", "arguments": {
            "target": "StandaloneOSX", "output_path": "Builds/Mac/Game.app"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        head = text(done).splitlines()[0]
        self.assertTrue(done["isError"], text(done))
        self.assertNotIn("done.", head)
        self.assertIn("not on disk", text(done))
        self.assertIn("Upstream said succeeded", text(done))
        self.assertEqual(list((self.fake.root / "Builds").glob("**/*")) if (self.fake.root / "Builds").exists() else [],
                         [])

    def test_a_build_that_leaves_the_old_output_is_not_success(self):
        self.use("build_lie")
        app = self.fake.root / "Builds" / "Mac" / "Game.app"
        app.mkdir(parents=True)
        (app / "old").write_text("old\n")
        body = self.plan([{"tool": "unity_build", "op": "manage_build.build", "arguments": {
            "target": "StandaloneOSX", "output_path": "Builds/Mac/Game.app"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("did not change", text(done))
        self.assertEqual((app / "old").read_text(), "old\n")

    def test_a_package_manifest_the_plan_did_not_name_is_put_back(self):
        self.use("pkg_write")
        man = self.fake.root / "Packages" / "manifest.json"
        man.parent.mkdir()
        original = '{"dependencies":{}}\n'
        man.write_text(original)
        body = self.plan([{"tool": "unity_scene", "op": "manage_scene.save", "arguments": {}},
                          {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("Packages/manifest.json", text(done))
        self.assertEqual(man.read_text(), original)

    def test_a_dirty_asset_is_not_overwritten(self):
        self.use("asset_dirty")
        data = self.fake.root / "Assets" / "Data"
        data.mkdir()
        asset = data / "Balance.asset"
        asset.write_text("%YAML 1.1\n--- !u!114 &1\nMonoBehaviour:\n  speed: 3\n")
        body = self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create", "arguments": {
            "type_name": "Balance", "folder_path": "Assets/Data", "asset_name": "Balance", "overwrite": True}}])
        self.assertNotIn("execute_code", self.fake.sent_names())
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("dirty", text(done))
        self.assertEqual(asset.read_text(), "%YAML 1.1\n--- !u!114 &1\nMonoBehaviour:\n  speed: 3\n")
        self.assertNotIn("manage_scriptable_object", self.fake.sent_names())

    def test_a_nested_scriptable_object_names_every_value_or_has_no_plan(self):
        data = self.fake.root / "Assets" / "Data"
        data.mkdir()
        asset = data / "Waves.asset"
        asset.write_text(
            "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!114 &11400000\nMonoBehaviour:\n"
            "  m_Name: Waves\n  waves:\n  - count: 10\n    delay: 1.5\n  - count: 20\n    delay: 0.5\n")
        body = self.plan([{"tool": "unity_script", "op": "manage_scriptable_object.create", "arguments": {
            "type_name": "Waves", "folder_path": "Assets/Data", "asset_name": "Waves", "overwrite": True}}])
        self.assertIn("count: 10", body)
        self.assertIn("delay: 0.5", body)
        self.assertIn("Second question:", body)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("count: 10", self.asked[-1])
        self.assertIn("delay: 0.5", self.asked[-1])

    def test_a_text_edit_names_the_text_it_removes(self):
        script = self.fake.root / "Assets" / "Scripts" / "GameState.cs"
        script.write_text("public class GameState {\n    public static int Score;\n"
                          "    public static void Add(int n) { Score += n; Debug.Log(\"SCORE \" + Score); }\n}\n")
        line = script.read_text().splitlines()[2]
        old = "Score += n; Debug.Log(\"SCORE \" + Score);"
        start = line.index(old) + 1
        body = self.plan([{"tool": "unity_script", "op": "apply_text_edits", "arguments": {
            "uri": "Assets/Scripts/GameState.cs",
            "edits": [{"startLine": 3, "startCol": start, "endLine": 3, "endCol": start + len(old),
                       "newText": ""}]}}])
        self.assertIn("Score += n; Debug.Log(\"SCORE \" + Score);", body)
        self.assertIn("Second question:", body)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertIn("Score += n;", self.asked[-1])

    def test_combined_attributes_are_editor_code(self):
        for contents in (
            "using UnityEditor;\n[Serializable, InitializeOnLoad]\npublic class LevelBootstrap {}\n",
            "using UnityEditor;\n[global::UnityEditor.InitializeOnLoad]\npublic class LevelBootstrap {}\n",
        ):
            body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
                "path": "Assets/Level/LevelBootstrap.cs", "contents": contents}}])
            self.assertIn("Second question:", body)
            self.assertIn("InitializeOnLoad", body)
            self.assertIn("runs this code by itself", body)

    def test_a_new_folder_meta_is_kept_and_a_deleted_folder_stays_deleted(self):
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Level/LevelBootstrap.cs", "contents": "public class LevelBootstrap {}\n"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertTrue((self.fake.root / "Assets" / "Level.meta").is_file())
        self.assertTrue((self.fake.root / "Assets" / "Level" / "LevelBootstrap.cs").is_file())
        level = self.fake.root / "Assets" / "Level"
        (level / "LevelBootstrap.cs").write_text("public class LevelBootstrap { static LevelBootstrap() {} }\n")
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Level"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertFalse((self.fake.root / "Assets" / "Level" / "LevelBootstrap.cs").exists())

    def test_an_asset_copied_without_meta_is_named_and_kept(self):
        self.use("import_meta")
        art = self.fake.root / "Assets" / "Art"
        art.mkdir()
        (art / "hero.png").write_bytes(b"\x89PNG\r\n")
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Bonus.cs", "contents": "public class Bonus {}\n"}}])
        self.assertIn("Unity will import these (.meta will be created):", body)
        self.assertIn("Assets/Art/hero.png", body)
        self.assertIn("Assets/Art", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertTrue((art / "hero.png.meta").is_file())
        self.assertTrue((self.fake.root / "Assets" / "Art.meta").is_file())
        again = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Bonus2.cs", "contents": "public class Bonus2 {}\n"}}])
        done2 = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(again)})
        self.assertFalse(done2["isError"], text(done2))
        self.assertTrue((art / "hero.png.meta").is_file())

    def test_a_script_written_during_apply_is_put_back(self):
        self.use("rogue_cs")
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Bonus.cs", "contents": "public class Bonus {}\n"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("Assets/Rogue.cs", text(done))
        self.assertIn("put back", text(done))
        self.assertFalse((self.fake.root / "Assets" / "Rogue.cs").exists())
        self.assertFalse((self.fake.root / "Assets" / "Rogue.cs.meta").exists())
        self.assertTrue((self.fake.root / "Assets" / "Scripts" / "Bonus.cs").is_file())

    def test_two_script_plans_keep_the_meta_of_a_copied_png(self):
        self.use("import_meta")
        art = self.fake.root / "Assets" / "Art"
        art.mkdir()
        (art / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        first = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Bonus.cs", "contents": "public class Bonus {}\n"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(first)})
        self.assertFalse(done["isError"], text(done))
        self.assertTrue((art / "hero.png.meta").is_file())
        self.assertTrue((self.fake.root / "Assets" / "Art.meta").is_file())
        second = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Bonus2.cs", "contents": "public class Bonus2 {}\n"}}])
        done2 = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(second)})
        self.assertFalse(done2["isError"], text(done2))
        self.assertTrue((art / "hero.png.meta").is_file())
        self.assertTrue((self.fake.root / "Assets" / "Art.meta").is_file())

    def test_a_text_file_and_an_unplanned_script_are_put_back(self):
        self.use("both_new")
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Bonus.cs", "contents": "public class Bonus {}\n"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("put back", text(done))
        self.assertIn("Assets/surprise.txt", text(done))
        self.assertIn("Assets/Rogue.cs", text(done))
        root = self.fake.root / "Assets"
        self.assertFalse((root / "surprise.txt").exists())
        self.assertFalse((root / "surprise.txt.meta").exists())
        self.assertFalse((root / "Rogue.cs").exists())
        self.assertFalse((root / "Rogue.cs.meta").exists())
        self.assertTrue((root / "Scripts" / "Bonus.cs").is_file())

    def test_a_package_the_plan_names_is_not_put_back(self):
        packages = self.fake.root / "Packages"
        packages.mkdir()
        (packages / "manifest.json").write_text('{"dependencies":{}}\n')
        (packages / "packages-lock.json").write_text("{}\n")
        body = self.plan([{"tool": "unity_packages", "op": "manage_packages.add_package",
                           "arguments": {"package": "com.unity.test-framework"}}])
        self.assertIn("Packages/manifest.json", body)
        self.assertIn("packages-lock.json", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertIn("com.unity.test-framework", (packages / "manifest.json").read_text())
        self.assertIn("com.unity.test-framework", (packages / "packages-lock.json").read_text())

    def test_a_write_outside_assets_is_put_back_and_named(self):
        self.use("outside")
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Plain.cs", "contents": "public class Plain {}\n"}}])
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertIn("UserSettings/claude_iol_outside.txt", text(done))
        self.assertIn("claude_iol_root.txt", text(done))
        self.assertIn("put back", text(done))
        self.assertFalse((self.fake.root / "UserSettings" / "claude_iol_outside.txt").exists())
        self.assertFalse((self.fake.root / "claude_iol_root.txt").exists())

    def test_an_untitled_dirty_scene_refuses_tests(self):
        self.use("untitled")
        refused = self.fake.bridge.call("plan_batch", {"steps": [
            {"tool": "unity_tests", "op": "run_tests", "arguments": {"mode": "EditMode"}}]})
        self.assertNotIn("plan_id: ", text(refused))
        self.assertIn("untitled scene", text(refused))
        self.assertIn("save dialog", text(refused))
        self.assertNotIn("run_tests", self.fake.sent_names())

    def _old_assembly(self) -> None:
        assemblies = self.fake.root / "Library" / "ScriptAssemblies"
        assemblies.mkdir(parents=True)
        dll = assemblies / "Assembly-CSharp.dll"
        dll.write_bytes(b"old")
        os.utime(dll, (1_700_000_000, 1_700_000_000))

    def test_a_changed_initialize_on_load_script_asks_before_a_compile(self):
        self._old_assembly()
        editor = self.fake.root / "Assets" / "Editor"
        editor.mkdir()
        (editor / "Boot.cs").write_text(
            "using UnityEditor;\n[InitializeOnLoad]\npublic class Boot { static Boot() {} }\n")
        plain = {"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Plain.cs", "contents": "public class Plain {}\n"}}
        body = self.plan([plain])
        self.assertIn("Second question: step 1 runs editor code", body)
        self.assertIn("Assets/Editor/Boot.cs", body)
        self.assertNotIn("there is no second question", body)
        refresh = self.plan([{"tool": "unity_editor", "op": "refresh_unity",
                               "arguments": {"compile": "request", "scope": "scripts", "wait_for_ready": True}}])
        self.assertIn("Second question: step 1 runs editor code", refresh)
        self.assertIn("Assets/Editor/Boot.cs", refresh)
        self.assertNotIn("there is no second question", refresh)

    def test_a_compile_without_that_script_does_not_ask(self):
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Plain.cs", "contents": "public class Plain {}\n"}}])
        self.assertIn("there is no second question", body)
        self.assertNotIn("Second question:", body)
        self._old_assembly()
        editor = self.fake.root / "Assets" / "Editor"
        editor.mkdir()
        boot = editor / "Boot.cs"
        boot.write_text("using UnityEditor;\n[InitializeOnLoad]\npublic class Boot { static Boot() {} }\n")
        os.utime(boot, (1_600_000_000, 1_600_000_000))
        again = self.plan([{"tool": "unity_editor", "op": "refresh_unity",
                            "arguments": {"compile": "request", "scope": "scripts", "wait_for_ready": True}}])
        self.assertIn("there is no second question", again)
        self.assertNotIn("runs: Assets/Editor/Boot.cs", again)
        self.assertNotIn("Second question:", again)

    def test_a_folder_delete_names_every_file_inside(self):
        level = self.fake.root / "Assets" / "Level"
        level.mkdir()
        for name in ("A.cs", "B.txt", "C.asset"):
            (level / name).write_text("x\n")
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Level"}}])
        for name in ("Assets/Level/A.cs", "Assets/Level/B.txt", "Assets/Level/C.asset"):
            self.assertIn(name, body)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(self.asked)
        self.assertLessEqual(len(self.asked[-1]), 1700)
        self.assertIn("A.cs", self.asked[-1])
        self.assertIn("B.txt", self.asked[-1])
        self.assertIn("C.asset", self.asked[-1])

    def test_a_large_folder_delete_fits_the_second_question(self):
        level = self.fake.root / "Assets" / "Level"
        level.mkdir()
        for index in range(40):
            (level / f"piece-{index:02d}-{('n' * 40)}.txt").write_text("x\n")
        body = self.plan([{"tool": "unity_asset", "op": "manage_asset.delete",
                           "arguments": {"path": "Assets/Level"}}])
        self.assertIn("files inside, first:", body)
        self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(self.asked)
        self.assertLessEqual(len(self.asked[-1]), 1700)
        self.assertIn("files inside, first:", self.asked[-1])

    def test_an_orphan_unity_meta_is_named_and_kept(self):
        self.use("orphan_refresh")
        meta = self.fake.root / "Assets" / "surprise.txt.meta"
        meta.parent.mkdir(parents=True, exist_ok=True)
        meta.write_text("fileFormatVersion: 2\nguid: abc\n")
        audio = self.fake.root / "Assets" / "Audio"
        audio.mkdir()
        (audio / "Loop.wav.meta").write_text("loopTime: 0\n")
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("Unity will refresh these .meta files because the asset is missing: "
                      "Assets/surprise.txt.meta", body)
        self.assertNotIn("Loop.wav.meta", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertIn("Unity is in play mode", text(done))
        self.assertEqual(meta.read_text(encoding="utf-8"), "fileFormatVersion: 2\nguid: changed\n")
        self.assertEqual((audio / "Loop.wav.meta").read_text(encoding="utf-8"), "loopTime: 0\n")

    def test_a_lock_behind_the_manifest_is_named_and_kept(self):
        self.use("lock_refresh")
        packages = self.fake.root / "Packages"
        packages.mkdir()
        (packages / "manifest.json").write_text('{"dependencies":{"com.unity.test-framework":"1.8.0"}}\n')
        lock = packages / "packages-lock.json"
        lock.write_text('{"dependencies":{}}\n')
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("Unity will rewrite Packages/packages-lock.json because the manifest lists a package the "
                      "lock does not.", body)
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertFalse(done["isError"], text(done))
        self.assertIn("1.8.0", lock.read_text(encoding="utf-8"))
        self.assertNotIn("put back", text(done))

    def test_a_lock_that_already_lists_the_manifest_is_not_named(self):
        packages = self.fake.root / "Packages"
        packages.mkdir()
        (packages / "manifest.json").write_text('{"dependencies":{"com.unity.test-framework":"1.8.0"}}\n')
        (packages / "packages-lock.json").write_text(
            '{"dependencies":{"com.unity.test-framework":{"version":"1.8.0"}}}\n')
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertNotIn("manifest lists a package", body)

    def test_a_file_unity_removed_before_apply_is_restored(self):
        self.use("orphan_meta")
        audio = self.fake.root / "Assets" / "Audio"
        audio.mkdir()
        meta = audio / "Loop.wav.meta"
        meta.write_text("loopTime: 0\n")
        body = self.plan([{"tool": "unity_script", "op": "create_script", "arguments": {
            "path": "Assets/Scripts/Plain.cs", "contents": "public class Plain {}\n"}}])
        meta.unlink()
        done = self.fake.bridge.call("apply_plan", {"plan_id": plan_id_of(body)})
        self.assertTrue(done["isError"], text(done))
        self.assertEqual(meta.read_text(encoding="utf-8"), "loopTime: 0\n")
        self.assertIn("Assets/Audio/Loop.wav.meta", text(done))
        self.assertNotIn("default-6000.dwlt", text(done))
        self.assertTrue((self.fake.root / "UserSettings" / "Layouts" / "default-6000.dwlt").is_file())

    def test_an_old_initialize_on_load_script_asks_before_play(self):
        editor = self.fake.root / "Assets" / "Editor"
        editor.mkdir()
        (editor / "Boot.cs").write_text("using UnityEditor;\n[InitializeOnLoad]\npublic class Boot {}\n")
        body = self.plan([{"tool": "unity_editor", "op": "manage_editor.play", "arguments": {}}])
        self.assertIn("Second question:", body)
        self.assertIn("Assets/Editor/Boot.cs", body)
        self.assertIn("InitializeOnLoad", body)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
