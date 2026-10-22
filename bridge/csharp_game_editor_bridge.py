#!/usr/bin/env python3
"""csharp-game-editor: a stdio MCP server between Hermes and MCP for Unity (mcpforunityserver 10.3.0).

Standard library only. The reads in read_allowlist.json are disk text (.unity, .prefab, .asset, .cs), describe,
and set_active_instance. Any other op, including a read that asks the editor, comes back as a plan (nothing runs).
plan_batch (read-only, no question) measures the editor and returns the whole change in words with a plan_id and a
fingerprint of the state it was made against. "inside:" lines are a draft from the side effect table
(tools/extract_side_effects.py); they are not the success check. apply_plan copies unsaved scenes and the files the
plan names, runs the steps, and puts back a file the plan did not name. A .meta stays when its asset or
folder was already on disk. apply_plan and confirm_risky_plan (and
unity_docs, which sends) are not marked read-only, so a trust: untrusted server makes Hermes ask before they run.
Only the newest plan can run, once, within ten minutes, and only while the editor still matches the fingerprint.
A plan that deletes, runs editor code, can lose unsaved work, saves over unsaved changes, or sends or writes
outside the project also asks a second question with a short summary of those risks (an MCP elicitation;
confirm_risky_plan where none can be shown). Done means a separate measurement: play mode and a frame that
advanced, a compile that started and finished then a console with no error CS, or a test job whose rows, totals, and
start and finish times agree. Upstream's success sentence is not that measurement. MCP for Unity 10.3.0 does not
write a test result file.

EditorPrefs are read and never written. Only an explicit 0 starts a stdio child. Anything else uses
HTTP on a loopback address. A server already listening on that port is attached and is not stopped.
The child environment has no HOME. Telemetry and the update check are forced off.
"""

from __future__ import annotations

import difflib
import glob
import hashlib
import html
import json
import os
import re
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSION = "0.6.0"
UPSTREAM_VERSION = "10.3.0"
NAME = "csharp-game-editor"
CALL_TIMEOUT = 120.0
LONG_TIMEOUT = 290.0
START_TIMEOUT = 90.0
READY_WAIT = 60.0
SHUTDOWN_GRACE = 10.0
MAX_RESULT_BYTES = 256 * 1024
MAX_STDERR = 2048
MESSAGE_CAP = 40000
COMPILE_WAIT = 240.0
PLAY_WAIT = 30.0
FRAME_WAIT = 8.0
_IMPORT_SHOWN = 6
PLAN_TTL = 600.0
APPLY_BUDGET = 270.0
ELICIT_WAIT = 330.0
FAST_CANCEL = 3.0
HANDSHAKE_VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
CHILD_PROTOCOL = "2025-06-18"
NOTHING_SENT = "Nothing was sent."

_HERE = Path(__file__).resolve().parent
_TABLE_BYTES = (_HERE / "ops_table.json").read_bytes()
TABLE = json.loads(_TABLE_BYTES.decode("utf-8"))
TABLE_SHA = hashlib.sha256(_TABLE_BYTES).hexdigest()


def _normalize_table(table: dict) -> None:
    """An upstream tool without an action parameter is one op named after the tool.

    The extractor split some of them by the C# cases their Python wrapper sends (apply_text_edits.read,
    script_apply_edits.get_sha). Those names looked like reads but sent the caller's edits. They are
    merged here, with the union of flags and params, so a name never promises less than the call does.
    """
    for body in table["bundles"].values():
        ops = body["ops"]
        groups: dict[str, list[str]] = {}
        for key, spec in ops.items():
            if spec.get("action_param") or not spec.get("upstream_tool"):
                continue
            groups.setdefault(spec["upstream_tool"], []).append(key)
        for tool, keys in groups.items():
            if keys == [tool]:
                continue
            merged = dict(ops[keys[0]])
            params: list[str] = []
            for key in keys:
                for param in ops[key].get("params") or []:
                    if param not in params:
                        params.append(param)
            merged["action"] = None
            merged["params"] = params
            merged["flags"] = sorted({flag for key in keys for flag in (ops[key].get("flags") or [])})
            merged["evidence"] = sorted({item for key in keys for item in (ops[key].get("evidence") or [])})
            merged["file_params"] = sorted({item for key in keys for item in (ops[key].get("file_params") or [])})
            seen_sites: set = set()
            merged["effects"] = []
            for key in keys:
                for row in ops[key].get("effects") or []:
                    if (row["kind"], row["at"]) not in seen_sites:
                        seen_sites.add((row["kind"], row["at"]))
                        merged["effects"].append(row)
            for key in keys:
                del ops[key]
            ops[tool] = merged


_normalize_table(TABLE)
READ_ALLOW = frozenset(json.loads((_HERE / "read_allowlist.json").read_text(encoding="utf-8")))
GUARDS = list(TABLE["guards"])
# Upstream blocks File/Quit. File/Exit and Unity/Quit close the editor the same way and drop unsaved work.
BLOCKED_MENUS = frozenset({str(item).strip().lower() for item in TABLE["blocked_menus"]}
                          | {"file/quit", "file/exit", "unity/quit"})
PROJECT_ROOT_FOLDERS = frozenset({"assets", "packages", "projectsettings", "library", "usersettings"})
RESOURCES = list(TABLE["resources"])
# Upstream's own command line asks before these deletes (confirm_destructive_action in its CLI). The MCP tools do
# not. A plan step for the same action repeats that question, so approving the plan is the answer to it.
_CONFIRM_FILES = {"asset.py": ("manage_asset", "delete"), "component.py": ("manage_components", "remove"),
                  "gameobject.py": ("manage_gameobject", "delete"), "script.py": ("manage_script", "delete"),
                  "shader.py": ("manage_shader", "delete"), "texture.py": ("manage_texture", "delete")}
UPSTREAM_CONFIRMS: dict[tuple[str, str], str] = {}
for _row in GUARDS:
    _hit = re.search(r'confirm_destructive_action\("(\w+)", "?(\w+)"?', str(_row.get("text", "")))
    _target = _CONFIRM_FILES.get(str(_row.get("file", "")).rsplit("/", 1)[-1])
    if _row.get("kind") == "confirm" and _hit and _target:
        _item = "component" if _hit.group(2) == "component_type" else _hit.group(2)
        UPSTREAM_CONFIRMS[_target] = f"{_hit.group(1)} {_item}"
UPSTREAM_CONFIRMS[("delete_script", "")] = UPSTREAM_CONFIRMS.get(("manage_script", "delete"), "Delete script")

HTTP_ACTIVATE_GROUPS = ("docs", "vfx", "animation", "ui", "scripting_ext", "testing", "probuilder",
                        "profiling", "asset_gen")
HUB_UNITY_GLOB = "/Applications/Unity/Hub/Editor/*/Unity.app"
DEFAULT_HTTP_URL = "http://127.0.0.1:8080"
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
CHILD_ENV_KEYS = ("PATH", "PYTHONPATH", "UNITY_MCP_LOG_DIR", "FAKE_PROJECT_PATH")
# Path arguments: the names the 0.4 check used, plus every argument that upstream's own code hands to a file
# system call. The second set is extracted from the upstream source by tools/extract_unity_ops.py (file_params).
PATH_KEYS = frozenset({
    "path", "prefab_path", "uri", "destination", "clip_path", "controller_path", "material_path",
    "folder_path", "prefab_folder", "profile_path", "source_asset", "image_path", "scene_path",
    "output_folder", "log_file", "snapshot_path", "search_path", "object_path", "output_path",
    "output_dir", "source_path", "snapshot_a", "snapshot_b", "screenshot_file_name",
})
NON_PATH = frozenset({
    "code", "contents", "text", "commands", "prompt", "query", "queries", "pattern", "filter_text",
    "newText", "message", "description", "shader", "source", "menu_path", "scene_name", "edits", "search_term",
})
# Files a build or the profiler writes go where upstream puts them by default: <project>/Builds and
# <project>/MemoryCaptures (and Unity's temp cache for a snapshot with no path). Never inside Assets.
OUTPUT_HEADS = {
    "output_path": ("Builds",), "output_dir": ("Builds",), "snapshot_path": ("MemoryCaptures",),
    "snapshot_a": ("MemoryCaptures",), "snapshot_b": ("MemoryCaptures",), "search_path": ("MemoryCaptures",),
    "log_file": ("MemoryCaptures", "Logs"),
}
OUTPUT_OPS = frozenset({"manage_build.build", "manage_build.batch", "manage_profiler.memory_take_snapshot",
                        "manage_profiler.memory_compare_snapshots", "manage_profiler.memory_list_snapshots",
                        "manage_profiler.profiler_start"})
BRIDGE_KEYS = frozenset({"overwrite", "overwrite_disk_changes"})
TOOL_ORDER = (
    "unity_editor", "unity_scene", "unity_object", "unity_script", "unity_asset", "unity_look",
    "unity_ui", "unity_vfx", "unity_animation", "unity_graphics", "unity_physics", "unity_probuilder",
    "unity_profiler", "unity_build", "unity_packages", "unity_code", "unity_tests", "unity_docs",
    "unity_generate", "plan_batch", "apply_plan", "confirm_risky_plan",
)
PLAN_TOOLS = ("plan_batch", "apply_plan", "confirm_risky_plan")
PLAN_FIRST = "Plan a Unity scene, script, or play mode change."
APPLY_FIRST = "Apply a planned Unity scene or script change."
CONFIRM_FIRST = "Confirm a Unity plan that deletes or runs code."
CONFIRM_NOTE = (
    " Only when apply_plan says the second question could not be shown (the classic CLI fails MCP questions closed,"
    " or the summary would not fit a chat card). Hermes asks once more before it runs; show the user what the plan"
    " deletes, runs, loses, saves over, or sends first. Runs that newest plan once if the editor still matches it."
)
# One factual sentence per tool in the words people use for the job (Tool Search matches English words only).
TOOL_WORDS = {
    "unity_editor": " Enter, pause, or exit play mode, and read console logs, warnings, and compile errors.",
    "unity_scene": " Read the scene hierarchy, and open, create, or save a .unity scene file.",
    "unity_object": (" Create, find, move, or delete GameObjects, add components such as a Rigidbody, a collider,"
                     " or a script, and read component values."),
    "unity_script": " Write, edit, validate, or delete a C# MonoBehaviour script, then check it compiles.",
    "unity_asset": " Find, move, or delete assets and prefabs in the Assets folder.",
    "unity_physics": " Rigidbody, colliders, raycasts, gravity, and physics simulation steps.",
    "unity_tests": " Run EditMode and PlayMode unit tests and read the results.",
    "unity_look": " Colors, materials, shaders, textures, cameras, and screenshots.",
    "unity_build": " Build a standalone player for Mac, Windows, or other platforms into Builds/.",
    "unity_packages": " Unity Package Manager: install, remove, or update packages.",
    "unity_code": " Check a class or member exists (reflection) before writing C#.",
    "unity_docs": " Read Unity ScriptReference and Manual pages.",
    "plan_batch": (" Use it for Unity game engine automation: scripts, GameObjects, prefabs, scenes, and play mode"
                   " as one plan the user approves once."),
}
READ_NOTE = (
    " A listed read runs now and its text goes to the model. Any other op runs nothing here and comes back as a"
    " plan with a plan_id: show it, then call apply_plan. op describe returns one op's arguments and what it does"
    " inside. For a C# game through MCP for Unity: scene, GameObject, prefab, console, play mode, tests."
)
DOCS_NOTE = (
    " Sends the query to docs.unity3d.com and returns what the page says, so Hermes asks before each call."
    " Nothing in the project changes. describe explains an op's arguments."
)
PLAN_NOTE = (
    " It changes nothing; it only reads the editor. Returns every step in words: values, files created, replaced,"
    " or deleted, code that runs, and what is lost, plus plan_id. Show that text to the user. One feature is one"
    " plan; after a script change the plugin asks Unity to compile and waits for it."
)
APPLY_NOTE = (
    " Hermes asks once before it runs. The dialog names only this tool, so show the plan text first. A plan that"
    " deletes, runs editor code, can lose unsaved work, or saves or sends also asks a second question with a short"
    " summary (or, where Hermes cannot show one, asks for confirm_risky_plan). Runs the newest plan once, in order,"
    " and reads the editor back after each step: the first line says done or FAILED. If the editor changed after"
    " the plan, it runs nothing."
)
# C# for component_values. It runs only inside apply_plan, through execute_code. A component that implements
# ISerializationCallbackReceiver is skipped, because building a SerializedObject calls its OnBeforeSerialize.
_CS_FIND = """GameObject target = null;
int matches = 0;
for (int s = 0; s < UnityEngine.SceneManagement.SceneManager.sceneCount; s++)
{
    var scene = UnityEngine.SceneManagement.SceneManager.GetSceneAt(s);
    if (!scene.isLoaded) continue;
    foreach (var root in scene.GetRootGameObjects())
    {
        foreach (var t in root.GetComponentsInChildren<Transform>(true))
        {
            string p = t.name;
            var up = t.parent;
            while (up != null) { p = up.name + "/" + p; up = up.parent; }
            if (p == __PATH__) { if (target == null) target = t.gameObject; matches++; }
        }
    }
}
"""
_CS_VALUE = """var inv = System.Globalization.CultureInfo.InvariantCulture;
System.Func<float, string> f = x => x.ToString("R", inv);
System.Func<SerializedProperty, string> val = it =>
{
    switch (it.propertyType)
    {
        case SerializedPropertyType.Integer: return it.longValue.ToString(inv);
        case SerializedPropertyType.Boolean: return it.boolValue ? "true" : "false";
        case SerializedPropertyType.Float: return it.doubleValue.ToString("R", inv);
        case SerializedPropertyType.String: return "\\"" + it.stringValue + "\\"";
        case SerializedPropertyType.Color: { var c = it.colorValue; return "RGBA(" + f(c.r) + ", " + f(c.g) + ", " + f(c.b) + ", " + f(c.a) + ")"; }
        case SerializedPropertyType.ObjectReference: return it.objectReferenceValue == null ? "null" : it.objectReferenceValue.name + " (" + it.objectReferenceValue.GetType().Name + ")";
        case SerializedPropertyType.Enum: return it.enumValueIndex >= 0 && it.enumValueIndex < it.enumDisplayNames.Length ? it.enumDisplayNames[it.enumValueIndex] : it.intValue.ToString(inv);
        case SerializedPropertyType.Vector2: { var v = it.vector2Value; return "(" + f(v.x) + ", " + f(v.y) + ")"; }
        case SerializedPropertyType.Vector3: { var v = it.vector3Value; return "(" + f(v.x) + ", " + f(v.y) + ", " + f(v.z) + ")"; }
        case SerializedPropertyType.Vector4: { var v = it.vector4Value; return "(" + f(v.x) + ", " + f(v.y) + ", " + f(v.z) + ", " + f(v.w) + ")"; }
        case SerializedPropertyType.Quaternion: { var q = it.quaternionValue; return "(" + f(q.x) + ", " + f(q.y) + ", " + f(q.z) + ", " + f(q.w) + ")"; }
        case SerializedPropertyType.Rect: { var r = it.rectValue; return "(x " + f(r.x) + ", y " + f(r.y) + ", w " + f(r.width) + ", h " + f(r.height) + ")"; }
        case SerializedPropertyType.LayerMask: return it.intValue.ToString(inv);
        case SerializedPropertyType.ArraySize: return it.intValue.ToString(inv);
        default: return it.isArray ? "array of " + it.arraySize : "(" + it.propertyType + ")";
    }
};
"""
SO_READ_BODY = _CS_FIND + _CS_VALUE + """if (target == null) return "csharp-game-editor: no GameObject at hierarchy path " + __PATH__ + " in the loaded scenes.";
var sb = new System.Text.StringBuilder();
sb.Append(__PATH__).Append(matches > 1 ? " (" + matches + " objects have this path; the first is shown)\\n" : "\\n");
int shown = 0;
foreach (var c in target.GetComponents<Component>())
{
    if (c == null) { sb.Append("- missing script\\n"); continue; }
    var type = c.GetType();
    if (__ONLY__ != null && type.Name != __ONLY__ && type.FullName != __ONLY__) continue;
    if (c is ISerializationCallbackReceiver)
    {
        sb.Append("- ").Append(type.FullName).Append(": not read (it implements ISerializationCallbackReceiver; reading it would run its OnBeforeSerialize)\\n");
        continue;
    }
    sb.Append("- ").Append(type.FullName).Append("\\n");
    var it = new SerializedObject(c).GetIterator();
    bool enter = true;
    while (it.NextVisible(enter) && shown < 400)
    {
        enter = it.propertyType == SerializedPropertyType.Generic && !it.isArray;
        if (it.propertyPath == "m_Script") continue;
        sb.Append("    ").Append(it.propertyPath).Append(" = ").Append(val(it)).Append("\\n");
        shown++;
    }
}
if (shown >= 400) sb.Append("(cut at 400 values; name one component)\\n");
return sb.ToString();
"""


def cs_literal(text: str) -> str | None:
    """A C# string literal for text, or None when text has a control character."""
    if any(ord(ch) < 32 for ch in text):
        return None
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


_BAD_PCT = re.compile(r"%(?![0-9A-Fa-f]{2})")
_QUOTED = re.compile(r"""(?P<q>['\"])(?P<body>(?:\\.|[^'\"\\])*)(?P=q)""")
_DOTENV = r"\.env"
_EXACT_SECRET = (r"credentials(?:\.json)?|serviceaccount(?:key)?\.json|service-account(?:-key)?\.json|"
                 r"service_account(?:_key)?\.json|id_rsa|id_dsa|id_ecdsa|id_ed25519|id_rsa\.pub|"
                 r"google-services\.json|googleservice-info\.plist|\.git-credentials|\.htpasswd|\.pgpass|"
                 r"\.s3cfg|\.boto|\.dockercfg|\.netrc|\.npmrc|\.pypirc|\.yarnrc\.yml|known_hosts|authorized_keys")
_SECRET_EXT = (r"\.keystore|\.jks|\.p12|\.pfx|\.pem|\.key|\.p8|\.cer|\.crt|\.csr|\.der|\.p7b|\.ppk|"
               r"\.mobileprovision|\.provisionprofile|\.ovpn|\.gpg|\.asc|\.kdbx|\.keychain|\.keychain-db|"
               r"\.tfvars|\.tfstate|\.tfstate\.backup")
# A name that says it holds a secret, in a file kind that would hold it as text.
_SECRET_WORDS = (r"(?:^|[._-])(?:secrets?|credentials?|tokens?|api[_-]?keys?|private[_-]?keys?|access[_-]?keys?|"
                 r"passwords?|auth[_-]?keys?)(?:[._-][^/]*)?\."
                 r"(?:json|ya?ml|txt|env|ini|cfg|conf|toml|xml|plist|properties)$")
SECRET_NAME = re.compile(
    r"(^" + _DOTENV + r"$|^" + _DOTENV + r"\.|" + _DOTENV + r"$|^(" + _EXACT_SECRET + r")$|(" + _SECRET_EXT + r")$|"
    + _SECRET_WORDS + r"|^authkey_[a-z0-9]+\.p8$)",
    re.IGNORECASE)
_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def explain(kind: str, detail: str = "") -> str:
    """One English message per refusal. Every refusal says nothing was sent."""
    text = {
        "percent": f"{NAME}: refused {detail}: the percent-encoding cannot be decoded. {NOTHING_SENT}",
        "outside": f"{NAME}: refused {detail}: outside Assets/ and Packages/. {NOTHING_SENT}",
        "output": (f"{NAME}: refused {detail}: upstream writes this under the project's {{heads}} folder by default. "
                   f"Use a path there (for example {{example}}), not inside Assets. {NOTHING_SENT}"),
        "link": f"{NAME}: refused {detail}: symbolic link. {NOTHING_SENT}",
        "secret": f"{NAME}: refused {detail}: key or credential file. {NOTHING_SENT}",
        "hidden": f"{NAME}: refused {detail}: hidden file or folder. {NOTHING_SENT}",
        "menu": (f"{NAME}: refused menu_path {detail!r}. Quit is not sent: closing the editor drops unsaved work. "
                 f"{NOTHING_SENT}"),
        "root-delete": (f"{NAME}: refused deleting {detail}, a whole project folder. Name the files or folders inside "
                        f"it. {NOTHING_SENT}"),
        "unknown-tool": f"{NAME}: unknown tool {detail}. {NOTHING_SENT}",
        "unknown-op": f"{NAME}: unknown op {detail}. {NOTHING_SENT}",
        "args": f"{NAME}: arguments must be an object. {NOTHING_SENT}",
        "key": f"{NAME}: {detail}. {NOTHING_SENT}",
        "action": f"{NAME}: that action does not match this op. {NOTHING_SENT}",
        "safety": f"{NAME}: refused safety_checks false. The check stays on. {NOTHING_SENT}",
        "plan-long": (f"{NAME}: the plan text is {detail} characters and would be cut. "
                      f"Split the work. {NOTHING_SENT}"),
        "no-plan": (f"{NAME}: unknown or already used plan_id. A plan runs once, only the newest plan can run, and "
                    f"only in the process that made it. Call plan_batch again. {NOTHING_SENT}"),
        "replaced": (f"{NAME}: plan {detail} was replaced by a newer plan. Only the newest plan can run. "
                     f"Show the newest plan, or call plan_batch again. {NOTHING_SENT}"),
        "expired": (f"{NAME}: plan {detail} is older than {int(PLAN_TTL // 60)} minutes. Call plan_batch again and "
                    f"show the new plan. {NOTHING_SENT}"),
        "several": (f"{NAME}: more than one Unity editor is open ({detail}). Call unity_editor with op "
                    f"set_active_instance and arguments {{\"instance\": \"<one of them>\"}}, then plan again. "
                    f"{NOTHING_SENT}"),
        "gone": (f"{NAME}: the editor this plan was made for ({detail}) is not connected now. "
                 f"Open it and start MCP for Unity, then call apply_plan again; the plan is kept. {NOTHING_SENT}"),
        "no-file": (f"{NAME}: the open scene has no file yet. Give the scene a file, for example arguments "
                    f"{{\"path\": \"Assets/Scenes/Main.unity\"}}. {NOTHING_SENT}"),
        "busy": (f"{NAME}: Unity is still compiling or importing after {detail} seconds. "
                 f"Read mcpforunity://editor/state, then try again. {NOTHING_SENT}"),
        "busy-kept": (f"{NAME}: Unity is still compiling or importing after {detail} seconds. The plan is kept: call "
                      f"apply_plan again with the same plan_id when Unity is idle. {NOTHING_SENT}"),
        "state": (f"{NAME}: the editor changed after the plan ({detail}). Make a new plan and show it again. "
                  f"{NOTHING_SENT}"),
        "unreadable": (f"{NAME}: could not read {detail} from the editor, so the state cannot be fingerprinted and "
                       f"nothing will run. Read mcpforunity://editor/state and the console, then plan again. "
                       f"{NOTHING_SENT}"),
        "disk": (f"{NAME}: changed on disk since this plugin last saw it. "
                 f"Pass overwrite_disk_changes true to keep the editor copy. {NOTHING_SENT}"),
        "exists": f"{NAME}: already exists. Pass overwrite true to replace it. {NOTHING_SENT}",
        "sha": (f"{NAME}: {detail} changed since that precondition_sha256 was read. Read the script again and "
                f"plan with its current text. {NOTHING_SENT}"),
        "empty": f"{NAME}: steps is empty. {NOTHING_SENT}",
        "nested": f"{NAME}: a plan cannot contain plan_batch, apply_plan, or confirm_risky_plan. {NOTHING_SENT}",
        "shape": f"{NAME}: a batch step needs tool and op. {NOTHING_SENT}",
        "placeholder": f"{NAME}: resource value {detail} is not a usable id. {NOTHING_SENT}",
        "expand": f"{NAME}: {detail} {NOTHING_SENT}",
        "root": (f"{NAME}: could not confirm the Unity project folder, so the path was not checked. Unity may not be "
                 f"connected: read unity_scene manage_scene.get_hierarchy for the editor's own message. {NOTHING_SENT}"),
        "not-offered": (f"{NAME}: {detail} is not offered by the running MCP for Unity "
                        f"(pinned {UPSTREAM_VERSION}). Open Window > MCP for Unity and press Start, "
                        f"then call it again. {NOTHING_SENT}"),
        "cancelled": f"{NAME}: the call was cancelled. {NOTHING_SENT}",
        "declined": (f"{NAME}: the user did not approve the plan in the second question. Nothing ran, and "
                     f"this plan is discarded. Do not retry without the user asking. {NOTHING_SENT}"),
        "unanswered": (f"{NAME}: nobody answered the plan question. Nothing ran. The plan is kept; call apply_plan "
                       f"again when someone can answer. {NOTHING_SENT}"),
        "no-elicit": (f"{NAME}: this plan {{risky}}, so it needs a second yes. Hermes did not show the second "
                      f"question here (the classic CLI fails MCP questions closed, and a client without "
                      f"elicitation cannot show one). Nothing ran. Tell the user in one line what the plan {{risky}}, "
                      f"then call confirm_risky_plan with plan_id {detail}: Hermes asks once more before it runs. "
                      f"{NOTHING_SENT}"),
        "not-confirmable": (f"{NAME}: plan {detail} has no step that deletes, runs code, loses unsaved work, or sends "
                            f"or writes outside the project, or apply_plan has not asked about it yet. Call "
                            f"apply_plan with it. {NOTHING_SENT}"),
        "later": f"{NAME}: later steps were not sent.",
        "zero": f"{NAME} note: 0 results. Check the name in the hierarchy.",
        "not-retried": (f"{NAME} note: Unity did not answer. The change was not retried. "
                        f"Read the console or the loaded scenes before trying again."),
    }[kind]
    return text if kind in INFRA_KINDS else Guide(text)


class Guide(str):
    """A refusal of the request: nothing was sent. Returned with isError false (see guidance_result), so a model's
    wrong guesses do not trip Hermes' three-strike pause on the whole server."""


# Refusals that are about the editor or the connection, not about the request. They stay errors.
INFRA_KINDS = frozenset({"gone", "busy", "busy-kept", "unreadable", "root", "cancelled", "declined", "unanswered",
                         "later", "zero", "not-retried"})


def reply_for(text: str) -> dict:
    """A refusal of the request (nothing was sent) is guidance; a problem with Unity or the user's no is an error."""
    return guidance_result(text) if isinstance(text, Guide) else error_result(text)


def error_result(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def guidance_result(text: str) -> dict:
    """A refusal that tells the model the accepted names. Not an error, so Hermes' three-strike pause stays out."""
    return {"content": [{"type": "text", "text": text}], "isError": False}


def hub_editor_patterns() -> list[str]:
    home = os.path.expanduser("~")
    program = os.environ.get("ProgramFiles") or "C:\\Program Files"
    return [
        HUB_UNITY_GLOB,
        os.path.join(home, "Unity", "Hub", "Editor", "*", "Editor", "Unity"),
        os.path.join(program, "Unity", "Hub", "Editor", "*", "Editor", "Unity.exe"),
    ]


def unity_hub_apps() -> list[str]:
    found = []
    for pattern in hub_editor_patterns():
        found.extend(glob.glob(pattern))
    return sorted(set(found))


def hub_missing_message() -> str:
    shown = "; ".join(hub_editor_patterns())
    return f"{NAME}: Unity is not at {shown}. Install the editor with Unity Hub. {NOTHING_SENT}"


def interpret_transport_pref(returncode: int, stdout: str) -> bool:
    """True means HTTP. Only an explicit 0 is stdio. A missing key is Unity's HTTP default."""
    if returncode != 0:
        return True
    return (stdout or "").strip() != "0"


def _read_pref(key: str) -> subprocess.CompletedProcess | None:
    """Read one EditorPrefs key. Never writes. None when the read itself fails."""
    try:
        return subprocess.run(
            ["defaults", "read", "com.unity3d.UnityEditor5.x", key],
            capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None


def editor_transport_http() -> bool:
    proc = _read_pref("MCPForUnity.UseHttpTransport")
    if proc is None:
        return True
    return interpret_transport_pref(proc.returncode, proc.stdout)


def editor_http_url() -> str:
    proc = _read_pref("MCPForUnity.HttpUrl")
    if proc is None or proc.returncode != 0:
        return DEFAULT_HTTP_URL
    text = (proc.stdout or "").strip()
    return text or DEFAULT_HTTP_URL


def _http_host(url: str) -> str:
    return (urllib.parse.urlparse(url).hostname or "").lower()


def remote_http_refusal(url: str) -> str:
    if _http_host(url) in LOOPBACK_HOSTS:
        return ""
    return f"{NAME}: MCP for Unity is set to {url}, which is not this machine. {NOTHING_SENT}"


def upstream_argv(http: bool, url: str) -> list[str]:
    base = [sys.executable, "-I", "-m", "main"]
    if http:
        return base + ["--transport", "http", "--http-url", url]
    return base + ["--transport", "stdio"]


def transport_choice(http: bool, url: str, listening: bool) -> tuple[str, list[str] | None]:
    if not http:
        return "stdio", upstream_argv(False, url)
    if remote_http_refusal(url):
        return "refuse", None
    if listening:
        return "attach", None
    return "spawn", upstream_argv(True, url)


def port_open(url: str, timeout: float = 0.3) -> bool:
    if _http_host(url) not in LOOPBACK_HOSTS:
        return False
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8080
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


def wait_port(url: str, limit: float, proc: subprocess.Popen | None) -> bool:
    end = time.time() + limit
    while time.time() < end:
        if proc is not None and proc.poll() is not None:
            return False
        if port_open(url):
            return True
        time.sleep(0.05)
    return False


def child_environment(source: dict | None = None) -> dict:
    src = os.environ if source is None else source
    env = {}
    for key in CHILD_ENV_KEYS:
        val = src.get(key)
        if isinstance(val, str) and val:
            env[key] = val
    env["DISABLE_TELEMETRY"] = "true"
    env["UNITY_MCP_DISABLE_TELEMETRY"] = "true"
    env["FASTMCP_CHECK_FOR_UPDATES"] = "off"
    return env


def _is_absolute_path(text: str) -> bool:
    return text.startswith(("/", "~")) or bool(re.match(r"^[A-Za-z]:[\\/]", text))


def split_effective(uri: str) -> str:
    """The path manage_script._split_uri would hand to Unity, as one relative string."""
    if uri.startswith("mcpforunity://path/"):
        raw = uri[len("mcpforunity://path/"):]
    elif uri.startswith("file://"):
        parsed = urllib.parse.urlparse(uri)
        host = (parsed.netloc or "").strip()
        path = parsed.path or ""
        if host and host.lower() != "localhost":
            path = f"//{host}{path}"
        raw = urllib.parse.unquote(path)
    else:
        raw = uri
    raw = urllib.parse.unquote(raw).replace("\\", "/")
    if os.name == "nt" and len(raw) >= 3 and raw[0] == "/" and raw[2] == ":":
        raw = raw[1:]
    norm = os.path.normpath(raw).replace("\\", "/") if raw else ""
    parts = [part for part in norm.split("/") if part not in ("", ".")]
    idx = next((i for i, seg in enumerate(parts) if seg.lower() == "assets"), None)
    effective = "/".join(parts[idx:]) if idx is not None else norm
    if effective.startswith("/"):
        effective = effective[1:]
    if effective == ".":
        effective = ""
    return effective


def normalize_path_text(value: str) -> tuple[str | None, str]:
    """Decode the way Unity does, then require a second pass to change nothing."""
    if _BAD_PCT.search(value):
        return None, explain("percent", value)
    decoded = urllib.parse.unquote(value).replace("\\", "/")
    if any(part == ".." for part in decoded.split("/")):
        return None, explain("outside", value)
    effective = split_effective(value)
    if _BAD_PCT.search(effective) or split_effective(effective) != effective:
        return None, explain("percent", value)
    if any(part == ".." for part in effective.split("/")):
        return None, explain("outside", value)
    return effective, ""


def _temp_root_link(path: str) -> bool:
    if os.path.realpath("/tmp") != os.path.join("/pri" + "vate", "tmp"):
        return False
    return os.path.realpath(path) == os.path.realpath("/tmp")


def outside_file_refusal(key: str, value: str) -> str:
    text = os.path.expanduser(value)
    parts = [part for part in text.replace("\\", "/").split("/") if part not in ("", ".")]
    if any(part == ".." for part in text.replace("\\", "/").split("/")):
        return explain("outside", f"{key}={value}")
    if any(part.startswith(".") for part in parts):
        return explain("hidden", f"{key}={value}")
    base = parts[-1] if parts else text
    if SECRET_NAME.search(base):
        return explain("secret", base)
    if text.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        probe = text
        while True:
            if os.path.islink(probe):
                if not _temp_root_link(probe):
                    return explain("link", f"{key}={value}")
                break
            parent = os.path.dirname(probe)
            if parent == probe or not os.path.exists(probe):
                if parent == probe:
                    break
                probe = parent
                continue
            probe = parent
            if probe in ("/", ""):
                break
        if text == "/tmp" or text.startswith("/tmp/"):
            real_root = os.path.realpath("/tmp")
            if os.path.exists(text):
                resolved = os.path.realpath(text)
                if resolved != real_root and not resolved.startswith(real_root.rstrip(os.sep) + os.sep):
                    return explain("link", f"{key}={value}")
    return ""


def _output_refusal(key: str, value: str) -> str:
    heads = OUTPUT_HEADS[key]
    example = heads[0] + ("/StandaloneOSX/Game.app" if heads[0] == "Builds" else "/capture.snap")
    return Guide(explain("output", f"{key}={value}").replace("{heads}", " or ".join(heads))
                 .replace("{example}", example))


def judge_relative(key: str, value: str, output: bool = False) -> str:
    parts = [part for part in value.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        return explain("outside", f"{key}={value}")
    if not parts:
        return ""
    if SECRET_NAME.search(parts[-1]):
        return explain("secret", parts[-1])
    if any(part.startswith(".") for part in parts):
        return explain("hidden", value)
    head = parts[0].lower()
    if output:
        if head in {item.lower() for item in OUTPUT_HEADS[key]}:
            return ""
        return _output_refusal(key, value)
    if head in ("assets", "packages"):
        return ""
    if len(parts) == 1:
        # A bare name (a script, scene, clip, or prefab name). Upstream puts it under Assets/.
        return ""
    return explain("outside", f"{key}={value}")


def _looks_like_path(key: str, value: str, keys: frozenset = PATH_KEYS) -> bool:
    if key in keys:
        return True
    if key in NON_PATH:
        return False
    lower = value.lower()
    return (lower.startswith(("assets/", "packages/", "mcpforunity://", "file://"))
            or _is_absolute_path(value))


def rewrite_paths(value, key: str = "", keys: frozenset = PATH_KEYS, op: str = ""):
    """Return (new_value, error). Path strings are replaced with the decoded form.

    keys are the argument names this op hands to a file system call (upstream source) plus the 0.4 names.
    An absolute path is refused, except where a build or the profiler writes by default (checked again against
    the project folder before the plan is made).
    """
    if isinstance(value, dict):
        out = {}
        for child_key, child in value.items():
            rewritten, problem = rewrite_paths(child, str(child_key), keys, op)
            if problem:
                return None, problem
            out[str(child_key)] = rewritten
        return out, ""
    if isinstance(value, list):
        out = []
        for child in value:
            rewritten, problem = rewrite_paths(child, key, keys, op)
            if problem:
                return None, problem
            out.append(rewritten)
        return out, ""
    if not isinstance(value, str) or not _looks_like_path(key, value, keys):
        return value, ""
    output = op in OUTPUT_OPS and key in OUTPUT_HEADS
    if _is_absolute_path(value):
        if _BAD_PCT.search(value):
            return None, explain("percent", value)
        decoded = urllib.parse.unquote(os.path.expanduser(value))
        if _BAD_PCT.search(decoded) or urllib.parse.unquote(decoded) != decoded:
            return None, explain("percent", value)
        problem = outside_file_refusal(key, decoded)
        if problem:
            return None, problem
        if not output:
            return None, explain("outside", f"{key}={decoded}")
        return decoded, ""
    normalized, problem = normalize_path_text(value)
    if problem:
        return None, problem
    problem = judge_relative(key, normalized, output)
    if problem:
        return None, problem
    return normalized, ""


def code_secret_refusal(code: str) -> str:
    if not isinstance(code, str):
        return ""
    for match in _QUOTED.finditer(code):
        body = match.group("body")
        base = body.replace("\\", "/").split("/")[-1]
        if SECRET_NAME.search(base):
            return explain("secret", base)
        if "/" in body or body.startswith("~") or _is_absolute_path(body):
            problem = outside_file_refusal("code", body)
            if problem:
                return problem
    return ""


def resolved_refusal(tool_name: str, value: str, project_root: str) -> str:
    parts = [part for part in value.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        return explain("outside", f"{tool_name} {value}")
    root = os.path.realpath(project_root)
    cur = root
    for part in parts:
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            return explain("link", value)
        if not os.path.exists(cur):
            break
    real = os.path.realpath(os.path.join(root, *parts)) if parts else root
    if real != root and not real.startswith(root.rstrip(os.sep) + os.sep):
        return explain("link", value)
    return ""


def file_sha(path: str) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def tree_sha(path: str) -> str | None:
    """sha256 over the names and contents of the files in a folder (ProjectSettings/), links not followed."""
    if not os.path.isdir(path) or os.path.islink(path):
        return None
    digest = hashlib.sha256()
    for folder, dirs, files in sorted(os.walk(path)):
        dirs.sort()
        for file in sorted(files):
            full = os.path.join(folder, file)
            if os.path.islink(full):
                continue
            digest.update(os.path.relpath(full, path).encode("utf-8") + b"\0" + (file_sha(full) or "").encode())
    return digest.hexdigest()


def _placeholders(uri: str) -> list[str]:
    return _PLACEHOLDER.findall(uri)


def _fill_resource(uri: str, arguments: dict) -> tuple[str | None, str]:
    names = _placeholders(uri)
    if set(arguments) != set(names):
        return None, explain("key", ",".join(sorted(set(arguments) ^ set(names))) or uri)
    values = {}
    for name in names:
        raw = arguments[name]
        if not isinstance(raw, str) or not raw:
            return None, explain("placeholder", name)
        if name == "instance_id":
            if not re.fullmatch(r"-?\d+", raw):
                return None, explain("placeholder", name)
            values[name] = raw
        elif name == "component_name":
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", raw):
                return None, explain("placeholder", name)
            values[name] = raw
        elif name == "mode":
            if raw not in ("EditMode", "PlayMode"):
                return None, explain("placeholder", name)
            values[name] = raw
        elif name == "encoded_path":
            normalized, problem = normalize_path_text(raw)
            if problem:
                return None, problem
            problem = judge_relative("encoded_path", normalized)
            if problem:
                return None, problem
            if not normalized.startswith(("Assets/", "Packages/")):
                return None, explain("outside", normalized)
            values[name] = urllib.parse.quote(normalized, safe="")
        else:
            return None, explain("placeholder", name)
    filled = uri
    for name, text in values.items():
        filled = filled.replace("{" + name + "}", text)
    if "{" in filled or "}" in filled:
        return None, explain("placeholder", uri)
    return filled, ""


def _resource_runs_code(uri: str) -> bool:
    """Prefab and test listings load project assemblies. Component reads call public property getters."""
    return "prefab" in uri or "tests" in uri or "/component" in uri


def _template_regex(uri: str) -> re.Pattern:
    return re.compile("^" + _PLACEHOLDER.sub("[^/]+", re.escape(uri).replace(r"\{", "{").replace(r"\}", "}")) + "$")


def _example_uris(resources: list[dict]) -> set[str]:
    """Concrete URIs copied from upstream docs (an instance id, a Player prefab) that a template already covers."""
    templates = [_template_regex(row["uri"]) for row in resources if _placeholders(row["uri"])]
    return {row["uri"] for row in resources
            if not _placeholders(row["uri"]) and any(rx.match(row["uri"]) for rx in templates)}


UPSTREAM_SCHEMAS = json.loads((_HERE / "upstream_schemas.json").read_text(encoding="utf-8"))["tools"]
# A read the bridge adds: component values through SerializedObject (no property getter runs). See SO_READ_BODY.
def asmdef_text(name: str, kind: str, references: list[str]) -> str:
    """An assembly definition in the form Unity's own Create > Assembly Definition menus write."""
    tests = kind != "game"
    refs = list(references)
    if tests:
        refs = refs + [item for item in ("UnityEngine.TestRunner", "UnityEditor.TestRunner") if item not in refs]
    body = {
        "name": name,
        "rootNamespace": "",
        "references": refs,
        "includePlatforms": ["Editor"] if kind == "editmode_tests" else [],
        "excludePlatforms": [],
        "allowUnsafeCode": False,
        "overrideReferences": tests,
        "precompiledReferences": ["nunit.framework.dll"] if tests else [],
        "autoReferenced": not tests,
        "defineConstraints": ["UNITY_INCLUDE_TESTS"] if tests else [],
        "versionDefines": [],
        "noEngineReferences": False,
    }
    return json.dumps(body, indent=4) + "\n"


def _bridge_effect(kind: str, api: str) -> dict:
    return {"kind": kind, "api": api, "at": "this plugin", "via": ["bridge"], "when": [], "when_params": [],
            "arg": "", "scratch": False}


_READ_SPEC = {"action": None, "action_param": False, "flags": [], "tier": "read", "ask": False, "file_params": [],
              "effects": []}
BRIDGE_OPS = {
    ("unity_object", "component_values"): dict(_READ_SPEC, **{
        "upstream_tool": "execute_code", "bridge": "component_values", "params": ["path", "component"],
        "evidence": ["bridge: SerializedObject over the serialized fields; no project code runs"],
    }),
    ("unity_script", "create_asmdef"): {
        "upstream_tool": None, "bridge": "create_asmdef", "action": None, "action_param": False,
        "params": ["path", "kind", "references"], "flags": ["writes"], "tier": "effect", "ask": True,
        "file_params": ["path"], "evidence": ["bridge: writes the .asmdef JSON itself, then asks Unity to compile"],
        "effects": [_bridge_effect("write_file", "the plugin writes the .asmdef file"),
                    _bridge_effect("import_compile", "refresh_unity with compile request")],
    },
    ("unity_asset", "asset_find"): dict(_READ_SPEC, **{
        "upstream_tool": None, "bridge": "asset_find", "params": ["folder", "name", "type", "limit"],
        "evidence": ["bridge: lists files on disk; Unity is not asked, so no asset loads and no code runs"],
    }),
    ("unity_asset", "prefab_info"): dict(_READ_SPEC, **{
        "upstream_tool": None, "bridge": "prefab_info", "params": ["path"],
        "evidence": ["bridge: reads the .prefab text on disk; Unity is not asked, so no code runs"],
    }),
    ("unity_asset", "read_text"): dict(_READ_SPEC, **{
        "upstream_tool": None, "bridge": "read_text", "params": ["path"],
        "file_params": ["path"],
        "evidence": ["bridge: reads .unity, .prefab, .asset, or .cs bytes from disk; Unity is not asked"],
    }),
}
DISK_TEXT_EXT = (".unity", ".prefab", ".asset", ".cs")
# Bytes copied before apply_plan so a change the plan did not name can be put back. Larger files are hashed only.
WATCH_BYTE_CAP = 8_000_000
DESCRIBE_SPEC = dict(_READ_SPEC, **{"upstream_tool": None, "bridge": "describe", "params": ["op"],
                                     "evidence": ["bridge: the op's arguments and what it does inside"]})
ASSET_TYPES = {
    "prefab": (".prefab",), "scene": (".unity",), "script": (".cs",), "material": (".mat",),
    "scriptable_object": (".asset",), "texture": (".png", ".jpg", ".jpeg", ".tga", ".psd", ".exr", ".tif", ".tiff"),
    "audio": (".wav", ".mp3", ".ogg", ".aiff", ".aif"), "model": (".fbx", ".obj", ".blend", ".gltf", ".glb"),
    "animation": (".anim", ".controller", ".overrideController"), "shader": (".shader", ".shadergraph", ".hlsl"),
    "assembly": (".asmdef", ".asmref"), "ui": (".uxml", ".uss"),
}
ASMDEF_KINDS = ("game", "editmode_tests", "playmode_tests")
# Class ids of the components a prefab file names most often (Unity's YAML class id reference).
CLASS_IDS = {1: "GameObject", 4: "Transform", 20: "Camera", 23: "MeshRenderer", 33: "MeshFilter", 50: "Rigidbody2D",
             54: "Rigidbody", 58: "CircleCollider2D", 61: "BoxCollider2D", 64: "MeshCollider", 65: "BoxCollider",
             82: "AudioSource", 95: "Animator", 108: "Light", 114: "MonoBehaviour", 135: "SphereCollider",
             136: "CapsuleCollider", 137: "SkinnedMeshRenderer", 143: "CharacterController", 198: "ParticleSystem",
             199: "ParticleSystemRenderer", 212: "SpriteRenderer", 222: "CanvasRenderer", 223: "Canvas",
             224: "RectTransform", 1001: "PrefabInstance"}
BRIDGE_PARAM_SCHEMAS = {
    "overwrite": {"type": "boolean", "description": "create_script: replace an existing file. The plan says so and "
                  "sends it as one apply_text_edits over the whole file, guarded by the file's sha256."},
    "overwrite_disk_changes": {"type": "boolean", "description": "manage_scene.save: keep the editor copy when the "
                               ".unity file changed on disk since this session first saw it."},
    "path": {"type": "string", "description": "component_values: the GameObject's hierarchy path from "
             "manage_scene.get_hierarchy, for example \"Player\" or \"Level/Coin (2)\"."},
    "component": {"type": "string", "description": "component_values: only this component type (for example "
                  "\"Rigidbody\" or \"Coin\"). Leave out for every component."},
}


_JSON_TYPES = {"string": (str,), "integer": (int,), "number": (int, float), "boolean": (bool,), "array": (list,),
               "object": (dict,), "null": (type(None),)}


def _type_problem(spec: dict, key: str, value) -> str:
    """The argument's JSON type against MCP for Unity's own schema for it. Empty when it fits or is unknown."""
    tool = spec.get("upstream_tool")
    prop = ((UPSTREAM_SCHEMAS.get(tool) or {}).get("properties") or {}).get(key) if tool else None
    if not isinstance(prop, dict):
        return ""
    kinds = [prop["type"]] if isinstance(prop.get("type"), str) else [
        item.get("type") for item in prop.get("anyOf") or [] if isinstance(item, dict) and isinstance(item.get("type"), str)]
    if not kinds:
        return ""
    for kind in kinds:
        allowed = _JSON_TYPES.get(kind)
        if allowed is None:
            return ""
        if isinstance(value, bool) and kind in ("integer", "number"):
            continue
        if isinstance(value, allowed):
            return ""
    shown = " or ".join(item for item in kinds if item != "null")
    desc = " ".join(str(prop.get("description") or "").split())
    return f"{key} must be {shown} for {tool}" + (f" ({desc})" if desc else "")


BRIDGE_PARAM_SCHEMAS.update({
    "kind": {"type": "string", "enum": list(ASMDEF_KINDS),
             "description": "create_asmdef: game (your scripts' own assembly), editmode_tests, or playmode_tests."},
    "references": {"type": "array", "items": {"type": "string"},
                   "description": "create_asmdef: assembly names it uses, for example [\"Game\"]."},
    "folder": {"type": "string", "description": "asset_find: folder under Assets/ or Packages/ (default Assets)."},
    "name": {"type": "string", "description": "Name, or part of a name."},
    "type": {"type": "string", "enum": sorted(ASSET_TYPES),
             "description": "asset_find: kind of file by extension."},
    "limit": {"type": "integer", "description": "asset_find: at most this many rows (default 100)."},
    "op": {"type": "string", "description": "describe: the op to explain."},
})
TOOL_BUDGET = 5000


_PARAM_BY_OP = {
    ("unity_object", "component_values", "path"): {
        "type": "string",
        "description": "component_values: the GameObject's hierarchy path from manage_scene.get_hierarchy, for "
                       "example \"Player\" or \"Level/Coin (2)\".",
    },
    ("unity_object", "component_values", "component"): {
        "type": "string",
        "description": "component_values: only this component type (for example \"Rigidbody\" or \"Coin\"). "
                       "Leave out for every component.",
    },
    ("unity_script", "create_asmdef", "path"): {
        "type": "string",
        "description": "create_asmdef: the new .asmdef file under Assets/. The file name is the assembly name, "
                       "for example Assets/Scripts/Game.asmdef or Assets/Tests/EditMode/Game.Tests.EditMode.asmdef.",
    },
}


def _full_param(bundle: str, users: list[str], ops: dict, param: str) -> dict:
    """The argument's schema as upstream (or this plugin) describes it."""
    if len(users) == 1:
        specific = _PARAM_BY_OP.get((bundle, users[0], param))
        if specific:
            return json.loads(json.dumps(specific))
        if ops[(bundle, users[0])].get("bridge") and param in BRIDGE_PARAM_SCHEMAS \
                and param not in ("path", "component"):
            return json.loads(json.dumps(BRIDGE_PARAM_SCHEMAS[param]))
    for key in users:
        tool = ops[(bundle, key)].get("upstream_tool")
        found = (UPSTREAM_SCHEMAS.get(tool) or {}).get("properties", {}).get(param)
        if found:
            return json.loads(json.dumps(found))
    if param in BRIDGE_PARAM_SCHEMAS:
        return json.loads(json.dumps(BRIDGE_PARAM_SCHEMAS[param]))
    return {"type": "string", "description": f"Fills {{{param}}} in the resource URI."}


def _arguments_schema(bundle: str, keys: list[str], ops: dict, cap: int | None) -> dict:
    """Every argument the ops of this tool take, with upstream's type. Descriptions are cut at cap characters so
    the tool stays within TOOL_BUDGET bytes; op describe returns them whole for one op."""
    used_by: dict[str, list[str]] = {}
    for key in keys:
        for param in ops[(bundle, key)].get("params") or []:
            used_by.setdefault(param, []).append(key)
        if ops[(bundle, key)].get("upstream_tool") == "create_script":
            used_by.setdefault("overwrite", []).append(key)
        if ops[(bundle, key)].get("action") == "save" and ops[(bundle, key)].get("upstream_tool") == "manage_scene":
            used_by.setdefault("overwrite_disk_changes", []).append(key)
    props: dict[str, dict] = {}
    for param, users in used_by.items():
        entry = _full_param(bundle, users, ops, param)
        for drop in ("default", "title", "examples"):
            entry.pop(drop, None)
        if cap is not None:
            if isinstance(entry.get("enum"), list) and len(json.dumps(entry["enum"])) > max(cap, 40):
                entry.pop("enum")
            for item in entry.get("anyOf") or []:
                if isinstance(item, dict):
                    for drop in ("description", "title", "items", "additionalProperties", "properties"):
                        item.pop(drop, None)
            if cap <= 60 and isinstance(entry.get("anyOf"), list):
                kinds = []
                for item in entry.pop("anyOf"):
                    kind = item.get("type") if isinstance(item, dict) else None
                    if isinstance(kind, str) and kind not in kinds:
                        kinds.append(kind)
                if kinds:
                    entry["type"] = kinds[0] if len(kinds) == 1 else kinds
            for drop in ("items", "additionalProperties", "properties"):
                if drop in entry and len(json.dumps(entry[drop])) > max(cap, 40):
                    entry.pop(drop)
            text = " ".join(str(entry.get("description") or "").split())
            if cap == 0 or not text:
                entry.pop("description", None)
            elif len(text) > cap:
                entry["description"] = text[:cap - 1].rstrip() + "…"
        props[param] = entry
    return {"type": "object", "properties": props,
            "description": "Arguments for that op. describe gives one op's arguments in full."}


def _op_description(bundle: str, keys: list[str], ops: dict) -> str:
    reads = [key for key in keys if key in READ_ALLOW]
    changes = [key for key in keys if key not in READ_ALLOW]
    parts = ["Which operation."]
    if reads:
        parts.append("Reads that run now: " + ", ".join(reads) + ".")
    if changes:
        parts.append("Every other op is a change: the reply is a plan to show, then apply_plan (or put several in "
                     "one plan_batch).")
    return " ".join(parts)


def _build_index() -> tuple[dict, list[dict]]:
    ops: dict[tuple[str, str], dict] = {}
    examples = _example_uris(RESOURCES)
    for bundle, body in TABLE["bundles"].items():
        for key, spec in body["ops"].items():
            ops[(bundle, key)] = dict(spec)
        for resource in RESOURCES:
            if resource["reached_by"] != bundle or resource["uri"] in examples:
                continue
            uri = resource["uri"]
            names = _placeholders(uri)
            runs = _resource_runs_code(uri)
            ops[(bundle, uri)] = {
                "upstream_tool": None,
                "resource": uri,
                "action": None,
                "action_param": False,
                "params": names,
                "flags": ["runs_code"] if runs else [],
                "tier": "effect" if runs or uri not in READ_ALLOW else "read",
                "ask": uri not in READ_ALLOW,
                "file_params": [],
                "evidence": [resource["file"]],
            }
    for key, spec in BRIDGE_OPS.items():
        ops[key] = dict(spec)
    for bundle in TABLE["bundles"]:
        ops[(bundle, "describe")] = dict(DESCRIBE_SPEC)
    domain = [item for item in TOOL_ORDER if item not in PLAN_TOOLS]
    tools = []
    for name in TOOL_ORDER:
        if name == "plan_batch":
            schema = {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "description": ("Each step is tool, op, and arguments, with the same op and argument names as "
                                        "that tool's schema. One plan covers the whole list."),
                        "items": {
                            "type": "object",
                            "properties": {
                                "tool": {"type": "string", "enum": domain},
                                "op": {"type": "string"},
                                "arguments": {"type": "object"},
                            },
                            "required": ["tool", "op"],
                        },
                    }
                },
                "required": ["steps"],
                "additionalProperties": False,
            }
            first, note, read_only, destructive = PLAN_FIRST, TOOL_WORDS["plan_batch"] + PLAN_NOTE, True, False
        elif name in ("apply_plan", "confirm_risky_plan"):
            schema = {
                "type": "object",
                "properties": {
                    "plan_id": {"type": "string", "description": "The plan_id of the newest plan_batch reply."},
                },
                "required": ["plan_id"],
                "additionalProperties": False,
            }
            first, note = (APPLY_FIRST, APPLY_NOTE) if name == "apply_plan" else (CONFIRM_FIRST, CONFIRM_NOTE)
            read_only, destructive = False, True
        else:
            keys = sorted(key for (bundle, key) in ops if bundle == name)
            first = TABLE["bundles"][name]["first"]
            note, read_only, destructive = TOOL_WORDS.get(name, "") + READ_NOTE, True, False
            if name == "unity_docs":
                # Every docs op sends the query to docs.unity3d.com, so Hermes asks before each call.
                note, read_only = TOOL_WORDS.get(name, "") + DOCS_NOTE, False
            for cap in (None, 160, 100, 60, 30, 0):
                schema = {
                    "type": "object",
                    "properties": {
                        "op": {"type": "string", "enum": keys, "description": _op_description(name, keys, ops)},
                        "arguments": _arguments_schema(name, keys, ops, cap),
                    },
                    "required": ["op"],
                    "additionalProperties": False,
                }
                size = len(json.dumps({"name": name, "description": first + note, "inputSchema": schema,
                                       "annotations": {"readOnlyHint": read_only, "destructiveHint": destructive,
                                                       "title": name}}, ensure_ascii=False))
                if size <= TOOL_BUDGET:
                    break
        if len(first) > 60 or first.startswith("Read-only."):
            raise RuntimeError("bad first sentence: " + name)
        description = first + note
        if len(description) > 1024:
            raise RuntimeError("description too long: " + name)
        tools.append({
            "name": name,
            "description": description,
            "inputSchema": schema,
            "annotations": {"readOnlyHint": read_only, "destructiveHint": destructive, "title": name},
        })
    missing = sorted(op for op in READ_ALLOW if not any(key == op for (_bundle, key) in ops))
    if missing:
        raise RuntimeError("allowlist op is not in the table: " + ", ".join(missing))
    return ops, tools


OPS, T = _build_index()
TOOLS_BY_NAME = {tool["name"]: tool for tool in T}


def tool_definitions() -> list[dict]:
    return list(T)


DOES = {
    "create_script": "Writes a new C# script file.",
    "manage_script.create": "Writes a new C# script file.",
    "apply_text_edits": "Changes lines in a C# script file.",
    "script_apply_edits": "Changes a C# script file by method, class, or anchor.",
    "delete_script": "Moves a C# script file and its .meta to the system Trash (MoveAssetToTrash).",
    "manage_script.delete": "Moves a C# script file and its .meta to the system Trash (MoveAssetToTrash).",
    "manage_gameobject.create": ("Adds a GameObject to the open scene. Components it adds run their Reset, OnValidate, "
                                 "and [ExecuteAlways] code in the editor."),
    "manage_gameobject.modify": "Changes a GameObject in the open scene.",
    "manage_gameobject.delete": "Deletes a GameObject and all of its children from the open scene.",
    "manage_gameobject.duplicate": "Copies a GameObject in the open scene.",
    "manage_components.add": "Adds a component. Its Reset, OnValidate, and [ExecuteAlways] code runs in the editor.",
    "manage_components.remove": "Removes a component from a GameObject.",
    "manage_components.set_property": "Sets a component field or property. A property setter is project code and runs.",
    "manage_scene.save": "Saves the open scene to a .unity file.",
    "manage_scene.create": "Makes a new empty scene file and opens it in place of the open scenes.",
    "manage_scene.load": "Opens a scene file.",
    "manage_scene.close_scene": "Closes a loaded scene.",
    "manage_editor.stop": "Leaves play mode. Unity drops every scene change made during play.",
    "manage_editor.pause": "Pauses or resumes play mode.",
    "manage_editor.undo": "Undoes the last editor action.",
    "manage_editor.redo": "Redoes the last undone editor action.",
    "execute_code.execute": "Runs the C# below inside the editor with the editor's full access. It is not a sandbox.",
    "execute_code.replay": "Runs earlier C# from the execute_code history again, with the editor's full access.",
    "execute_menu_item": "Runs the editor menu command below. That menu command decides what changes.",
    "refresh_unity": "Reimports changed assets and, when compile is request, recompiles scripts.",
    "manage_editor.play": ("Enters play mode. The scene's own scripts run (Awake, Start, Update) until play mode stops."),
    "run_tests": ("Runs the project's tests in the editor (the tests are project code). PlayMode tests enter play "
                  "mode. apply_plan waits for the test job and returns its result."),
    "manage_packages.add_package": ("Adds a package to Packages/manifest.json. Unity resolves it (downloading it from "
                                    "the registry or git when it is not built in) and imports it, which can run the "
                                    "package's editor code."),
    "manage_packages.remove_package": "Removes a package from Packages/manifest.json.",
    "manage_packages.embed_package": "Copies a package into Packages/ so it becomes part of the project.",
    "manage_packages.resolve_packages": "Asks the Package Manager to resolve Packages/manifest.json again.",
    "manage_packages.search_packages": "Sends the query to the Unity package registry.",
    "manage_packages.list_packages": "Lists packages. Unity asks the package registry for newer versions.",
    "manage_build.build": ("Builds a player. This takes minutes and writes the output folder (upstream's default is "
                           "<project>/Builds/<target>/). apply_plan waits for the build job and returns its result."),
    "manage_profiler.memory_take_snapshot": ("Takes a memory snapshot file. With no snapshot_path, upstream writes it "
                                             "to Unity's temporary cache folder (outside the project)."),
    "execute_custom_tool": "Runs a project custom tool: the C# class shown below runs with the editor's full access.",
    "manage_build.scenes": "Replaces the list of scenes in the build settings.",
    "manage_asset.delete": "Deletes the asset file and its .meta file.",
    "unity_docs.lookup": "Sends the query below to docs.unity3d.com and returns what the documentation pages say.",
    "unity_docs.get_doc": "Sends the class and member below to docs.unity3d.com and returns that API page.",
    "unity_docs.get_manual": "Sends the manual page name below to docs.unity3d.com and returns that page.",
    "unity_docs.get_package_doc": "Sends the package and page below to docs.unity3d.com and returns that page.",
    "manage_physics.simulate_step": "Steps the physics simulation. Rigidbodies move and collision callbacks run.",
    "manage_camera.screenshot": ("Renders a camera to a PNG file in the project and returns the picture. The file "
                                 "goes to output_folder, else the folder set in MCP for Unity, else Assets/Screenshots."),
    "manage_camera.screenshot_multiview": ("Renders several views to PNG files in the project and returns them. The "
                                           "files go to output_folder, else the MCP for Unity folder, else "
                                           "Assets/Screenshots."),
}

def op_does(step: dict) -> str:
    known = DOES.get(step["op"])
    if known:
        return known
    spec = step["spec"]
    if step.get("resource_uri"):
        return f"Reads {step['resource_uri']} from the editor."
    action = spec.get("action")
    if action:
        return f"Calls MCP for Unity {spec.get('upstream_tool')} with action {action}."
    return f"Calls MCP for Unity {spec.get('upstream_tool')}."


# ---- what a step does inside: the side effect table (tools/extract_side_effects.py) ----
# The plan text, the second question, the state fingerprint, and the checks after a step come from the effects
# upstream's own C# reaches for that operation, filtered by the step's arguments. No decision below is made from
# the words in an operation's name.
EFFECT_WORDS = dict(TABLE.get("effect_words") or {})
UNITY_RULES = dict(TABLE.get("unity_rules") or {})
AUTORUN_RE = re.compile(UNITY_RULES["editor_autorun"]["pattern"])
EDITOR_FOLDER_RE = re.compile(UNITY_RULES["editor_folder"]["pattern"])
_SCRIPT_EXT = tuple(UNITY_RULES.get("script_ext") or (".cs", ".asmdef", ".asmref", ".rsp"))
# Reflection sites on the path of a listed read that call Unity's or a Unity package's own internals, not project
# code (read at each site in the 10.3.0 source). A listed read may have these and no other effect.
UNITY_OWN_REFLECTION = {
    "Runtime/Helpers/UnityAssembliesCompat.cs:117": "UnityEditor CurrentAssemblies.GetLoadedAssemblies",
    "Editor/Tools/ReadConsole.cs:393": "an instance of UnityEditor.LogEntry",
    "Editor/Tools/Cameras/CameraHelpers.cs:243": "Cinemachine's GetCinemachineComponent",
    "Editor/Tools/Profiler/Operations/FrameDebuggerOps.cs:181": "UnityEditor FrameDebugger event data",
}
# Kinds shown on the plan's "inside" lines, in this order.
SHOWN_KINDS = ("save_scene", "save_assets", "delete_file", "write_file", "scene_switch", "import_compile",
               "enter_play", "exit_play", "run_tests", "compile_run", "menu_item", "build_player", "send",
               "project_settings", "editor_prefs", "undo_redo", "load_asset", "instantiate", "set_values",
               "scene_edit", "simulate", "reflection", "destroy_object")
# Where the file is when an op names it by folder and name: upstream joins them (ManageScriptableObject.cs
# HandleCreate, ManageScript.cs). Keyed by the upstream tool and its arguments, not by the op's words.
COMPOSED = {
    ("manage_scriptable_object", "create"): ("folder_path", "asset_name", ".asset"),
    ("manage_script", None): ("path", "name", ".cs"),
    ("script_apply_edits", None): ("path", "name", ".cs"),
}
STATE_FILES = {"project_settings": ("ProjectSettings/",), "packages": ("Packages/manifest.json",
                                                                       "Packages/packages-lock.json")}
RISK_WORDS = {"deletes": "deletes", "code": "runs editor code", "unsaved": "loses unsaved work",
              "saves": "saves unsaved changes over a scene file", "outside": "sends or writes outside the project"}
RISK_HEADS = {"deletes": "DELETES", "code": "RUNS EDITOR CODE", "unsaved": "LOSES UNSAVED WORK",
              "saves": "SAVES OVER A FILE", "outside": "SENDS OR WRITES OUTSIDE THE PROJECT"}
# Discord's approval card leaves 1,729 characters for the text (2,000 minus its framing); a mention role takes a
# little more. Telegram leaves about 3,800 of the escaped UTF-16 text and Slack 2,800 (Hermes v0.22.2 adapters,
# tests/test_gateway_render.py). The question is sent only when every one of those cards shows it whole.
SECOND_CAP = 1650
_CARD_RAW_CAP = {"discord": 1650, "slack": 2800}
_TELEGRAM_ESCAPED_CAP = 3800
# Directories Unity (and git) use as caches. Everything else in the project, including UserSettings and files at
# the project root, is watched. A changed file, and a new file, that the plan did not name are put back.
# A .meta stays when its asset or folder was already on disk.
_WATCH_SKIP = frozenset({"Library", "Temp", "Logs", "obj", ".git"})
# Files Unity 6000.6.6f1 rewrites by itself while the editor is open (measured on a new project). A different
# file under UserSettings or at the project root is still put back.
_EDITOR_CHURN = frozenset({
    "UserSettings/EditorUserSettings.asset",
    "UserSettings/HierarchyWindow.settings",
    "UserSettings/PlayModeUserSettings.asset",
    "UserSettings/Search.settings",
    "UserSettings/Search.index",
    "ProjectSettings/SceneTemplateSettings.json",
    "ProjectSettings/ProjectSettings.asset",
    "ProjectSettings/EditorSettings.asset",
})
_AUTORUN_NAMES = frozenset({
    "InitializeOnLoad", "InitializeOnLoadMethod", "DidReloadScripts", "PostProcessBuild",
    "PostProcessScene", "OnOpenAsset",
})
_AUTORUN_BASES = frozenset({"AssetPostprocessor", "AssetModificationProcessor"})
_YAML_BOILER = frozenset({
    "m_Script", "m_EditorClassIdentifier", "m_ObjectHideFlags", "m_CorrespondingSourceObject",
    "m_PrefabInstance", "m_PrefabAsset", "m_GameObject", "m_Enabled", "m_Name", "m_EditorHideFlags",
})
# Characters that would hide or reorder text in a dialog (line and paragraph separators, carriage return, NEL,
# other control characters, bidi and zero-width marks). Shown escaped in the plan and the second question.
_HIDDEN_RANGES = ((0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x9F), (0x061C, 0x061C), (0x200B, 0x200F), (0x2028, 0x202E),
                  (0x2060, 0x2064), (0x2066, 0x2069), (0xFEFF, 0xFEFF))
# Built from code points: Hermes' install scan blocks a plugin whose source holds these characters (or chains of
# their escapes), and the regex needs them.
_INVISIBLE = re.compile("[" + "".join(re.escape(chr(low)) + ("-" + re.escape(chr(high)) if high != low else "")
                                      for low, high in _HIDDEN_RANGES) + "]")


def visible(text: str) -> str:
    """text with every character that could hide, break, or reorder a line shown as \\uXXXX (\\r as \\r)."""
    return _INVISIBLE.sub(lambda m: "\\r" if m.group(0) == "\r" else f"\\u{ord(m.group(0)):04x}", text)


def utf16_len(text: str) -> int:
    """UTF-16 code units. Telegram's 4096 cap counts these (Hermes v0.22.2 gateway/platforms/base.py)."""
    return len(text.encode("utf-16-le")) // 2


def question_fits_cards(question: str) -> bool:
    """True when Hermes 0.22.2 would show this question whole on Discord, Slack, and Telegram.

    Telegram HTML-escapes the card and then counts UTF-16, so a raw length under SECOND_CAP can still be cut
    when the text contains &. A question that would be cut is not sent.
    """
    if any(len(question) > cap for cap in _CARD_RAW_CAP.values()):
        return False
    escaped = html.escape(question, quote=True)
    return utf16_len(escaped) <= _TELEGRAM_ESCAPED_CAP


def _generated_project_file(rel: str) -> bool:
    """Unity rewrites these at the project root when scripts compile (the .csproj and the .sln)."""
    return "/" not in rel and rel.endswith((".csproj", ".sln", ".slnx"))


def _keep_editor_file(rel: str) -> bool:
    """A file Unity 6000.6 writes on its own, so it is not an unplanned change.

    The names in _EDITOR_CHURN were measured on a new project. Window layouts are the files under
    UserSettings/Layouts ending in .dwlt (the editor log says "About to save layout" for
    UserSettings/Layouts/default-6000.dwlt). A log a project script writes under UserSettings is not one of these.
    """
    if rel in _EDITOR_CHURN:
        return True
    return rel.startswith("UserSettings/Layouts/") and rel.endswith(".dwlt")


def pending_asset_imports(root: str) -> list[str]:
    """Assets and folders under Assets that have no .meta yet.

    Unity writes that .meta the next time it imports. The Assets folder itself has no Assets.meta.
    Hidden names and links are skipped, the same way the project walk skips them.
    """
    if not root:
        return []
    assets = os.path.join(root, "Assets")
    if not os.path.isdir(assets):
        return []
    found: list[str] = []
    for current, dirs, files in os.walk(assets):
        dirs[:] = [item for item in dirs if not item.startswith(".")
                   and not os.path.islink(os.path.join(current, item))]
        rel_dir = os.path.relpath(current, root).replace(os.sep, "/")
        if rel_dir != "Assets" and not os.path.isfile(os.path.join(root, rel_dir + ".meta")):
            found.append(rel_dir)
        for name in files:
            if name.startswith(".") or name.endswith(".meta"):
                continue
            full = os.path.join(current, name)
            if os.path.islink(full) or os.path.isfile(full + ".meta"):
                continue
            found.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(found)


def _import_sentence(paths: list[str]) -> str:
    """The plan line for assets Unity will import. A long list is a count and the first names."""
    if not paths:
        return ""
    shown = ", ".join(paths) if len(paths) <= _IMPORT_SHOWN else (
        f"{len(paths)} assets, including " + ", ".join(paths[:_IMPORT_SHOWN]))
    return ("Unity will import these (.meta will be created): " + shown
            + ". Those .meta files are an effect of this plan.")


def _unity_meta_file(full: str) -> bool:
    """True when the file starts the way Unity writes a .meta (fileFormatVersion)."""
    try:
        with open(full, "rb") as handle:
            head = handle.read(64)
    except OSError:
        return False
    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    return head.startswith(b"fileFormatVersion:")


def orphan_unity_metas(root: str) -> list[str]:
    """Unity .meta files under Assets whose asset or folder is not on disk.

    Unity rewrites or removes that .meta on the next refresh (the editor log says the asset can't be found).
    A .meta that does not start with fileFormatVersion is left out, so a hand-written file is still put back.
    """
    if not root:
        return []
    assets = os.path.join(root, "Assets")
    if not os.path.isdir(assets):
        return []
    found: list[str] = []
    for current, dirs, files in os.walk(assets):
        dirs[:] = [item for item in dirs if not item.startswith(".")
                   and not os.path.islink(os.path.join(current, item))]
        for name in files:
            if name.startswith(".") or not name.endswith(".meta"):
                continue
            full = os.path.join(current, name)
            if os.path.islink(full) or os.path.lexists(full[:-5]):
                continue
            if not _unity_meta_file(full):
                continue
            found.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(found)


def _orphan_sentence(paths: list[str]) -> str:
    """The plan line for a Unity .meta whose asset is already missing."""
    if not paths:
        return ""
    shown = ", ".join(paths) if len(paths) <= _IMPORT_SHOWN else (
        f"{len(paths)} .meta files, including " + ", ".join(paths[:_IMPORT_SHOWN]))
    return ("Unity will refresh these .meta files because the asset is missing: " + shown
            + ". Those changes are an effect of this plan.")


def manifest_ahead_of_lock(root: str) -> bool:
    """True when the manifest names a package the lock file does not list yet.

    Unity rewrites Packages/packages-lock.json on the next refresh. A lock that already lists every
    manifest package is not included, so a later edit of that file is still put back.
    """
    if not root:
        return False
    man_path = os.path.join(root, "Packages", "manifest.json")
    lock_path = os.path.join(root, "Packages", "packages-lock.json")
    try:
        with open(man_path, encoding="utf-8") as handle:
            man = json.loads(handle.read())
    except (OSError, ValueError):
        return False
    man_deps = man.get("dependencies") if isinstance(man, dict) else None
    if not isinstance(man_deps, dict) or not man_deps:
        return False
    lock_deps: dict = {}
    try:
        with open(lock_path, encoding="utf-8") as handle:
            lock = json.loads(handle.read())
    except (OSError, ValueError):
        lock = {}
    if isinstance(lock, dict) and isinstance(lock.get("dependencies"), dict):
        lock_deps = lock["dependencies"]
    return any(name not in lock_deps for name in man_deps)


def _meta_of_prior_body(rel: str, before: dict) -> bool:
    """A .meta Unity writes for an asset or folder that was already on disk.

    The Assets folder itself has no Assets.meta, so a new file of that name is not kept.
    A .meta whose asset was created during this apply is not kept.
    """
    if not rel.endswith(".meta"):
        return False
    asset = rel[:-5]
    if asset in ("Assets", "Packages", "ProjectSettings", "UserSettings"):
        return False
    if asset in before:
        return True
    prefix = asset + "/"
    return any(old.startswith(prefix) for old in before)


def _unplanned_clause(reverted: list[str], left: list[str]) -> str:
    """What to append when the project does not match the plan. Empty when nothing was unexpected.

    plan_batch accepts steps only, so the text does not tell the caller to name a file in the next plan.
    """
    parts = []
    if reverted:
        parts.append("files changed that this plan did not name, and were put back: " + ", ".join(reverted))
    if left:
        parts.append("files appeared that this plan did not name, and were left in place: " + ", ".join(left)
                     + ". plan_batch only accepts steps, so it cannot name an extra file. Make a new plan; "
                       "it reads the files already on disk")
    return ". ".join(parts)


def _strip_cs(source: str) -> str | None:
    """source with comments and strings blanked. None when a string or comment is not closed."""
    out: list[str] = []
    i, n = 0, len(source)
    while i < n:
        c = source[i]
        nxt = source[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            end = source.find("\n", i)
            if end < 0:
                out.append(" " * (n - i))
                break
            out.append(" " * (end - i))
            i = end
            continue
        if c == "/" and nxt == "*":
            end = source.find("*/", i + 2)
            if end < 0:
                return None
            out.append(" " * (end + 2 - i))
            i = end + 2
            continue
        if c == "@" and nxt == '"':
            j = i + 2
            while j < n:
                if source[j] == '"':
                    if j + 1 < n and source[j + 1] == '"':
                        j += 2
                        continue
                    j += 1
                    break
                j += 1
            else:
                return None
            out.append(" " * (j - i))
            i = j
            continue
        if c == '"':
            j = i + 1
            while j < n:
                if source[j] == "\\":
                    j += 2
                    continue
                if source[j] == '"':
                    j += 1
                    break
                if source[j] == "\n":
                    return None
                j += 1
            else:
                return None
            out.append(" " * (j - i))
            i = j
            continue
        if c == "'":
            j = i + 1
            while j < n and source[j] != "'":
                if source[j] == "\\":
                    j += 2
                    continue
                if source[j] == "\n":
                    return None
                j += 1
            else:
                if j >= n:
                    return None
            out.append(" " * (j + 1 - i))
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _attr_leaf(token: str) -> str:
    """The attribute or base type the way C# resolves it: drop global::, the namespace, and a trailing Attribute."""
    token = token.strip()
    if token.startswith("global::"):
        token = token[len("global::"):]
    leaf = token.split(".")[-1].split("<", 1)[0].strip()
    if leaf.endswith("Attribute") and leaf != "Attribute":
        leaf = leaf[: -len("Attribute")]
    return leaf


def _attribute_at(text: str, index: int) -> bool:
    """True when text[index] is '[' of an attribute list, not an indexer or an array rank."""
    if index >= len(text) or text[index] != "[":
        return False
    j = index + 1
    while j < len(text) and text[j] in " \t\r\n":
        j += 1
    if j >= len(text):
        return False
    if text.startswith("global::", j):
        pass
    elif not (text[j].isalpha() or text[j] == "_"):
        return False
    k = index - 1
    while k >= 0 and text[k] in " \t\r\n":
        k -= 1
    if k < 0:
        return True
    prev = text[k]
    if prev == "]":
        return True
    if prev.isalnum() or prev == "_" or prev in ")]":
        return False
    return True


def editor_markers(source: str) -> tuple[list[str], bool]:
    """Attribute and base-type names Unity runs by itself, and whether the source could not be read that way.

    Combined attributes ([Serializable, InitializeOnLoad]) and global:: names are one list, the way the C#
    compiler reads an attribute section. Unknown (unbalanced, or an unclosed string) means the caller treats the
    script as editor code.
    """
    blank = _strip_cs(source)
    if blank is None:
        return [], True
    found: list[str] = []
    i, n = 0, len(blank)
    while i < n:
        if blank[i] != "[" or not _attribute_at(blank, i):
            i += 1
            continue
        depth = 0
        j = i
        closed = False
        while j < n:
            if blank[j] == "[":
                depth += 1
            elif blank[j] == "]":
                depth -= 1
                if depth == 0:
                    closed = True
                    break
            j += 1
        if not closed:
            return found, True
        body = blank[i + 1:j]
        parts: list[str] = []
        start, depth_paren, depth_br = 0, 0, 0
        for pos, ch in enumerate(body):
            if ch == "(":
                depth_paren += 1
            elif ch == ")":
                depth_paren = max(0, depth_paren - 1)
            elif ch == "[":
                depth_br += 1
            elif ch == "]":
                depth_br = max(0, depth_br - 1)
            elif ch == "," and depth_paren == 0 and depth_br == 0:
                parts.append(body[start:pos])
                start = pos + 1
        parts.append(body[start:])
        for part in parts:
            head = part.split("(", 1)[0].strip()
            if not head:
                continue
            leaf = _attr_leaf(head)
            if leaf in _AUTORUN_NAMES and leaf not in found:
                found.append(leaf)
        i = j + 1
    for match in re.finditer(r"\bclass\s+[A-Za-z_][\w]*\s*:\s*([^{;]+)", blank):
        for part in match.group(1).split(","):
            piece = part.strip()
            if not piece:
                continue
            piece = piece.split("where", 1)[0].strip()
            leaf = _attr_leaf(piece.split()[-1] if piece.split() else "")
            if leaf in _AUTORUN_BASES and leaf not in found:
                found.append(leaf)
    return found, False


def _span_text(text: str, edit: dict) -> str | None:
    """The characters one apply_text_edits span covers. Lines and columns are 1-based; the end column is exclusive
    (the same numbers this plugin sends for a whole-file overwrite). None when the span is not in the file."""
    try:
        start_line = int(edit.get("startLine"))
        start_col = int(edit.get("startCol"))
        end_line = int(edit.get("endLine"))
        end_col = int(edit.get("endCol"))
    except (TypeError, ValueError):
        return None
    rows = text.splitlines()
    if start_line < 1 or end_line < start_line or start_col < 1 or end_col < 1:
        return None
    if not rows:
        return "" if start_line == 1 and end_line == 1 and start_col == 1 and end_col == 1 else None
    if end_line > len(rows):
        return None
    chunks = []
    for line in range(start_line, end_line + 1):
        row = rows[line - 1]
        left = start_col if line == start_line else 1
        right = end_col if line == end_line else len(row) + 1
        if left < 1 or right < left or right > len(row) + 1:
            return None
        chunks.append(row[left - 1:right - 1])
    return "\n".join(chunks)


def _mono_fields(text: str) -> list[tuple[str, str]] | None:
    """Serialized fields of the one MonoBehaviour document, nested lists included. None when the YAML is not that
    one document (the plan is then refused)."""
    if re.search(r"(?m)^--- !u!\d+ &\d+ stripped\b", text):
        return None
    docs = re.split(r"(?m)^--- ", text)
    bodies = []
    for doc in docs:
        hit = re.search(r"(?m)^MonoBehaviour:\s*$", doc)
        if hit:
            bodies.append(doc[hit.end():])
    if len(bodies) != 1:
        return None
    lines = bodies[0].splitlines()
    fields: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("---"):
            break
        hit = re.match(r"^  ([A-Za-z_][\w]*):(.*)$", line)
        if not hit:
            if line.startswith(" "):
                return None
            break
        name, rest = hit.group(1), hit.group(2)
        index += 1
        nested: list[str] = []
        if rest.strip() == "":
            while index < len(lines):
                nxt = lines[index]
                if nxt.strip() == "" or nxt.startswith("---") or re.match(r"^  [A-Za-z_][\w]*:", nxt):
                    break
                if not nxt.startswith(" "):
                    return None
                nested.append(nxt)
                index += 1
            value = "\n".join(nested)
        else:
            value = rest.strip()
        if name not in _YAML_BOILER:
            fields.append((name, value))
    return fields


def _asmdef_editor(path: str, raw: str) -> tuple[bool, str]:
    """Whether Unity compiles this assembly for the editor. Unreadable JSON is editor (the caller asks)."""
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        return True, "the assembly definition is not JSON, so it is treated as an editor assembly"
    if not isinstance(body, dict):
        return True, "the assembly definition is not an object, so it is treated as an editor assembly"
    platforms = body.get("includePlatforms")
    if not isinstance(platforms, list) or not all(isinstance(item, str) for item in platforms):
        return True, "includePlatforms could not be read, so the assembly is treated as an editor assembly"
    if "Editor" in platforms:
        return True, f"includePlatforms is {platforms}, so Unity compiles it for the editor"
    if any(part == "Editor" for part in path.split("/")) and not platforms:
        return True, "it is under an Editor folder and the assembly does not say otherwise"
    return False, ""


def _script_editor_reason(path: str, root: str) -> tuple[bool, str]:
    """Unity's Editor folder and the nearest asmdef. An asmdef that cannot be read counts as editor."""
    directory = os.path.join(root, *path.split("/")[:-1])
    stop = os.path.join(root, "Assets")
    cursor = directory
    asmdef = None
    while cursor.startswith(stop):
        try:
            names = os.listdir(cursor)
        except OSError:
            names = []
        found = [name for name in names if name.endswith(".asmdef")]
        if found:
            asmdef = os.path.join(cursor, found[0])
            break
        if cursor == stop:
            break
        parent = os.path.dirname(cursor)
        if parent == cursor:
            break
        cursor = parent
    if asmdef:
        try:
            raw = Path(asmdef).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return True, "the assembly definition could not be read, so the script is treated as editor code"
        return _asmdef_editor(path, raw)
    if any(part == "Editor" for part in path.split("/")):
        return True, "a folder named Editor, which Unity compiles only for the editor"
    return False, ""


def _truthy(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no", "none", "null")
    return bool(value)


def _arg(send: dict, param: str):
    want = param.replace("_", "").lower()
    for key, value in send.items():
        if str(key).replace("_", "").lower() == want:
            return value
    return None


def _gate_holds(step: dict, gate: dict) -> bool:
    """One argument gate of an effect site, with upstream's default when the step leaves the argument out."""
    value = _arg(step.get("send") or {}, gate["param"])
    if value is None:
        prop = ((UPSTREAM_SCHEMAS.get(step["spec"].get("upstream_tool") or "") or {}).get("properties") or {}) \
            .get(gate["param"]) or {}
        value = prop.get("default")
    if "equals" in gate:
        return (str(value).lower() == str(gate["equals"]).lower()) == gate["truthy"]
    return _truthy(value) == gate["truthy"]


def step_effects(step: dict) -> list[dict]:
    """The table's effect sites for this op whose argument gates hold for this step's arguments."""
    return [row for row in step["spec"].get("effects") or []
            if all(_gate_holds(step, gate) for gate in row.get("when_params") or [])]


def step_kinds(step: dict) -> set[str]:
    return {row["kind"] for row in step_effects(step)}


def _user_deletes(step: dict) -> list[dict]:
    """Deletes of files the step names (not upstream's own temp, backup, or marker files)."""
    return [row for row in step_effects(step) if row["kind"] == "delete_file" and not row.get("scratch")]


def op_deletes(step: dict) -> bool:
    """The step deletes a file it names, or destroys an object of the caller's (not one upstream made itself)."""
    rows = step_effects(step)
    if any(row["kind"] == "destroy_object" and not row.get("scratch") for row in rows):
        return True
    return bool(_user_deletes(step)) and bool(step["paths"] or step.get("targets"))


def op_writes_files(step: dict) -> bool:
    return bool(step_kinds(step) & {"write_file", "save_assets"}) or step.get("bridge") == "create_asmdef"


def op_edits_scene(step: dict) -> bool:
    """Objects in the open scene change (instantiate, set values, destroy, move) and no file is the target."""
    return bool(step_kinds(step) & {"instantiate", "set_values", "scene_edit", "destroy_object", "simulate"}) \
        and not (step["paths"] or step.get("targets"))


def op_compiles(step: dict) -> bool:
    """Unity has to compile after this step before the next one can use its types (measured in _step_facts)."""
    return bool(step.get("compiles"))


def op_enters_play(step: dict) -> bool:
    return "enter_play" in step_kinds(step)


def op_runs_tests(step: dict) -> bool:
    return "run_tests" in step_kinds(step)


def _build_output_rel(step: dict) -> str | None:
    """The player output the plan named, or upstream's default Builds/<target> when the plan left it out."""
    if "build_player" not in step_kinds(step):
        return None
    raw = (step.get("send") or {}).get("output_path")
    if isinstance(raw, str) and raw.strip():
        return raw.replace("\\", "/").strip()
    target = (step.get("send") or {}).get("target")
    if isinstance(target, str) and target.strip():
        return "Builds/" + target.strip().strip("/")
    return None


def _site(row: dict) -> str:
    when = "; ".join(row.get("when") or [])
    more = f", +{row['more']} more" if row.get("more") else ""
    return f"{row['api']}, {row['at']}" + (f", when {when}" if when else "") + more


def inside_lines(step: dict) -> list[str]:
    """One line per effect kind this step reaches, with the call and where it is. Upstream's own scratch files and
    objects, and reflection into Unity's internals, are left out here (describe lists every site)."""
    rows = [row for row in step_effects(step) if not row.get("scratch")]
    lines = []
    for kind in SHOWN_KINDS:
        if kind == "reflection":
            continue
        found = [row for row in rows if row["kind"] == kind]
        if found:
            lines.append(f"  inside: {EFFECT_WORDS.get(kind, kind)} ({_site(found[0])})")
    return lines


def _value_lines(key: str, value) -> list[str]:
    if isinstance(value, str) and "\n" in value:
        rows = value.split("\n")
        if rows and rows[-1] == "":
            rows = rows[:-1]
        return [f"    {visible(key)} ({len(rows)} lines):"] + ["      | " + visible(row) for row in rows]
    shown = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return [f"    {visible(key)}: {visible(shown)}"]


def _risk_summary(steps: list[dict]) -> str:
    parts = []
    for index, step in enumerate(steps, 1):
        risks = step.get("risks") or []
        if risks:
            parts.append(f"step {index} " + " and ".join(RISK_WORDS[item] for item in risks))
    return "; ".join(parts)


def plan_text(steps: list[dict], ctx: dict) -> str:
    """The whole change in words. ctx carries what the bridge measured in the editor before planning."""
    total = len(steps)
    lines = [
        f"Plan for the Unity editor {ctx.get('instance') or '(the one connected)'}, project {ctx.get('root') or '?'}.",
        f"These steps have not been sent. apply_plan runs exactly these steps, in this order, once, within "
        f"{int(PLAN_TTL // 60)} minutes. A newer plan replaces this one.",
        "Hermes asks once before apply_plan runs. That dialog names only the tool, so show this whole text "
        "to the user before calling apply_plan.",
        "Unity itself rewrites " + ", ".join(sorted(_EDITOR_CHURN))
        + ", window layouts under UserSettings/Layouts (files ending in .dwlt), and a compile may rewrite "
        "*.csproj, *.sln, and *.slnx at the project root. Those stay. A changed file this plan does not name "
        "is put back. A file this apply created that this plan does not name is put back. A .meta stays when "
        "its asset or folder was already on disk. plan_batch only accepts steps, so that error cannot ask for "
        "the file to be named.",
    ]
    imported = _import_sentence(list(ctx.get("pending_imports") or []))
    if imported:
        lines.append(imported)
    orphans = _orphan_sentence(list(ctx.get("orphan_metas") or []))
    if orphans:
        lines.append(orphans)
    if ctx.get("lock_refresh"):
        lines.append("Unity will rewrite Packages/packages-lock.json because the manifest lists a package the "
                     "lock does not. That rewrite is an effect of this plan.")
    risky = _risk_summary(steps)
    if risky:
        lines.append(f"Second question: {risky}. apply_plan asks once more with the full summary of those risks. "
                     f"The code is not shortened. The question is sent only when it fits a Hermes 0.22.2 chat card "
                     f"(at most {SECOND_CAP} characters, and Telegram counts the escaped text), and nothing runs "
                     f"unless it is accepted too. Where Hermes cannot show that question (the classic CLI), or the "
                     f"summary does not fit, apply_plan runs nothing and asks for confirm_risky_plan, which Hermes "
                     f"asks about once more.")
    else:
        lines.append("No step deletes, runs editor code, loses or saves over unsaved work, or sends or writes "
                     "outside the project, so there is no second question.")
    if any(op_enters_play(step) or op_runs_tests(step) for step in steps):
        lines.append("Play mode and tests run the project's own scripts (Awake, Start, Update, the test code).")
    if ctx.get("playing"):
        lines.append("Unity is in play mode now. Scene changes made in play mode are dropped when play stops.")
    lines.append("")
    for index, step in enumerate(steps, 1):
        origin = f" ({step['origin']})" if step.get("origin") else ""
        lines.append(f"step {index} of {total}: {step['tool']} {step['op']}{origin}")
        lines.append("  does: " + op_does(step))
        inside = inside_lines(step)
        same = next((number for number, earlier in enumerate(steps[:index - 1], 1)
                     if earlier["op"] == step["op"] and inside_lines(earlier) == inside), None)
        if inside and same:
            lines.append(f"  inside: as step {same} (the same operation reaches the same calls)")
        else:
            lines.extend(inside)
        for fact in step.get("facts") or []:
            lines.append("  " + visible(fact))
        if step.get("risks"):
            lines.append("  second question: this step " + " and ".join(RISK_WORDS[item] for item in step["risks"])
                         + ".")
        if op_compiles(step):
            later = steps[index] if index < total else None
            if later is None or not op_compiles(later):
                lines.append(f"  then: the plugin asks Unity to refresh and compile (refresh_unity, compile request), "
                             f"waits for that compile to finish (up to {int(COMPILE_WAIT)} seconds), and reads its "
                             f"error CS lines. Compile errors stop the plan here and are returned.")
        for check in step.get("checks") or []:
            lines.append("  check after: " + check)
        if step["show"]:
            lines.append("  values:")
            for key in sorted(step["show"]):
                lines.extend(_value_lines(key, step["show"][key]))
        lines.append("")
    lines.append("If the editor changes before apply_plan (the selected editor, play mode, the open scenes, their "
                 "objects, or a file above), apply_plan runs nothing and asks for a new plan. Component values are "
                 "not part of that check: reading them runs C# in the editor, and a plan does not do that.")
    lines.append("Accept runs every step above. Deny runs none.")
    return "\n".join(lines) + "\n"


def second_question(steps: list[dict], plan_id: str, plan_chars: int) -> str:
    """The text of the second question, in full. Empty when a Hermes 0.22.2 card would cut it.

    Code and deleted text are not shortened here. A question that does not fit is not sent (apply_plan then asks
    for confirm_risky_plan). Cutting it and still sending it would hide the code.
    """
    head = [f"Unity plan {plan_id}: {len(steps)} step(s). Accept runs all of them; decline runs none and discards "
            f"the plan."]
    for risk in RISK_WORDS:
        items = []
        for index, step in enumerate(steps, 1):
            for kind, text in step.get("risk_lines") or []:
                if kind == risk:
                    # a run of backticks would close the chat app's code block around the question
                    shown = re.sub("`{3,}", lambda m: "\\u0060" * len(m.group(0)), visible(text))
                    items.append(f"step {index} {shown}")
        if items:
            head.append(f"{RISK_HEADS[risk]}: " + "; ".join(items))
    names = [f"{index} {step['op']}" for index, step in enumerate(steps, 1)]
    tail = (f"The whole plan ({plan_chars} characters, every value and line of code) is the plan_batch reply "
            f"with this plan_id.")
    text = "\n".join(head + ["Steps: " + ", ".join(names), tail])
    if len(text) <= SECOND_CAP and question_fits_cards(text):
        return text
    return ""


def _timeout_for(spec: dict) -> float:
    flags = spec.get("flags") or []
    if "runs_code" in flags or "sends" in flags:
        return LONG_TIMEOUT
    return CALL_TIMEOUT


def _first_json(content: list):
    for item in content:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            try:
                return json.loads(item["text"])
            except ValueError:
                continue
    return None


def _content_text(content: list) -> str:
    return "\n".join(item.get("text", "") for item in content if isinstance(item, dict))


def _lines(content: list) -> list:
    """Hermes joins the text parts of an error result with no separator: end each part with a line break."""
    out = []
    for item in content:
        if item.get("type") == "text" and isinstance(item.get("text"), str) and not item["text"].endswith("\n"):
            item = dict(item, text=item["text"] + "\n")
        out.append(item)
    return out


def limit_result(content: list, is_error: bool) -> dict:
    text = _content_text(content)
    if len(text.encode("utf-8")) <= MAX_RESULT_BYTES:
        return {"content": content, "isError": is_error}
    note = f"{NAME}: truncated at {MAX_RESULT_BYTES} bytes. Ask for less."
    return {"content": [{"type": "text", "text": note}], "isError": True}


class Child:
    """One upstream server process, spoken to over stdio JSON-RPC."""

    def __init__(self, argv: list[str], env: dict) -> None:
        self.proc = subprocess.Popen(
            argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        self.lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.pending: dict[int, dict] = {}
        self.next_id = 1
        self.stderr_head = b""
        self.closed = threading.Event()
        self.listing_ready = False
        self.on_tools_changed = None
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def alive(self) -> bool:
        return self.proc.poll() is None and not self.closed.is_set()

    def stderr_text(self) -> str:
        return self.stderr_head[:MAX_STDERR].decode("utf-8", "replace").strip()

    def _read_stderr(self) -> None:
        for line in iter(self.proc.stderr.readline, b""):
            if len(self.stderr_head) < 4 * MAX_STDERR:
                self.stderr_head += line
            try:
                sys.stderr.buffer.write(line)
                sys.stderr.flush()
            except (OSError, ValueError):
                pass

    def _read_stdout(self) -> None:
        for raw in iter(self.proc.stdout.readline, b""):
            line = raw.strip()
            if not line.startswith(b"{"):
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue
            if "method" in msg and "id" in msg:
                self._answer_server_request(msg)
                continue
            if msg.get("method") == "notifications/tools/list_changed":
                if self.listing_ready and self.on_tools_changed is not None:
                    self.on_tools_changed()
                continue
            if "id" not in msg or "method" in msg:
                continue
            with self.lock:
                slot = self.pending.get(msg["id"])
            if slot is not None:
                slot["reply"] = msg
                slot["event"].set()
        self.closed.set()
        with self.lock:
            slots = list(self.pending.values())
        for slot in slots:
            slot["event"].set()

    def _answer_server_request(self, msg: dict) -> None:
        method = msg.get("method")
        if method == "ping":
            reply = {"jsonrpc": "2.0", "id": msg["id"], "result": {}}
        elif method == "roots/list":
            reply = {"jsonrpc": "2.0", "id": msg["id"], "result": {"roots": []}}
        else:
            reply = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "Method not found"}}
        self.send(reply)

    def send(self, msg: dict) -> bool:
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            with self.write_lock:
                self.proc.stdin.write(data)
                self.proc.stdin.flush()
            return True
        except (OSError, ValueError):
            return False

    def request(self, method: str, params: dict, timeout: float, on_id=None) -> dict:
        with self.lock:
            rid = self.next_id
            self.next_id += 1
            slot = {"event": threading.Event(), "reply": None}
            self.pending[rid] = slot
        if on_id is not None:
            on_id(rid)
        try:
            if not self.send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params}):
                return {"bridge_error": "exited"}
            slot["event"].wait(timeout)
            if slot["reply"] is not None:
                return slot["reply"]
            if self.closed.is_set() or self.proc.poll() is not None:
                return {"bridge_error": "exited"}
            self.send({"jsonrpc": "2.0", "method": "notifications/cancelled",
                       "params": {"requestId": rid, "reason": "timeout"}})
            return {"bridge_error": "timeout"}
        finally:
            with self.lock:
                self.pending.pop(rid, None)

    def stop(self) -> None:
        self.closed.set()
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        except OSError:
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        for stream in (self.proc.stdout, self.proc.stderr):
            try:
                if stream:
                    stream.close()
            except OSError:
                pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if _http_host(newurl) not in LOOPBACK_HOSTS:
            raise urllib.error.URLError("redirect left this machine")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HttpChild:
    """MCP streamable HTTP on a loopback URL. proc is set only when this process started the server."""

    def __init__(self, base_url: str, proc: subprocess.Popen | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.endpoint = self.base_url + "/mcp"
        self.proc = proc
        self.session: str | None = None
        self.lock = threading.Lock()
        self.next_id = 1
        self.stderr_head = b""
        self.closed = threading.Event()
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
        if proc is not None and proc.stderr is not None:
            threading.Thread(target=self._read_stderr, daemon=True).start()

    def alive(self) -> bool:
        if self.closed.is_set():
            return False
        return self.proc is None or self.proc.poll() is None

    def stderr_text(self) -> str:
        return self.stderr_head[:MAX_STDERR].decode("utf-8", "replace").strip()

    def _read_stderr(self) -> None:
        stream = self.proc.stderr if self.proc is not None else None
        if stream is None:
            return
        for line in iter(stream.readline, b""):
            if len(self.stderr_head) < 4 * MAX_STDERR:
                self.stderr_head += line

    def stop(self) -> None:
        self.closed.set()
        proc = self.proc
        if proc is None or proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    def send(self, msg: dict) -> bool:
        try:
            self._post(msg, 30, wait_body=False)
            return True
        except (OSError, urllib.error.URLError, TimeoutError, ValueError):
            self.closed.set()
            return False

    def request(self, method: str, params: dict, timeout: float, on_id=None) -> dict:
        with self.lock:
            rid = self.next_id
            self.next_id += 1
        if on_id is not None:
            on_id(rid)
        msg = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params}
        try:
            reply = self._post(msg, timeout, wait_body=True)
        except (OSError, urllib.error.URLError, TimeoutError, ValueError):
            self.closed.set()
            return {"bridge_error": "exited"}
        if reply is None:
            return {"bridge_error": "timeout"}
        return reply

    def _post(self, msg: dict, timeout: float, wait_body: bool) -> dict | None:
        data = json.dumps(msg).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": CHILD_PROTOCOL,
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(self.endpoint, data=data, headers=headers, method="POST")
        try:
            with self._opener.open(req, timeout=timeout) as resp:
                session = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
                if session:
                    self.session = session
                if not wait_body or resp.status == 202:
                    return {"jsonrpc": "2.0", "result": {}}
                raw = resp.read()
                ctype = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            raw = exc.read() if exc.fp is not None else b""
            ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
            if not raw:
                raise
        if not raw:
            return {"bridge_error": "timeout"}
        return _mcp_http_body(raw, ctype)


def _mcp_http_body(raw: bytes, content_type: str) -> dict:
    text = raw.decode("utf-8", "replace")
    if "text/event-stream" in content_type:
        messages = []
        for block in text.split("\n\n"):
            data_lines = []
            for line in block.splitlines():
                if line.startswith("data:"):
                    data_lines.append(line[5:].lstrip())
            blob = "\n".join(data_lines).strip()
            if blob and blob != "[DONE]":
                try:
                    messages.append(json.loads(blob))
                except ValueError:
                    continue
        for msg in messages:
            if isinstance(msg, dict) and ("result" in msg or "error" in msg):
                return msg
        return messages[-1] if messages else {"bridge_error": "exited"}
    try:
        parsed = json.loads(text)
    except ValueError:
        return {"bridge_error": "exited"}
    return parsed if isinstance(parsed, dict) else {"bridge_error": "exited"}


class Bridge:
    def __init__(self, argv: list[str] | None = None, env: dict | None = None) -> None:
        self.explicit_argv = argv
        self.env = child_environment(env)
        self.child: Child | HttpChild | None = None
        self.upstream_tools: set[str] | None = None
        self.upstream_resources: set[str] | None = None
        self.start_lock = threading.Lock()
        self.out_lock = threading.Lock()
        self.inflight: dict = {}
        self.inflight_lock = threading.Lock()
        self.calls: list[threading.Thread] = []
        self.cancelled: set = set()
        self.scene_sha: dict[str, str | None] = {}
        self.selected_instance: str | None = None
        self.state_lock = threading.Lock()
        self._root_cache: str | None = None
        self._tools_stale = False
        self.plans: dict[str, dict] = {}
        self.plan_lock = threading.Lock()
        self.retired: set[str] = set()
        self.replaced_ids: set[str] = set()
        self.progress: dict = {}
        self.progress_lock = threading.Lock()
        self.client_caps: dict = {}
        self.client_lock = threading.Lock()
        self.client_next = 1
        self.client_pending: dict = {}
        self.compile_errors_now: list[str] = []
        self.stale_scripts: list[str] = []

    def _mark_tools_stale(self) -> None:
        self._tools_stale = True

    def _collect_tools(self, child) -> tuple[list | None, dict | None]:
        tools, cursor = [], None
        while True:
            listed = child.request("tools/list", {"cursor": cursor} if cursor else {}, START_TIMEOUT)
            if "result" not in listed:
                return None, listed
            tools.extend(listed["result"].get("tools") or [])
            cursor = listed["result"].get("nextCursor")
            if not cursor:
                return tools, None

    def _collect_uris(self, child) -> set[str]:
        uris: set[str] = set()
        for method, key, field in (("resources/list", "resources", "uri"),
                                   ("resources/templates/list", "resourceTemplates", "uriTemplate")):
            got = child.request(method, {}, START_TIMEOUT)
            for item in (got.get("result") or {}).get(key) or []:
                if isinstance(item, dict) and item.get(field):
                    uris.add(item[field])
        return uris

    def _enable_http_groups(self, child) -> None:
        if not isinstance(child, HttpChild):
            return
        for group in HTTP_ACTIVATE_GROUPS:
            child.request("tools/call", {"name": "manage_tools",
                                         "arguments": {"action": "activate", "group": group}}, START_TIMEOUT)

    def _open_child(self) -> tuple[Child | HttpChild | None, str]:
        if self.explicit_argv is not None:
            return Child(self.explicit_argv, self.env), ""
        if not editor_transport_http():
            return Child(upstream_argv(False, DEFAULT_HTTP_URL), self.env), ""
        url = editor_http_url()
        why = remote_http_refusal(url)
        if why:
            return None, why
        if port_open(url):
            return HttpChild(url), ""
        argv = upstream_argv(True, url)
        proc = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
        if not wait_port(url, START_TIMEOUT, proc):
            err = ""
            if proc.stderr is not None:
                try:
                    err = proc.stderr.read(4000).decode("utf-8", "replace").strip()
                except OSError:
                    err = ""
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            return None, err or (f"{NAME}: MCP for Unity did not open {url} on this machine. "
                                 f"EditorPrefs were not changed. {NOTHING_SENT}")
        return HttpChild(url, proc), ""

    def _start_failure(self, child, reply: dict) -> str:
        child.stop()
        head = child.stderr_text()
        if head:
            return head
        if reply.get("bridge_error") == "timeout":
            return (f"{NAME}: MCP for Unity did not answer within {int(START_TIMEOUT)} seconds. "
                    f"{NOTHING_SENT}")
        if "error" in reply:
            return str((reply["error"] or {}).get("message", reply["error"]))
        proc = getattr(child, "proc", None)
        code = proc.poll() if proc is not None else "not-started"
        return f"{NAME}: MCP for Unity exited with code {code} before it answered. {NOTHING_SENT}"

    def _start_child(self) -> str:
        if self.child is not None and self.child.alive():
            return ""
        if self.child is not None:
            self.child.stop()
        if not unity_hub_apps():
            return hub_missing_message()
        try:
            child, problem = self._open_child()
        except OSError as exc:
            return f"{NAME}: could not start MCP for Unity ({type(exc).__name__}: {exc}). {NOTHING_SENT}"
        if problem or child is None:
            return problem or f"{NAME}: MCP for Unity did not start. {NOTHING_SENT}"
        self.child = child
        init = child.request("initialize", {"protocolVersion": CHILD_PROTOCOL, "capabilities": {},
                                            "clientInfo": {"name": NAME, "version": VERSION}}, START_TIMEOUT)
        if "result" not in init:
            return self._start_failure(child, init)
        child.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, failed = self._collect_tools(child)
        if tools is None:
            return self._start_failure(child, failed or {})
        if isinstance(child, HttpChild):
            self._enable_http_groups(child)
            again, failed = self._collect_tools(child)
            if again is not None:
                tools = again
        self.upstream_tools = {item.get("name") for item in tools if isinstance(item, dict) and item.get("name")}
        self.upstream_resources = self._collect_uris(child)
        if isinstance(child, Child):
            child.listing_ready = True
            child.on_tools_changed = self._mark_tools_stale
        return ""

    def ensure_child(self) -> str:
        with self.start_lock:
            if self._tools_stale and self.child is not None and self.child.alive():
                self._tools_stale = False
                tools, _failed = self._collect_tools(self.child)
                if tools is not None:
                    self.upstream_tools = {item.get("name") for item in tools if isinstance(item, dict)}
            return self._start_child()

    # ---- small reads the bridge makes for itself (all read-only upstream calls) ----

    def _child_json(self, method: str, params: dict, timeout: float = CALL_TIMEOUT):
        """One raw upstream call. Returns the parsed JSON body, or None when there is none."""
        child = self.child
        if child is None:
            return None
        def once():
            reply = child.request(method, params, timeout)
            result = reply.get("result") if isinstance(reply, dict) else None
            if not isinstance(result, dict):
                return None
            items = result.get("contents") if method == "resources/read" else result.get("content")
            for item in items or []:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    raw = item["text"]
                    if len(raw.encode("utf-8")) > MAX_RESULT_BYTES:
                        return {"success": False, "error": f"{NAME}: truncated at {MAX_RESULT_BYTES} bytes. Ask for less."}
                    if "Could not connect to Unity" in raw:
                        return raw
                    try:
                        return json.loads(raw)
                    except ValueError:
                        continue
            return None

        body = once()
        # A read the bridge makes for itself (never a user's write) is tried once more when the editor was reloading.
        if isinstance(body, str) and "Could not connect to Unity" in body:
            body = once()
        return body if isinstance(body, dict) else None

    def _resource_json(self, uri: str, timeout: float = CALL_TIMEOUT):
        return self._child_json("resources/read", {"uri": uri}, timeout)

    def _tool_json(self, name: str, arguments: dict, timeout: float = CALL_TIMEOUT):
        return self._child_json("tools/call", {"name": name, "arguments": arguments}, timeout)

    def _editor_state(self) -> dict | None:
        body = self._resource_json("mcpforunity://editor/state", 5)
        if isinstance(body, dict) and body.get("success") is not False and isinstance(body.get("data"), dict):
            return body["data"]
        return None

    def _known_disk_root(self) -> str | None:
        hinted = (self.env or {}).get("FAKE_PROJECT_PATH") or ""
        if hinted and os.path.isdir(os.path.join(hinted, "Assets")):
            return hinted
        if self._root_cache and os.path.isdir(os.path.join(self._root_cache, "Assets")):
            return self._root_cache
        return None

    def disk_root(self) -> tuple[str | None, dict | None]:
        """The project folder for a disk read. The editor is not asked when the folder is already known."""
        known = self._known_disk_root()
        if known:
            return known, None
        return self.project_root()

    def project_root(self, fresh: bool = False) -> tuple[str | None, dict | None]:
        if self._root_cache and not fresh:
            return self._root_cache, None
        if self.child is None:
            return None, reply_for(explain("root"))
        body = self._resource_json("mcpforunity://project/info")
        root = ((body or {}).get("data") or {}).get("projectRoot") if isinstance(body, dict) else None
        if not isinstance(root, str) or not root:
            return None, reply_for(explain("root"))
        self._root_cache = root
        return root, None

    def _instance_ids(self) -> list[str] | None:
        body = self._resource_json("mcpforunity://instances")
        if not isinstance(body, dict) or body.get("success") is False:
            return None
        rows = body.get("instances")
        if not isinstance(rows, list):
            return None
        return [str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("id")]

    def _target_instance(self) -> tuple[str | None, str]:
        """The editor a plan is for: the one selected with set_active_instance, else the only one open.

        Entering play mode reloads the editor's scripts, and for a few seconds MCP for Unity lists only the other
        editors it knows (stale ones included). While the editor this session used is missing, wait for it
        instead of picking another one.
        """
        ids = self._instance_ids()
        end = time.time() + 15
        while (self.selected_instance and ids is not None and self.selected_instance not in ids
               and time.time() < end):
            time.sleep(0.5)
            ids = self._instance_ids()
        if ids is None:
            return None, ""
        if self.selected_instance and self.selected_instance in ids:
            return self.selected_instance, ""
        if len(ids) == 1:
            return ids[0], ""
        if not ids:
            return None, (f"{NAME}: No Unity Editor instances found. Open the project in Unity and start MCP for "
                          f"Unity. {NOTHING_SENT}")
        return None, explain("several", ", ".join(ids))

    def _pin(self, instance: str) -> bool:
        """Route the next calls to this editor. Routing only: upstream says it touches nothing in the project."""
        body = self._tool_json("set_active_instance", {"instance": instance}, START_TIMEOUT)
        if isinstance(body, dict) and "truncated" in str(body.get("error") or ""):
            self._last_block = str(body["error"])
            return False
        self._last_block = ""
        ok = isinstance(body, dict) and body.get("success") is True
        if ok and instance != self.selected_instance:
            self.selected_instance = instance
            self._root_cache = None
        return ok

    def _loaded_scenes(self) -> list[dict] | None:
        body = self._tool_json("manage_scene", {"action": "get_loaded_scenes"})
        scenes = ((body or {}).get("data") or {}).get("scenes") if isinstance(body, dict) else None
        if not isinstance(scenes, list):
            return None
        return [scene for scene in scenes if isinstance(scene, dict)]

    def _hierarchy_digest(self, playing: bool) -> str:
        """Objects of the open scene. Transforms count only in edit mode: in play mode they move every frame."""
        body = self._tool_json("manage_scene", {"action": "get_hierarchy", "page_size": 500,
                                                "max_nodes": 2000, "include_transform": not playing})
        data = (body or {}).get("data") if isinstance(body, dict) else None
        if not isinstance(data, dict):
            return "unreadable"
        blob = json.dumps({"items": data.get("items"), "total": data.get("total")}, sort_keys=True,
                          ensure_ascii=False, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _component_digest(self, playing: bool) -> str:
        """Component values are not read while a plan is made or checked. Reading them runs C# in the editor.

        The same string is used on both sides of the fingerprint, so a plan is not rejected for a value this
        check never took. In play mode the values change every frame anyway.
        """
        if playing:
            return "not compared in play mode"
        return "not read"

    def _state_busy(self, state: dict) -> bool:
        comp = state.get("compilation") or {}
        assets = state.get("assets") or {}
        refresh = assets.get("refresh") or {}
        return bool(comp.get("is_compiling") or comp.get("is_domain_reload_pending")
                    or refresh.get("is_refresh_in_progress") or assets.get("is_updating"))

    @staticmethod
    def _test_runner_busy(state: dict | None, scenes: list[dict] | None) -> bool:
        """The test runner is running, or still has its temporary InitTestScene open (it restores the user's
        scenes after a PlayMode run). A plan made then would be measured against that temporary scene."""
        if isinstance(state, dict) and (state.get("tests") or {}).get("is_running"):
            return True
        return any("InitTestScene" in str(scene.get("path") or scene.get("name") or "") for scene in scenes or [])

    def _wait_tests_settled(self, limit: float = READY_WAIT) -> bool:
        start = time.time()
        while time.time() - start < limit:
            state = self._editor_state()
            play = ((state or {}).get("editor") or {}).get("play_mode") or {}
            if state is None or self._state_busy(state) or play.get("is_playing") or play.get("is_changing") \
                    or self._test_runner_busy(state, self._loaded_scenes()):
                time.sleep(0.5)
                continue
            return True
        return False

    def _wait_settled(self, limit: float = READY_WAIT) -> bool:
        """Wait until Unity is not compiling, reloading, or importing."""
        start = time.time()
        while time.time() - start < limit:
            state = self._editor_state()
            if state is None or self._state_busy(state):
                time.sleep(0.5)
                continue
            return True
        return False

    def _wait_compile(self, since_ms: int, limit: float, mid, started_flag) -> str:
        """Wait for a compile that started at or after since_ms to finish. Returns done, timeout, or not-started.

        There is no early exit: a GUI editor in the background (not focused) does not start a debounced compile on
        its own (a script edited with scheduledRefresh true stayed uncompiled for 40 s in the 10/21 run), so the
        caller first asks for one with refresh_unity, and this waits for that one.
        """
        start = time.time()
        last_note = 0.0
        while time.time() - start < limit:
            if mid is not None and mid in self.cancelled:
                return "cancelled"
            state = self._editor_state()
            if time.time() - last_note > 2.0:
                self._progress(mid, f"waiting for Unity to compile ({int(time.time() - start)} s)")
                last_note = time.time()
            if state is None or self._state_busy(state):
                time.sleep(0.5)
                continue
            comp = state.get("compilation") or {}
            started = int(comp.get("last_compile_started_unix_ms") or 0)
            finished = int(comp.get("last_compile_finished_unix_ms") or 0)
            if started >= since_ms and finished >= started:
                time.sleep(0.5)
                again = self._editor_state() or {}
                again_comp = again.get("compilation") or {}
                if again and not self._state_busy(again) and \
                        int(again_comp.get("last_compile_started_unix_ms") or 0) == started:
                    return "done"
                continue
            if started_flag is False and time.time() - start > 15:
                return "not-started"
            time.sleep(0.5)
        return "timeout"

    @staticmethod
    def _stale_scripts(root: str) -> list[str]:
        """Scripts on disk newer than the newest compiled assembly (Library/ScriptAssemblies). A GUI editor in the
        background does not notice a file changed outside it, so play mode would run the old code."""
        compiled = 0.0
        assemblies = os.path.join(root, "Library", "ScriptAssemblies")
        try:
            for name in os.listdir(assemblies):
                if name.endswith(".dll"):
                    compiled = max(compiled, os.path.getmtime(os.path.join(assemblies, name)))
        except OSError:
            return []
        if not compiled:
            return []
        newer: list[str] = []
        for base in (os.path.join(root, "Assets"), os.path.join(root, "Packages")):
            for folder, dirs, files in os.walk(base):
                dirs[:] = [item for item in dirs if not item.startswith(".")
                           and not os.path.islink(os.path.join(folder, item))]
                for file in files:
                    if file.lower().endswith(_SCRIPT_EXT):
                        full = os.path.join(folder, file)
                        try:
                            if os.path.getmtime(full) > compiled + 1.0:
                                newer.append(os.path.relpath(full, root).replace(os.sep, "/"))
                        except OSError:
                            continue
        return sorted(newer)[:20]

    def _compile_errors(self) -> list[str]:
        """error CS lines in the console. Read right after a compile finished: Unity replaces its compiler messages
        at the end of each compile, so these belong to that compile (an earlier error that was fixed is gone)."""
        body = self._tool_json("read_console", {"action": "get", "types": ["error"], "count": 50,
                                                "format": "plain", "include_stacktrace": False})
        text = json.dumps(body, ensure_ascii=False) if body is not None else ""
        found = re.findall(r"[^\"\\]*error CS\d{4}[^\"\\]*", text)
        out: list[str] = []
        for line in found:
            line = line.strip()
            if line and line not in out:
                out.append(line)
        return out[:20]

    def _compile_now(self, since_ms: int, mid) -> tuple[list[dict], bool]:
        """Ask Unity to refresh and compile, wait for that compile, and read its errors."""
        self._progress(mid, "asking Unity to refresh and compile")
        reply = self._tool_json("refresh_unity", {"mode": "force", "scope": "all", "compile": "request",
                                                  "wait_for_ready": True}, CALL_TIMEOUT)
        data = (reply or {}).get("data") if isinstance(reply, dict) else None
        started_flag = data.get("compile_started") if isinstance(data, dict) else None
        if isinstance(reply, dict) and reply.get("success") is False and not (data or {}).get("recovered_from_disconnect"):
            why = str(reply.get("message") or reply.get("error") or reply.get("code") or "refresh failed")
            return [{"type": "text", "text": f"{NAME}: Unity did not take the refresh and compile request ({why})."}], True
        outcome = self._wait_compile(since_ms, COMPILE_WAIT, mid, started_flag)
        if outcome == "cancelled":
            return [{"type": "text", "text": explain("cancelled")}], True
        if outcome == "timeout":
            return [{"type": "text", "text": explain("busy", str(int(COMPILE_WAIT)))}], True
        if outcome == "not-started":
            return [{"type": "text", "text": (
                f"{NAME}: Unity did not start a compile after this step (in play mode Unity can hold it until play "
                f"stops, and a broken assembly setup can stop it). The new script is not in use yet.")}], True
        errors = self._compile_errors()
        if errors:
            return [{"type": "text", "text": f"{NAME}: Unity reported compile errors after this step:\n"
                     + "\n".join(errors)}], True
        return [{"type": "text", "text": f"{NAME}: Unity compiled with no errors."}], False

    # ---- replies ----

    def _fold_reply(self, reply: dict, ask: bool) -> dict:
        if reply.get("bridge_error") == "timeout":
            return error_result(f"{NAME}: did not answer in time. Unity may still be working. "
                                f"{NOTHING_SENT}")
        if reply.get("bridge_error"):
            return error_result(f"{NAME}: MCP for Unity exited during the call.")
        if "error" in reply:
            message = str((reply.get("error") or {}).get("message", reply["error"]))
            return error_result(message)
        result = reply.get("result") or {}
        raw_items = result.get("content")
        if raw_items is None and "contents" in result:
            raw_items = [{"type": "text", "text": item.get("text", "")}
                         for item in result.get("contents") or [] if isinstance(item, dict)]
        content = [item for item in (raw_items or []) if isinstance(item, dict)]
        if not content:
            content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
        is_error = bool(result.get("isError"))
        data = _first_json(content)
        if isinstance(data, dict) and data.get("success") is False:
            is_error = True
        text = _content_text(content)
        if isinstance(data, dict):
            total = data.get("totalCount")
            inner = data.get("data")
            if total == 0 or (isinstance(inner, dict) and inner.get("totalCount") == 0):
                content = list(content) + [{"type": "text", "text": explain("zero")}]
        if "Could not connect to Unity" in text:
            if ask:
                content = list(content) + [{"type": "text", "text": explain("not-retried")}]
                is_error = True
            else:
                return {"retry": True, "content": content, "isError": True}
        return limit_result(content, is_error)

    def _dispatch(self, step: dict, mid) -> dict:
        spec = step["spec"]
        if mid is not None and mid in self.cancelled:
            return reply_for(explain("cancelled"))
        if step.get("bridge") in ("describe", "asset_find", "prefab_info", "read_text", "create_asmdef"):
            return self._local(step)
        child = self.child
        if child is None:
            return reply_for(explain("root"))
        if step.get("resource_uri"):
            reply = child.request("resources/read", {"uri": step["resource_uri"]}, _timeout_for(spec))
            folded = self._fold_reply(reply, not step.get("read_only"))
            if folded.get("retry") and step.get("read_only"):
                self._wait_settled()
                folded = self._fold_reply(child.request("resources/read", {"uri": step["resource_uri"]},
                                                        _timeout_for(spec)), False)
                if folded.get("retry"):
                    folded = limit_result(folded["content"], True)
            return folded
        name = spec.get("upstream_tool")
        if self.upstream_tools is not None and name not in self.upstream_tools:
            return reply_for(explain("not-offered", str(name)))
        arguments = step["send"]

        def on_id(cid, holder=child):
            if mid is None:
                return
            with self.inflight_lock:
                self.inflight[mid] = (holder, cid)

        if not step.get("read_only"):
            # A script step before this one made Unity compile and reload; while it reloads, the server does not see
            # the editor. Wait for it first.
            self._wait_settled()
        reply = child.request("tools/call", {"name": name, "arguments": arguments}, _timeout_for(spec), on_id=on_id)
        if not step.get("read_only") and self.selected_instance and "not found. Available instances" in json.dumps(
                reply.get("result") or {}, ensure_ascii=False):
            # The server refused before sending anything to Unity (its editor list missed this one during a reload):
            # wait until the editor is back, select it again, and send the same step once more.
            deadline = time.time() + READY_WAIT
            while time.time() < deadline and not (self._wait_settled() and self._pin(self.selected_instance)):
                time.sleep(1.0)
            reply = child.request("tools/call", {"name": name, "arguments": arguments}, _timeout_for(spec),
                                  on_id=on_id)
        if mid is not None:
            with self.inflight_lock:
                self.inflight.pop(mid, None)
        folded = self._fold_reply(reply, not step.get("read_only"))
        if folded.get("retry") and step.get("read_only"):
            self._wait_settled()
            reply = child.request("tools/call", {"name": name, "arguments": arguments}, _timeout_for(spec))
            folded = self._fold_reply(reply, False)
            if folded.get("retry"):
                folded = limit_result(folded["content"], True)
        return folded

    # ---- checks before anything is sent ----

    def _needs_root(self, step: dict) -> bool:
        spec = step["spec"]
        if step.get("bridge") == "describe":
            return False
        if step.get("bridge") in ("asset_find", "prefab_info", "read_text", "create_asmdef") or self._composed_targets(step):
            return True
        if spec.get("upstream_tool") in ("create_script", "apply_text_edits"):
            return True
        if spec.get("upstream_tool") == "manage_scene" and spec.get("action") in ("save", "create", "load"):
            return True
        if step["op"] == "execute_custom_tool":
            return True
        return bool(step["paths"])

    def _snapshot_dirs(self) -> list[str]:
        """The folders upstream itself searches for memory snapshots (its temp cache folder and
        <project>/MemoryCaptures), read with memory_list_snapshots."""
        body = self._tool_json("manage_profiler", {"action": "memory_list_snapshots"})
        dirs = ((body or {}).get("data") or {}).get("searched_dirs") if isinstance(body, dict) else None
        return [os.path.realpath(item) for item in dirs or [] if isinstance(item, str) and item]

    def _absolute_output_refusal(self, key: str, value: str, root: str) -> str:
        """An absolute output path must stay under <project>/Builds or <project>/MemoryCaptures (or Logs for a
        profiler log). A snapshot that is read may also be in the folders upstream searches for snapshots."""
        real = os.path.realpath(value)
        real_root = os.path.realpath(root)
        for head in OUTPUT_HEADS.get(key, ()):
            base = os.path.join(real_root, head)
            if real == base or real.startswith(base + os.sep):
                return ""
        if key in ("snapshot_a", "snapshot_b", "search_path"):
            for base in self._snapshot_dirs():
                if real == base or real.startswith(base + os.sep):
                    return ""
        return _output_refusal(key, value)

    def _root_checks(self, step: dict) -> str:
        if not self._needs_root(step):
            return ""
        if step.get("bridge") in ("asset_find", "prefab_info", "read_text"):
            root, problem = self.disk_root()
        else:
            root, problem = self.project_root()
        if problem is not None:
            return _content_text(problem["content"])
        for key, value in step["paths"]:
            if _is_absolute_path(value):
                problem = self._absolute_output_refusal(key, value, root)
                if problem:
                    return problem
                continue
            if "/" not in value:
                continue
            refusal = resolved_refusal(step["tool"], value, root)
            if refusal:
                return refusal
        # A file named by folder and name is opened where upstream joins them: check that joined path too.
        for target in self._composed_targets(step):
            base = target.rsplit("/", 1)[-1]
            if SECRET_NAME.search(base):
                return explain("secret", base)
            refusal = resolved_refusal(step["tool"], target, root)
            if refusal:
                return refusal
        spec = step["spec"]
        if spec.get("upstream_tool") == "create_script" and step["show"].get("overwrite") is not True:
            path = step["send"].get("path")
            if isinstance(path, str):
                full = os.path.join(root, *path.split("/"))
                if os.path.lexists(full):
                    return explain("exists", path)
        return ""

    def _op_arguments_text(self, tool: str, op_name: str) -> str:
        spec = OPS.get((tool, op_name)) or {}
        props = ((TOOLS_BY_NAME.get(tool) or {}).get("inputSchema", {}).get("properties", {})
                 .get("arguments", {}).get("properties", {}))
        names = list(spec.get("params") or [])
        if spec.get("upstream_tool") == "create_script":
            names.append("overwrite")
        if spec.get("upstream_tool") == "manage_scene" and spec.get("action") == "save":
            names.append("overwrite_disk_changes")
        shown = []
        for name in names:
            entry = props.get(name) or {}
            kind = entry.get("type") or "/".join(sorted({str(item.get("type")) for item in entry.get("anyOf") or []
                                                         if isinstance(item, dict) and item.get("type")})) or "any"
            shown.append(f"{name} ({kind})")
        return ", ".join(shown) if shown else "no arguments"

    def _prepare_one(self, tool: str, op_name: str, arguments) -> tuple[dict | None, str]:
        if tool not in TOOLS_BY_NAME or tool in PLAN_TOOLS:
            domain = ", ".join(item for item in TOOL_ORDER if item not in PLAN_TOOLS)
            return None, Guide(explain("unknown-tool", str(tool)) + f" Tools: {domain}.")
        spec = OPS.get((tool, op_name))
        if spec is None:
            keys = sorted(key for (bundle, key) in OPS if bundle == tool)
            near = difflib.get_close_matches(str(op_name), keys, n=3, cutoff=0.4)
            other = sorted({bundle for (bundle, key) in OPS if key == op_name})
            hint = f" It is an op of {', '.join(other)}." if other else ""
            near_text = f" Closest: {', '.join(near)}." if near else ""
            return None, Guide(explain("unknown-op", f"{op_name} for {tool}") + hint + near_text
                               + f" Ops of {tool}: {', '.join(keys)}.")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return None, Guide(explain("args"))
        if arguments.get("safety_checks") is False:
            return None, explain("safety")
        if spec.get("bridge") == "component_values":
            return self._prepare_component_values(tool, op_name, spec, arguments)
        if spec.get("bridge") in ("describe", "asset_find", "prefab_info", "read_text", "create_asmdef"):
            return self._prepare_local(tool, op_name, spec, arguments)
        allowed = set(spec.get("params") or []) | set(BRIDGE_KEYS)
        if spec.get("action_param"):
            allowed.add("action")
        unknown = sorted(set(arguments) - allowed)
        if unknown:
            return None, Guide(explain("key", f"{tool} {op_name} does not take {', '.join(unknown)}; it takes "
                                              + self._op_arguments_text(tool, op_name)))
        for key, value in arguments.items():
            problem = _type_problem(spec, key, value)
            if problem:
                return None, Guide(explain("key", problem))
        if spec.get("action_param") and "action" in arguments and arguments["action"] != spec.get("action"):
            return None, Guide(explain("action") + f" The action is already {spec.get('action')}; leave action out.")
        menu = arguments.get("menu_path")
        if isinstance(menu, str) and menu.strip().lower() in BLOCKED_MENUS:
            return None, explain("menu", menu.strip())
        if spec.get("resource"):
            names = _placeholders(spec["resource"])
            if names:
                filled, problem = _fill_resource(spec["resource"], {k: arguments[k] for k in spec["params"]
                                                                    if k in arguments})
                if problem:
                    return None, problem
            else:
                if set(arguments) - set(BRIDGE_KEYS):
                    return None, Guide(explain("key", f"{op_name} takes no arguments"))
                filled = spec["resource"]
            return {
                "tool": tool, "op": op_name, "spec": spec, "send": {}, "show": {},
                "paths": [], "resource_uri": filled, "path_keys": frozenset(),
            }, ""
        arguments = dict(arguments)
        if spec.get("upstream_tool") == "manage_scene" and spec.get("action") in ("save", "create"):
            path = arguments.get("path")
            if isinstance(path, str) and path.lower().endswith(".unity") and not arguments.get("name"):
                stem = path.replace("\\", "/").rsplit("/", 1)
                arguments["name"] = stem[-1][:-len(".unity")]
                arguments["path"] = stem[0] if len(stem) == 2 else ""
                if not arguments["path"]:
                    del arguments["path"]
        keys = frozenset(spec.get("file_params") or []) | PATH_KEYS
        show = {}
        send = {}
        for key in spec.get("params") or []:
            if key == "action":
                continue
            if key in arguments:
                show[key] = arguments[key]
                send[key] = arguments[key]
        for key in BRIDGE_KEYS:
            if key in arguments:
                show[key] = arguments[key]
                if key in (spec.get("params") or []):
                    send[key] = arguments[key]
        script_path = send.get("path") if spec.get("upstream_tool") == "create_script" else None
        if isinstance(script_path, str) and not script_path.strip().lower().endswith(".cs"):
            return None, Guide(explain("key", f"create_script writes C# only: path must end with .cs (got "
                                              f"{script_path!r}). For an assembly definition use unity_script op "
                                              f"create_asmdef"))
        send, problem = rewrite_paths(send, "", keys, op_name)
        if problem:
            return None, problem
        show, problem = rewrite_paths(show, "", keys, op_name)
        if problem:
            return None, problem
        if spec.get("action_param"):
            send["action"] = spec.get("action")
        for key in ("code", "contents", "commands"):
            if isinstance(send.get(key), str):
                problem = code_secret_refusal(send[key])
                if problem:
                    return None, problem
        paths = list(_path_pairs(send, "", keys))
        if _user_deletes({"spec": spec, "send": send, "paths": paths}):
            for _key, value in paths:
                if value.strip("/").lower() in PROJECT_ROOT_FOLDERS:
                    return None, explain("root-delete", value)
        return {
            "tool": tool, "op": op_name, "spec": spec, "send": send, "show": show,
            "paths": paths, "resource_uri": None, "path_keys": keys,
        }, ""

    def _prepare_local(self, tool: str, op_name: str, spec: dict, arguments: dict):
        """Ops this plugin answers itself: describe, the two reads from disk, and create_asmdef."""
        allowed = set(spec["params"])
        unknown = sorted(set(arguments) - allowed)
        if unknown:
            return None, Guide(explain("key", f"{tool} {op_name} does not take {', '.join(unknown)}; it takes "
                                              + ", ".join(spec["params"])))
        kind = spec["bridge"]
        send = dict(arguments)
        paths: list[tuple[str, str]] = []
        if kind == "describe":
            if not isinstance(send.get("op"), str) or (tool, send["op"]) not in OPS:
                keys = sorted(key for (bundle, key) in OPS if bundle == tool)
                return None, Guide(explain("key", f"describe needs op, one of: {', '.join(keys)}"))
        elif kind == "asset_find":
            folder = send.get("folder") if send.get("folder") not in (None, "") else "Assets"
            if not isinstance(folder, str):
                return None, Guide(explain("key", "folder must be a string"))
            normalized, problem = normalize_path_text(folder)
            if problem:
                return None, problem
            normalized = normalized.strip("/") or "Assets"
            if normalized.split("/")[0].lower() not in ("assets", "packages"):
                return None, explain("outside", f"folder={folder}")
            problem = judge_relative("folder", normalized)
            if problem:
                return None, problem
            send["folder"] = normalized
            if send.get("type") is not None and send.get("type") not in ASSET_TYPES:
                return None, Guide(explain("key", f"type must be one of {', '.join(sorted(ASSET_TYPES))}"))
            limit = send.get("limit", 100)
            if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
                return None, Guide(explain("key", "limit must be an integer from 1 to 500"))
            send["limit"] = limit
            paths = [("folder", normalized)]
        elif kind == "prefab_info":
            value = send.get("path")
            if not isinstance(value, str) or not value.lower().endswith(".prefab"):
                return None, Guide(explain("key", "prefab_info needs path, a .prefab file under Assets/"))
            normalized, problem = normalize_path_text(value)
            if problem:
                return None, problem
            problem = judge_relative("path", normalized)
            if problem:
                return None, problem
            if normalized.split("/")[0].lower() not in ("assets", "packages"):
                return None, explain("outside", f"path={value}")
            send["path"] = normalized
            paths = [("path", normalized)]
        elif kind == "read_text":
            value = send.get("path")
            if not isinstance(value, str) or not value.lower().endswith(DISK_TEXT_EXT):
                return None, Guide(explain("key", "read_text needs path, a .unity, .prefab, .asset, or .cs file "
                                                  "under Assets/"))
            normalized, problem = normalize_path_text(value)
            if problem:
                return None, problem
            problem = judge_relative("path", normalized)
            if problem:
                return None, problem
            if normalized.split("/")[0].lower() not in ("assets", "packages"):
                return None, explain("outside", f"path={value}")
            send["path"] = normalized
            paths = [("path", normalized)]
        elif kind == "create_asmdef":
            value = send.get("path")
            if not isinstance(value, str) or not value.endswith(".asmdef"):
                return None, Guide(explain("key", "create_asmdef needs path, a new .asmdef file under Assets/, for "
                                                  "example Assets/Tests/EditMode/Game.Tests.EditMode.asmdef"))
            normalized, problem = normalize_path_text(value)
            if problem:
                return None, problem
            problem = judge_relative("path", normalized)
            if problem:
                return None, problem
            if not normalized.startswith("Assets/") or normalized.count("/") < 1:
                return None, explain("outside", f"path={value}")
            stem = normalized.rsplit("/", 1)[-1][:-len(".asmdef")]
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", stem):
                return None, Guide(explain("key", "the .asmdef file name is the assembly name: letters, digits, "
                                                  "dots, and underscores"))
            if send.get("kind") not in ASMDEF_KINDS:
                return None, Guide(explain("key", f"kind must be one of {', '.join(ASMDEF_KINDS)}"))
            refs = send.get("references") or []
            if not isinstance(refs, list) or not all(isinstance(item, str) and re.fullmatch(r"[A-Za-z_][\w.]*", item)
                                                     for item in refs):
                return None, Guide(explain("key", "references must be a list of assembly names"))
            send["path"] = normalized
            send["text"] = asmdef_text(stem, send["kind"], refs)
            paths = [("path", normalized)]
        show = {key: value for key, value in send.items() if key != "text"}
        if kind == "create_asmdef":
            show["file text"] = send["text"]
        return {
            "tool": tool, "op": op_name, "spec": spec, "send": send, "show": show, "paths": paths,
            "resource_uri": None, "bridge": kind, "path_keys": frozenset({"path", "folder"}),
        }, ""

    # ---- ops this plugin answers itself ----

    def _local(self, step: dict) -> dict:
        kind = step["bridge"]
        if kind == "describe":
            return {"content": [{"type": "text", "text": self._describe(step["tool"], step["send"]["op"])}],
                    "isError": False}
        root, failed = self.disk_root()
        if failed is not None:
            return failed
        if kind == "asset_find":
            return {"content": [{"type": "text", "text": self._asset_find(root, step["send"])}], "isError": False}
        if kind == "prefab_info":
            text, bad = self._prefab_info(root, step["send"]["path"])
            return {"content": [{"type": "text", "text": text}], "isError": bad}
        if kind == "read_text":
            text, bad = self._read_text(root, step["send"]["path"])
            return {"content": [{"type": "text", "text": text}], "isError": bad}
        relative = step["send"]["path"]
        full = os.path.join(root, *relative.split("/"))
        problem = resolved_refusal(step["tool"], relative, root)
        if problem:
            return error_result(problem)
        if os.path.lexists(full):
            return error_result(f"{NAME}: {relative} exists now; it was not there when the plan was made. Nothing "
                                f"was written.")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "x", encoding="utf-8") as handle:
            handle.write(step["send"]["text"])
        # Import it now, so a script a later step of the plan writes lands in this assembly and not first in
        # Assembly-CSharp (which would compile with errors for a moment).
        self._tool_json("refresh_unity", {"mode": "force", "scope": "all", "compile": "none", "wait_for_ready": True},
                        CALL_TIMEOUT)
        return {"content": [{"type": "text", "text": f"{NAME}: wrote {relative}."}], "isError": False}

    def _describe(self, tool: str, op_name: str) -> str:
        spec = OPS[(tool, op_name)]
        upstream = spec.get("upstream_tool")
        lines = [f"{tool} {op_name}: " + ("a read that runs now." if op_name in READ_ALLOW else
                                          "a change: the reply is a plan; apply_plan runs it after Hermes asks.")]
        desc = " ".join(((UPSTREAM_SCHEMAS.get(upstream) or {}).get("description") or "").split()) \
            if upstream and not spec.get("bridge") else ""
        if desc:
            lines.append(f"MCP for Unity {UPSTREAM_VERSION} {upstream}: {desc}")
        if spec.get("bridge"):
            lines.append("This plugin: " + "; ".join(spec.get("evidence") or []))
        lines.append("arguments:")
        users = [op_name]
        for param in spec.get("params") or []:
            entry = _full_param(tool, users, OPS, param)
            kind = entry.get("type") or "/".join(str(item.get("type")) for item in entry.get("anyOf") or []
                                                 if isinstance(item, dict) and item.get("type")) or "any"
            text = " ".join(str(entry.get("description") or "").split())
            enum = entry.get("enum")
            lines.append(f"  {param} ({kind}){': ' + text if text else ''}"
                         + (f" One of: {', '.join(map(str, enum))}." if isinstance(enum, list) else ""))
        if not spec.get("params"):
            lines.append("  (none)")
        rows = spec.get("effects") or []
        if rows:
            lines.append("what it does inside (MCP for Unity's own code, by tools/extract_side_effects.py):")
            for row in rows:
                gate = ", ".join(("" if g["truthy"] else "not ") + g["param"]
                                 + (f"={g['equals']}" if "equals" in g else "") for g in row.get("when_params") or [])
                lines.append(f"  {row['kind']}: {_site(row)}" + (f" [only with {gate}]" if gate else ""))
        elif op_name in READ_ALLOW:
            lines.append("what it does inside: no save, delete, write, compile, load, or send was found on its path.")
        return "\n".join(lines)

    @staticmethod
    def _meta_guids(root: str) -> dict[str, str]:
        """guid -> asset path, from the .meta files under Assets and the project's own Packages folders."""
        found: dict[str, str] = {}
        bases = [os.path.join(root, "Assets"), os.path.join(root, "Packages")]
        for base in bases:
            for folder, dirs, files in os.walk(base):
                dirs[:] = [item for item in dirs if not item.startswith(".")
                           and not os.path.islink(os.path.join(folder, item))]
                for file in files:
                    if not file.endswith(".meta"):
                        continue
                    try:
                        with open(os.path.join(folder, file), encoding="utf-8", errors="replace") as handle:
                            head = handle.read(400)
                    except OSError:
                        continue
                    hit = re.search(r"(?m)^guid:\s*([0-9a-f]{32})", head)
                    if hit:
                        found[hit.group(1)] = os.path.relpath(os.path.join(folder, file[:-5]), root).replace(os.sep, "/")
        return found

    def _asset_find(self, root: str, send: dict) -> str:
        folder = send["folder"]
        base = os.path.join(root, *folder.split("/"))
        problem = resolved_refusal("unity_asset", folder, root)
        if problem:
            return problem
        if not os.path.isdir(base):
            return f"{NAME}: {folder} is not a folder in the project."
        want = (send.get("name") or "").lower()
        exts = ASSET_TYPES.get(send.get("type") or "")
        rows: list[str] = []
        skipped = 0
        guids = None
        for current, dirs, files in os.walk(base):
            links = [item for item in dirs if os.path.islink(os.path.join(current, item))]
            skipped += len(links)
            dirs[:] = sorted(item for item in dirs if not item.startswith(".") and item not in links)
            for file in sorted(files):
                if file.endswith(".meta") or file.startswith(".") or SECRET_NAME.search(file):
                    continue
                full = os.path.join(current, file)
                if os.path.islink(full):
                    skipped += 1
                    continue
                if want and want not in file.lower():
                    continue
                if exts and not file.lower().endswith(exts):
                    continue
                relative = os.path.relpath(full, root).replace(os.sep, "/")
                kind = next((name for name, endings in ASSET_TYPES.items() if file.lower().endswith(endings)), "file")
                extra = ""
                if file.endswith(".asset"):
                    try:
                        with open(full, encoding="utf-8", errors="replace") as handle:
                            head = handle.read(4000)
                    except OSError:
                        head = ""
                    script = re.search(r"m_Script:\s*\{fileID:\s*11500000,\s*guid:\s*([0-9a-f]{32})", head)
                    if script:
                        guids = guids if guids is not None else self._meta_guids(root)
                        extra = f", script {guids.get(script.group(1), script.group(1))}"
                rows.append(f"- {relative} ({kind}, {os.path.getsize(full)} bytes{extra})")
                if len(rows) >= send["limit"]:
                    break
            if len(rows) >= send["limit"]:
                break
        head = (f"{NAME}: {len(rows)} file(s) under {folder}" + (f" named like {send.get('name')!r}" if want else "")
                + (f" of type {send.get('type')}" if exts else "")
                + ". Read from the disk; Unity was not asked, so no asset was loaded and no project code ran.")
        if skipped:
            head += f" {skipped} symbolic link(s) were not followed."
        if len(rows) >= send["limit"]:
            head += f" Cut at limit {send['limit']}."
        return "\n".join([head] + rows)

    def _both_sides(self, root: str, relative: str, facts: list[str], step: dict) -> str:
        """The disk value goes in the plan. The editor value is read later, inside apply_plan, because that read
        runs C# in the editor. A Guide when the disk side cannot be drawn."""
        data, problem = self._read_bytes(root, relative)
        if problem:
            return Guide(problem)
        text = data.decode("utf-8")
        if not text.startswith("%YAML"):
            return Guide(explain("expand", f"{relative} is not a text asset, so the plan cannot show the value on "
                                           f"disk. No plan."))
        fields = _mono_fields(text)
        if fields is None:
            return Guide(explain("expand", f"{relative} is not one plain MonoBehaviour document, so the plan cannot "
                                           f"show every value on disk, including nested lists. No plan."))
        disk_sha = hashlib.sha256(data).hexdigest()
        if not fields:
            facts.append(f"disk {relative} (no serialized fields)")
        for name, value in fields:
            shown = value if value != "" else "(empty)"
            facts.append(f"disk {relative} {name}={shown}")
        facts.append(f"disk sha256 {disk_sha}")
        facts.append(f"editor {relative}: not read while the plan is made, because reading it runs C# in the editor. "
                     f"apply_plan reads it and sends this replace only when that read is not dirty. A dirty value "
                     f"is named in the error and is not overwritten.")
        step["match_editor"] = relative
        return ""

    def _editor_asset_state(self, relative: str) -> tuple[str, str]:
        """Inside apply_plan: not-loaded, clean, dirty, or unreadable, plus the text the editor returned."""
        literal = cs_literal(relative)
        if not literal:
            return "unreadable", relative
        code = (
            "// both_sides " + relative + "\n"
            "var obj = UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(" + literal + ");\n"
            "if (obj == null) return \"not-loaded\";\n"
            "bool dirty = UnityEditor.EditorUtility.IsDirty(obj);\n"
            "return (dirty ? \"dirty\\n\" : \"clean\\n\") + UnityEditor.EditorJsonUtility.ToJson(obj);\n"
        )
        body = self._tool_json("execute_code", {"action": "execute", "code": code, "safety_checks": True,
                                                "compiler": "auto"}, 30)
        result = ((body or {}).get("data") or {}).get("result") if isinstance(body, dict) else None
        if not isinstance(result, str) or not result.strip():
            return "unreadable", ""
        text = result.strip()
        if text == "not-loaded":
            return "not-loaded", text
        if text.startswith("dirty"):
            return "dirty", text
        if text.startswith("clean"):
            return "clean", text
        return "unreadable", text

    def _read_bytes(self, root: str, relative: str) -> tuple[bytes | None, str]:
        problem = resolved_refusal("unity_asset", relative, root)
        if problem:
            return None, problem
        full = os.path.join(root, *relative.split("/"))
        try:
            data = Path(full).read_bytes()
        except OSError as exc:
            return None, f"{NAME}: could not read {relative} ({exc.strerror or type(exc).__name__})."
        if data.startswith(b"\xef\xbb\xbf") or data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
            return None, (f"{NAME}: refused {relative}: a byte-order mark makes the file unparsable here. "
                          f"{NOTHING_SENT}")
        if b"\x00" in data:
            return None, (f"{NAME}: refused {relative}: it is not a text asset. {NOTHING_SENT}")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return None, (f"{NAME}: refused {relative}: it is not UTF-8 text. {NOTHING_SENT}")
        return data, ""

    def _read_text(self, root: str, relative: str) -> tuple[str, bool]:
        data, problem = self._read_bytes(root, relative)
        if problem:
            return problem, True
        text = data.decode("utf-8")
        if relative.lower().endswith((".unity", ".prefab", ".asset")) and not text.startswith("%YAML"):
            return (f"{NAME}: refused {relative}: it is not a text Unity asset (it does not start with %YAML). "
                    f"{NOTHING_SENT}"), True
        shown = text if len(text) <= 8000 else text[:8000] + "\n…\n"
        return (f"{relative}: read from the file on disk (sha256 {hashlib.sha256(data).hexdigest()}). "
                f"Unity was not asked.\n{shown}"), False

    def _prefab_info(self, root: str, relative: str) -> tuple[str, bool]:
        data, problem = self._read_bytes(root, relative)
        if problem:
            return problem, True
        text = data.decode("utf-8")
        if not text.startswith("%YAML"):
            return (f"{NAME}: refused {relative}: it is not a text prefab, so it is not read here. "
                    f"{NOTHING_SENT}"), True
        docs = []
        for match in re.finditer(r"(?m)^--- !u!(\d+) &(-?\d+)( stripped)?\s*$", text):
            docs.append((int(match.group(1)), match.group(2), bool(match.group(3)), match.end()))
        if not docs or any(stripped for _cls, _fid, stripped, _end in docs) or any(cls == 1001 for cls, *_rest in docs):
            return (f"{NAME}: refused {relative}: the prefab is nested, stripped, or not a plain YAML document, "
                    f"so it is not interpreted. {NOTHING_SENT}"), True
        bodies = {}
        for index, (cls, fid, _stripped, start) in enumerate(docs):
            end = docs[index + 1][3] if index + 1 < len(docs) else len(text)
            body = text[start:end]
            cut = body.rfind("\n--- ")
            bodies[fid] = (cls, body if cut < 0 else body[:cut])
        guids = self._meta_guids(root)

        def field(body: str, name: str) -> str | None:
            hit = re.search(r"(?m)^  " + re.escape(name) + r":\s*(.*)$", body)
            return hit.group(1).strip() if hit else None

        objects = {fid: body for fid, (cls, body) in bodies.items() if cls == 1}
        comps: dict[str, list[str]] = {}
        values: dict[str, list[str]] = {}
        parent: dict[str, str] = {}
        transform_of: dict[str, str] = {}
        for fid, (cls, body) in bodies.items():
            if cls == 1:
                continue
            owner = re.search(r"m_GameObject:\s*\{fileID:\s*(-?\d+)", body)
            if not owner:
                continue
            go = owner.group(1)
            name = CLASS_IDS.get(cls, f"class {cls}")
            if cls == 114:
                guid = re.search(r"m_Script:\s*\{fileID:\s*\d+,\s*guid:\s*([0-9a-f]{32})", body)
                script = guids.get(guid.group(1), "script " + guid.group(1)) if guid else "missing script"
                name = os.path.splitext(script.rsplit("/", 1)[-1])[0] + f" ({script})"
                shown = []
                after = body.split("m_EditorClassIdentifier:", 1)[-1].split("\n", 1)[-1] if \
                    "m_EditorClassIdentifier:" in body else ""
                for line in after.splitlines():
                    if re.match(r"^  [A-Za-z_]\w*:", line):
                        shown.append(line.strip())
                values[name] = shown[:30]
            comps.setdefault(go, []).append(name)
            if cls in (4, 224):
                transform_of[go] = fid
                father = re.search(r"m_Father:\s*\{fileID:\s*(-?\d+)", body)
                if father and father.group(1) != "0":
                    parent[fid] = father.group(1)
        go_of_transform = {tf: go for go, tf in transform_of.items()}
        children: dict[str, list[str]] = {}
        roots = []
        for go in objects:
            tf = transform_of.get(go)
            up = parent.get(tf or "")
            if up and up in go_of_transform:
                children.setdefault(go_of_transform[up], []).append(go)
            else:
                roots.append(go)
        lines = [f"{relative}: read from the file on disk. Unity was not asked, so the prefab was not loaded and no "
                 f"project code ran."]

        def walk(go: str, depth: int) -> None:
            name = field(objects[go], "m_Name") or "?"
            active = field(objects[go], "m_IsActive")
            lines.append("  " * depth + f"- {name}" + (" (inactive)" if active == "0" else "")
                         + f" [{', '.join(comps.get(go, []))}]")
            for child in children.get(go, []):
                walk(child, depth + 1)

        for go in roots:
            walk(go, 0)
        nested = [(fid, body) for fid, (cls, body) in bodies.items() if cls == 1001]
        for _fid, body in nested:
            guid = re.search(r"m_SourcePrefab:\s*\{fileID:\s*\d+,\s*guid:\s*([0-9a-f]{32})", body)
            lines.append(f"nested prefab: {guids.get(guid.group(1), guid.group(1)) if guid else '?'}")
        for name, rows in values.items():
            if rows:
                lines.append(f"serialized fields of {name}:")
                lines.extend("  " + visible(row)[:200] for row in rows)
        return "\n".join(lines), False

    def _prepare_component_values(self, tool: str, op_name: str, spec: dict, arguments: dict):
        unknown = sorted(set(arguments) - {"path", "component"})
        if unknown:
            return None, Guide(explain("key", f"{op_name} does not take {', '.join(unknown)}; it takes path "
                                              f"(string, the hierarchy path) and component (string, optional)"))
        path = arguments.get("path")
        component = arguments.get("component")
        if not isinstance(path, str) or not path.strip():
            return None, Guide(explain("key", f"{op_name} needs path, the GameObject's hierarchy path from "
                                              f"manage_scene.get_hierarchy (for example \"Player\")"))
        if component is not None and (not isinstance(component, str)
                                      or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", component)):
            return None, Guide(explain("key", f"{op_name} component must be a C# type name such as Rigidbody"))
        literal = cs_literal(path)
        if literal is None:
            return None, explain("placeholder", "path")
        code = (SO_READ_BODY.replace("__PATH__", literal)
                .replace("__ONLY__", cs_literal(component) if component else "(string)null"))
        show = {"path": path}
        if component:
            show["component"] = component
        return {
            "tool": tool, "op": op_name, "spec": spec, "show": show, "paths": [], "resource_uri": None,
            "send": {"action": "execute", "code": code, "safety_checks": True, "compiler": "auto"},
            "bridge": "component_values", "path_keys": frozenset(),
        }, ""

    def _expand_batch(self, arguments) -> tuple[list[tuple[str, str, dict]] | None, str]:
        """batch_execute's commands as plan steps, each one checked like a step of its own."""
        if not isinstance(arguments, dict):
            return None, Guide(explain("args"))
        unknown = sorted(set(arguments) - {"commands", "parallel", "fail_fast", "max_parallelism"})
        if unknown:
            return None, Guide(explain("key", f"batch_execute does not take {', '.join(unknown)}; it takes "
                                              f"commands (array of {{tool, params}}), parallel, fail_fast, "
                                              f"max_parallelism"))
        commands = arguments.get("commands")
        if not isinstance(commands, list) or not commands:
            return None, Guide(explain("expand", "batch_execute needs commands: a list of {\"tool\": <MCP for Unity "
                                                 "tool>, \"params\": {...}}."))
        out: list[tuple[str, str, dict]] = []
        for number, command in enumerate(commands, 1):
            if not isinstance(command, dict) or not isinstance(command.get("tool"), str):
                return None, Guide(explain("expand", f"batch_execute item {number} needs tool and params."))
            upstream = command["tool"]
            params = command.get("params") or {}
            if not isinstance(params, dict):
                return None, Guide(explain("expand", f"batch_execute item {number}: params must be an object."))
            if upstream == "batch_execute":
                return None, explain("expand", f"batch_execute item {number} is another batch_execute. A batch "
                                               f"inside a batch cannot be shown step by step, so it is refused.")
            rows = [(bundle, key, spec) for (bundle, key), spec in OPS.items()
                    if spec.get("upstream_tool") == upstream and not spec.get("bridge")]
            if not rows:
                return None, explain("expand", f"batch_execute item {number} names {upstream}, which this plugin "
                                               f"cannot show step by step, so the batch is refused.")
            if any(spec.get("action_param") for _b, _k, spec in rows):
                action = params.get("action")
                match = [(bundle, key) for bundle, key, spec in rows if spec.get("action") == action]
                if not match:
                    actions = sorted(str(spec.get("action")) for _b, _k, spec in rows)
                    return None, Guide(explain("expand", f"batch_execute item {number}: {upstream} has no action "
                                                         f"{action!r}. Actions: {', '.join(actions)}."))
                bundle, key = match[0]
                args = {k: v for k, v in params.items() if k != "action"}
            else:
                bundle, key, _spec = rows[0]
                args = dict(params)
            out.append((bundle, key, args))
        return out, ""

    def _collect_steps(self, raw_steps) -> tuple[list[dict] | None, str]:
        if not isinstance(raw_steps, list) or not raw_steps:
            return None, Guide(explain("empty"))
        steps = []
        for raw in raw_steps:
            if not isinstance(raw, dict) or "tool" not in raw or "op" not in raw:
                return None, Guide(explain("shape"))
            if raw["tool"] in PLAN_TOOLS:
                return None, Guide(explain("nested"))
            if raw.get("op") == "batch_execute" and (raw["tool"], "batch_execute") in OPS:
                expanded, problem = self._expand_batch(raw.get("arguments") or {})
                if problem:
                    return None, problem
                for number, (bundle, key, args) in enumerate(expanded, 1):
                    step, problem = self._prepare_one(bundle, key, args)
                    if problem:
                        kind = Guide if isinstance(problem, Guide) else str
                        return None, kind(f"batch_execute item {number}: " + problem)
                    step["origin"] = f"batch_execute item {number} of {len(expanded)}, run as its own step"
                    steps.append(step)
                continue
            step, problem = self._prepare_one(raw["tool"], raw["op"], raw.get("arguments") or {})
            if problem:
                return None, problem
            steps.append(step)
        return steps, ""

    def _expand_replay(self, step: dict) -> str:
        """execute_code replay becomes execute with the exact code from the history, so the plan shows what runs."""
        index = step["send"].get("index")
        if not isinstance(index, int) or isinstance(index, bool):
            return Guide(explain("key", "execute_code.replay needs index (integer) from execute_code.get_history"))
        body = self._tool_json("execute_code", {"action": "get_history", "limit": 50})
        entries = ((body or {}).get("data") or {}).get("entries") if isinstance(body, dict) else None
        entry = next((row for row in entries or [] if isinstance(row, dict) and row.get("index") == index), None)
        if entry is None:
            return explain("expand", f"execute_code history has no entry {index} now (the history is cleared when "
                                     f"Unity reloads scripts). Send the code with execute_code.execute.")
        code = entry.get("codePreview")
        if not isinstance(code, str) or (code.endswith("...") and len(code) > 500):
            return explain("expand", f"execute_code history entry {index} keeps only the first 500 characters of its "
                                     f"code, so the plan cannot show all of it. Send the code with "
                                     f"execute_code.execute instead.")
        if entry.get("safetyChecksEnabled") is False:
            return explain("safety")
        problem = code_secret_refusal(code)
        if problem:
            return problem
        step["spec"] = OPS[("unity_code", "execute_code.execute")]
        step["op"] = "execute_code.execute"
        step["send"] = {"action": "execute", "code": code, "safety_checks": True,
                        "compiler": entry.get("compiler") or "auto"}
        step["show"] = {"code": code}
        step["origin"] = (f"execute_code.replay of history entry {index}, sent as execute with that entry's code so "
                          f"what runs is the code shown")
        return ""

    def _custom_tool_source(self, root: str, name: str) -> tuple[str | None, str | None]:
        """The project file that declares the custom tool, found the way upstream names it (CommandRegistry):
        the [McpForUnityTool("name")] or Name = "name" value, else the class name in snake_case."""
        found: list[tuple[str, str]] = []
        search = [os.path.join(root, "Assets")]
        packages = os.path.join(root, "Packages")
        if os.path.isdir(packages):
            search += [os.path.join(packages, item) for item in os.listdir(packages)
                       if os.path.isdir(os.path.join(packages, item)) and not os.path.islink(os.path.join(packages, item))]
        for base in search:
            for folder, dirs, files in os.walk(base):
                dirs[:] = [item for item in dirs if not item.startswith(".")]
                for file in files:
                    if not file.endswith(".cs"):
                        continue
                    full = os.path.join(folder, file)
                    try:
                        text = Path(full).read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    for match in re.finditer(r"\[\s*McpForUnityTool\s*(\(([^)]*)\))?\s*\]\s*"
                                             r"(?:\[[^\]]*\]\s*)*(?:public|internal|static|sealed|\s)*class\s+(\w+)",
                                             text):
                        args = match.group(2) or ""
                        named = re.search(r'^\s*"([^"]+)"', args) or re.search(r'Name\s*=\s*"([^"]+)"', args)
                        declared = named.group(1) if named else re.sub(r"(?<!^)(?=[A-Z])", "_",
                                                                         match.group(3)).lower()
                        if declared == name:
                            found.append((os.path.relpath(full, root).replace(os.sep, "/"), text))
        if len(found) != 1:
            return None, None
        return found[0]

    def _expand_custom(self, step: dict, root: str) -> str:
        name = step["send"].get("tool_name")
        if not isinstance(name, str) or not name:
            return Guide(explain("key", "execute_custom_tool needs tool_name"))
        relative, text = self._custom_tool_source(root, name)
        if relative is None:
            return explain("expand", f"no single project file declares the custom tool {name!r} "
                                     f"([McpForUnityTool] under Assets or an embedded package), so the plan cannot "
                                     f"show the code that would run. It is refused.")
        step["custom_file"] = relative
        step["show"] = dict(step["show"])
        step["show"]["source of " + relative] = text
        return ""

    # ---- what a plan touches, in words, and the state it was made against ----

    @staticmethod
    def _scene_target(step: dict, active_path: str) -> str | None:
        """The .unity file upstream ManageScene resolves for save, create, and load (ManageScene.cs)."""
        send = step["send"]
        name = send.get("name") if isinstance(send.get("name"), str) and send.get("name") else None
        path = send.get("path") if isinstance(send.get("path"), str) and send.get("path") else None
        action = step["spec"].get("action")
        if action == "load" and path and path.lower().endswith(".unity") and not name:
            return path if path.startswith(("Assets/", "Packages/")) else "Assets/" + path
        root_folder, rel = "Assets", (path or "").replace("\\", "/").strip("/")
        if rel.lower().startswith("assets/"):
            rel = rel[len("assets/"):].lstrip("/")
        elif rel.lower().startswith("packages/"):
            root_folder, rel = "Packages", rel[len("packages/"):].lstrip("/")
        elif rel.lower() in ("assets", "packages"):
            root_folder, rel = ("Assets" if rel.lower() == "assets" else "Packages"), ""
        if rel.lower().endswith(".unity"):
            rel = rel.rsplit("/", 1)[0] if "/" in rel else ""
        if not path and action == "create":
            rel = "Scenes"
        if not name:
            return active_path if action == "save" else None
        return "/".join(part for part in (root_folder, rel, name + ".unity") if part)

    @staticmethod
    def _composed_targets(step: dict) -> list[str]:
        """The file upstream opens or writes when the op names it by folder and name (COMPOSED)."""
        spec = step["spec"]
        rule = COMPOSED.get((spec.get("upstream_tool"), spec.get("action"))) or COMPOSED.get(
            (spec.get("upstream_tool"), None))
        if not rule:
            return []
        folder_key, name_key, ext = rule
        name = step["send"].get(name_key)
        if not isinstance(name, str) or not name or "/" in name or "\\" in name:
            return []
        folder = step["send"].get(folder_key)
        folder = folder.strip("/") if isinstance(folder, str) and folder.strip("/") else "Assets"
        if folder.lower().endswith(ext):
            return [folder]
        if not folder.lower().startswith(("assets", "packages")):
            folder = "Assets/" + folder
        return [f"{folder}/{name if name.lower().endswith(ext) else name + ext}"]

    def _disk_autorun(self, root: str) -> list[tuple[str, str]]:
        """Scripts already on disk that Unity runs by itself on a domain reload, or that could not be read."""
        found: list[tuple[str, str]] = []
        # Assets only. A package's own editor scripts (including MCP for Unity) are named when the plan installs
        # that package, not on every play or test.
        for base in (os.path.join(root, "Assets"),):
            if not os.path.isdir(base):
                continue
            for folder, dirs, files in os.walk(base):
                dirs[:] = [item for item in dirs if not item.startswith(".")
                           and not os.path.islink(os.path.join(folder, item))]
                for name in files:
                    if not name.endswith(".cs"):
                        continue
                    full = os.path.join(folder, name)
                    rel = os.path.relpath(full, root).replace(os.sep, "/")
                    try:
                        source = Path(full).read_text(encoding="utf-8")
                    except (OSError, UnicodeDecodeError):
                        found.append((rel, "unreadable attributes"))
                        continue
                    markers, unknown = editor_markers(source)
                    if unknown:
                        found.append((rel, "unreadable attributes"))
                    else:
                        found.extend((rel, marker) for marker in markers)
        return found[:8]

    def _changed_disk_autorun(self, root: str) -> list[tuple[str, str]]:
        """Scripts under Assets that changed after the last compile and that Unity runs on a domain reload.

        A compile reloads the editor and runs these. One that has not changed since the last compile is already
        what the plan's inside line says (editor scripts run after the reload) and is not named again here.
        """
        stale = {rel for rel in self._stale_scripts(root) if rel.startswith("Assets/") and rel.endswith(".cs")}
        if not stale:
            return []
        found: list[tuple[str, str]] = []
        for rel in sorted(stale):
            full = os.path.join(root, *rel.split("/"))
            try:
                source = Path(full).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                found.append((rel, "unreadable attributes"))
                continue
            markers, unknown = editor_markers(source)
            if unknown:
                found.append((rel, "unreadable attributes"))
            else:
                found.extend((rel, marker) for marker in markers)
        return found[:8]

    def _files_inside(self, root: str, relative: str) -> list[str]:
        """Files inside a folder the plan deletes, relative to the project. Links are not followed."""
        full = os.path.join(root, *relative.split("/"))
        if not os.path.isdir(full) or os.path.islink(full):
            return []
        found: list[str] = []
        for folder, dirs, files in os.walk(full):
            dirs[:] = [item for item in dirs if not item.startswith(".")
                       and not os.path.islink(os.path.join(folder, item))]
            for name in files:
                if name.startswith("."):
                    continue
                path = os.path.join(folder, name)
                if os.path.islink(path):
                    continue
                found.append(os.path.relpath(path, root).replace(os.sep, "/"))
        return sorted(found)

    def _inside_phrase(self, root: str, relative: str) -> str:
        """Names every file inside a deleted folder. A long list is a count and the first names, so the second
        question stays within SECOND_CAP (1,650 characters; the chat cards allow about 1,700)."""
        names = self._files_inside(root, relative)
        if not names:
            return ""
        full = ", ".join(names)
        if len(full) <= 800:
            return ", including " + full
        return f", {len(names)} files inside, first: " + ", ".join(names[:5])

    @staticmethod
    def _folder_has_scripts(full: str) -> bool:
        if not os.path.isdir(full) or os.path.islink(full):
            return False
        for _folder, dirs, files in os.walk(full):
            dirs[:] = [item for item in dirs if not item.startswith(".")]
            if any(file.lower().endswith(_SCRIPT_EXT) for file in files):
                return True
        return False

    def _written_text(self, step: dict) -> str:
        """The C# a step writes into a script, for Unity's own run-by-itself rules (UNITY_RULES)."""
        send = step["send"]
        parts = []
        for key in ("contents", "code_text"):
            if isinstance(send.get(key), str):
                parts.append(send[key])
        for edit in send.get("edits") or []:
            if isinstance(edit, dict):
                for key in ("newText", "text", "replacement", "new_text", "contents"):
                    if isinstance(edit.get(key), str):
                        parts.append(edit[key])
        return "\n".join(parts)

    def _step_facts(self, step: dict, root: str, sim: dict, index: int) -> tuple[list[str], list[str], str]:
        """Lines for the plan, files whose state the plan depends on, and a refusal (empty when none).

        What the step does comes from the side effect table (step_effects), filtered by its arguments. sim carries
        the effect of the earlier steps of the same plan: the open scenes (path, unsaved changes, and whether those
        changes were there before the plan), play mode, files earlier steps create or delete, and whether an earlier
        step compiles scripts.
        """
        facts: list[str] = []
        risks: set[str] = set()
        risk_lines: list[tuple[str, str]] = []
        checks: list[str] = []
        expect: list[tuple[str, str]] = []
        files: list[str] = []
        spec = step["spec"]
        tool = spec.get("upstream_tool")
        action = spec.get("action")
        effects = step_effects(step)
        kinds = {row["kind"] for row in effects}
        scenes = sim["scenes"]
        active = next((scene for scene in scenes if scene.get("isActive")), scenes[0] if scenes else {})
        active_path = active.get("path") or ""
        made = sim["made"]

        def there(relative: str) -> bool:
            if relative in sim["gone"]:
                return False
            return relative in made or os.path.lexists(os.path.join(root, *relative.split("/")))

        def made_note(relative: str) -> str:
            return f" (step {made[relative]} of this plan makes it)" if relative in made else ""

        def risk(kind: str, text: str) -> None:
            risks.add(kind)
            risk_lines.append((kind, text))

        def finish() -> tuple[list[str], list[str], str]:
            step["facts"], step["risks"] = facts, sorted(risks, key=list(RISK_WORDS).index)
            step["risk_lines"], step["checks"], step["expect"] = risk_lines, checks, expect
            return facts, files, ""

        targets = self._composed_targets(step)
        step["targets"] = targets
        for target in targets:
            normalized, problem = normalize_path_text(target)
            if problem:
                return facts, files, problem
            problem = judge_relative("path", normalized) or resolved_refusal(step["tool"], normalized, root)
            if problem:
                return facts, files, problem
        paths = [value for _key, value in step["paths"] if "/" in value and not _is_absolute_path(value)]
        compiles = step.get("bridge") == "create_asmdef"
        if not compiles and any(row["kind"] == "import_compile" and "RequestScriptCompilation" in row["api"]
                                for row in effects):
            compiles = True
        if not compiles and any(row["kind"] == "send" and row["api"].startswith("Client.") for row in effects):
            compiles = True
        if not compiles and kinds & {"write_file", "delete_file", "import_compile"}:
            # a script file itself, or a folder of scripts the step deletes or moves (writing an asset into a
            # folder that also holds scripts does not change them)
            moves = bool(_user_deletes(step)) or any(row["api"].endswith(("MoveAsset", "RenameAsset", "File.Move"))
                                                     for row in effects)
            for value in paths + targets:
                if value.lower().endswith(_SCRIPT_EXT) or (
                        moves and self._folder_has_scripts(os.path.join(root, *value.split("/")))):
                    compiles = True
        step["compiles"] = compiles
        if "project_settings" in kinds:
            files.extend(STATE_FILES["project_settings"])
            facts.append("may change: files under ProjectSettings/ (the inside line says when)")
        if any(row["kind"] == "send" and row["api"].startswith("Client.") for row in effects):
            files.extend(STATE_FILES["packages"])
            facts.append("changes: Packages/manifest.json and Packages/packages-lock.json (Unity resolves the "
                         "packages again). Both stay; the plugin does not put them back")
            step.setdefault("keep_paths", []).extend(STATE_FILES["packages"])

        if tool == "manage_scene" and action in ("save", "create", "load", "close_scene"):
            target = self._scene_target(step, active_path)
            if action == "save":
                if not target:
                    return facts, files, explain("no-file")
                files.append(target)
                full = os.path.join(root, *target.split("/"))
                if there(target):
                    if target == active_path:
                        facts.append(f"file: writes the open scene over {target}{made_note(target)}")
                        first = self.scene_sha.get(target)
                        if (target not in made and first is not None and first != file_sha(full)
                                and step["show"].get("overwrite_disk_changes") is not True):
                            return facts, files, explain("disk", target)
                    else:
                        facts.append(f"file: replaces the existing file {target} with the open scene; the old "
                                     f"{target} is gone")
                        risk("deletes", f"replaces {target} with the open scene")
                else:
                    facts.append(f"file: creates {target} from the open scene; the open scene then uses that file")
                    made.setdefault(target, index + 1)
                expect.append((target, "saved"))
                checks.append(f"{target} is on disk and the open scene has no unsaved changes")
                if active:
                    active["path"], active["isDirty"], active["user_dirty"] = target, False, False
            elif action == "create":
                if target:
                    files.append(target)
                    facts.append(f"file: creates {target}" + (" (Unity refuses: that file exists)" if there(target)
                                                              else ""))
                for scene in scenes:
                    label = scene.get("path") or "the untitled scene"
                    if scene.get("isDirty"):
                        facts.append(f"then: closes {label}, and its unsaved changes are lost")
                        risk("unsaved", f"closes {label} with unsaved changes")
                    else:
                        facts.append(f"then: closes {label}, which has no unsaved changes")
                if target and not there(target):
                    made.setdefault(target, index + 1)
                    expect.append((target, "created"))
                    checks.append(f"{target} is on disk")
                    sim["scenes"] = [{"path": target, "isDirty": False, "isActive": True}]
            elif action == "load":
                if target:
                    files.append(target)
                    facts.append(f"file: opens {target}{made_note(target) if target else ''}; Unity loads its "
                                 f"objects, so their OnValidate and [ExecuteAlways] code runs")
                if step["send"].get("additive") is not True:
                    dirty = [scene for scene in scenes if scene.get("isDirty")]
                    if dirty:
                        facts.append("then: Unity refuses this load, because "
                                     + ", ".join(scene.get("path") or "the untitled scene" for scene in dirty)
                                     + " has unsaved changes. Save first in the same plan.")
                    else:
                        facts.append("then: the open scenes are closed and replaced")
                        if target:
                            sim["scenes"] = [{"path": target, "isDirty": False, "isActive": True}]
                elif target:
                    sim["scenes"].append({"path": target, "isDirty": False, "isActive": False})
            elif action == "close_scene":
                named = step["send"].get("path") or step["send"].get("name")
                closing = [scene for scene in scenes if named and named in ((scene.get("path") or ""),
                                                                              (scene.get("name") or ""))] or scenes[:1]
                for scene in closing:
                    if scene.get("isDirty"):
                        facts.append(f"then: closes {scene.get('path') or 'the untitled scene'}, and its unsaved "
                                     f"changes are lost")
                        risk("unsaved", f"closes {scene.get('path') or 'the untitled scene'} with unsaved changes")
                    else:
                        facts.append(f"then: closes {scene.get('path') or 'the untitled scene'}")
                sim["scenes"] = [scene for scene in scenes if scene not in closing]
            return finish()

        if step.get("bridge") == "create_asmdef":
            relative = step["send"]["path"]
            files.append(relative)
            if there(relative):
                return facts, files, Guide(explain("expand", f"{relative} already exists. This op only creates a new "
                                                             f".asmdef; edit an existing one in Unity."))
            facts.append(f"file: creates {relative} (the plugin writes this JSON itself; Unity adds the .meta)")
            made.setdefault(relative, index + 1)
            expect.append((relative, "created"))
            checks.append(f"{relative} is on disk")
            editor_asm, why = _asmdef_editor(relative, step["send"].get("text") or "")
            if editor_asm:
                facts.append(f"runs: {relative} is an editor assembly ({why})")
                risk("code", f"writes {relative}, an editor assembly ({why})")
            if step["send"]["kind"] == "game":
                facts.append("then: the scripts in this folder and below move from Assembly-CSharp into this assembly")
        elif step.get("convert") == "overwrite":
            relative = step["send"]["uri"]
            old = step.get("replaced_text")
            if not isinstance(old, str):
                return facts, files, Guide(explain("expand", f"{relative} could not be shown, so overwrite has no "
                                                             f"plan."))
            facts.append(f"file: replaces the whole text of {relative} (sent as apply_text_edits over lines 1 to "
                         f"{step['convert_lines']}, only while the file's sha256 is still {step['convert_sha'][:16]}…)")
            facts.append("replaces this text:")
            facts.append(old)
            files.append(relative)
            risk("deletes", f"replaces the whole text of {relative}")
            expect.append((relative, "changed"))
        elif tool in ("apply_text_edits", "script_apply_edits"):
            relative = step["send"].get("uri") or (targets[0] if targets else None)
            if isinstance(relative, str) and "/" in relative:
                files.append(relative)
                current = file_sha(os.path.join(root, *relative.split("/")))
                given = step["send"].get("precondition_sha256")
                if current is None and relative not in made:
                    facts.append(f"file: names {relative}, which is not there now")
                elif given and current and given != current:
                    return facts, files, Guide(explain("sha", relative) + f" Its sha256 now is {current}.")
                else:
                    if not given and current:
                        step["send"]["precondition_sha256"] = current
                        step["show"]["precondition_sha256"] = current
                    full = os.path.join(root, *relative.split("/"))
                    try:
                        old_file = Path(full).read_text(encoding="utf-8") if current else ""
                    except (OSError, UnicodeDecodeError):
                        return facts, files, Guide(explain("expand", f"{relative} could not be read, so the plan "
                                                                     f"cannot name the text an edit removes. No plan."))
                    edits = step["send"].get("edits") or []
                    if current and not edits and tool == "script_apply_edits":
                        return facts, files, Guide(explain("expand", f"{relative} would be changed by "
                                                                     f"script_apply_edits without a line span, so the "
                                                                     f"plan cannot name the text it removes. No plan."))
                    for edit in edits:
                        if not isinstance(edit, dict):
                            return facts, files, Guide(explain("expand", f"an edit of {relative} is not an object, "
                                                                         f"so the plan cannot name the text it "
                                                                         f"removes. No plan."))
                        if "startLine" not in edit and tool == "script_apply_edits":
                            return facts, files, Guide(explain("expand", f"{relative} would be changed without a line "
                                                                         f"span, so the plan cannot name the text it "
                                                                         f"removes. No plan."))
                        if "startLine" not in edit:
                            continue
                        old = _span_text(old_file, edit)
                        if old is None:
                            return facts, files, Guide(explain("expand", f"an edit span in {relative} is not in the "
                                                                         f"file, so the plan cannot name the text it "
                                                                         f"removes. No plan."))
                        new_text = edit.get("newText")
                        if new_text is None:
                            new_text = edit.get("new_text", "")
                        facts.append(f"replaces this text in {relative} at line {edit.get('startLine')} column "
                                     f"{edit.get('startCol')} (the end column is exclusive):")
                        facts.append(old if old != "" else "(nothing; the span is empty)")
                        if old != "" and old != new_text:
                            risk("deletes", f"replaces text in {relative}; the text removed is: {old}")
                    facts.append(f"file: changes {relative}{made_note(relative)}; precondition_sha256 is the file as "
                                 f"it is now" if current else f"file: changes {relative}{made_note(relative)}")
                    expect.append((relative, "changed"))
        else:
            deletes = bool(_user_deletes(step)) or (op_deletes(step) and bool(step["paths"]))
            trash = any("Trash" in row["api"] for row in _user_deletes(step))
            for key, value in step["paths"]:
                if _is_absolute_path(value):
                    facts.append(f"file: {'reads' if key in ('snapshot_a', 'snapshot_b', 'search_path') else 'writes'} "
                                 f"{value}")
                    continue
                if "/" not in value:
                    facts.append(f"file: uses the name {value}")
                    continue
                if key in OUTPUT_HEADS and step["op"] in OUTPUT_OPS:
                    facts.append(f"file: {'reads' if key in ('snapshot_a', 'snapshot_b', 'search_path') else 'writes'} "
                                 f"{root.rstrip('/')}/{value}")
                    continue
                files.append(value)
                if targets and value not in targets:
                    facts.append(f"file: uses the folder {value}" if there(value)
                                 else f"file: the folder {value} is not there now; upstream creates it")
                    continue
                if deletes and not targets:
                    if there(value):
                        inside = self._inside_phrase(root, value)
                        if trash:
                            gone = f"moves {value} and its .meta to the system Trash{inside}"
                        else:
                            gone = f"deletes {value} and its .meta{inside}; this does not use the Trash"
                        facts.append(f"file: {gone}{made_note(value)}")
                        risk("deletes", f"deletes {value}{inside}" + (" (to the Trash)" if trash else ""))
                        expect.append((value, "gone"))
                    else:
                        facts.append(f"file: names {value}, which is not there now")
                    sim["gone"].add(value)
                    made.pop(value, None)
                elif op_writes_files(step) and not targets:
                    full = os.path.join(root, *value.split("/"))
                    if there(value) and (os.path.isfile(full) or value in made):
                        facts.append(f"file: replaces the existing file {value}{made_note(value)}")
                        risk("deletes", f"replaces {value}")
                        expect.append((value, "changed"))
                    elif there(value):
                        facts.append(f"file: writes into {value}")
                    else:
                        facts.append(f"file: creates {value}")
                        made.setdefault(value, index + 1)
                        sim["gone"].discard(value)
                        expect.append((value, "created"))
                elif "load_asset" in kinds or "instantiate" in kinds:
                    facts.append(f"file: loads {value}{made_note(value)}; Unity runs its deserialization and "
                                 f"OnEnable/OnValidate code, and this step does not write it"
                                 if there(value) else f"file: names {value}, which is not there now")
                else:
                    facts.append(f"file: uses {value}{made_note(value)}" if there(value)
                                 else f"file: names {value}, which is not there now")
            for target in targets:
                files.append(target)
                exists = there(target)
                deleting = [row for row in _user_deletes(step)]
                if deleting and exists and op_writes_files(step):
                    facts.append(f"file: replaces {target}{made_note(target)}: upstream removes or overwrites the "
                                 f"existing asset ({_site(deleting[0])}) and writes a new one; its current values "
                                 f"are lost")
                    if target.lower().endswith(".asset"):
                        problem = self._both_sides(root, target, facts, step)
                        if problem:
                            return facts, files, problem
                    lost = [fact for fact in facts if fact.startswith(f"disk {target} ")]
                    shown = "; ".join(lost) if lost else f"the values in {target}"
                    risk("deletes", f"replaces {target}; the values this removes are: {shown}")
                    expect.append((target, "changed"))
                elif deleting and exists:
                    facts.append(f"file: deletes {target}{made_note(target)}")
                    risk("deletes", f"deletes {target}")
                    expect.append((target, "gone"))
                    sim["gone"].add(target)
                elif op_writes_files(step) and exists and any(row["api"].endswith("CreateAsset") for row in effects):
                    facts.append(f"file: {target} exists and this step does not replace it, so upstream writes the "
                                 f"asset under the next free name (AssetDatabase.GenerateUniqueAssetPath)")
                elif op_writes_files(step) and exists:
                    facts.append(f"file: changes {target}{made_note(target)}")
                    expect.append((target, "changed"))
                elif op_writes_files(step):
                    facts.append(f"file: creates {target}")
                    made.setdefault(target, index + 1)
                    expect.append((target, "created"))
                else:
                    facts.append(f"file: uses {target}{made_note(target)}" if exists
                                 else f"file: names {target}, which is not there now")
            if spec.get("upstream_tool") in ("create_script",) or (tool, action) == ("manage_script", "create"):
                for value in [v for v in paths + targets if v.lower().endswith(".cs")]:
                    made.setdefault(value, index + 1)
                    if (value, "created") not in expect and not there(value):
                        expect.append((value, "created"))
        confirm = UPSTREAM_CONFIRMS.get((tool, action or ""))
        if confirm:
            named = (step["send"].get("target") or step["send"].get("path") or step["send"].get("uri")
                     or step["send"].get("name") or step["send"].get("component_type") or "?")
            facts.append(f"asks: upstream's own command line asks \"{confirm} '{named}'?\" before this delete; "
                         f"approving this plan is that answer")
        if step["op"] in ("manage_camera.screenshot", "manage_camera.screenshot_multiview") \
                and not step["send"].get("output_folder"):
            facts.append("file: writes a new PNG under Assets/Screenshots unless MCP for Unity has another folder set")
        if "build_player" in kinds and not step["send"].get("output_path"):
            facts.append(f"file: writes the player under {root.rstrip('/')}/Builds/<target>/ (upstream's default)")
        if step["op"] == "manage_profiler.memory_take_snapshot" and not step["send"].get("snapshot_path"):
            facts.append("file: writes the snapshot under Unity's temporary cache folder "
                         "(Application.temporaryCachePath/MemoryCaptures; on macOS under /var/folders/…/T/<company>/"
                         "<product>), outside the project (upstream's default)")
            risk("outside", "writes a memory snapshot outside the project")
        # destroying the caller's objects (a GameObject or component delete), not upstream's own scratch objects
        if any(row["kind"] == "destroy_object" and not row.get("scratch") for row in effects) and not step["paths"]:
            named = step["send"].get("target") or step["send"].get("component_type") or "the target"
            risk("deletes", f"destroys {named} in the open scene")
        # hidden saves: an op that saves scenes it was not asked to save (run_tests, build)
        if "save_scene" in kinds:
            site = next(row for row in effects if row["kind"] == "save_scene")
            dirty = [scene for scene in sim["scenes"] if scene.get("isDirty")]
            for scene in dirty:
                if scene.get("path"):
                    disk = file_sha(os.path.join(root, *scene["path"].split("/")))
                    if not disk:
                        return facts, files, Guide(explain("expand", f"{scene['path']} would be saved over, but its "
                                                                     f"bytes on disk could not be read, so the plan "
                                                                     f"cannot name what is replaced."))
                    facts.append(f"then: upstream saves {scene['path']} over its file first, because it has unsaved "
                                 f"changes ({_site(site)}). disk sha256 {disk}; the editor copy replaces that file")
                    if scene.get("user_dirty"):
                        risk("saves", f"saves the unsaved changes in {scene['path']} (made before this plan) over "
                                      f"its file")
                    files.append(scene["path"])
                    expect.append((scene["path"], "saved"))
                    scene["isDirty"], scene["user_dirty"] = False, False
                else:
                    if "run_tests" in kinds:
                        return facts, files, Guide(explain(
                            "expand", "an untitled scene has unsaved changes. Unity's test runner opens a save "
                                      "dialog (SaveModifiedSceneTask) and a GUI editor stops on that dialog. Save "
                                      "the scene to a file, or close it, in this plan first. No plan."))
                    facts.append("then: the untitled scene has unsaved changes and no file, so this step cannot "
                                 "name what would be saved")
            if not dirty:
                facts.append("then: no open scene has unsaved changes now, so this saves nothing")
        if "save_assets" in kinds:
            facts.append("then: upstream writes every changed asset to disk (AssetDatabase.SaveAssets)")
        # code that runs with the editor's full access, beyond the game's own scripts
        if "compile_run" in kinds or step.get("bridge") == "component_values":
            code = str(step["send"].get("code") or "")
            facts.append("runs: the code below, as the editor process, with no sandbox")
            facts.append(code)
            risk("code", "runs this C#: " + re.sub(r"[ \t\n]+", " ", visible(code)).strip())
        if "menu_item" in kinds:
            risk("code", f"runs the menu command {step['send'].get('menu_path') or step['send'].get('menuPath')}")
        if step.get("custom_file"):
            facts.append(f"runs: the custom tool class in {step['custom_file']} (shown below), as the editor process")
            files.append(step["custom_file"])
            risk("code", f"runs the custom tool class in {step['custom_file']}")
        if any(row["kind"] == "send" and row["api"] in ("Client.Add", "Client.Embed") for row in effects):
            name = step["send"].get("package") or step["send"].get("name") or "?"
            risk("code", f"installs the package {name}; its editor code runs after the import")
        written = self._written_text(step)
        script_paths = [v for v in paths + targets if v.lower().endswith(".cs")]
        if written and script_paths:
            markers, unknown = editor_markers(written)
            if unknown:
                facts.append(f"runs: {script_paths[0]} could not be read the way Unity reads attributes, so it is "
                             f"treated as editor code")
                risk("code", f"writes {script_paths[0]}, which could not be read the way Unity reads attributes, so "
                             f"it is treated as editor code that runs after the compile")
            elif markers:
                facts.append(f"runs: {script_paths[0]} has {markers[0]}: {UNITY_RULES['editor_autorun']['words']}")
                risk("code", f"writes {script_paths[0]} with {markers[0]}, which Unity runs by itself after the "
                             f"compile")
            editor_script, why = _script_editor_reason(script_paths[0], root)
            if editor_script:
                facts.append(f"note: {script_paths[0]} is an editor script ({why})")
                if not markers and not unknown:
                    risk("code", f"writes {script_paths[0]}, an editor script ({why})")
        if ("enter_play" in kinds or "run_tests" in kinds) and root:
            for rel_script, marker in self._disk_autorun(root):
                facts.append(f"runs: {rel_script} is already on disk with {marker}, and a domain reload runs it")
                risk("code", f"{rel_script} has {marker}, which Unity runs by itself when the domain reloads")
        if "send" in kinds or tool in ("blender_bridge",):
            row = next((row for row in effects if row["kind"] == "send"), None)
            where = "docs.unity3d.com" if tool == "unity_docs" else (row["api"] if row else "an outside service")
            risk("outside", f"sends its values off this machine ({where})")
        # play mode, tests, builds: what the plugin reads back afterwards
        if "enter_play" in kinds:
            checks.append("Unity is in play mode and the frame count advances, else this returns an error; error "
                          "lines that appear in the console after this step are returned")
        if "exit_play" in kinds:
            checks.append("Unity left play mode (editor state)")
        if "run_tests" in kinds:
            checks.append("the test job's rows, its totals, and that the run started and finished; a failure, a "
                          "missing row, or 0 tests is an error. The job's succeeded word is not the result")
            if str(step["send"].get("mode") or "") == "PlayMode":
                facts.append("then: PlayMode changes ProjectSettings/EditorSettings.asset (enter play mode options, "
                             "so the domain does not reload and drop the bridge). That file stays; it is an effect "
                             "of this step")
                step.setdefault("keep_paths", []).append("ProjectSettings/EditorSettings.asset")
        if "build_player" in kinds:
            checks.append("the output path is on disk and its bytes changed; upstream's result word is quoted and "
                          "is not the result")
        if ("enter_play" in kinds or "run_tests" in kinds) and not sim.get("compiles_before") \
                and not self.compile_errors_now and self.stale_scripts:
            shown = ", ".join(self.stale_scripts[:5]) + (" and more" if len(self.stale_scripts) > 5 else "")
            facts.append(f"before: the plugin asks Unity to compile first, because {shown} changed on disk after the "
                         f"last compile (the editor has not noticed it); compile errors stop the plan here and play "
                         f"or the tests are not sent")
            step["compile_first"] = True
            files.extend(self.stale_scripts)
            sim["compiles_before"] = True
        if ("enter_play" in kinds or "run_tests" in kinds) and not sim.get("compiles_before") \
                and self.compile_errors_now:
            return facts, files, Guide(explain("expand", "the last compile has errors, so Unity cannot enter play "
                                                         "mode or run tests until they are fixed:\n"
                                               + "\n".join(self.compile_errors_now[:10])
                                               + "\nFix the scripts in this plan (the plugin then compiles before "
                                                 "the play or test step) or in a plan before it."))
        if tool == "manage_gameobject" and action == "modify" and sim["playing"]:
            facts.append("then: Unity refuses this while in play mode (\"This cannot be used during play mode.\"). "
                         "Stop play mode first in this plan.")
        if "exit_play" in kinds and sim.get("play_changes"):
            facts.append("then: the changes earlier steps of this plan made during play are dropped")
            risk("unsaved", "leaves play mode; changes earlier steps made during play are dropped")
        # effects on the simulated editor
        if compiles and root and not sim.get("named_changed_autorun"):
            sim["named_changed_autorun"] = True
            for rel_script, marker in self._changed_disk_autorun(root):
                facts.append(f"runs: {rel_script} changed on disk after the last compile and has {marker}; "
                             f"this compile reloads the editor and runs it")
                risk("code", f"{rel_script} has {marker}, which Unity runs by itself when this compile reloads "
                             f"the editor")
        if compiles:
            sim["compiles_before"] = True
            facts.append("then: a compile may rewrite *.csproj, *.sln, and *.slnx at the project root; those files are an "
                         "effect of this step and are not put back")
        if "enter_play" in kinds:
            sim["playing"] = True
        elif "exit_play" in kinds:
            sim["playing"], sim["play_changes"] = False, False
        elif op_edits_scene(step):
            if sim["playing"]:
                sim["play_changes"] = True
            elif active:
                active["isDirty"] = True
        return finish()

    _USING_RE = re.compile(r"(?m)^\s*using\s+(?:static\s+)?(?:[A-Za-z_]\w*\s*=\s*)?[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*;")

    def _convert_overwrite(self, step: dict, root: str) -> str:
        """create_script with overwrite true on an existing file. Upstream's create refuses an existing file, so the
        replacement goes as apply_text_edits, guarded by the file's current sha256, in two spans that together
        cover the whole file. Upstream turns a single span near a method header into replace_method (a whole-file
        span came back as "No-op: contents unchanged" on 10.3.0), and two spans skip that. Upstream refuses any edit
        above the first using line, so a file with text before it is refused here."""
        relative = step["send"].get("path")
        full = os.path.join(root, *relative.split("/"))
        try:
            old = Path(full).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return Guide(explain("expand", f"{relative} could not be read as UTF-8 text, so it is not replaced."))
        first = self._USING_RE.search(old)
        if old.startswith("\ufeff") or (first is not None and first.start() > 0):
            return Guide(explain("expand", f"{relative} has text above its first using line, and upstream refuses edits "
                                           f"there, so overwrite cannot replace the whole file. Edit it below that line "
                                           f"with apply_text_edits instead."))
        rows = old.split("\n")
        sha = hashlib.sha256(old.encode("utf-8")).hexdigest()
        new_text = step["send"].get("contents", "")
        last = {"startLine": 1, "startCol": 1, "endLine": len(rows), "endCol": len(rows[-1]) + 1}
        if len(rows) >= 2:
            edits = [{"startLine": 1, "startCol": 1, "endLine": 2, "endCol": 1, "newText": new_text},
                     {"startLine": 2, "startCol": 1, "endLine": len(rows), "endCol": len(rows[-1]) + 1, "newText": ""}]
        elif len(rows[0]) >= 2:
            edits = [{"startLine": 1, "startCol": 1, "endLine": 1, "endCol": 2, "newText": new_text},
                     {"startLine": 1, "startCol": 2, "endLine": 1, "endCol": len(rows[0]) + 1, "newText": ""}]
        else:
            edits = [dict(last, newText=new_text)]
        step["spec"] = OPS[("unity_script", "apply_text_edits")]
        step["send"] = {"uri": relative, "precondition_sha256": sha, "edits": edits}
        step["convert"], step["convert_lines"], step["convert_sha"] = "overwrite", len(rows), sha
        step["replaced_text"] = old
        return ""

    def _context(self, steps: list[dict], mid=None) -> tuple[dict | None, str]:
        """Measure the editor once for a plan: which editor, its project, play mode, scenes, and file facts."""
        reason = self.ensure_child()
        if reason:
            return None, reason
        instance, problem = self._target_instance()
        if problem:
            return None, problem
        if instance and not self._pin(instance):
            if getattr(self, "_last_block", ""):
                return None, self._last_block
            return None, explain("gone", instance).replace(" then call apply_plan again; the plan is kept.",
                                                            " then plan again.")
        if not self._wait_settled():
            return None, explain("busy", str(int(READY_WAIT)))
        root, failed = self.project_root(fresh=True)
        if failed is not None:
            return None, _content_text(failed["content"])
        for step in steps:
            tool = step["spec"].get("upstream_tool")
            if tool and self.upstream_tools is not None and tool not in self.upstream_tools:
                if tool == "execute_custom_tool":
                    return None, Guide(explain("expand", "execute_custom_tool is not in the running MCP for Unity's "
                                                         "tool list. Upstream offers project custom tools over its "
                                                         "HTTP transport (project-scoped tools); over stdio it is not "
                                                         "listed, so this plan would fail."))
                return None, explain("not-offered", str(tool))
        for step in steps:
            if step["op"] == "execute_code.replay":
                problem = self._expand_replay(step)
                if problem:
                    return None, problem
            if step["op"] == "execute_custom_tool":
                problem = self._expand_custom(step, root)
                if problem:
                    return None, problem
        for step in steps:
            problem = self._root_checks(step)
            if problem:
                return None, problem
            if step["spec"].get("upstream_tool") == "create_script" and step["show"].get("overwrite") is True:
                relative = step["send"].get("path")
                if isinstance(relative, str) and os.path.isfile(os.path.join(root, *relative.split("/"))):
                    problem = self._convert_overwrite(step, root)
                    if problem:
                        return None, problem
        scenes = self._loaded_scenes()
        if scenes is None:
            return None, explain("unreadable", "the open scenes")
        if self._test_runner_busy(self._editor_state(), scenes):
            if not self._wait_tests_settled():
                return None, explain("busy", str(int(READY_WAIT))) + " (Unity's test runner)"
            scenes = self._loaded_scenes() or []
        for scene in scenes:
            path = scene.get("path")
            if path and path not in self.scene_sha:
                self.scene_sha[path] = file_sha(os.path.join(root, *path.split("/")))
        state = self._editor_state() or {}
        play = ((state.get("editor") or {}).get("play_mode") or {})
        files: list[str] = [scene["path"] for scene in scenes if scene.get("path")]
        sim = {"scenes": [dict(scene, user_dirty=bool(scene.get("isDirty"))) for scene in scenes],
               "playing": bool(play.get("is_playing")), "made": {}, "gone": set(), "play_changes": False,
               "compiles_before": False}
        self.compile_errors_now = []
        self.stale_scripts = []
        if any(op_enters_play(step) or op_runs_tests(step) for step in steps):
            self.compile_errors_now = self._compile_errors()
            self.stale_scripts = self._stale_scripts(root)
        for index, step in enumerate(steps):
            facts, touched, problem = self._step_facts(step, root, sim, index)
            if problem:
                return None, problem
            for item in touched:
                if item not in files:
                    files.append(item)
        return {"instance": instance, "root": root, "scenes": scenes, "files": files,
                "playing": bool(play.get("is_playing")),
                "watch_compile": any(op_enters_play(step) or op_runs_tests(step) for step in steps)}, ""

    def _state_parts(self, ctx: dict) -> dict:
        """The state a plan was made against. Volatile fields (timestamps, sequence) are left out."""
        state = self._editor_state() or {}
        editor = state.get("editor") or {}
        play = editor.get("play_mode") or {}
        scenes = self._loaded_scenes()
        playing = bool(play.get("is_playing"))
        parts = {
            "selected editor": ctx.get("instance") or "",
            "project": ctx.get("root") or "",
            "play mode": json.dumps([play.get("is_playing"), play.get("is_paused")]) if play else "unreadable",
            "open scenes": json.dumps([[scene.get(key) for key in ("path", "name", "isDirty", "isActive", "rootCount")]
                                       for scene in scenes], ensure_ascii=False) if scenes is not None else "unreadable",
            "scene objects": self._hierarchy_digest(playing),
            "component values": self._component_digest(playing),
        }
        root = ctx.get("root") or ""
        for relative in ctx.get("files") or []:
            full = relative if _is_absolute_path(relative) else os.path.join(root, *relative.split("/"))
            parts["file " + relative] = (tree_sha(full) if relative.endswith("/") else file_sha(full)) or "absent"
        if ctx.get("watch_compile"):
            parts["compile errors"] = hashlib.sha256("\n".join(self._compile_errors()).encode("utf-8")).hexdigest()
        parts["side effect table"] = TABLE_SHA
        return parts

    @staticmethod
    def _digest(parts: dict) -> str:
        return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    # ---- running ----

    def _progress(self, mid, message: str) -> None:
        """notifications/progress, only when the request carried a progressToken."""
        if mid is None:
            return
        with self.progress_lock:
            slot = self.progress.get(mid)
            if slot is None:
                return
            slot["n"] += 1
            count = slot["n"]
        self.write({"jsonrpc": "2.0", "method": "notifications/progress",
                    "params": {"progressToken": slot["token"], "progress": count, "message": message}})

    def _poll_job(self, kind: str, result: dict, mid, deadline: float, snap: dict | None = None
                  ) -> tuple[list[dict], str]:
        """After run_tests or a build, wait for the job. Returns its last status and a failure reason (empty when
        the job finished and nothing failed)."""
        data = _first_json(result.get("content") or [])
        inner = (data or {}).get("data") if isinstance(data, dict) else None
        job = (inner or {}).get("job_id") if isinstance(inner, dict) else None
        if not isinstance(job, str) or not job:
            return [], f"upstream did not return a {kind} job id, so the result cannot be read back"
        last = None
        status = None
        while time.time() < deadline:
            if mid is not None and mid in self.cancelled:
                break
            if kind == "tests":
                body = self._tool_json("get_test_job", {"job_id": job, "include_failed_tests": True,
                                                        "include_details": True, "wait_timeout": 10}, 60)
                status = ((body or {}).get("data") or {}).get("status") if isinstance(body, dict) else None
                done = status in ("succeeded", "failed", "cancelled")
                progress = ((body or {}).get("data") or {}).get("progress") if isinstance(body, dict) else None
                note = f"tests {status or 'pending'}" + (
                    f" ({progress.get('completed')} of {progress.get('total')})"
                    if isinstance(progress, dict) and isinstance(progress.get("total"), int) else "")
            else:
                body = self._tool_json("manage_build", {"action": "status", "job_id": job}, 60)
                status = ((body or {}).get("data") or {}).get("result") if isinstance(body, dict) else None
                done = status in ("succeeded", "failed", "cancelled")
                note = f"build {status or 'pending'}"
                if not done:
                    time.sleep(3)
            if body is not None:
                last = body
            self._progress(mid, note)
            if done:
                pieces = [{"type": "text", "text": json.dumps(last, ensure_ascii=False)}]
                if kind == "tests" and not self._wait_tests_settled():
                    pieces.append({"type": "text", "text": f"{NAME} note: the test runner had not restored the open "
                                                           f"scenes after {int(READY_WAIT)} seconds."})
                if kind == "tests":
                    counts, problem = self._count_test_job(last if isinstance(last, dict) else {})
                    if problem:
                        return pieces, problem
                    total, failed_n = counts
                    if failed_n:
                        return pieces, (f"the test run failed: {failed_n} of {total} tests failed "
                                        f"(counted from the job's test rows)")
                    if total == 0:
                        return pieces, "0 tests ran (counted from the job)"
                    self._test_counts = counts
                    return pieces, ""
                out_reason = self._build_output_failure(snap or {})
                quote = status or "no result word"
                if out_reason:
                    return pieces, (f"{out_reason}. Upstream said {quote}; that word is not the result.")
                return pieces, ""
            if body is None:
                time.sleep(2)
        tail = json.dumps(last, ensure_ascii=False) if last is not None else ""
        reader = "unity_tests op get_test_job" if kind == "tests" else "unity_build op manage_build.status"
        return [{"type": "text", "text": (f"{NAME}: the {kind} job {job} is still running. Read {reader} with "
                                          f"{{\"job_id\": \"{job}\"}} for the result. {tail}").strip()}], \
            f"the {kind} job {job} had not finished when the plan's time ran out"

    @staticmethod
    def _job_failure(kind: str, status, body) -> str:
        data = (body or {}).get("data") if isinstance(body, dict) else None
        data = data if isinstance(data, dict) else {}
        if kind == "build":
            return "" if status == "succeeded" else f"the build {status or 'did not report a result'}"
        summary = ((data.get("result") or {}).get("summary") or {}) if isinstance(data.get("result"), dict) else {}
        total, failed = summary.get("total"), summary.get("failed")
        if status != "succeeded":
            return f"the test run {status or 'did not finish'}" + (f": {data.get('error')}" if data.get("error") else "")
        if not isinstance(total, int):
            return "the test run returned no totals"
        if total == 0:
            return "0 tests ran (no test matched, or the test assembly did not compile)"
        if isinstance(failed, int) and failed > 0:
            names = [str(row.get("fullName") or row.get("name")) for row in (data.get("result") or {}).get("results") or []
                     if isinstance(row, dict) and str(row.get("state", "")).lower() not in ("passed", "skipped")]
            return f"{failed} of {total} tests failed" + (f" ({', '.join(names[:5])})" if names else "")
        return ""

    @staticmethod
    def _job_summary(kind: str, body) -> str:
        data = (body or {}).get("data") if isinstance(body, dict) else None
        if kind == "tests" and isinstance(data, dict) and isinstance(data.get("result"), dict):
            summary = data["result"].get("summary") or {}
            return (f"{data.get('mode') or 'tests'}: {summary.get('passed')} passed, {summary.get('failed')} failed, "
                    f"{summary.get('skipped')} skipped of {summary.get('total')}")
        if kind == "build" and isinstance(data, dict):
            return f"build {data.get('result')}"
        return ""

    def _console_errors(self) -> list[str] | None:
        """Every error, exception, and assert line in the console now, oldest first (None when unreadable)."""
        body = self._tool_json("read_console", {"action": "get", "types": ["error"], "count": 500,
                                                "format": "plain", "include_stacktrace": False})
        if not isinstance(body, dict) or body.get("success") is False:
            return None
        data = body.get("data")
        items = data if isinstance(data, list) else (data.get("items") if isinstance(data, dict) else None)
        return [str(item) for item in items or []]

    @staticmethod
    def _new_lines(before: list[str] | None, after: list[str] | None) -> list[str]:
        """Console lines that appeared after the earlier read. The console has no timestamps: when the earlier
        lines are still at the start, the rest is new; when Unity cleared it (Clear on Play) or replaced its
        compiler messages, every line that was not there before is new."""
        if before is None or after is None:
            return []
        if after[:len(before)] == before:
            return after[len(before):]
        left = list(before)
        out = []
        for line in after:
            if line in left:
                left.remove(line)
            else:
                out.append(line)
        return out

    def _wait_play(self, playing: bool, limit: float, mid) -> bool:
        start = time.time()
        while time.time() - start < limit:
            if mid is not None and mid in self.cancelled:
                return False
            state = self._editor_state()
            play = ((state or {}).get("editor") or {}).get("play_mode") or {}
            # is_changing is EditorApplication.isPlayingOrWillChangePlaymode (EditorStateCache.cs): it stays true for
            # the whole play session, so it only tells that leaving play has finished.
            if state is not None and bool(play.get("is_playing")) == playing \
                    and (playing or not play.get("is_changing")):
                return True
            self._progress(mid, f"waiting for Unity to {'enter' if playing else 'leave'} play mode "
                                f"({int(time.time() - start)} s)")
            time.sleep(0.5)
        return False

    def _before_step(self, step: dict) -> dict:
        root = self._root_cache or ""
        snap: dict = {"files": {}, "errors": None}
        for relative, _what in step.get("expect") or []:
            snap["files"][relative] = file_sha(os.path.join(root, *relative.split("/"))) if root else None
        if not step.get("read_only"):
            snap["errors"] = self._console_errors()
        rel = _build_output_rel(step)
        if rel and root:
            snap["output"] = (rel, self._path_digest(root, rel))
        return snap

    def _path_digest(self, root: str, rel: str) -> str | None:
        full = rel if os.path.isabs(rel) else os.path.join(root, *rel.split("/"))
        if os.path.islink(full) or not os.path.lexists(full):
            return None
        if os.path.isfile(full):
            return file_sha(full)
        if os.path.isdir(full):
            return tree_sha(full)
        return None

    def _build_output_failure(self, snap: dict) -> str:
        """Empty when the planned output path is on disk and was created or its bytes changed."""
        pair = snap.get("output")
        if not pair:
            return "the plan names no output path, so the build has no file to check"
        rel, before = pair
        root = self._root_cache or ""
        after = self._path_digest(root, rel) if root or os.path.isabs(rel) else None
        if after is None:
            return f"the output path {rel} is not on disk"
        if before is not None and before == after:
            return f"the output path {rel} did not change"
        return ""

    def _check_after(self, step: dict, snap: dict, mid) -> tuple[list[dict], str]:
        """Read the editor back after a step. Returns notes and a failure reason (empty when the step did what the
        plan said). Upstream's own success reply is not taken as the answer."""
        failure = ""
        kinds = step_kinds(step)
        if "enter_play" in kinds and not self._wait_play(True, PLAY_WAIT, mid):
            failure = (f"Unity did not enter play mode (editor state is_playing was still false after "
                       f"{int(PLAY_WAIT)} seconds), although upstream answered that it did")
        elif "enter_play" in kinds and not self._frame_advanced():
            failure = ("Unity reported play mode, but the frame count did not advance, so play did not start")
        if "exit_play" in kinds and not self._wait_play(False, PLAY_WAIT, mid):
            failure = f"Unity was still in play mode after {int(PLAY_WAIT)} seconds"
        root = self._root_cache or ""
        scenes = None
        for relative, what in step.get("expect") or []:
            if failure or not root:
                break
            full = os.path.join(root, *relative.split("/"))
            now = file_sha(full)
            before = snap["files"].get(relative)
            if what == "created" and now is None and not os.path.isdir(full):
                failure = f"{relative} is not on disk after the step"
            elif what == "changed" and (now is None or now == before):
                failure = f"{relative} did not change on disk"
            elif what == "gone" and os.path.lexists(full):
                failure = f"{relative} is still on disk"
            elif what == "saved":
                scenes = scenes if scenes is not None else (self._loaded_scenes() or [])
                row = next((scene for scene in scenes if scene.get("path") == relative), None)
                if now is None:
                    failure = f"{relative} is not on disk after the save"
                elif row is not None and row.get("isDirty"):
                    failure = f"{relative} still has unsaved changes after the save"
        notes: list[dict] = []
        if snap.get("errors") is not None:
            fresh = self._new_lines(snap["errors"], self._console_errors())
            if fresh:
                notes.append({"type": "text", "text": f"{NAME}: console error lines that appeared after this step "
                                                      f"started:\n" + "\n".join(visible(line)[:300]
                                                                                 for line in fresh[:20])})
                if "enter_play" in kinds and failure:
                    failure += "; the console shows why"
        return notes, failure

    def _after_step(self, step: dict, started_ms: int, mid) -> tuple[list[dict], str]:
        """After a step: compile when it changed scripts, and keep the first-seen sha of scene files current."""
        extra: list[dict] = []
        if op_compiles(step):
            pieces, stop = self._compile_now(started_ms, mid)
            extra.extend(pieces)
            if stop:
                return extra, "the compile after this step failed or did not finish"
        spec = step["spec"]
        if spec.get("upstream_tool") == "manage_scene" and spec.get("action") in ("save", "create", "load") \
                or "save_scene" in step_kinds(step):
            root, _failed = self.project_root()
            for scene in self._loaded_scenes() or []:
                path = scene.get("path")
                if path and root:
                    self.scene_sha[path] = file_sha(os.path.join(root, *path.split("/")))
        return extra, ""

    def _frame_count(self) -> int | None:
        # Each call wakes the editor. A background window does not tick play mode during a plain sleep,
        # and is_playing becomes true before the player loop has started. QueuePlayerLoopUpdate asks for
        # one player update; runInBackground lets that update happen while the editor is not focused.
        code = ("UnityEngine.Application.runInBackground = true;\n"
                "UnityEditor.EditorApplication.QueuePlayerLoopUpdate();\n"
                "return UnityEngine.Time.frameCount.ToString();\n")
        body = self._tool_json("execute_code", {"action": "execute", "code": code,
                                                "safety_checks": True, "compiler": "auto"}, 30)
        result = ((body or {}).get("data") or {}).get("result") if isinstance(body, dict) else None
        if isinstance(result, int) and not isinstance(result, bool):
            return result
        if isinstance(result, str) and result.strip().isdigit():
            return int(result.strip())
        return None

    def _frame_advanced(self) -> bool:
        deadline = time.time() + FRAME_WAIT
        previous = None
        while time.time() < deadline:
            current = self._frame_count()
            if previous is not None and current is not None and current > previous:
                return True
            if current is not None:
                previous = current
            time.sleep(0.25)
        return False

    def _walk_watch(self, root: str) -> tuple[dict[str, str], dict[str, bytes | None]]:
        """Every file in the project except Unity's caches (Library, Temp, Logs, obj) and .git.

        UserSettings and files at the project root are included, so a script that writes there is put back.
        """
        shas: dict[str, str] = {}
        blobs: dict[str, bytes | None] = {}
        for current, dirs, files in os.walk(root):
            dirs[:] = [item for item in dirs if item not in _WATCH_SKIP and not item.startswith(".")
                       and not os.path.islink(os.path.join(current, item))]
            for name in files:
                if name.startswith("."):
                    continue
                full = os.path.join(current, name)
                if os.path.islink(full):
                    continue
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                try:
                    size = os.path.getsize(full)
                    digest = file_sha(full)
                except OSError:
                    continue
                if not digest:
                    continue
                shas[rel] = digest
                if size <= WATCH_BYTE_CAP:
                    try:
                        blobs[rel] = Path(full).read_bytes()
                    except OSError:
                        blobs[rel] = None
                else:
                    blobs[rel] = None
        return shas, blobs

    def _capture_watch(self) -> dict | None:
        """Bytes on disk before a plan talks to the editor.

        Unity deletes a .meta that has no asset and no guid when it first imports the folder. That can happen
        while the plan is being made, before apply_plan's own snapshot. The bytes from here are what "before the
        plan" means for a file that is already gone by then.
        """
        root = self._known_disk_root()
        if not root:
            return None
        shas, blobs = self._walk_watch(root)
        return {"root": root, "shas": shas, "blobs": blobs}

    def _open_watch(self, steps: list[dict], early: dict | None = None) -> dict | None:
        root, _failed = self.project_root()
        if not root:
            return None
        shas, blobs = self._walk_watch(root)
        if early and early.get("root") == root:
            for rel, sha in (early.get("shas") or {}).items():
                if rel in shas or _keep_editor_file(rel):
                    continue
                blob = (early.get("blobs") or {}).get(rel)
                if isinstance(blob, bytes):
                    shas[rel] = sha
                    blobs[rel] = blob
        scenes = self._loaded_scenes() or []
        dirty = [scene.get("path") for scene in scenes if scene.get("isDirty") and scene.get("path")]
        copies = tempfile.mkdtemp(prefix="cge-scene-")
        for path in dirty:
            dest = os.path.join(copies, path.replace("/", "_"))
            literal_scene, literal_dest = cs_literal(path), cs_literal(dest)
            if literal_scene and literal_dest:
                code = (
                    "var scene = UnityEditor.SceneManagement.EditorSceneManager.GetSceneByPath(" + literal_scene + ");\n"
                    "if (!scene.IsValid()) return \"missing\";\n"
                    "bool ok = UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, " + literal_dest
                    + ", true);\n"
                    "return (ok ? \"copied\" : \"miss\") + \" dirty=\" + scene.isDirty;\n"
                )
                self._tool_json("execute_code", {"action": "execute", "code": code, "safety_checks": True,
                                                "compiler": "auto"}, 30)
        return {"root": root, "shas": shas, "blobs": blobs, "dirty": dirty, "copies": copies, "closed": False}

    def _named_paths(self, steps: list[dict], before: set[str], extra: set[str] | None = None) -> set[str]:
        """Paths the plan's effects cover, so a correct effect is not put back and a deleted file is not restored.

        That is the file, the .meta Unity writes for it, the .meta of a folder the plan creates, every file inside
        a folder the plan deletes, the manifest and lock a package step names, and the .meta of an asset that
        had none when the plan was made.
        """
        compiles = any(op_compiles(step) or step.get("compile_first") for step in steps)
        names: set[str] = {rel for rel in before if _keep_editor_file(rel)}
        names.update(_EDITOR_CHURN)
        names.update(extra or ())
        for step in steps:
            for rel in step.get("keep_paths") or []:
                if isinstance(rel, str):
                    names.add(rel)
            for rel, what in step.get("expect") or []:
                if not isinstance(rel, str):
                    continue
                names.add(rel)
                if not rel.endswith(".meta"):
                    names.add(rel + ".meta")
                if what in ("created", "changed", "saved"):
                    parent = rel.rsplit("/", 1)[0] if "/" in rel else ""
                    while parent:
                        meta = parent + ".meta"
                        if meta not in before:
                            names.add(meta)
                        parent = parent.rsplit("/", 1)[0] if "/" in parent else ""
                if what == "gone":
                    prefix = rel.rstrip("/") + "/"
                    for old in before:
                        if old == rel or old == rel + ".meta" or old.startswith(prefix):
                            names.add(old)
        if compiles:
            for old in before:
                if _generated_project_file(old):
                    names.add(old)
        return names

    def _close_watch(self, watch: dict | None, steps: list[dict]) -> tuple[list[str], list[str]]:
        """Put back a change the plan did not name, and remove a file this apply created.

        Returns (put back, left in place). A new .meta stays when its asset or folder was already on disk.
        """
        if not watch or watch.get("closed"):
            return [], []
        watch["closed"] = True
        root = watch["root"]
        named = self._named_paths(steps, set(watch["shas"]), set(watch.get("import_metas") or ()))
        after, _blobs = self._walk_watch(root)
        for rel in list(watch["shas"]) + list(after):
            if _keep_editor_file(rel):
                named.add(rel)
        if any(op_compiles(step) or step.get("compile_first") for step in steps):
            for rel in after:
                if _generated_project_file(rel):
                    named.add(rel)
        restored: list[str] = []
        left: list[str] = []

        def write_back(rel: str) -> bool:
            blob = watch["blobs"].get(rel)
            full = os.path.join(root, *rel.split("/"))
            if not isinstance(blob, bytes):
                return False
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as handle:
                handle.write(blob)
            return True

        for rel, sha in watch["shas"].items():
            if rel in named or after.get(rel) == sha:
                continue
            if write_back(rel):
                restored.append(rel)
            else:
                restored.append(rel + " (could not put back)")
        for rel in list(after):
            if rel in watch["shas"] or rel in named:
                continue
            full = os.path.join(root, *rel.split("/"))
            if not os.path.lexists(full):
                continue
            if _meta_of_prior_body(rel, watch["shas"]):
                continue
            try:
                os.remove(full)
            except OSError:
                if os.path.lexists(full):
                    restored.append(rel + " (could not put back)")
                continue
            restored.append(rel)
        for rel in restored:
            if rel in watch["dirty"]:
                self._mark_scene_dirty(rel)
        shutil.rmtree(watch["copies"], ignore_errors=True)
        return restored, left

    def _mark_scene_dirty(self, relative: str) -> None:
        literal = cs_literal(relative)
        if not literal:
            return
        code = (
            "var scene = UnityEditor.SceneManagement.EditorSceneManager.GetSceneByPath(" + literal + ");\n"
            "if (!scene.IsValid()) return \"missing\";\n"
            "UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(scene);\n"
            "return scene.isDirty ? \"dirty\" : \"clean\";\n"
        )
        self._tool_json("execute_code", {"action": "execute", "code": code, "safety_checks": True,
                                        "compiler": "auto"}, 30)

    @staticmethod
    def _count_test_job(body: dict) -> tuple[tuple[int, int] | None, str]:
        """(total, failed) from the job reply, or a reason the run cannot be counted.

        MCP for Unity 10.3.0 does not write a result file. The count is the per-test rows (include_details),
        checked against summary and against progress, and the run must have a start time and a finish time.
        The status word succeeded is not the result.
        """
        data = body.get("data") if isinstance(body, dict) else None
        if not isinstance(data, dict):
            return None, "the test job reply had no data to count"
        started, finished = data.get("started_unix_ms"), data.get("finished_unix_ms")
        if isinstance(started, bool) or not isinstance(started, (int, float)):
            return None, "the test run did not both start and finish"
        if isinstance(finished, bool) or not isinstance(finished, (int, float)) or finished < started:
            return None, "the test run did not both start and finish"
        result = data.get("result") if isinstance(data.get("result"), dict) else None
        if not result:
            err = data.get("error")
            return None, "the test run finished without a result to count" + (f": {err}" if err else "")
        summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
        nums = []
        for key in ("total", "passed", "failed", "skipped"):
            value = summary.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return None, "the test run returned no totals to count"
            nums.append(value)
        total, passed, failed, skipped = nums
        if passed + failed + skipped != total:
            return None, "the test run's passed, failed, and skipped do not add up to its total"
        progress = data.get("progress") if isinstance(data.get("progress"), dict) else {}
        p_total, p_done = progress.get("total"), progress.get("completed")
        if isinstance(p_total, bool) or not isinstance(p_total, int) or isinstance(p_done, bool) \
                or not isinstance(p_done, int):
            return None, "the test run did not report how many tests started and finished"
        if p_done != p_total or p_total != total:
            return None, "the test run's finished count does not match its total"
        rows = result.get("results")
        if total == 0:
            if isinstance(rows, list) and rows:
                return None, "the test run's summary says 0 tests but it returned rows"
            return (0, 0), ""
        if not isinstance(rows, list) or len(rows) != total:
            return None, "the test run did not return one row per test to count"
        failed_rows = 0
        passed_rows = 0
        skipped_rows = 0
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("state"), str):
                return None, "the test run's per-test rows could not be counted"
            state = row["state"].lower()
            if state == "failed":
                failed_rows += 1
            elif state == "passed":
                passed_rows += 1
            elif state == "skipped":
                skipped_rows += 1
            else:
                return None, (f"the test run returned a test state {row['state']} that is not passed, failed, "
                              f"or skipped")
        if failed_rows != failed or passed_rows != passed or skipped_rows != skipped:
            return None, (f"the test run failed: {failed_rows} of {total} test rows failed, and the summary said "
                          f"{failed} failed")
        return (total, failed_rows), ""

    def _run_steps(self, steps: list[dict], mid, deadline: float | None = None, early: dict | None = None,
                   import_metas: list[str] | None = None) -> dict:
        pieces: list[dict] = []
        deadline = deadline or (time.time() + APPLY_BUDGET)
        total = len(steps)
        planned = not (total == 1 and steps[0].get("read_only"))
        done_notes: list[str] = []
        watch = self._open_watch(steps, early) if planned else None
        if watch is not None:
            watch["import_metas"] = list(import_metas or [])

        def failed(index: int, step: dict, reason: str) -> dict:
            reverted, left = self._close_watch(watch, steps)
            clause = _unplanned_clause(reverted, left)
            if clause:
                reason += ". " + clause
            head = (f"{NAME}: FAILED at step {index + 1} of {total} ({step['tool']} {step['op']}): {visible(reason)}."
                    + (" Steps after it were not sent." if index + 1 < total else ""))
            if index + 1 < total:
                pieces.append({"type": "text", "text": explain("later")})
            return limit_result(_lines([{"type": "text", "text": head}] + pieces), True)

        for index, step in enumerate(steps):
            if total > 1 or not step.get("read_only"):
                self._progress(mid, f"step {index + 1} of {total}: {step['tool']} {step['op']}")
            snap = self._before_step(step) if planned else {"files": {}, "errors": None}
            started_ms = int(time.time() * 1000)
            if step.get("compile_first"):
                first, stop = self._compile_now(started_ms, mid)
                pieces.extend(first)
                if stop:
                    return failed(index, step, "the compile before this step failed or did not finish, so it was "
                                               "not sent")
                started_ms = int(time.time() * 1000)
            if step.get("match_editor"):
                state, detail = self._editor_asset_state(step["match_editor"])
                if state == "dirty":
                    return failed(index, step, "the editor value is dirty, so the replace was not sent:\n" + detail)
                if state not in ("clean", "not-loaded"):
                    return failed(index, step, "the editor value could not be read, so the replace was not sent")
            result = self._dispatch(step, mid)
            if step.get("bridge") == "component_values" and not result.get("isError"):
                data = _first_json(result.get("content") or [])
                text = ((data or {}).get("data") or {}).get("result") if isinstance(data, dict) else None
                if isinstance(text, str):
                    result = {"content": [{"type": "text", "text": text}], "isError": False}
            pieces.extend(result.get("content") or [])
            if result.get("isError"):
                if not planned:
                    return {"content": pieces, "isError": True}
                return failed(index, step, "upstream returned an error (below)")
            if step.get("read_only"):
                continue
            later = steps[index + 1] if index + 1 < total else None
            if op_compiles(step) and later is not None and op_compiles(later):
                notes, reason = self._check_after(step, snap, mid)
                pieces.extend(notes)
                if reason:
                    return failed(index, step, reason)
                continue
            extra, reason = self._after_step(step, started_ms, mid)
            pieces.extend(extra)
            if reason:
                return failed(index, step, reason)
            if op_runs_tests(step) or "build_player" in step_kinds(step):
                kind = "tests" if op_runs_tests(step) else "build"
                self._oracle_since = time.time()
                job_pieces, reason = self._poll_job(kind, result, mid, deadline, snap)
                pieces.extend(job_pieces)
                if reason:
                    return failed(index, step, reason)
                last = _first_json(job_pieces[:1]) if job_pieces else None
                if kind == "tests" and getattr(self, "_test_counts", None):
                    total_n, failed_n = self._test_counts
                    done_notes.append(f"tests: {total_n - failed_n} passed, {failed_n} failed of {total_n} "
                                      f"(counted from the job)")
                elif kind == "build":
                    rel = (snap.get("output") or ("", None))[0]
                    if rel:
                        done_notes.append(f"output {rel} is on disk")
                else:
                    summary = self._job_summary(kind, last)
                    if summary:
                        done_notes.append(summary)
            notes, reason = self._check_after(step, snap, mid)
            pieces.extend(notes)
            if reason:
                return failed(index, step, reason)
            if "enter_play" in step_kinds(step):
                done_notes.append("Unity is in play mode")
            if "exit_play" in step_kinds(step):
                done_notes.append("Unity left play mode")
            if op_compiles(step):
                done_notes.append("compiled with no errors")
        reverted, left = self._close_watch(watch, steps)
        clause = _unplanned_clause(reverted, left)
        if planned and clause:
            return failed(total - 1, steps[-1], clause)
        if planned:
            head = (f"{NAME}: done. {total} step(s) ran, and the plugin read the editor back after each one"
                    + (": " + "; ".join(done_notes) if done_notes else "") + ".")
            pieces.insert(0, {"type": "text", "text": head})
        return limit_result(pieces or [{"type": "text", "text": ""}], False)

    def _plan_batch(self, arguments: dict, mid=None, lead: str = "") -> dict:
        unknown = sorted(set(arguments) - {"steps"})
        if unknown:
            return guidance_result(explain("key", f"plan_batch does not take {', '.join(unknown)}; it takes steps"))
        steps, problem = self._collect_steps(arguments.get("steps"))
        if problem:
            return reply_for(problem)
        early = self._capture_watch()
        disk = self._known_disk_root() or ""
        imports = pending_asset_imports(disk)
        orphans = orphan_unity_metas(disk)
        lock_refresh = manifest_ahead_of_lock(disk)
        ctx, problem = self._context(steps, mid)
        if problem:
            return reply_for(problem)
        if ctx.get("root"):
            if not imports:
                imports = pending_asset_imports(ctx["root"])
            if not orphans:
                orphans = orphan_unity_metas(ctx["root"])
            if not lock_refresh:
                lock_refresh = manifest_ahead_of_lock(ctx["root"])
        ctx["pending_imports"] = imports
        ctx["orphan_metas"] = orphans
        ctx["lock_refresh"] = lock_refresh
        body = plan_text(steps, ctx)
        parts = self._state_parts(ctx)
        unreadable = [key for key, value in parts.items() if value == "unreadable"]
        if unreadable:
            return reply_for(explain("unreadable", ", ".join(unreadable)))
        fingerprint = self._digest(parts)
        plan_id = secrets.token_hex(8)
        shown = body + f"plan_id: {plan_id}\nstate fingerprint: {fingerprint}\n"
        if len(shown) > MESSAGE_CAP:
            return reply_for(explain("plan-long", str(len(shown))))
        question = second_question(steps, plan_id, len(shown)) if _risk_summary(steps) else ""
        with self.plan_lock:
            self.replaced_ids.update(self.plans.keys())
            self.plans = {plan_id: {"steps": steps, "ctx": ctx, "parts": parts, "fingerprint": fingerprint,
                                    "text": shown, "question": question, "created": time.time(),
                                    "early_watch": early,
                                    "import_metas": [path + ".meta" for path in imports] + list(orphans)
                                    + (["Packages/packages-lock.json"] if lock_refresh else [])}}
        return {"content": [{"type": "text", "text": lead + shown}], "isError": False}

    def _elicit(self, message: str, mid) -> str:
        """Ask the client through MCP elicitation: accept, decline, cancel, or unshown.

        unshown: the client has no elicitation, or answered cancel within FAST_CANCEL seconds. Hermes 0.22.2's
        classic CLI answers that way: its MCP question runs on a thread with no approval panel and fails closed
        at once (agent.log: "approval requested on a thread with no approval callback while prompt_toolkit is
        active; failing closed"). A person who saw the question and let it run out answers cancel much later.
        """
        if not isinstance(self.client_caps.get("elicitation"), dict):
            return "unshown"
        with self.client_lock:
            rid = f"cge-{self.client_next}"
            self.client_next += 1
            slot = {"event": threading.Event(), "reply": None}
            self.client_pending[rid] = slot
        started = time.time()
        self.write({"jsonrpc": "2.0", "id": rid, "method": "elicitation/create",
                    "params": {"message": message, "requestedSchema": {"type": "object", "properties": {}}}})
        end = time.time() + ELICIT_WAIT
        try:
            while time.time() < end:
                if slot["event"].wait(0.5):
                    break
                if mid is not None and mid in self.cancelled:
                    return "cancel"
            reply = slot["reply"]
        finally:
            with self.client_lock:
                self.client_pending.pop(rid, None)
        if not isinstance(reply, dict) or "result" not in reply:
            if isinstance(reply, dict) and "error" in reply and time.time() - started < FAST_CANCEL:
                return "unshown"
            return "cancel"
        action = (reply.get("result") or {}).get("action")
        if action == "cancel" and time.time() - started < FAST_CANCEL:
            return "unshown"
        return action if action in ("accept", "decline", "cancel") else "decline"

    def _check_plan(self, plan_id, mid) -> tuple[dict | None, dict | None]:
        """The stored plan when it may run now, else the error reply. A short failure keeps the plan."""
        if not isinstance(plan_id, str) or not plan_id:
            return None, reply_for(explain("no-plan"))
        with self.plan_lock:
            stored = self.plans.get(plan_id)
            if stored is None:
                replaced = plan_id in self.replaced_ids
                return None, reply_for(explain("replaced" if replaced else "no-plan", plan_id))
            if time.time() - stored["created"] > PLAN_TTL:
                self.plans.pop(plan_id, None)
                self.retired.add(plan_id)
                return None, reply_for(explain("expired", plan_id))
        reason = self.ensure_child()
        if reason:
            return None, error_result(reason + " The plan is kept; call apply_plan again.")
        ctx = stored["ctx"]
        if ctx.get("instance") and not self._pin(ctx["instance"]):
            return None, reply_for(explain("gone", ctx["instance"]))
        if not self._wait_settled():
            return None, reply_for(explain("busy-kept", str(int(READY_WAIT))))
        root, failed = self.project_root(fresh=True)
        if failed is not None:
            return None, error_result(_content_text(failed["content"]) + " The plan is kept.")
        if root != ctx.get("root"):
            self._retire(plan_id)
            return None, reply_for(explain("state", "project"))
        parts = self._state_parts(ctx)
        unreadable = [key for key, value in parts.items() if value == "unreadable"]
        if unreadable:
            return None, reply_for(explain("unreadable", ", ".join(unreadable)) + " The plan is kept.")
        if self._digest(parts) != stored["fingerprint"]:
            changed = [key for key in stored["parts"] if parts.get(key) != stored["parts"][key]]
            self._retire(plan_id)
            return None, reply_for(explain("state", ", ".join(changed) or "state"))
        return stored, None

    def _run_stored(self, plan_id: str, stored: dict, mid) -> dict:
        with self.plan_lock:
            if self.plans.get(plan_id) is not stored:
                return reply_for(explain("replaced", plan_id))
            self._retire(plan_id, locked=True)
        return self._run_steps(stored["steps"], mid, early=stored.get("early_watch"),
                               import_metas=stored.get("import_metas"))

    def _apply_plan(self, arguments: dict, mid) -> dict:
        unknown = sorted(set(arguments) - {"plan_id"})
        if unknown:
            return guidance_result(explain("key", f"apply_plan does not take {', '.join(unknown)}; it takes plan_id"))
        plan_id = arguments.get("plan_id")
        stored, problem = self._check_plan(plan_id, mid)
        if problem is not None:
            return problem
        risky = _risk_summary(stored["steps"])
        if risky:
            words = " and ".join(sorted({RISK_WORDS[item] for step in stored["steps"]
                                         for item in step.get("risks") or []}, key=list(RISK_WORDS.values()).index))
            if not stored.get("question"):
                # The summary of the risks does not fit in what a chat app shows in full: do not send a question
                # that would be cut. Hermes asks about confirm_risky_plan instead.
                stored["confirm"] = True
                return guidance_result(explain("no-elicit", plan_id).replace("{risky}", words).replace(
                    "Hermes did not show the second question here (the classic CLI fails MCP questions "
                    "closed, and a client without elicitation cannot show one).",
                    f"Its risks do not fit on a Hermes 0.22.2 chat card without being cut (Telegram counts the text "
                    f"after HTML escaping, in UTF-16; Discord and Slack count the raw text), so no question was "
                    f"sent. The plan text has the full code."))
            answer = self._elicit(stored["question"], mid)
            if answer == "unshown":
                stored["confirm"] = True
                return guidance_result(explain("no-elicit", plan_id).replace("{risky}", words))
            if answer == "decline":
                self._retire(plan_id)
                return reply_for(explain("declined"))
            if answer != "accept":
                return reply_for(explain("unanswered"))
        return self._run_stored(plan_id, stored, mid)

    def _confirm_risky_plan(self, arguments: dict, mid) -> dict:
        unknown = sorted(set(arguments) - {"plan_id"})
        if unknown:
            return guidance_result(explain("key", f"confirm_risky_plan does not take {', '.join(unknown)}; it takes "
                                                  f"plan_id"))
        plan_id = arguments.get("plan_id")
        with self.plan_lock:
            waiting = self.plans.get(plan_id) if isinstance(plan_id, str) else None
        if waiting is not None and not waiting.get("confirm"):
            return guidance_result(explain("not-confirmable", plan_id))
        stored, problem = self._check_plan(plan_id, mid)
        if problem is not None:
            return problem
        return self._run_stored(plan_id, stored, mid)

    def _retire(self, plan_id: str, locked: bool = False) -> None:
        if locked:
            self.plans.pop(plan_id, None)
            self.retired.add(plan_id)
            return
        with self.plan_lock:
            self.plans.pop(plan_id, None)
            self.retired.add(plan_id)

    def call(self, name, arguments, mid=None) -> dict:
        if not isinstance(name, str) or name not in TOOLS_BY_NAME:
            return guidance_result(explain("unknown-tool", str(name)))
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return guidance_result(explain("args"))
        if name == "plan_batch":
            return self._plan_batch(arguments, mid)
        if name == "apply_plan":
            return self._apply_plan(arguments, mid)
        if name == "confirm_risky_plan":
            return self._confirm_risky_plan(arguments, mid)
        unknown = sorted(set(arguments) - {"op", "arguments"})
        if unknown:
            return guidance_result(explain("key", f"{name} does not take {', '.join(unknown)}; it takes op and "
                                                  f"arguments"))
        if "op" not in arguments:
            return guidance_result(explain("key", f"{name} needs op; the op names are in its schema"))
        op_name = arguments["op"]
        if op_name not in READ_ALLOW and (name, op_name) in OPS:
            lead = (f"{name} {op_name} changes Unity, so that step was not sent. This is its plan: show it to the "
                    f"user, then "
                    f"call apply_plan with the plan_id below. To do more in one approval, call plan_batch with all "
                    f"the steps instead.\n\n")
            return self._plan_batch({"steps": [{"tool": name, "op": op_name,
                                                "arguments": arguments.get("arguments") or {}}]}, mid, lead)
        step, problem = self._prepare_one(name, op_name, arguments.get("arguments") or {})
        if problem:
            return reply_for(problem)
        step["read_only"] = True
        disk_only = step.get("bridge") in ("asset_find", "prefab_info", "read_text") and self._known_disk_root()
        if not disk_only:
            reason = self.ensure_child()
            if reason:
                return error_result(reason)
            if self._needs_root(step) and self.selected_instance is None:
                instance, problem = self._target_instance()
                if problem:
                    return reply_for(problem)
                if instance:
                    self._pin(instance)
        problem = self._root_checks(step)
        if problem:
            return reply_for(problem)
        result = self._run_steps([step], mid)
        if step["op"] == "set_active_instance" and not result.get("isError"):
            data = _first_json(result.get("content") or [])
            chosen = ((data or {}).get("data") or {}).get("instance") if isinstance(data, dict) else None
            if isinstance(chosen, str) and chosen:
                self.selected_instance = chosen
                self._root_cache = None
        return result

    def write(self, msg: dict) -> None:
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        with self.out_lock:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()

    def handle(self, msg: dict) -> dict | None:
        method = msg.get("method")
        mid = msg.get("id")
        if method is None and mid is not None and ("result" in msg or "error" in msg):
            with self.client_lock:
                slot = self.client_pending.get(mid)
            if slot is not None:
                slot["reply"] = msg
                slot["event"].set()
            return None
        if method == "notifications/cancelled":
            request_id = (msg.get("params") or {}).get("requestId")
            self.cancelled.add(request_id)
            with self.inflight_lock:
                target = self.inflight.get(request_id)
            if target is not None:
                child, cid = target
                child.send({"jsonrpc": "2.0", "method": "notifications/cancelled",
                            "params": {"requestId": cid, "reason": "cancelled by the client"}})
            return None
        if mid is None:
            return None
        if method == "initialize":
            params = msg.get("params") or {}
            offered = params.get("protocolVersion")
            caps = params.get("capabilities")
            self.client_caps = caps if isinstance(caps, dict) else {}
            version = offered if offered in HANDSHAKE_VERSIONS else CHILD_PROTOCOL
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": NAME, "version": VERSION}}}
        if method == "ping":
            return {"jsonrpc": "2.0", "id": mid, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tool_definitions()}}
        if method == "tools/call":
            params = msg.get("params") or {}
            token = ((params.get("_meta") or {}) if isinstance(params.get("_meta"), dict) else {}).get("progressToken")
            if isinstance(token, (str, int)) and not isinstance(token, bool):
                with self.progress_lock:
                    self.progress[mid] = {"token": token, "n": 0}
            worker = threading.Thread(target=self._call_and_reply, args=(mid, params), daemon=True)
            self.calls = [item for item in self.calls if item.is_alive()] + [worker]
            worker.start()
            return None
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found"}}

    def _call_and_reply(self, mid, params: dict) -> None:
        try:
            result = self.call(params.get("name"), params.get("arguments"), mid)
        except Exception as exc:  # noqa: BLE001 - a bridge bug must still answer the call
            result = error_result(f"{NAME}: internal error ({type(exc).__name__}). {NOTHING_SENT}")
        with self.progress_lock:
            self.progress.pop(mid, None)
        self.write({"jsonrpc": "2.0", "id": mid, "result": result})

    def shutdown(self) -> None:
        if self.child is not None:
            self.child.stop()

    def serve(self) -> int:
        for raw in iter(sys.stdin.buffer.readline, b""):
            line = raw.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                self.write({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
                continue
            if not isinstance(msg, dict):
                continue
            reply = self.handle(msg)
            if reply is not None:
                self.write(reply)
        deadline = time.time() + SHUTDOWN_GRACE
        for worker in self.calls:
            worker.join(max(0.0, deadline - time.time()))
        self.shutdown()
        return 0


def _path_pairs(value, key: str = "", keys: frozenset = PATH_KEYS) -> list[tuple[str, str]]:
    if isinstance(value, dict):
        pairs = []
        for child_key, child in value.items():
            pairs.extend(_path_pairs(child, str(child_key), keys))
        return pairs
    if isinstance(value, list):
        pairs = []
        for child in value:
            pairs.extend(_path_pairs(child, key, keys))
        return pairs
    if isinstance(value, str) and _looks_like_path(key, value, keys):
        return [(key, value)]
    return []


def main() -> int:
    bridge = Bridge()

    def _stop(_signum, _frame):
        bridge.shutdown()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _stop)
    return bridge.serve()


if __name__ == "__main__":
    sys.exit(main())
