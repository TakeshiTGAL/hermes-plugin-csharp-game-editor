"""A stand-in for the MCP for Unity server used by the offline tests. Standard library only.

    python fake_upstream.py <calls.jsonl> [mode]

mode:
  normal      tools and resources like mcpforunityserver 10.3.0 (names and actions from upstream_schemas.json);
              with FAKE_PROJECT_PATH set, an editor is "connected" to that folder, otherwise no editor
  drop_op     like normal, but manage_scene has no get_loaded_scenes action
  start_fail  prints an error to stderr and exits 1
  big         every tools/call answers with 300 KB of text
  slow        tools/call never answers
  reconnect   the first tools/call answers "Could not connect to Unity"; later calls succeed
  old_error   read_console returns an old error CS and one that names Assets/Game/Coin.cs
  compile_error  like normal, but after create_script read_console returns an error CS line
  two_editors like normal, but two editors are open and none is selected until set_active_instance
Every tools/call and resources/read it receives is appended to calls.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

CALLS = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "normal"
SCHEMAS = json.loads((Path(__file__).resolve().parents[1] / "bridge" / "upstream_schemas.json").read_text())["tools"]
ROOT = os.environ.get("FAKE_PROJECT_PATH", "")


def _write_missing_metas(root: Path) -> None:
    """Write a .meta for each asset and folder under Assets that does not have one, as an import would."""
    assets = root / "Assets"
    if not assets.is_dir():
        return
    for current, dirs, files in os.walk(assets):
        dirs[:] = [item for item in dirs if not item.startswith(".")]
        folder = Path(current)
        if folder != assets and not Path(str(folder) + ".meta").exists():
            Path(str(folder) + ".meta").write_text("fileFormatVersion: 2\nguid: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n")
        for name in files:
            if name.startswith(".") or name.endswith(".meta"):
                continue
            full = folder / name
            if not Path(str(full) + ".meta").exists():
                Path(str(full) + ".meta").write_text("fileFormatVersion: 2\nguid: cccccccccccccccccccccccccccccccc\n")


def _unity_create(path: Path, data: str) -> None:
    """Write a file the way Unity does: a .meta for the file, and a .meta for each folder this call creates."""
    created = []
    cursor = path.parent
    while not cursor.exists():
        created.append(cursor)
        cursor = cursor.parent
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)
    Path(str(path) + ".meta").write_text("fileFormatVersion: 2\nguid: 0123456789abcdef0123456789abcdef\n")
    for folder in created:
        meta = Path(str(folder) + ".meta")
        if not meta.exists():
            meta.write_text("fileFormatVersion: 2\nguid: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n")


def _finished_job(job_id: str, total: int, failed: int, status: str, row_failed: int | None = None) -> dict:
    """A finished get_test_job body. row_failed lets the rows disagree with the summary (the old result-file lie)."""
    if row_failed is None:
        row_failed = failed
    passed = total - failed
    results = [{"name": f"T{index}", "fullName": f"T{index}",
                "state": "Failed" if index < row_failed else "Passed"} for index in range(total)]
    return {"success": True, "data": {
        "job_id": job_id, "status": status, "mode": "EditMode",
        "started_unix_ms": 1000, "finished_unix_ms": 2000,
        "progress": {"completed": total, "total": total, "failures_so_far": []},
        "error": None,
        "result": {"mode": "EditMode",
                   "summary": {"total": total, "passed": passed, "failed": failed, "skipped": 0},
                   "results": results},
    }}
NO_EDITOR = ("{\"success\":false,\"message\":\"success=False message=None error='No Unity Editor instances found. "
             "Please ensure Unity is running with MCP for Unity bridge.' data=None hint=None\"}")
RESOURCES = ["mcpforunity://editor/state", "mcpforunity://project/info", "mcpforunity://editor/selection",
             "mcpforunity://editor/active-tool", "mcpforunity://editor/windows", "mcpforunity://editor/prefab-stage",
             "mcpforunity://project/tags", "mcpforunity://project/layers", "mcpforunity://menu-items",
             "mcpforunity://instances", "mcpforunity://scene/cameras", "mcpforunity://scene/volumes",
             "mcpforunity://pipeline/renderer-features", "mcpforunity://rendering/stats",
             "mcpforunity://scene/gameobject-api", "mcpforunity://prefab-api", "mcpforunity://tests",
             "mcpforunity://tool-groups"]
TEMPLATES = ["mcpforunity://scene/gameobject/{instance_id}", "mcpforunity://scene/gameobject/{instance_id}/components",
             "mcpforunity://scene/gameobject/{instance_id}/component/{component_name}", "mcpforunity://tests/{mode}",
             "mcpforunity://prefab/{encoded_path}", "mcpforunity://prefab/{encoded_path}/hierarchy"]


STATE = {"objects": [], "compile_started": 0, "compile_finished": 0, "selected": None, "playing": False,
         "compiled_once": False, "values": [], "dirty": True, "frame": 0}
# no_play: manage_editor play answers "Entered play mode." but the editor never enters it (upstream 10.3.0 does the
# same when scripts have compile errors). no_file_effects: deletes, edits, and saves answer success and change
# nothing on disk.
IDS = ["proj@1", "other@2"] if MODE == "two_editors" else ["proj@1"]


def now_ms() -> int:
    return int(time.time() * 1000)


def tools() -> list[dict]:
    out = []
    for name, spec in SCHEMAS.items():
        props = json.loads(json.dumps(spec["properties"]))
        if MODE == "drop_op" and name == "manage_scene":
            props["action"]["enum"] = [a for a in props["action"]["enum"] if a != "get_loaded_scenes"]
        out.append({"name": name, "description": spec.get("description", ""),
                    "inputSchema": {"type": "object", "properties": props, "required": spec["required"]}})
    out.append({"name": "execute_custom_tool", "description": "Run one project custom tool.",
                "inputSchema": {"type": "object", "properties": {
                    "tool_name": {"type": "string"},
                    "parameters": {"type": "object"}}, "required": ["tool_name"]}})
    return out


def text(obj) -> dict:
    return {"content": [{"type": "text", "text": obj if isinstance(obj, str) else json.dumps(obj)}], "isError": False}


def reply(mid, result) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}) + "\n")
    sys.stdout.flush()


def call_tool(name: str, args: dict) -> dict:
    if not ROOT:
        return text(NO_EDITOR)
    if MODE == "big":
        return text("x" * 300_000)
    action = args.get("action")
    if MODE == "reconnect":
        try:
            logged = Path(CALLS).read_text(encoding="utf-8").splitlines()
        except OSError:
            logged = []
        tool_calls = [line for line in logged if '"method": "tools/call"' in line]
        # The current call is already logged, so the first tools/call is the only one.
        if len(tool_calls) <= 1:
            return text("Could not connect to Unity. The editor may be reloading.")
    if name == "set_active_instance":
        if args.get("instance") not in IDS:
            return text({"success": False, "error": "no such instance"})
        STATE["selected"] = args["instance"]
        return text({"success": True, "message": "Active instance set", "data": {"instance": args["instance"]}})
    if MODE == "two_editors" and STATE["selected"] is None:
        return text({"success": False, "error": "Multiple Unity instances are connected and none is selected."})
    if name == "manage_scene" and action == "get_hierarchy":
        objects = list(STATE["objects"])
        if (Path(ROOT) / "Assets" / "intruder.txt").exists():
            objects.append("Intruder")
        items = [{"name": item, "instanceID": 100 + index} for index, item in enumerate(objects)]
        return text({"success": True, "data": {"items": items, "total": len(items)}})
    if name == "manage_gameobject" and action == "create":
        STATE["objects"].append(args.get("name") or "GameObject")
        STATE["dirty"] = True
    if name == "manage_editor" and action in ("play", "stop"):
        if action == "play" and MODE == "orphan_refresh" and ROOT:
            meta = Path(ROOT) / "Assets" / "surprise.txt.meta"
            if meta.is_file():
                meta.write_text("fileFormatVersion: 2\nguid: changed\n")
        if action == "play" and MODE == "lock_refresh" and ROOT:
            lock = Path(ROOT) / "Packages" / "packages-lock.json"
            if lock.is_file():
                lock.write_text('{"dependencies":{"com.unity.test-framework":{"version":"1.8.0"}}}\n')
        if action == "stop":
            STATE["playing"] = False
        elif MODE != "no_play":
            STATE["playing"] = True
        return text({"success": True, "message": "Entered play mode." if action == "play" else "Exited play mode."})
    if name == "manage_scene" and action == "get_loaded_scenes":
        if MODE == "untitled":
            return text({"success": True, "data": {"scenes": [{"name": "Untitled", "path": "", "isDirty": True,
                                                              "isActive": True}]}})
        return text({"success": True, "data": {"scenes": [{"name": "Main", "path": "Assets/Scenes/Main.unity",
                                                          "isDirty": STATE["dirty"], "isActive": True}]}})
    if MODE != "no_file_effects":
        target = None
        if name == "manage_asset" and action == "delete":
            target = Path(ROOT) / args["path"]
        if name == "delete_script":
            target = Path(ROOT) / args["uri"]
        if target is not None:
            if target.is_dir():
                import shutil
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
            meta = Path(str(target) + ".meta")
            if meta.exists():
                meta.unlink()
        if name == "apply_text_edits" and (Path(ROOT) / args["uri"]).exists():
            with open(Path(ROOT) / args["uri"], "a") as handle:
                handle.write("// edited\n")
        if name == "manage_scene" and action == "save":
            scene = Path(ROOT) / "Assets" / "Scenes" / "Main.unity"
            scene.parent.mkdir(parents=True, exist_ok=True)
            scene.write_text("%YAML 1.1\n# saved " + str(now_ms()) + "\n")
            STATE["dirty"] = False
        if name == "manage_scene" and action == "create" and args.get("name"):
            folder = Path(ROOT) / (args.get("path") or "Assets/Scenes")
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (args["name"] + ".unity")).write_text("%YAML 1.1\n")
        if name == "manage_scriptable_object" and action == "create":
            folder = Path(ROOT) / (args.get("folder_path") or "Assets")
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (args["asset_name"] + ".asset")).write_text("%YAML 1.1\n# " + str(now_ms()) + "\n")
    if name == "find_gameobjects" and args.get("search_term") == "Nobody":
        return text({"success": True, "message": "Found GameObjects", "data": {"instanceIDs": [], "totalCount": 0}})
    if name == "manage_components" and args.get("component_type") == "Rigidbodyy":
        msg = "Component type 'Rigidbodyy' not found. Use a fully-qualified name if needed."
        return text({"success": False, "code": msg, "error": msg})
    if name == "get_sha":
        p = Path(ROOT) / args["uri"]
        return text({"success": True, "data": {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "lengthBytes": 1}})
    if name == "create_script":
        p = Path(ROOT) / args["path"]
        if p.exists():
            msg = f"Script already exists at '{args['path']}'. Use 'update' action to modify."
            return text({"success": False, "code": msg, "error": msg})
        _unity_create(p, args["contents"])
        if MODE == "import_meta" and ROOT:
            _write_missing_metas(Path(ROOT))
        if MODE == "rogue_cs" and ROOT:
            rogue = Path(ROOT) / "Assets" / "Rogue.cs"
            rogue.write_text("public class Rogue {}\n")
            Path(str(rogue) + ".meta").write_text("guid: rogue\n")
        if MODE == "both_new" and ROOT:
            surprise = Path(ROOT) / "Assets" / "surprise.txt"
            surprise.write_text("surprise\n")
            Path(str(surprise) + ".meta").write_text("fileFormatVersion: 2\nguid: surprise\n")
            rogue = Path(ROOT) / "Assets" / "Rogue.cs"
            rogue.write_text("public class Rogue {}\n")
            Path(str(rogue) + ".meta").write_text("guid: rogue\n")
        STATE["compile_started"] = now_ms()
        STATE["compile_finished"] = now_ms()
        STATE["compiled_once"] = True
        return text({"success": True, "message": "created"})
    if name == "read_console":
        if MODE == "old_error":
            return text({"success": True, "message": "Retrieved 2 log entries.", "data": [
                "Assets/Old.cs(1,1): error CS0103: The name 'x' does not exist",
                "Assets/Game/Coin.cs(1,10): error CS0246: The type or namespace name 'Missing' could not be found",
            ]})
        if MODE == "compile_error" and STATE["compiled_once"]:
            return text({"success": True, "message": "Retrieved 1 log entries.", "data": [
                "Assets/Scripts/Coin.cs(3,5): error CS1002: ; expected"]})
        return text({"success": True, "message": "Retrieved 0 log entries.", "data": []})
    if name == "run_tests":
        if MODE == "pkg_write" and ROOT:
            man = Path(ROOT) / "Packages" / "manifest.json"
            man.parent.mkdir(parents=True, exist_ok=True)
            man.write_text('{"dependencies":{"com.unity.pkgwrite":"9.9.9"}}\n')
        if STATE["dirty"] and MODE != "no_file_effects" and ROOT:
            scene = Path(ROOT) / "Assets" / "Scenes" / "Main.unity"
            scene.parent.mkdir(parents=True, exist_ok=True)
            previous = scene.read_text(encoding="utf-8") if scene.exists() else ""
            scene.write_text(previous + "# saved by tests\n")
            STATE["dirty"] = False
        if MODE == "surprise" and ROOT:
            (Path(ROOT) / "Assets" / "surprise.txt").write_text("surprise\n")
        if MODE == "audio_loop" and ROOT:
            meta = Path(ROOT) / "Assets" / "Audio" / "Loop.wav.meta"
            meta.parent.mkdir(parents=True, exist_ok=True)
            meta.write_text("loopTime: 1\n")
        return text({"success": True, "data": {"job_id": {"tests_bad": "bad", "tests_zero": "zero",
                                                          "tests_lie": "lie"}.get(MODE, "ok")}})
    if name == "get_test_job":
        job = args.get("job_id")
        if job == "run":
            return text({"success": True, "data": {"job_id": "run", "status": "running",
                                                   "progress": {"completed": 1, "total": 4, "failures_so_far": []}}})
        if job == "zero":
            return text(_finished_job("zero", 0, 0, "succeeded"))
        if job == "bad":
            return text(_finished_job("bad", 2, 1, "failed"))
        if job == "lie":
            # summary says every test passed; one row says Failed. 10.3.0 has no result file to override it.
            return text(_finished_job("lie", 2, 0, "succeeded", row_failed=1))
        if job == "ok" and MODE == "no_results":
            payload = _finished_job("ok", 2, 0, "succeeded")
            payload["data"]["result"]["results"] = None
            return text(payload)
        if job in ("ok", "counts", "persisted", "lie"):
            return text(_finished_job(job, 2, 0, "succeeded"))
    if name == "refresh_unity":
        if args.get("compile") == "request":
            STATE["compile_started"] = now_ms()
            STATE["compile_finished"] = now_ms() + 1
            STATE["compiled_once"] = True
            if MODE == "outside" and ROOT:
                outside = Path(ROOT) / "UserSettings"
                outside.mkdir(parents=True, exist_ok=True)
                (outside / "claude_iol_outside.txt").write_text("wrote\n")
                (Path(ROOT) / "claude_iol_root.txt").write_text("wrote\n")
            if MODE == "orphan_meta" and ROOT:
                meta = Path(ROOT) / "Assets" / "Audio" / "Loop.wav.meta"
                meta.parent.mkdir(parents=True, exist_ok=True)
                meta.write_text("loopTime: 1\n")
                layout = Path(ROOT) / "UserSettings" / "Layouts" / "default-6000.dwlt"
                layout.parent.mkdir(parents=True, exist_ok=True)
                layout.write_text("layout-changed\n")
        return text({"success": True, "message": "Refresh requested.",
                     "data": {"compile_requested": args.get("compile") == "request", "compile_started": True}})
    if name == "execute_code" and "sha256:" in (args.get("code") or ""):
        blob = json.dumps([STATE["objects"], STATE["values"]])
        return text({"success": True, "data": {"result": "values:%d skipped:0 sha256:%s" % (
            len(STATE["objects"]), hashlib.sha256(blob.encode()).hexdigest())}})
    if name == "execute_code" and "GetComponentsInChildren<Transform>(true)" in (args.get("code") or ""):
        return text({"success": True, "data": {"result": "Player\n- UnityEngine.Transform\n    m_LocalPosition = (0, 1, 0)\n"}})
    if name == "manage_components" and action == "set_property":
        STATE["values"].append([args.get("target"), args.get("property"), args.get("value")])
    if name == "execute_code":
        code = args.get("code") or ""
        if "Time.frameCount" in code:
            if not STATE["playing"] or MODE == "play_frozen":
                return text({"success": True, "data": {"result": "0"}})
            STATE["frame"] += 1
            return text({"success": True, "data": {"result": str(STATE["frame"])}})
        if "both_sides " in code:
            if MODE == "asset_dirty":
                return text({"success": True, "data": {"result": "dirty\n{\"speed\":9}"}})
            return text({"success": True, "data": {"result": "not-loaded"}})
        if "MarkSceneDirty" in code:
            STATE["dirty"] = True
            return text({"success": True, "data": {"result": "dirty"}})
        if "SaveScene" in code and ", true)" in code:
            return text({"success": True, "data": {"result": "copied dirty=" + ("True" if STATE["dirty"] else "False")}})
        if action == "get_history":
            shown = {"history_match": "Debug.Log(1);", "history_other": "Debug.Log(999);",
                     "history_prefix": ("string SerialName" + (" " * 490) + "...")}.get(MODE, "")
            entries = [{"index": 0, "codePreview": shown, "safetyChecksEnabled": True, "compiler": "codedom"}] \
                if shown else []
            return text({"success": True, "data": {"entries": entries}})
        if "removed-confirmed" in code:
            if MODE == "prefab_removed":
                return text({"success": True, "data": {"result":
                             "prefab-children:1 removed-confirmed:1 scene-deleted:0 fileids:424242"}})
            if MODE == "prefab_signed":
                return text({"success": True, "data": {"result":
                             "prefab-children:1 removed-confirmed:1 scene-deleted:0 "
                             "fileids:-4733365628477956816 reverted:0 unconfirmed:0 added:0"}})
            if MODE == "added_child":
                return text({"success": True, "data": {"result":
                             "prefab-children:0 removed-confirmed:0 scene-deleted:0 fileids: "
                             "reverted:0 unconfirmed:0 added:1"}})
            if MODE == "group_reverted":
                return text({"success": True, "data": {"result":
                             "prefab-children:1 removed-confirmed:1 scene-deleted:1 fileids:7 "
                             "reverted:1 unconfirmed:1 added:1"}})
            if MODE == "prefab_unconfirmed":
                return text({"success": True, "data": {"result":
                             "prefab-children:1 removed-confirmed:0 scene-deleted:0 fileids:"}})
            if MODE == "scene_deleted":
                return text({"success": True, "data": {"result":
                             "prefab-children:0 removed-confirmed:0 scene-deleted:1 fileids:"}})
            if MODE == "prepass_fail":
                return text({"success": False, "error": "execute failed"})
            return text({"success": True, "data": {"result":
                         "prefab-children:0 removed-confirmed:0 scene-deleted:0 fileids:"}})
        return execute_reply()
    if MODE == "build_pending" and name == "manage_build":
        return text({"success": True, "_mcp_status": "pending", "data": {"job_id": "job-1"}})
    if MODE == "build_lie" and name == "manage_build":
        if args.get("action") == "status":
            return text({"success": True, "data": {"job_id": "job-1", "result": "succeeded",
                                                   "output": "Builds/Mac/Game.app"}})
        STATE["dirty"] = False
        if ROOT:
            scene = Path(ROOT) / "Assets" / "Scenes" / "Main.unity"
            scene.parent.mkdir(parents=True, exist_ok=True)
            scene.write_text("%YAML 1.1\n# saved by build\n")
        return text({"success": True, "message": "build started", "data": {"job_id": "job-1"}})
    if MODE == "prefab_removed" and name == "manage_gameobject" and action == "delete":
        return text({"success": False, "error": "Target not found using method 'by_path'."})
    if MODE == "prefab_unconfirmed" and name == "manage_gameobject" and action == "delete":
        return text({"success": True, "message": "deleted"})
    if name == "manage_packages" and action in ("add_package", "remove_package") and ROOT \
            and MODE != "no_file_effects":
        packages = Path(ROOT) / "Packages"
        packages.mkdir(parents=True, exist_ok=True)
        (packages / "manifest.json").write_text('{"dependencies":{"com.unity.test-framework":"1.6.0"}}\n')
        (packages / "packages-lock.json").write_text('{"dependencies":{"com.unity.test-framework":{"version":"1.6.0"}}}\n')
    body = {"success": True, "echo": {"name": name, "arguments": args}}
    if MODE != "no_id" and name in ("manage_gameobject", "manage_components", "manage_camera", "manage_prefabs"):
        body["data"] = {"instanceID": 4242}
    return text(body)


def read_resource(uri: str) -> dict:
    if uri == "mcpforunity://editor/state":
        unity = {"instance_id": "proj@1", "unity_version": "6000.6.6f1"} if ROOT else \
            {"instance_id": None, "unity_version": None}
        data = {"success": True, "data": {
            "observed_at_unix_ms": now_ms(), "sequence": now_ms() % 997, "unity": unity,
            "editor": {"play_mode": {"is_playing": STATE["playing"], "is_paused": False,
                                     "is_changing": STATE["playing"]},
                       "active_scene": {"path": "Assets/Scenes/Main.unity"}},
            "activity": {"phase": "idle"},
            "compilation": {"is_compiling": False, "is_domain_reload_pending": False,
                            "last_compile_started_unix_ms": STATE["compile_started"],
                            "last_compile_finished_unix_ms": STATE["compile_finished"]},
            "transport": {"last_message_unix_ms": now_ms()}}}
    elif uri == "mcpforunity://instances":
        data = {"success": True, "transport": "stdio", "instance_count": len(IDS),
                "instances": [{"id": item} for item in IDS]} if ROOT else \
            {"success": True, "instance_count": 0, "instances": []}
    elif uri == "mcpforunity://project/info":
        if MODE == "two_editors" and STATE["selected"] is None:
            return {"contents": [{"uri": uri, "text": json.dumps({"success": False, "error": "Multiple Unity "
                                                                  "instances are connected and none is selected."})}]}
        if not ROOT:
            return {"contents": [{"uri": uri, "text": NO_EDITOR}]}
        data = {"success": True, "data": {"projectRoot": ROOT, "projectName": "proj"}}
    elif not ROOT:
        return {"contents": [{"uri": uri, "text": NO_EDITOR}]}
    else:
        data = {"success": True, "echo": {"uri": uri}}
    return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data)}]}


def execute_reply() -> dict:
    """Record and delete pre-pass results. The C# text is not inspected."""
    if MODE == "no_result":
        return text({"success": True, "data": {}})
    if MODE == "prepass_fail":
        return text({"success": False, "error": "execute failed"})
    if MODE == "prefab_removed":
        return text({"success": True, "data": {"result": "prefab-children:1 removed-confirmed:1"}})
    if MODE == "prefab_unconfirmed":
        return text({"success": True, "data": {"result": "prefab-children:1 removed-confirmed:0"}})
    counts = {
        "record_gap": "no-object:0 not-recorded:1 memory-only:0 scene-dirty:0 recorded:0",
        "record_missing": "no-object:1 not-recorded:0 memory-only:0 scene-dirty:0 recorded:0",
        "record_memory": "no-object:0 not-recorded:0 memory-only:1 scene-dirty:0 recorded:0",
        "record_prefab": "no-object:0 not-recorded:0 memory-only:0 scene-dirty:0 recorded:1",
        "record_mixed": "no-object:0 not-recorded:1 memory-only:0 scene-dirty:0 recorded:1",
    }
    result = counts.get(MODE, "no-object:0 not-recorded:0 memory-only:0 scene-dirty:1 recorded:0")
    return text({"success": True, "data": {"result": result}})


def main() -> int:
    Path(CALLS + ".env.json").write_text(json.dumps(dict(os.environ), sort_keys=True), encoding="utf-8")
    if MODE == "start_fail":
        sys.stderr.write("fake upstream: could not start (test)\n")
        sys.stderr.flush()
        return 1
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        mid, method = msg.get("id"), msg.get("method")
        if mid is None:
            continue
        params = msg.get("params") or {}
        if method == "initialize":
            reply(mid, {"protocolVersion": params["protocolVersion"],
                        "capabilities": {"tools": {"listChanged": True}, "resources": {}, "prompts": {}},
                        "serverInfo": {"name": "fake-mcp-for-unity", "version": "10.3.0"}})
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/tools/list_changed"}) + "\n")
            sys.stdout.flush()
        elif method == "tools/list":
            reply(mid, {"tools": tools()})
        elif method == "resources/list":
            reply(mid, {"resources": [{"uri": u, "name": u} for u in RESOURCES]})
        elif method == "resources/templates/list":
            reply(mid, {"resourceTemplates": [{"uriTemplate": u, "name": u} for u in TEMPLATES]})
        elif method in ("tools/call", "resources/read"):
            with open(CALLS, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"method": method, **params}) + "\n")
            if MODE == "slow" and method == "tools/call":
                continue
            if method == "tools/call":
                reply(mid, call_tool(params["name"], params.get("arguments") or {}))
            else:
                reply(mid, read_resource(params["uri"]))
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid,
                                         "error": {"code": -32601, "message": "Method not found"}}) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
