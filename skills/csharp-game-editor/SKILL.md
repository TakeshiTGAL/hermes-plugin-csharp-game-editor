---
name: csharp-game-editor
description: "Unity editor for a C# game. Scenes, scripts, prefabs, play mode, console and tests. Disk reads run at once. An editor read or a change is a plan, shown to the user, then run with apply_plan. Search with tool_search for unity scene, unity script, unity play mode."
version: 0.6.0
author: TakeshiTGAL
license: MIT
platforms: [macos]
metadata:
  tags: "unity, game-engine, gamedev, csharp, scene, gameobject, prefab, editor, mcp"
---

# C# game editor (Unity)

## When to use

Use this skill when the user works on a Unity game that is open in the Unity editor: the scene, GameObjects, C# scripts, prefabs, materials, UI, animation, physics, play mode, the console, tests, or a build.

Use the csharp-game-editor tools. Do not edit `.unity`, `.prefab`, `.meta` or `.cs` files with `patch`, `write_file` or the terminal, and do not run `Unity -batchmode` yourself. The editor holds the live scene, and a file written behind its back is overwritten by the next save.

Answer in the language the user used. Do not invent values a tool did not return.

## Search

`tool_search` matches English words only. Search with an English phrase that contains `unity`:

- `unity scene hierarchy`
- `unity gameobject`
- `unity c# script`
- `unity plan change`
- `unity play mode`
- `unity console`
- `unity tests`
- `unity component values`
- `unity build`

Tool names, each called as `mcp__csharp_game_editor__<name>`:

`unity_editor`, `unity_scene`, `unity_object`, `unity_script`, `unity_asset`, `unity_look`, `unity_ui`, `unity_vfx`, `unity_animation`, `unity_graphics`, `unity_physics`, `unity_probuilder`, `unity_profiler`, `unity_build`, `unity_packages`, `unity_code`, `unity_tests`, `unity_docs`, `unity_generate`, `plan_batch`, `apply_plan`, `confirm_risky_plan`

The 19 `unity_*` tools take `op` and `arguments`. Their schema (read it with `tool_describe`) lists every op, which ops are reads, and every argument with its type. For one op's arguments in full and what it does inside (saves, deletes, compiles, loads, runs code), call that tool with `{"op":"describe","arguments":{"op":"<op>"}}`; it is a read. `plan_batch` takes `steps`; each step is `tool`, `op`, `arguments` with the same names. `apply_plan` and `confirm_risky_plan` take `plan_id`.

## Procedure

Look at files without asking Unity. These read the bytes on disk and do not load an asset:

- `unity_asset` op `read_text` with `{"path": "Assets/Scripts/Player.cs"}` (a `.unity`, `.prefab`, `.asset`, or `.cs` file)
- `unity_asset` op `asset_find` with `{"type": "prefab"}` or `{"name": "Coin"}`
- `unity_asset` op `prefab_info` with `{"path": "Assets/Prefabs/Coin.prefab"}` (a plain text prefab; a nested or stripped prefab, or a file with a byte-order mark, is refused)

Anything that asks the editor is a plan, including a read. Call it, show the plan, then `apply_plan`:

- `unity_scene` op `manage_scene.get_hierarchy`, `manage_scene.get_loaded_scenes`
- `unity_editor` op `read_console.get`, `mcpforunity://editor/state`
- `unity_script` op `manage_script.read`, `validate_script`
- `unity_object` op `component_values` with `{"path": "Player"}` (the plan shows the C# that reads SerializedObject)
- `unity_code` op `unity_reflect.get_member`
- `unity_docs` op `unity_docs.get_doc` sends the query to docs.unity3d.com; Hermes asks, and the reply is a plan

If a reply says more than one Unity editor is open, call `unity_editor` op `set_active_instance` with `{"instance": "<name@hash>"}` from that reply. It only picks the editor.

Make one change as one plan. Put the whole feature in one `plan_batch`: scripts, objects, save, and play if the user wants to play it. Example, a coin the player can collect:

```json
{"steps":[
  {"tool":"unity_script","op":"create_script","arguments":{"path":"Assets/Scripts/Coin.cs","contents":"using UnityEngine;\npublic class Coin : MonoBehaviour {\n  void Update(){ transform.Rotate(0f, 180f * Time.deltaTime, 0f); }\n  void OnTriggerEnter(Collider other){ if (other.CompareTag(\"Player\")) Destroy(gameObject); }\n}\n"}},
  {"tool":"unity_object","op":"manage_gameobject.create","arguments":{"name":"Coin","primitive_type":"Sphere","position":[3,0.75,0],"components_to_add":["Coin"],"component_properties":{"SphereCollider":{"isTrigger":true}}}},
  {"tool":"unity_scene","op":"manage_scene.save","arguments":{"path":"Assets/Scenes/Main.unity"}},
  {"tool":"unity_editor","op":"manage_editor.play","arguments":{}}
]}
```

`plan_batch` does not run the steps, and it does not run C# in the editor. It returns the plan in words: each step, every value (script text in full), each file it creates, replaces, or deletes, code that runs, what is lost, and "inside:" lines drafted from MCP for Unity's own code (for example `run_tests` saves an open scene with unsaved changes first, with that file's sha256). Overwriting an existing `.asset` lists every serialized field of the one MonoBehaviour document, including fields inside lists. If that document cannot be read, there is no plan. The editor value is read when `apply_plan` runs, and the replace is sent only when that read is not dirty. A dirty value is named in the error and is not overwritten. A text edit names the characters the range removes. `create_script` with `overwrite` true shows the file's current text; if that text cannot be shown, there is no plan. Show that whole text to the user. Then call `apply_plan` with the `plan_id` from it. Only the newest plan runs, once, within 10 minutes. Calling an editor read or a change on a `unity_*` tool also returns a plan (that step is not sent).

`apply_plan` copies the open scenes that have unsaved changes, the files the plan names, and their `.meta` files, then runs the steps. A file that changed and was not named in the plan is put back, and a file this apply created that the plan did not name is put back. A .meta stays when the asset or folder was already on disk before the plan. `plan_batch` only accepts steps, so the error does not ask for that file to be named. Assets and folders under `Assets` with no `.meta` yet are named in the plan, and the `.meta` Unity writes for them is kept. A Unity `.meta` (it starts with `fileFormatVersion`) whose asset or folder is already missing is named too, and a change Unity makes to it is kept. A `.meta` that does not start that way is still put back. When `Packages/manifest.json` lists a package that `Packages/packages-lock.json` does not, the plan names the lock file and Unity's rewrite of it is kept. A lock that already lists every manifest package is still put back if it changes. (`Library`, `Temp`, `Logs`, `obj`, `.git`, and hidden directories are left out; `UserSettings` and the project root are included.) Unity's own window layouts under `UserSettings/Layouts` (`.dwlt`) are not put back. A file that was on disk when the plan was made is put back even if it was already gone when the steps started. A script already on disk that changed after the last compile, and that Unity runs by itself, is editor code when the plan compiles: second question. A package add or remove names `Packages/manifest.json` and `Packages/packages-lock.json`, so those two are not put back. Say a step worked only when the first line says `done`. Play mode is done only when the editor is in play mode and the frame count advanced. A compile is done only after a compile started and finished and the console has no `error CS` from it. A test run is done only from the job's per-test rows, checked against the summary and against progress; "succeeded" in the job reply is not the result. A failed test, 0 tests, or a job with no row per test is an error. MCP for Unity 10.3.0 does not write a result file. A player build is done only when the output path is on disk and its bytes changed. Upstream's "succeeded" is not the result. After a script step the plugin waits for that compile. If it fails, later steps are not sent.

Save with `manage_scene.save` and `{"path": "Assets/Scenes/Name.unity"}` when the open scene has no file yet. In play mode Unity refuses `manage_gameobject.modify`; stop play mode first. `manage_editor.stop` drops every change made during play.

To add tests, put `unity_script` op `create_asmdef` steps in the plan: `{"path":"Assets/Scripts/Game.asmdef","kind":"game"}` for the game's scripts, then `{"path":"Assets/Tests/EditMode/Game.Tests.EditMode.asmdef","kind":"editmode_tests","references":["Game"]}` (and `playmode_tests` the same way), then the test scripts with `create_script`. To run tests, plan `unity_tests` op `run_tests` with `{"mode":"EditMode"}` or `{"mode":"PlayMode"}` and apply it. `apply_plan` waits for the job and counts its per-test rows. A failed test, 0 tests, or a job with no row per test is an error. Say the tests passed only when the first line says `done` and the note says how many passed. Do not plan `run_tests` while an untitled scene is unsaved: the plan is refused, because a GUI editor would stop on Unity's save dialog.

A player build goes to `Builds/<target>/` in the project (`output_path` such as `Builds/StandaloneOSX/Game.app`), never inside `Assets`. Say it worked only when the reply says that output path is on disk. A path that was already there and did not change is an error.

## Approval

`plan_batch` never asks. Hermes asks once before `apply_plan` runs: "MCP tool 'apply_plan' on UNTRUSTED server 'csharp-game-editor' wants to run". That dialog does not show the change, so the plan text you showed is what the user approves. Never call `apply_plan` for a plan the user has not seen.

A plan that deletes, runs editor code, can lose unsaved work, saves unsaved changes over a scene file, or sends or writes outside the project says "Second question" at the top. On a gateway chat, `apply_plan` then asks a second question with the full summary of those risks. The code is not shortened. If the summary does not fit the chat card (Telegram counts the escaped text), it is not sent. In the terminal CLI Hermes cannot show that question, so `apply_plan` runs nothing and replies "call confirm_risky_plan with plan_id ...". Then tell the user what the plan deletes, runs, loses, saves over, or sends, including the code in full, and call `confirm_risky_plan` with that `plan_id`; Hermes asks once more. Play mode and tests run the project's code; they do not get the second question.

Accept runs every step of that plan, in order, once. Deny runs none. Every `apply_plan` asks again; a session answer does not carry over. A plan runs only in the Hermes session that made it.

If the editor changed after the plan (another editor selected, play mode, the open scenes, their objects, or a file the plan names), nothing runs and the reply says what changed. Component values are not part of that check. Make a new plan and show it again.

If the user or Hermes denies, say that nothing ran. Do not retry, and do not do the same change with the terminal or `write_file`. Cron and other sessions with nobody to answer decline, so a change does not run there. Reads still run.

## When a call fails

Quote the first line. Use the phrase in the reply.

- `changes Unity, so that step was not sent` → the reply is a plan. Show it, then `apply_plan`. Making the plan did not run C# in the editor.
- `unknown op` → pick an op from the list in the reply (it names the closest ones).
- `does not take` → use the argument names and types listed in the reply.
- `more than one Unity editor is open` → call `set_active_instance` with one id from the reply.
- `replaced by a newer plan` → only the newest plan runs. Show the newest plan, or plan again.
- `older than 10 minutes` → plan again and show it.
- `changed after the plan` → make a new plan and show it again. Nothing ran.
- `already used plan_id` → a plan runs once. Make a new plan.
- `did not approve` → the user denied it. Nothing ran. Do not retry.
- `FAILED at step` → that step did not do what the plan said (the reply says why); later steps were not sent. Read the console or the scene before planning again.
- `the last compile has errors` → play mode and tests are refused until the scripts compile. Fix them in a plan first (the plugin compiles before the play or test step).
- `0 tests ran` → no test matched, or the test assembly did not compile. Check the `.asmdef` references.
- `create_script writes C# only` → for an `.asmdef` use `create_asmdef`.
- `call confirm_risky_plan` → tell the user what the plan deletes, runs, loses, or sends, then call `confirm_risky_plan` with the plan_id.
- `nobody answered` → nothing ran; the plan is kept for 10 minutes.
- `error CS` → the script did not compile. The later steps did not run. Fix the script, then plan again.
- `did not start a compile` → in play mode Unity can hold a compile until play stops. Stop play mode, then plan again.
- `percent-encoding` → the path cannot be decoded the way Unity decodes it. Nothing was sent.
- `key or credential` or `hidden` or `symbolic link` or `outside Assets` → the plugin does not reach that file. Nothing was sent.
- `upstream writes this under the project's` → use the `Builds/` or `MemoryCaptures/` path the reply names.
- `a whole project folder` → name files or folders inside `Assets`, not `Assets` itself.
- `Quit is not sent` → `File/Quit`, `File/Exit` and `Unity/Quit` are refused.
- `has no file yet` → give `manage_scene.save` a path such as `Assets/Scenes/Main.unity`.
- `changed on disk` → the `.unity` file changed since this session first saw it. Pass `overwrite_disk_changes` true only if the user wants the editor copy kept.
- `already exists` → the file is there. Edit it, or pass `overwrite` true if the user wants it replaced.
- `changed since that precondition_sha256` → read the script again and plan with its current text.
- `cannot show` or `refused` for `batch_execute`, `replay`, or `execute_custom_tool` → send the steps or the code directly in `plan_batch`.
- `would be cut` → the plan text is too long to show. Split the work into two plans.
- `No Unity Editor instances found` → open the project and check MCP for Unity's transport (Window > MCP for Unity), then read once.
- `0 results` → the name did not match. Read `manage_scene.get_hierarchy` and use that name.
- `later steps were not sent` → an earlier step failed. Do not assume the later ones ran.
- `still compiling` → Unity is busy. Read `mcpforunity://editor/state`, then try again; a kept plan can be applied again.
- `is not offered` or `is not in the running MCP for Unity's tool list` → that upstream tool is not available on this transport.
- `did not answer in time` → Unity is busy. Read the console before trying again.
- `truncated` → the reply was cut. Ask for a smaller page.
- `Unity is not at` → install the editor with Unity Hub.

## Limits

Play mode in the editor does not read the user's keyboard through these tools; the user presses Play in Unity to play by hand. Screenshots render a camera into a PNG under `Assets/Screenshots`.

This skill does not change EditorPrefs. Do not use MCP for Unity's Configure buttons for other clients as a way to use Hermes. Paid asset generation (`unity_generate`) is a plan like any change; use it only when the user asked.
