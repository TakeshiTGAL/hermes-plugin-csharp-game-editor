# Claims for 0.6.0

Checked on macOS with Unity 6000.6.6f1 (a new project, no Roslyn package) and MCP for Unity 10.3.0, and offline against `tests/fake_upstream.py`. The live rows ran the bridge's upstream child with the environment from Hermes 0.22.2 `_build_safe_env`. Gateway cards were rendered with that Hermes source (`tests/test_gateway_render.py`, 2 passed).

## What is immediate

- `read_text`, `asset_find`, `prefab_info`, and `describe` read files on disk. They do not ask the editor when the project folder is already known. Live: `read_text` of `Assets/Editor/ObsProbe.cs` returned a sha256 and added no file.
- `set_active_instance` only picks which editor later plans use. It stays immediate because a plan cannot be measured until an editor is chosen, and choosing one does not run project code.
- A read that asks the editor (hierarchy, console, component values, reflection, a test job) returns a plan. The reply says that step was not sent. Making the plan does not send `execute_code`.

## What apply_plan does

- It copies open scenes that have unsaved changes, and the bytes of files the plan names, including `.meta` files. After the steps, a changed file the plan did not name is put back, and a file this apply created that the plan did not name is put back. A .meta stays when the asset or folder was already on disk before the plan. `plan_batch` only accepts steps, so the error does not ask for that file to be named. Assets and folders under `Assets` that have no `.meta` when the plan is made are named, and the `.meta` Unity writes for them is an effect of the plan. A Unity `.meta` (it starts with `fileFormatVersion`) whose asset or folder is already missing is named, and a change Unity makes to it is an effect of the plan. A `.meta` that does not start that way is still put back. When `Packages/manifest.json` lists a package that `Packages/packages-lock.json` does not, the plan names the lock file and Unity's rewrite of it is an effect of the plan. A lock that already lists every manifest package is still put back if it changes. `Library`, `Temp`, `Logs`, `obj`, `.git`, and hidden directories are left out. `UserSettings` and files at the project root are included. The plan names a new folder's `.meta`, every file inside a folder it deletes, and, for a package add or remove, `Packages/manifest.json` and `Packages/packages-lock.json`. Those are not put back. Unity's window layouts under `UserSettings/Layouts` (`.dwlt`) are not put back. A file present when the plan was made is put back even if it was already gone when the steps started.
- Live: a script with `[InitializeOnLoad]` that wrote `Assets/surprise.txt` and changed `Assets/Audio/Loop.wav.meta` was planned (the second question named the attribute). After apply, `Loop.wav.meta` was back to its earlier bytes, `surprise.txt` was removed, and the reply was `FAILED`.
- Measured on this Unity before the bridge change: `SaveScene` with `saveAsCopy` true leaves the scene unsaved. Writing the previous bytes back leaves `isDirty` false. The bridge marks the scene unsaved again after that restore. That mark was measured in a batchmode project, not repeated inside the live fixture's play row.

## What "done" means

- Play mode is done only when the editor state says it is playing and `Time.frameCount` advanced. Live: `manage_editor.play` returned `done` and `Unity is in play mode` (the frame check runs before that sentence). Upstream's "Entered play mode." is not the check. Offline, a playing editor whose frame stays 0 is an error.
- A compile is done only after a compile started and finished, then the console has no `error CS` from it.
- A test run is done only from the test job's per-test rows (`include_details`), checked against the summary (`passed` + `failed` + `skipped` equals `total`) and against progress (`completed` equals `total`). The job must have a start time and a finish time. MCP for Unity 10.3.0 does not write a result file. A job status of succeeded is not the result. A failed test, 0 tests, or a job that does not return one row per test is an error. Offline, one failed row is an error even when the summary says 0 failed. Live, on this editor: EditMode pass `tests: 1 passed, 0 failed of 1 (counted from the job)`; EditMode fail `1 of 1 tests failed (counted from the job's test rows)`; EditMode 0 `0 tests ran (counted from the job)`. PlayMode pass, fail, and 0 used the same three sentences.
- A player build is done only when the output path named in the plan is on disk and its bytes changed. Upstream's `succeeded` is quoted and is not the result. Offline, a job that says succeeded and writes no output is an error, and so is a path that was already there and did not change.

## What is refused

- A `.prefab` or `.asset` with a byte-order mark, and a prefab that is nested (`!u!1001`) or stripped, is refused and not interpreted. Live: both refusals returned `Nothing was sent.`
- Overwriting an existing `.asset` lists every serialized field of the one MonoBehaviour document, including fields inside lists. If that document cannot be read, there is no plan. The editor value is read when `apply_plan` runs, and the replace is sent only when that read is not dirty. A dirty value is named in the error and is not overwritten. `Garbage.asset` (not YAML) produces no plan. A text edit names the characters the range removes, and a removal is in the second question. `create_script` with `overwrite` true shows the file's current text in the plan. `run_tests` is refused when an open scene has no path.
- `create_script` refuses anything but `.cs` when the plan is made. `create_asmdef` writes one assembly definition.

## What the second question is

- The question is the full summary. Code is not shortened. It is sent only when it fits 1,650 raw characters and Hermes 0.22.2's Telegram (escaped UTF-16), Slack, and Discord cards can show every line. A summary that does not fit is not sent; `confirm_risky_plan` is the next step. Hidden characters are escaped (`\u2028`). `tests/test_gateway_render.py` covers a question full of `&` and a question whose code does not fit.
- Play mode and tests do not get that second question. The plan says they run the project's own scripts.
