#!/usr/bin/env python3
"""Extract MCP for Unity operations and the effect of each one.

Reads the upstream Python tools and the Unity editor C# handlers. Writes a table
the bridge loads. The ask column is not the runtime gate. Domain tools run only
bridge/read_allowlist.json. Every other operation is plan_batch, then apply_plan.

Usage:
  python3 tools/extract_unity_ops.py /path/to/unity-mcp
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_side_effects import KINDS, UNITY_RULES, compact_effects, effects_for, effects_self_check, table_markdown  # noqa: E402

# Surface tools. Every upstream tool name must appear in exactly one list.
# plan_batch and apply_plan are synthetic. They are not upstream tools.
BUNDLES: dict[str, list[str]] = {
    "unity_editor": [
        "manage_editor", "refresh_unity", "set_active_instance", "read_console",
        "execute_menu_item", "manage_tools", "debug_request_context",
    ],
    "unity_scene": ["manage_scene"],
    "unity_object": ["manage_gameobject", "find_gameobjects", "manage_components"],
    "unity_script": [
        "manage_script", "create_script", "delete_script", "validate_script", "get_sha",
        "apply_text_edits", "script_apply_edits", "find_in_file", "manage_scriptable_object",
        "manage_script_capabilities",
    ],
    "unity_asset": ["manage_asset", "manage_prefabs"],
    "unity_look": ["manage_material", "manage_shader", "manage_texture", "manage_camera"],
    "unity_ui": ["manage_ui"],
    "unity_vfx": ["manage_vfx"],
    "unity_animation": ["manage_animation"],
    "unity_graphics": ["manage_graphics"],
    "unity_physics": ["manage_physics"],
    "unity_probuilder": ["manage_probuilder"],
    "unity_profiler": ["manage_profiler"],
    "unity_build": ["manage_build"],
    "unity_packages": ["manage_packages"],
    "unity_code": ["execute_code", "execute_custom_tool", "unity_reflect"],
    "unity_tests": ["run_tests", "get_test_job"],
    "unity_docs": ["unity_docs"],
    "unity_generate": [
        "generate_image", "generate_audio", "generate_model", "import_model",
        "import_model_file", "blender_bridge", "batch_execute",
    ],
}

FIRST_SENTENCE = {
    "unity_editor": "Unity play mode, console, menu, and open editors.",
    "unity_scene": "Unity scene hierarchy, load, save, and create.",
    "unity_object": "Unity GameObjects, components, and find by name.",
    "unity_script": "Unity C# scripts: read, create, edit, and compile.",
    "unity_asset": "Unity assets and prefabs: list, open, and edit.",
    "unity_look": "Unity materials, shaders, textures, and cameras.",
    "unity_ui": "Unity UI Toolkit documents and visual trees.",
    "unity_vfx": "Unity VFX graphs and particle systems.",
    "unity_animation": "Unity Animator controllers, clips, and parameters.",
    "unity_graphics": "Unity lighting, volumes, skybox, and bake.",
    "unity_physics": "Unity physics materials, forces, and simulation.",
    "unity_probuilder": "Unity ProBuilder mesh edit operations.",
    "unity_profiler": "Unity profiler counters and memory snapshots.",
    "unity_build": "Unity player build, scenes in build, and status.",
    "unity_packages": "Unity packages: list, add, and remove.",
    "unity_code": "Run C# in the Unity editor or a project custom tool.",
    "unity_tests": "Unity Test Framework EditMode and PlayMode runs.",
    "unity_docs": "Look up a Unity API page on docs.unity3d.com.",
    "unity_generate": "Generate or import a Unity asset, or call Blender.",
}

# Mechanism calls. A hit means the operation is not a plain read.
RUNS_RE = re.compile(
    r"EditorSceneManager\.OpenScene|EditorSceneManager\.LoadScene|"
    r"PrefabUtility\.LoadPrefabContents|PrefabUtility\.LoadAssetAtPath|"
    r"AssetDatabase\.LoadAssetAtPath|AssetDatabase\.LoadMainAssetAtPath|"
    r"AssetDatabase\.ImportAsset|AssetDatabase\.Refresh|"
    r"EditorApplication\.EnterPlaymode|isPlaying\s*=\s*true|"
    r"EditorApplication\.ExecuteMenuItem|ExecuteMenuItem\(|"
    r"Lightmapping\.Bake|Lightmapping\.BakeAsync|Lightmapping\.Cancel|"
    r"CSharpCodeProvider|CodeDomProvider|CodeDomCompile|CompileAndExecute|"
    r"RoslynCompiler\.Compile|Assembly\.Load|"
    r"TestRunnerApi|TestJobManager\.StartJob|RunTests\(|SendMessage\(|"
    r"CompilationPipeline|ScriptCompilation|"
    r"CommandRegistry\.Invoke|InvokeCommandAsync"
)
WRITES_RE = re.compile(
    r"File\.Write|File\.Append|File\.Copy|File\.Move|File\.Create|"
    r"AssetDatabase\.CreateAsset|AssetDatabase\.CreateFolder|"
    r"AssetDatabase\.SaveAssets|AssetDatabase\.RenameAsset|"
    r"AssetDatabase\.MoveAsset|AssetDatabase\.CopyAsset|"
    r"EditorSceneManager\.Save|EditorSceneManager\.NewScene|"
    r"ApplyModifiedProperties|Undo\.Record|Undo\.Register|"
    r"EditorUtility\.SetDirty|EditorPrefs\.Set|PlayerSettings\.|"
    r"EditorUserBuildSettings\.|SaveAndReimport|"
    r"RenderSettings\.[A-Za-z]+\s*=(?!=)|"
    r"QualitySettings\.SetQualityLevel|"
    r"Physics\.[A-Za-z]+\s*=(?!=)|"
    r"\.AddForce\(|\.AddForceAtPosition\(|\.AddTorque\(|"
    r"SetAreaEnabled\(|"
    r"\.SetFloat\(|\.SetBool\(|\.SetInt\(|\.SetVector"
)
DELETES_RE = re.compile(
    r"AssetDatabase\.DeleteAsset|AssetDatabase\.MoveAssetToTrash|File\.Delete|_history\.Clear\(\)|DestroyImmediate|"
    r"Lightmapping\.Clear|"
    r"Object\.Destroy|Undo\.DestroyObjectImmediate|EditorSceneManager\.CloseScene"
)
SENDS_RE = re.compile(
    r"UnityWebRequest|HttpClient|HttpRequestSpec|WebRequest\.|Process\.Start|TcpClient|"
    r"BlenderSocketClient|Client\.Add\(|Client\.Remove\(|Client\.Search|docs\.unity3d\.com"
)
PY_SENDS_RE = re.compile(
    r"urlopen|httpx\.|requests\.(get|post|put)|aiohttp|websocket|socket\.|"
    r"docs\.unity3d\.com|urllib\.request"
)
PY_RUNS_RE = re.compile(r"subprocess|os\.system|exec\(|eval\(")
PY_WRITES_RE = re.compile(r"open\([^)]*[\"']w|Path\([^)]*\)\.write|os\.remove|unlink\(")

READ_ONLY_RE = re.compile(r"Read-only actions:\s*([^.]+)")
MODIFY_RE = re.compile(r"Modifying actions:\s*([^.]+)")
INLINE_READ_RE = re.compile(
    r"['\"]([A-Za-z_][A-Za-z0-9_]*)['\"](?:\s+action)?\s+is read-only", re.I
)
INLINE_MODIFY_RE = re.compile(
    r"['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s+modifies", re.I
)
MENU_BLOCK_RE = re.compile(r"\"(File/[A-Za-z][A-Za-z ]*)\"")
CONST_RE = re.compile(
    r"(?:const|static\s+readonly)\s+string\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\"([^\"]+)\""
)
SWITCH_RE = re.compile(
    r"switch\s*\(\s*action(?:\s*\.\s*ToLowerInvariant\s*\(\s*\))?\s*\)"
)
CASE_RE = re.compile(r"case\s+([A-Za-z_][A-Za-z0-9_]*|\"[^\"]+\")\s*:")
ARM_RE = re.compile(r"(?m)^[ \t]*\"([a-z][a-z0-9_]*)\"\s*=>\s*(.+)$")
CLASS_RE = re.compile(r"\b(?:class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)")
ACTION_EQ_RE = re.compile(r"action\s*==\s*\"([^\"]+)\"")
METH_RE = re.compile(
    r"(?m)^[ \t]*"
    r"(?:(?:public|private|protected|internal|static|async|override|virtual|sealed|new|unsafe|partial)\s+)+"
    r"(?:[\w.<>,\[\]?]+\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
SKIP_METHOD = {
    "if", "for", "while", "switch", "catch", "lock", "foreach", "using", "fixed",
}

# Audit cases. The extractor exits non-zero when any of these drift.
SELF_CHECK = {
    "manage_prefabs.get_info": {"ask": True, "flag": "runs_code"},
    "manage_prefabs.get_hierarchy": {"ask": True, "flag": "runs_code"},
    "manage_scene.load": {"ask": True, "flag": "runs_code"},
    "run_tests": {"ask": True, "flag": "runs_code"},
    "execute_code.execute": {"ask": True, "flag": "runs_code"},
    "manage_scene.get_hierarchy": {"ask": False, "tier": "read"},
    "read_console.get": {"ask": False, "tier": "read"},
    "create_script": {"ask": True, "flag": "writes"},
    "delete_script": {"ask": True, "flag": "deletes"},
    "manage_gameobject.create": {"ask": True, "flag": "writes"},
    "manage_gameobject.delete": {"ask": True, "flag": "deletes"},
    "generate_image.generate": {"ask": True, "flag": "sends"},
    "blender_bridge.run_python": {"ask": True, "flag": "sends"},
}


def _decorator_name(dec: ast.expr) -> str | None:
    func = dec.func if isinstance(dec, ast.Call) else dec
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _type_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _literal_strings(node: ast.expr | None) -> list[str]:
    """Action names from Annotated[Literal["a", "b"], "desc"] | None.

    Description strings and None are not actions.
    """
    if node is None:
        return []
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _literal_strings(node.left) + _literal_strings(node.right)
    if isinstance(node, ast.Constant):
        return []
    if isinstance(node, ast.Name):
        return []
    if isinstance(node, ast.Subscript):
        name = _type_name(node.value)
        sl = node.slice
        if name == "Annotated":
            if isinstance(sl, ast.Tuple) and sl.elts:
                return _literal_strings(sl.elts[0])
            return _literal_strings(sl)
        if name == "Literal":
            elts = sl.elts if isinstance(sl, ast.Tuple) else [sl]
            out = []
            for elt in elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    out.append(elt.value)
                else:
                    out.extend(_literal_strings(elt))
            return out
        return _literal_strings(sl)
    if isinstance(node, ast.Tuple):
        out = []
        for elt in node.elts:
            out.extend(_literal_strings(elt))
        return out
    return []


def _kw(call: ast.Call, name: str):
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _const_str(node: ast.expr | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _sent_actions(fn: ast.AST) -> list[str]:
    """String actions this function itself puts in a params dict.

    Nested helpers (a verify read after a create) are not the operation.
    """
    found: list[str] = []

    def walk(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(child, ast.Dict):
                for key, val in zip(child.keys, child.values):
                    if (
                        isinstance(key, ast.Constant)
                        and key.value == "action"
                        and isinstance(val, ast.Constant)
                        and isinstance(val.value, str)
                    ):
                        if val.value not in found:
                            found.append(val.value)
            walk(child)

    walk(fn)
    return found


def parse_python_tools(server_src: Path) -> list[dict]:
    tools_dir = server_src / "services" / "tools"
    found = []
    for path in sorted(tools_dir.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path.name))
        except SyntaxError as exc:
            found.append({"error": f"syntax {path.name}: {exc}"})
            continue
        for node in tree.body:
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            deco = None
            for dec in node.decorator_list:
                if _decorator_name(dec) == "mcp_for_unity_tool":
                    deco = dec
                    break
            if deco is None or not isinstance(deco, ast.Call):
                continue
            name = _const_str(_kw(deco, "name")) or node.name
            description = _const_str(_kw(deco, "description")) or ""
            if not description:
                description = ast.get_docstring(node) or ""
            unity_target = _const_str(_kw(deco, "unity_target"))
            if unity_target == "self" or unity_target is None:
                unity_target = name
            actions: list[str] = []
            params: list[str] = []
            has_action = False
            for arg in node.args.args:
                if arg.arg in ("self", "ctx"):
                    continue
                params.append(arg.arg)
                if arg.arg == "action":
                    has_action = True
                    actions = _literal_strings(arg.annotation)
            body = ast.get_source_segment(source, node) or ""
            rel = "Server/src/services/tools/" + str(path.relative_to(tools_dir))
            py_actions: list[str] = []
            if has_action and not actions:
                # action is a plain str: the module's ALL_ACTIONS list, else the literals the body compares against.
                listed = re.search(r"(?m)^ALL_ACTIONS\s*=\s*\[([^\]]*)\][ \t]*$", source)
                if listed:
                    py_actions = re.findall(r"[\"']([a-z_]+)[\"']", listed.group(1))
            found.append({
                "name": name,
                "description": description,
                "unity_target": unity_target,
                "actions": actions,
                "has_action": has_action,
                "sent_actions": [] if has_action else _sent_actions(node),
                "params": params,
                "py_file": rel,
                "body": body,
                "py_actions": py_actions,
                "module": source,
            })
    return found


def _brace_end(text: str, open_at: int) -> int:
    depth = 0
    i = open_at
    n = len(text)
    while i < n:
        c = text[i]
        if c == "@" and i + 1 < n and text[i + 1] == '"':
            i += 2
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        i += 2
                        continue
                    break
                i += 1
        elif c == '"':
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\":
                    i += 2
                    continue
                i += 1
        elif c == "'":
            i += 1
            while i < n and text[i] != "'":
                if text[i] == "\\":
                    i += 2
                    continue
                i += 1
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            nl = text.find("\n", i)
            i = n if nl < 0 else nl
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1


def _methods(text: str) -> dict[str, str]:
    """name -> body. The last method of a name in the file wins for unqualified calls."""
    found = {}
    for name, body, _pos in _method_spans(text):
        found[name] = body
    return found


def _method_spans(text: str) -> list[tuple[str, str, int]]:
    spans = []
    for match in METH_RE.finditer(text):
        name = match.group(1)
        if name in SKIP_METHOD:
            continue
        paren = match.end() - 1
        depth = 0
        i = paren
        while i < len(text):
            ch = text[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        window = text[i + 1:i + 80]
        brace_rel = window.find("{")
        if brace_rel < 0 or ";" in window[:brace_rel]:
            continue
        open_at = i + 1 + brace_rel
        end = _brace_end(text, open_at)
        spans.append((name, text[open_at:end + 1], match.start()))
    return spans


def _class_methods(text: str) -> dict[tuple[str, str], str]:
    """(class, method) -> body. A method belongs to the innermost class around it."""
    spans = []
    for decl in CLASS_RE.finditer(text):
        brace = text.find("{", decl.end(), decl.end() + 400)
        if brace < 0:
            continue
        spans.append((decl.group(1), decl.start(), _brace_end(text, brace)))
    indexed = {}
    for name, body, pos in _method_spans(text):
        owner = None
        best = -1
        for cls, start, end in spans:
            if start < pos <= end and start >= best:
                owner = cls
                best = start
        if owner:
            indexed[(owner, name)] = body
    return indexed


def _const_map(text: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in CONST_RE.finditer(text)}


def _line_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _following_block(text: str, start: int) -> str:
    window = text[start:start + 160]
    brace_rel = window.find("{")
    semi_rel = window.find(";")
    if brace_rel >= 0 and (semi_rel < 0 or brace_rel < semi_rel):
        open_at = start + brace_rel
        end = _brace_end(text, open_at)
        return text[open_at:end + 1]
    if 0 <= semi_rel < 400:
        return text[start:start + semi_rel + 1]
    return text[start:start + 800]


def _case_bodies(text: str) -> dict[str, dict]:
    """action switch cases and `action == "name"` blocks, const labels resolved."""
    consts = _const_map(text)
    bodies: dict[str, dict] = {}

    def add(name: str, chunk: str, line: int) -> None:
        slot = bodies.setdefault(name, {"text": "", "line": line})
        slot["text"] += "\n" + chunk
        if slot["line"] > line:
            slot["line"] = line

    for match in SWITCH_RE.finditer(text):
        open_at = text.find("{", match.end())
        if open_at < 0:
            continue
        end = _brace_end(text, open_at)
        block = text[open_at:end + 1]
        base = open_at
        cases = list(CASE_RE.finditer(block))
        parsed = []
        for case in cases:
            raw = case.group(1)
            if raw.startswith('"'):
                name = raw.strip('"')
            else:
                name = consts.get(raw)
            parsed.append((name, case))
        for i, (name, case) in enumerate(parsed):
            if not name:
                continue
            start = case.end()
            stop = parsed[i + 1][1].start() if i + 1 < len(parsed) else len(block)
            chunk = block[start:stop]
            # Empty cases fall through until a case that returns.
            if not re.search(r"\b(return|break|throw)\b", chunk):
                j = i + 1
                while j < len(parsed):
                    start_j = parsed[j][1].end()
                    stop_j = parsed[j + 1][1].start() if j + 1 < len(parsed) else len(block)
                    more = block[start_j:stop_j]
                    chunk += more
                    if re.search(r"\b(return|break|throw)\b", more):
                        break
                    j += 1
            add(name, chunk, _line_at(text, base + case.start()))
    for match in ACTION_EQ_RE.finditer(text):
        add(match.group(1), _following_block(text, match.end()), _line_at(text, match.start()))
    for match in ARM_RE.finditer(text):
        add(match.group(1), match.group(2), _line_at(text, match.start()))
    return bodies


def _flags_in(text: str) -> set[str]:
    flags = set()
    if RUNS_RE.search(text):
        flags.add("runs_code")
    if WRITES_RE.search(text):
        flags.add("writes")
    if DELETES_RE.search(text):
        flags.add("deletes")
    if SENDS_RE.search(text):
        flags.add("sends")
    return flags


def _expand(body: str, methods: dict[str, str], class_index: dict[tuple[str, str], str]) -> tuple[str, set]:
    """Inline same-file methods and Class.Method calls.

    A method inlined from class C resolves its own bare calls against C, not
    against the tool file. Unity APIs stay in the text for the flag regex.
    """
    parts = [body]
    seen = set()
    # depth 0 is the case. Two hops reach Class.Method and the helper it calls.
    queue = [(body, None, 0)]
    while queue and len(seen) < 40:
        chunk, owner, depth = queue.pop(0)
        if depth >= 3:
            continue
        for name in re.findall(r"(?<!\.)\b([A-Z][A-Za-z0-9_]+)\s*\(", chunk):
            extra = None
            next_owner = owner
            if owner and (owner, name) in class_index:
                key = (owner, name)
                extra = class_index[key]
            else:
                key = ("file", name)
                extra = methods.get(name)
                next_owner = None
            if not extra or key in seen:
                continue
            seen.add(key)
            parts.append(extra)
            queue.append((extra, next_owner, depth + 1))
        for cls, name in re.findall(r"\b([A-Z][A-Za-z0-9_]+)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", chunk):
            key = (cls, name)
            if key in seen or key not in class_index:
                continue
            seen.add(key)
            extra = class_index[key]
            parts.append(extra)
            queue.append((extra, cls, depth + 1))
    inlined = {key for key in seen if isinstance(key, tuple) and len(key) == 2 and key[0] != "file"}
    return "\n".join(parts), inlined


def parse_csharp(editor: Path) -> tuple[dict[str, dict], list[dict], list[str], dict[tuple[str, str], str]]:
    """tool name -> handler; guards; blocked menu paths; (class, method) -> body."""
    by_tool: dict[str, dict] = {}
    guards = []
    blocked: list[str] = []
    class_index: dict[tuple[str, str], str] = {}
    root = editor.parents[1]
    runtime = editor.parent / "Runtime"
    if runtime.is_dir():
        for path in sorted(runtime.rglob("*.cs")):
            class_index.update(_class_methods(path.read_text(encoding="utf-8", errors="replace")))
    for path in sorted(editor.rglob("*.cs")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(root))
        methods = _methods(text)
        class_index.update(_class_methods(text))
        attr = re.search(r'\[McpForUnityTool\(\s*"([^"]+)"', text)
        if attr:
            by_tool[attr.group(1)] = {
                "file": rel,
                "cases": _case_bodies(text),
                "methods": methods,
                "text": text,
            }
        if "_menuPathBlacklist" in text:
            block = text[text.find("_menuPathBlacklist"):text.find("_menuPathBlacklist") + 600]
            blocked.extend(MENU_BLOCK_RE.findall(block))
        for match in re.finditer(r"EditorUtility\.DisplayDialog\s*\(", text):
            line = _line_at(text, match.start())
            snippet = " ".join(text[match.start():match.start() + 180].split())
            guards.append({"kind": "dialog", "file": rel, "line": line, "text": snippet[:160]})
        for match in re.finditer(r"#if\s+(UNITY_[A-Z0-9_]+)", text):
            line = _line_at(text, match.start())
            guards.append({"kind": "version", "file": rel, "line": line, "text": match.group(0)})
        for match in re.finditer(r'return new ErrorResponse\(\s*"([^"]{0,180})"', text):
            msg = match.group(1)
            if re.search(r"cannot|not allowed|blocked|refused|not supported|Unknown action", msg, re.I):
                line = _line_at(text, match.start())
                guards.append({"kind": "refuse", "file": rel, "line": line, "text": msg})
    return by_tool, guards, sorted(set(blocked)), class_index


def parse_cli_guards(server_src: Path) -> list[dict]:
    guards = []
    cli = server_src / "cli"
    if not cli.is_dir():
        return guards
    for path in sorted(cli.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = "Server/src/cli/" + str(path.relative_to(cli))
        for match in re.finditer(r"confirm_destructive_action\s*\(|click\.confirm\s*\(", text):
            line = _line_at(text, match.start())
            snippet = " ".join(text[match.start():match.start() + 160].split())
            guards.append({"kind": "confirm", "file": rel, "line": line, "text": snippet[:160]})
    return guards


def _split_names(blob: str) -> set[str]:
    return {part.strip() for part in re.split(r"[,/]|\bor\b", blob) if part.strip()}


def _py_flags(body: str) -> set[str]:
    flags = set()
    if PY_SENDS_RE.search(body):
        flags.add("sends")
    if PY_RUNS_RE.search(body):
        flags.add("runs_code")
    if PY_WRITES_RE.search(body):
        flags.add("writes")
    return flags


# Calls that open, list, write, move, or delete a file or folder. An argument that reaches one of these is a path.
FS_CALL_RE = re.compile(
    r"\b(?:File|Directory|Path)\.[A-Za-z]+\s*\(|\bnew\s+(?:FileInfo|DirectoryInfo|FileStream|StreamWriter|StreamReader)\s*\(|"
    r"\bAssetDatabase\.[A-Za-z]+\s*\(|\bAssetImporter\.GetAtPath\s*\(|\bPrefabUtility\.[A-Za-z]+\s*\(|"
    r"\bEditorSceneManager\.(?:OpenScene|SaveScene|SaveScenes|NewScene)\s*\(|\bScreenCapture\.[A-Za-z]+\s*\(|"
    r"\bProfilerDriver\.[A-Za-z]+\s*\(|\bMemoryProfiler\.[A-Za-z]+\s*\(|\bTakeSnapshot\s*\(|"
    r"\b[A-Za-z]*Path[A-Za-z]*Utility\.[A-Za-z]+\s*\(|\bSanitize[A-Za-z]*Path\s*\(|\bAssetPathUtility\.[A-Za-z]+\s*\(|"
    r"\b(?:Load|Save)(?:Asset|Image|Texture)[A-Za-z]*\s*\(|\bImportAsset\s*\("
)
FS_ASSIGN_RE = re.compile(r"\b(?:locationPathName|logFile|outputPath|OutputPath)\s*=\s*([^,;\n]+)")
PY_FS_RE = re.compile(r"\bopen\s*\(|\bPath\s*\(|\bos\.path\.[a-z]+\s*\(|\b_split_uri\s*\(|\bshutil\.[a-z]+\s*\(")
PARAM_READ_RE = re.compile(
    r"(?:\[\s*\"([A-Za-z_][A-Za-z0-9_]*)\"\s*\]|\.(?:Get|TryGet|GetRequired)[A-Za-z]*\s*\(\s*\"([A-Za-z_][A-Za-z0-9_]*)\"|"
    r"\bCoerce[A-Za-z]*\s*\(\s*@?params\s*\[\s*\"([A-Za-z_][A-Za-z0-9_]*)\")")
ASSIGN_RE = re.compile(
    r"(?:^|[;{}(,\n])\s*(?:(string|var|[A-Za-z_][\w<>\[\],.?]*)\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(?![=>])\s*([^;,\n]+(?:\([^;]*\))?[^;,\n]*)")
# A value that stays a string (a path is a string). Object construction and component lookups do not carry a path.
STRINGISH_RE = re.compile(
    r"ToString\(\)|\.Value\b|\bPath\.|\.Replace\(|\.Trim|\.Substring\(|Sanitize|Normalize|\+\s*[\"$@]|[\"]\s*\+|"
    r"\$\"|\bstring\.|\.Get(?:String)?\(|GetRequired\(|\[\s*\"|\?\?|\bas\s+string\b")


def _norm(name: str) -> str:
    return name.replace("_", "").lower()


def _call_args(text: str, start: int) -> str:
    """The argument text of the call whose opening parenthesis is at or after start."""
    open_at = text.find("(", start)
    if open_at < 0:
        return ""
    depth = 0
    for i in range(open_at, min(len(text), open_at + 2000)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[open_at + 1:i]
    return text[open_at + 1:open_at + 2000]


def _split_top(args: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in args:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
            continue
        cur += ch
    parts.append(cur)
    return parts


def file_params(cs_text: str, py_body: str, params: list[str]) -> list[str]:
    """Parameters whose value reaches a file system call, by taint through assignments.

    A parameter is read by its JSON name (@params["x"], p.Get("x"), p.GetRequired("x")). Each variable assigned
    from an expression that holds that read, or another tainted variable, carries the parameter. A parameter is a
    path when a tainted name, or the read itself, appears inside the arguments of a file system call.
    """
    wanted = {_norm(p): p for p in params}
    found: set[str] = set()
    for text, fs_re in ((cs_text or "", FS_CALL_RE), (py_body or "", PY_FS_RE)):
        if not text:
            continue
        taint: dict[str, set[str]] = {}
        reads_by_param: dict[str, set[str]] = {}
        for match in PARAM_READ_RE.finditer(text):
            name = match.group(1) or match.group(2) or match.group(3)
            if _norm(name) in wanted:
                reads_by_param.setdefault(wanted[_norm(name)], set()).add(name)
        if text is py_body:
            for param in params:
                reads_by_param.setdefault(param, set()).add(param)
        assigns = []
        for m in ASSIGN_RE.finditer(text):
            decl, var, rhs = m.group(1), m.group(2), m.group(3)
            if var in ("if", "return", "case", "new", "else"):
                continue
            if rhs.lstrip().startswith("new ") and not rhs.lstrip().startswith("new string"):
                continue
            if text is cs_text and decl != "string" and not STRINGISH_RE.search(rhs):
                continue
            assigns.append((var, rhs))
        if text is cs_text:
            for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\.(?:Add|Insert|AddRange)\s*\(([^;]*)\)\s*;", text):
                assigns.append((m.group(1), m.group(2)))
            for m in re.finditer(r"foreach\s*\(\s*(?:var|string)\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+([^)]+)\)", text):
                assigns.append((m.group(1), m.group(2)))
        for _round in range(6):
            changed = False
            for var, rhs in assigns:
                carried: set[str] = set()
                for param, names in reads_by_param.items():
                    if any(re.search(r"[\"']" + re.escape(n) + r"[\"']", rhs) for n in names):
                        carried.add(param)
                    if text is py_body and re.search(r"\b" + re.escape(param) + r"\b", rhs):
                        carried.add(param)
                for other, ps in list(taint.items()):
                    if other != var and re.search(r"\b" + re.escape(other) + r"\b", rhs):
                        carried |= ps
                if carried - taint.get(var, set()):
                    taint.setdefault(var, set()).update(carried)
                    changed = True
            if not changed:
                break
        sinks = []
        for m in fs_re.finditer(text):
            args = _call_args(text, m.start())
            if re.match(r"File\.(?:WriteAll|AppendAll)", m.group(0)):
                args = _split_top(args)[0] if args else ""
            sinks.append(args)
        if text is cs_text:
            # A string handed to a method found by reflection goes somewhere this scan cannot see: count it.
            sinks += [_call_args(text, m.start()) for m in re.finditer(r"\.Invoke\s*\(", text)]
        sinks += [m.group(1) for m in FS_ASSIGN_RE.finditer(text)] if text is cs_text else []
        for arg in sinks:
            for param, names in reads_by_param.items():
                if text is cs_text and any(re.search(r"[\"']" + re.escape(n) + r"[\"']", arg) for n in names):
                    found.add(param)
                if text is py_body and re.search(r"\b" + re.escape(param) + r"\b", arg):
                    found.add(param)
            for var, ps in taint.items():
                if re.search(r"\b" + re.escape(var) + r"\b", arg):
                    found |= ps
    return sorted(p for p in found if p in params)


def _one_op(tool: dict, action, handler: dict, class_index: dict[tuple[str, str], str], read_named: set[str], modify_named: set[str]) -> dict:
    evidence = []
    flags = set(_py_flags(tool["body"]))
    # A Python tool that only forwards a command is not itself a send.
    # The C# handler is the source of truth for that hop.
    if "send_with_unity_instance" in tool["body"] or "async_send_command_with_retry" in tool["body"]:
        flags.discard("sends")
        flags.discard("runs_code")
    if not handler and tool.get("py_actions"):
        # Python-side actions: the module's own fetch code is the effect.
        flags |= {flag for flag in _py_flags(tool.get("module", "")) if flag == "sends"}
    known = False
    case_line = None
    expanded = ""
    origin = ""
    inlined: set = set()
    if handler and action and action in handler["cases"]:
        known = True
        case = handler["cases"][action]
        case_line = case["line"]
        origin = case["text"]
        expanded, inlined = _expand(origin, handler["methods"], class_index)
        flags |= _flags_in(expanded)
        evidence.append(f"{handler['file']}:{case_line}")
    elif handler and action and handler["cases"] and action not in handler["cases"]:
        known = False
        evidence.append(f"{handler['file']} has no case {action}")
    elif handler and not action:
        known = True
        if handler["cases"]:
            # The tool does not name an action, but the handler dispatches one.
            # That is not one read. Ask.
            known = False
            evidence.append(f"{handler['file']} dispatches actions")
        else:
            origin = handler["methods"].get("HandleCommand") or handler["text"]
            expanded, inlined = _expand(origin, handler["methods"], class_index)
            flags |= _flags_in(expanded)
            evidence.append(handler["file"])
    elif not handler:
        evidence.append(tool["py_file"])
    if action and action in read_named:
        evidence.append("description read-only")
    if action and action in modify_named:
        evidence.append("description modifying")
    # batch_execute carries a list of other commands. The C# dispatcher is the flag.
    # If that scan missed, still ask: an unnamed command list is not a read.
    if tool["name"] == "batch_execute" and "commands" in tool["params"] and not flags:
        flags.add("runs_code")
        evidence.append("command list")
    # A call into an editor class whose method we could not see is not a read.
    if origin and not flags and action not in read_named:
        known_classes = {cls for cls, _name in class_index}
        for cls, name in re.findall(r"\b([A-Z][A-Za-z0-9_]+)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", origin):
            if cls in known_classes and (cls, name) not in class_index:
                known = False
                evidence.append(f"unresolved {cls}.{name}")
                break
            if (cls, name) in class_index and (cls, name) not in inlined:
                known = False
                evidence.append(f"not inlined {cls}.{name}")
                break
    if flags:
        tier = "effect"
    elif action in modify_named:
        tier = "effect"
    elif known and action in read_named and action not in modify_named:
        tier = "read"
    elif known and not flags and action not in modify_named and (
        action in read_named or not read_named or action is None
    ):
        # A resolved body with no effect call, and the description does not call it modifying.
        tier = "read"
    elif known and action in read_named and not flags and not modify_named:
        tier = "read"
    else:
        tier = "unknown"
    if flags and tier == "read":
        tier = "effect"
    ask = tier != "read"
    key = tool["name"] if not action else f"{tool['name']}.{action}"
    preamble = ""
    if handler:
        head = handler["methods"].get("HandleCommand") or ""
        cut = SWITCH_RE.search(head)
        preamble = head[:cut.start()] if cut else head
        preamble, _seen = _expand(preamble, handler["methods"], class_index)
    paths = file_params(preamble + "\n" + expanded, tool["body"], [p for p in tool["params"] if p != "action"])
    return {
        "key": key,
        "tool": tool["name"],
        "action": action,
        "action_param": bool(tool["has_action"]),
        "params": [p for p in tool["params"] if p != "action"],
        "flags": sorted(flags),
        "tier": tier,
        "ask": ask,
        "file_params": paths,
        "evidence": evidence,
        "py_file": tool["py_file"],
        "unity_target": tool["unity_target"],
    }


def classify(py_tools: list[dict], csharp: dict[str, dict], class_index: dict[tuple[str, str], str]) -> list[dict]:
    ops = []
    for tool in py_tools:
        if "error" in tool:
            continue
        desc = tool["description"]
        read_named = _split_names(READ_ONLY_RE.search(desc).group(1)) if READ_ONLY_RE.search(desc) else set()
        modify_named = _split_names(MODIFY_RE.search(desc).group(1)) if MODIFY_RE.search(desc) else set()
        read_named |= {m.group(1) for m in INLINE_READ_RE.finditer(desc)}
        modify_named |= {m.group(1) for m in INLINE_MODIFY_RE.finditer(desc)}
        handler = csharp.get(tool["unity_target"]) or csharp.get(tool["name"]) or {}
        if tool.get("py_actions") and not set(tool["py_actions"]) & set(handler.get("cases") or {}):
            # The Python tool decides its own actions (unity_docs fetches pages itself). A C# handler with
            # other case names is not this tool's handler.
            handler = {}
            tool = dict(tool, unity_target=tool["name"])
            actions = tool["py_actions"]
        elif tool["has_action"] and tool["actions"]:
            actions = tool["actions"]
        elif tool["has_action"] and handler and handler.get("cases"):
            actions = sorted(handler["cases"])
        elif tool["sent_actions"]:
            actions = tool["sent_actions"]
        else:
            actions = [None]
        for action in actions:
            ops.append(_one_op(tool, action, handler, class_index, read_named, modify_named))
    return ops


def resources_of(server_src: Path) -> list[dict]:
    found = []
    root = server_src / "services" / "resources"
    if not root.is_dir():
        return found
    for path in sorted(root.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r'["\'](mcpforunity://[^"\']+)["\']', text):
            found.append({"uri": match.group(1), "file": "Server/src/services/resources/" + path.name})
    seen = {}
    for row in found:
        seen.setdefault(row["uri"], row["file"])
    return [{"uri": uri, "file": file} for uri, file in sorted(seen.items())]


def assign(ops: list[dict]) -> tuple[dict, list[str], list[str]]:
    tool_to_bundle = {}
    for bundle, names in BUNDLES.items():
        for name in names:
            if name in tool_to_bundle:
                raise SystemExit(f"{name} is in two bundles")
            tool_to_bundle[name] = bundle
    bundles: dict[str, dict] = {}
    missing = []
    for op in ops:
        bundle = tool_to_bundle.get(op["tool"])
        if bundle is None:
            missing.append(op["tool"])
            continue
        slot = bundles.setdefault(bundle, {"first": FIRST_SENTENCE[bundle], "ops": {}})
        slot["ops"][op["key"]] = {
            "upstream_tool": op["tool"],
            "unity_target": op["unity_target"],
            "action": op["action"],
            "action_param": op["action_param"],
            "params": op["params"],
            "flags": op["flags"],
            "tier": op["tier"],
            "ask": op["ask"],
            "file_params": op["file_params"],
            "evidence": op["evidence"],
            "effects": op.get("effects", []),
            "entry": op.get("entry", ""),
        }
    assigned = set(tool_to_bundle)
    present = {op["tool"] for op in ops}
    unused = sorted(assigned - present)
    return bundles, sorted(set(missing)), unused


def _self_check(ops: list[dict]) -> list[str]:
    by_key = {op["key"]: op for op in ops}
    by_tool: dict[str, list[dict]] = {}
    for op in ops:
        by_tool.setdefault(op["tool"], []).append(op)
    problems = []
    for key, expect in SELF_CHECK.items():
        op = by_key.get(key)
        if op is None and "." not in key:
            rows = by_tool.get(key) or []
            op = rows[0] if len(rows) == 1 else None
            if op is None and rows:
                problems.append(f"{key}: expected one op, found {[row['key'] for row in rows]}")
                continue
        if op is None:
            problems.append(f"{key}: missing")
            continue
        if op["ask"] != expect["ask"]:
            problems.append(f"{key}: ask={op['ask']} want {expect['ask']} flags={op['flags']} tier={op['tier']}")
        if expect.get("flag") and expect["flag"] not in op["flags"]:
            problems.append(f"{key}: flags={op['flags']} missing {expect['flag']}")
        if expect.get("tier") and op["tier"] != expect["tier"]:
            problems.append(f"{key}: tier={op['tier']} want {expect['tier']}")
    return problems


def _reached(uri: str) -> str:
    if "prefab" in uri:
        return "unity_asset"
    if uri.endswith("/tests") or "/tests/" in uri:
        return "unity_tests"
    if "custom-tools" in uri:
        return "unity_code"
    if "tool-groups" in uri:
        return "unity_editor"
    if "script" in uri:
        return "unity_script"
    if "scene" in uri:
        return "unity_scene"
    if "editor" in uri or "console" in uri or "instances" in uri:
        return "unity_editor"
    return "unity_editor"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract_unity_ops.py /path/to/unity-mcp", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    server = root / "Server" / "src"
    editor = root / "MCPForUnity" / "Editor"
    if not server.is_dir() or not editor.is_dir():
        print("not a unity-mcp tree", file=sys.stderr)
        return 2
    for bundle, sentence in FIRST_SENTENCE.items():
        if len(sentence) > 60 or sentence.startswith("Read-only"):
            print(f"first sentence too long or shaped wrong: {bundle} ({len(sentence)})", file=sys.stderr)
            return 1
    py_tools = parse_python_tools(server)
    errors = [row["error"] for row in py_tools if "error" in row]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    csharp, cs_guards, blocked, class_index = parse_csharp(editor)
    guards = cs_guards + parse_cli_guards(server)
    ops = classify([row for row in py_tools if "error" not in row], csharp, class_index)
    found = effects_for(root, ops, csharp, {row["name"]: row for row in py_tools if "error" not in row})
    for op in ops:
        row = found.get(op["key"]) or {}
        op["effects"] = compact_effects(row.get("effects", []))
        op["entry"] = row.get("entry", "")
    problems = _self_check(ops) + effects_self_check(ops)
    if problems:
        print("self-check failed:", file=sys.stderr)
        print("\n".join(problems), file=sys.stderr)
        return 1
    bundles, missing, unused = assign(ops)
    if missing or unused:
        print("missing bundles: " + ", ".join(missing), file=sys.stderr)
        print("unused bundle names: " + ", ".join(unused), file=sys.stderr)
        return 1
    resource_rows = []
    for row in resources_of(server):
        resource_rows.append({
            "uri": row["uri"],
            "file": row["file"],
            "reached_by": _reached(row["uri"]),
        })
    out = {
        "upstream": "10.3.0",
        "bundles": bundles,
        "blocked_menus": blocked,
        "guards": guards,
        "resources": resource_rows,
        "unity_rules": UNITY_RULES,
        "effect_words": {kind: words for kind, (_rx, words) in KINDS.items()},
        "counts": {
            "tools": len({op["tool"] for op in ops}),
            "ops": len(ops),
            "ask": sum(1 for op in ops if op["ask"]),
            "read": sum(1 for op in ops if not op["ask"]),
            "unknown": sum(1 for op in ops if op["tier"] == "unknown"),
            "bundles": len(bundles) + 2,
        },
    }
    blob = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    if "/Us" + "ers/" in blob or "takeshi" + "tgal" in blob or "ship" + "/" in blob:
        print("output contains a local path", file=sys.stderr)
        return 1
    dest_json = Path(__file__).resolve().parents[1] / "bridge" / "ops_table.json"
    dest_md = Path(__file__).resolve().parent / "ops_table.md"
    dest_json.write_text(blob + "\n", encoding="utf-8")
    lines = [
        "# Upstream operations",
        "",
        f"Upstream {out['upstream']}. Tools {out['counts']['tools']}. "
        f"Ops {out['counts']['ops']}. Ask {out['counts']['ask']}. "
        f"Read {out['counts']['read']}. Unknown {out['counts']['unknown']}.",
        "",
        "Blocked menu paths taken from the editor handler: " + ", ".join(blocked or ["(none)"]),
        "",
        "| bundle | op | flags | ask | evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for bundle, slot in bundles.items():
        for key, op in slot["ops"].items():
            lines.append(
                f"| {bundle} | {key} | {', '.join(op['flags']) or '-'} | {op['ask']} | {'; '.join(op['evidence']) or '-'} |"
            )
    lines.append("")
    lines.append(f"Guards listed: {len(guards)}. Resources listed: {len(resource_rows)}.")
    lines.append("")
    lines.append("plan_batch and apply_plan are not upstream tools. plan_batch returns the text. apply_plan runs that plan once.")
    dest_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (Path(__file__).resolve().parent / "side_effects.md").write_text(table_markdown(bundles), encoding="utf-8")
    print(json.dumps(out["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
