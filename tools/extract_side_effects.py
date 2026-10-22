#!/usr/bin/env python3
"""What each MCP for Unity operation does inside, read from the upstream C# source.

The plan text, the second question, and the state fingerprint are decided from this table, not from the
operation's name. For every operation the extractor starts at the code the editor runs for that action and
follows the calls it makes through the whole MCPForUnity package: Class.Method calls, calls inside the same
class and its partial parts, service locator properties (MCPServiceLocator.Tests -> TestRunnerService), interface
calls to their implementing classes, constructors, and method groups handed to editor events. Each call to a
Unity API with an effect (a save, a delete, a file write, a compile, entering play mode, loading or creating
objects, a network send) is an effect site. A site records:

  kind    the effect (see KINDS)
  api     the Unity call, as written
  at      file:line of the call
  via     the chain of methods from the operation to the call
  when    the if conditions around the call along that chain; when_params names the operation's own arguments
          in them (overwrite, generate_preview), with polarity, so the bridge can tell whether the effect
          applies to the arguments of a given step

Usage:
  python3 tools/extract_side_effects.py /path/to/unity-mcp     (prints a summary; extract_unity_ops.py calls effects_for)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# kind -> (regex over C# text, words for the plan)
KINDS: dict[str, tuple[str, str]] = {
    "save_scene": (
        r"EditorSceneManager\.(?:SaveScene|SaveScenes|SaveOpenScenes|SaveCurrentModifiedScenesIfUserWantsTo|"
        r"SaveModifiedScenesIfUserWantsTo)\s*\(",
        "saves scene files to disk",
    ),
    "save_assets": (
        r"AssetDatabase\.(?:SaveAssets|SaveAssetIfDirty|ForceReserializeAssets)\s*\(",
        "writes every changed asset to disk",
    ),
    "delete_file": (
        r"AssetDatabase\.(?:DeleteAsset|DeleteAssets|MoveAssetToTrash|MoveAssetsToTrash)\s*\(|"
        r"FileUtil\.DeleteFileOrDirectory\s*\(|\bFile\.Delete\s*\(|\bDirectory\.Delete\s*\(",
        "deletes files",
    ),
    "write_file": (
        r"\bFile\.(?:WriteAll\w*|AppendAll\w*|Copy|Move|Create|Replace)\s*\(|"
        r"AssetDatabase\.(?:CreateAsset|CopyAsset|MoveAsset|RenameAsset|CreateFolder|AddObjectToAsset)\s*\(|"
        r"PrefabUtility\.(?:SaveAsPrefabAsset\w*|ApplyPrefabInstance|SavePrefabAsset|ReplacePrefab)\s*\(|"
        r"\.EncodeToPNG\s*\(|ScreenCapture\.CaptureScreenshot\s*\(",
        "writes files",
    ),
    "scene_switch": (
        r"EditorSceneManager\.(?:NewScene|OpenScene|CloseScene)\s*\(",
        "opens, closes, or replaces the open scenes",
    ),
    "import_compile": (
        r"AssetDatabase\.(?:Refresh|ImportAsset)\s*\(|CompilationPipeline\.RequestScriptCompilation\s*\(|"
        r"EditorUtility\.RequestScriptReload\s*\(",
        "imports assets; a changed script recompiles and editor scripts run after the reload",
    ),
    "enter_play": (
        r"EditorApplication\.EnterPlaymode\s*\(|EditorApplication\.isPlaying\s*=\s*true",
        "enters play mode: the scene's scripts run",
    ),
    "exit_play": (
        r"EditorApplication\.ExitPlaymode\s*\(|EditorApplication\.isPlaying\s*=\s*false",
        "leaves play mode: changes made during play are dropped",
    ),
    "run_tests": (
        r"TestRunnerApi\b|new\s+ExecutionSettings\s*\(",
        "runs the project's tests (project code)",
    ),
    "compile_run": (
        r"CompileAndExecute|CSharpCodeProvider|CodeDomProvider|RoslynCompiler|\bAssembly\.Load\w*\s*\(",
        "compiles C# it was given and runs it with the editor's full access",
    ),
    "menu_item": (
        r"EditorApplication\.ExecuteMenuItem\s*\(",
        "runs an editor menu command (that command decides what changes)",
    ),
    "reflection": (
        r"MethodInfo\b[^;\n]*\.Invoke\s*\(|\bmethod\w*\.Invoke\s*\(|Activator\.CreateInstance\s*\(",
        "calls a method or constructor found by reflection",
    ),
    "load_asset": (
        r"AssetDatabase\.(?:LoadAssetAtPath|LoadMainAssetAtPath|LoadAllAssetsAtPath|"
        r"LoadAllAssetRepresentationsAtPath)\b|PrefabUtility\.LoadPrefabContents\s*\(|Resources\.Load\w*\s*\(|"
        r"AssetPreview\.GetAssetPreview\s*\(",
        "loads assets: their deserialization, OnEnable, and OnValidate code runs",
    ),
    "instantiate": (
        r"PrefabUtility\.InstantiatePrefab\s*\(|\bObject\.Instantiate\s*[<(]|(?<![\w.])Instantiate\s*[<(]|"
        r"\.AddComponent\s*[<(]|ObjectFactory\.(?:AddComponent|CreateGameObject)\s*[<(]|"
        r"GameObject\.CreatePrimitive\s*\(|Undo\.AddComponent\s*[<(]",
        "creates objects or components: their Reset, OnValidate, and [ExecuteAlways] code runs",
    ),
    "set_values": (
        r"\.ApplyModifiedProperties\w*\s*\(|PropertyInfo\b[^;\n]*\.SetValue\s*\(|\bprop\w*\.SetValue\s*\(",
        "sets serialized values or properties: OnValidate or a property setter runs",
    ),
    "scene_edit": (
        r"Undo\.RecordObjects?\s*\(|Undo\.RegisterCompleteObjectUndo\s*\(|Undo\.SetTransformParent\s*\(|"
        r"EditorSceneManager\.MarkSceneDirty\s*\(|EditorUtility\.SetDirty\s*\(|\.SetActive\s*\(|\.SetParent\s*\(|"
        r"\.(?:localPosition|position|localRotation|rotation|localScale|eulerAngles|localEulerAngles)\s*=(?!=)",
        "changes objects in memory (a scene object or an asset; they then have unsaved changes)",
    ),
    "simulate": (
        r"Physics2?D?\.Simulate\s*\(|PhysicsScene2?D?\b[^;\n]*\.Simulate\s*\(",
        "steps physics: rigidbodies move and collision and trigger code runs",
    ),
    "destroy_object": (
        r"\bObject\.DestroyImmediate\s*\(|(?<![\w.])DestroyImmediate\s*\(|Undo\.DestroyObjectImmediate\s*\(",
        "destroys objects",
    ),
    "send": (
        r"\bUnityWebRequest\b|\bHttpClient\b|\bWebRequest\.|\bTcpClient\b|\bClientWebSocket\b|"
        r"\bClient\.(?:Add|AddAndRemove|Remove|Search|SearchAll|Embed|Resolve)\s*\(|\bProcess\.Start\s*\(",
        "sends data off the editor or starts a process",
    ),
    "project_settings": (
        r"PlayerSettings\.\w+\s*=(?!=)|PlayerSettings\.Set\w+\s*\(|EditorBuildSettings\.scenes\s*=(?!=)|"
        r"EditorUserBuildSettings\.\w+\s*=(?!=)|EditorUserBuildSettings\.SwitchActiveBuildTarget\w*\s*\(|"
        r"QualitySettings\.\w+\s*=(?!=)|QualitySettings\.SetQualityLevel\s*\(|"
        r"InternalEditorUtility\.(?:AddTag|RemoveTag)\s*\(|tagManager\b|TagManager\.asset",
        "changes project settings files",
    ),
    "build_player": (
        r"BuildPipeline\.BuildPlayer\s*\(",
        "builds a player",
    ),
    "editor_prefs": (
        r"EditorPrefs\.(?:Set\w+|Delete\w*)\s*\(",
        "changes editor preferences",
    ),
    "undo_redo": (
        r"Undo\.(?:PerformUndo|PerformRedo|ClearAll)\s*\(",
        "undoes or redoes editor actions",
    ),
}
KIND_RE = {kind: re.compile(rx) for kind, (rx, _words) in KINDS.items()}
# An object upstream made in the same call and destroys again (the new GameObject when a later step of the call
# fails, a preview texture, a temporary renderer): the first argument names it. Destroying the caller's object
# (targetGo, component, componentToRemove) is not scratch.
SCRATCH_OBJECT = re.compile(r"(?i)^(?:new\w*|temp\w*|tmp\w*|readable\w*|tex|downscaled\w*|\w*preview\w*|instance|go|"
                            r"clone\w*)$")
# A file upstream makes for itself and removes (a temp copy, a backup, a marker, a compiled assembly): the first
# argument of the delete names it. Such a delete is not a delete of the user's file.
SCRATCH_ARG = re.compile(r"(?i)^(?:tmp\w*|temp\w*|\w*backup\w*|bak|\w*marker\w*|response\w*|output\w*assembly\w*|"
                         r"pid\w*|status\w*)$")
KIND_WORDS = {kind: words for kind, (_rx, words) in KINDS.items()}

# What Unity itself does with a script a plan writes. These are Unity's rules, not MCP for Unity's code, so they
# are listed here with the page that states them, and the bridge applies them to the text a step writes.
UNITY_RULES = {
    "editor_autorun": {
        "pattern": (r"\[\s*(?:UnityEditor\.)?(?:Callbacks\.)?(?:InitializeOnLoad|InitializeOnLoadMethod|"
                    r"DidReloadScripts|PostProcessBuild|PostProcessScene|OnOpenAsset)(?:Attribute)?\b|"
                    r":\s*(?:UnityEditor\.)?(?:AssetPostprocessor|AssetModificationProcessor)\b|"
                    r"\bclass\s+\w+\s*:\s*[^{]*\b(?:AssetPostprocessor|AssetModificationProcessor)\b"),
        "words": "Unity runs this code by itself in the editor, with the editor's full access, after the compile "
                 "(no menu, play mode, or test run is needed)",
        "source": "Unity Manual 'Running Editor script code on launch' ([InitializeOnLoad], [InitializeOnLoadMethod]); "
                  "ScriptReference Callbacks.DidReloadScripts, AssetPostprocessor, AssetModificationProcessor",
    },
    "editor_folder": {
        "pattern": r"(?i)(?:^|/)Editor/",
        "words": "an editor script: it can use the whole UnityEditor API with the editor's full access when "
                 "something calls it (a menu, the test runner)",
        "source": "Unity Manual 'Special folder names' (Editor)",
    },
    "script_ext": [".cs", ".asmdef", ".asmref", ".rsp"],
}

# Python side: the tool itself sends (unity_docs fetches docs.unity3d.com).
PY_SEND_RE = re.compile(r"urlopen|httpx\.|requests\.(?:get|post|put)|aiohttp|urllib\.request|docs\.unity3d\.com")

CLASS_DECL_RE = re.compile(
    r"\b(?:class|struct|interface)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*<[^>{]*>)?\s*(?::\s*([^{]+))?\{"
)
METH_RE = re.compile(
    r"(?m)^[ \t]*"
    r"(?:\[[^\]\n]*\]\s*)*"
    r"(?:(?:public|private|protected|internal|static|async|override|virtual|sealed|new|unsafe|partial|extern)\s+)*"
    r"(?:[\w.<>,\[\]?]+(?:\s*<[^>()]*>)?\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>()]*>)?\s*\("
)
NOT_METHODS = {
    "if", "for", "while", "switch", "catch", "lock", "foreach", "using", "fixed", "return", "new", "throw",
    "nameof", "typeof", "sizeof", "default", "when", "get", "set", "base", "this", "await", "else",
}
# Method names too common to resolve by name alone on an untyped receiver.
COMMON = {
    "Add", "Remove", "Get", "Set", "Contains", "ToString", "Equals", "Dispose", "Clear", "Find", "Parse",
    "TryParse", "Create", "Execute", "Run", "Start", "Stop", "Update", "Load", "Save", "Apply", "Count", "Any",
    "Where", "Select", "First", "FirstOrDefault", "ToList", "ToArray", "Invoke", "GetValue", "SetValue",
    "TryGetValue", "ContainsKey", "Append", "AppendLine", "Write", "WriteLine", "Read", "Close", "Open", "Value",
    "ToObject", "Split", "Trim", "Replace", "Substring", "StartsWith", "EndsWith", "IndexOf", "Format", "Join",
    "GetComponent", "AddComponent", "Log", "Warn", "Error", "Info", "Debug", "Handle", "HandleCommand",
}


def _brace_end(text: str, open_at: int) -> int:
    """Index of the brace that closes the one at open_at; skips strings, chars, and comments."""
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
        elif c == "$" and i + 1 < n and text[i + 1] == '"':
            i += 2
            while i < n and text[i] != '"':
                if text[i] == "\\":
                    i += 2
                    continue
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


def _paren_end(text: str, open_at: int) -> int:
    depth = 0
    for i in range(open_at, min(len(text), open_at + 4000)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _strip_comments(text: str) -> str:
    """Comments become spaces (offsets and line numbers stay), so a commented-out call is not an effect."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '"' or (c in "@$" and i + 1 < n and text[i + 1] == '"'):
            j = i + (2 if c in "@$" else 1)
            verbatim = c == "@"
            while j < n:
                if text[j] == "\\" and not verbatim:
                    j += 2
                    continue
                if text[j] == '"':
                    if verbatim and j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            i = j + 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


class Method:
    __slots__ = ("cls", "name", "file", "start", "body_at", "body", "text")

    def __init__(self, cls, name, file, start, body_at, body, text):
        self.cls, self.name, self.file, self.start = cls, name, file, start
        self.body_at, self.body, self.text = body_at, body, text

    @property
    def line(self) -> int:
        return self.text.count("\n", 0, self.start) + 1


class Index:
    """Every class, method, base type, and service property of the C# package."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.methods: dict[tuple[str, str], list[Method]] = {}
        self.by_name: dict[str, list[Method]] = {}
        self.bases: dict[str, set[str]] = {}
        self.implementers: dict[str, set[str]] = {}
        self.props: dict[tuple[str, str], set[str]] = {}
        self.field_types: dict[tuple[str, str], str] = {}
        self.files: dict[str, str] = {}
        self.classes: set[str] = set()
        editor = root / "MCPForUnity" / "Editor"
        runtime = root / "MCPForUnity" / "Runtime"
        for folder in (editor, runtime):
            if not folder.is_dir():
                continue
            for path in sorted(folder.rglob("*.cs")):
                rel = str(path.relative_to(root))
                text = _strip_comments(path.read_text(encoding="utf-8", errors="replace"))
                self.files[rel] = text
                self._index_file(rel, text)

    def _index_file(self, rel: str, text: str) -> None:
        spans = []
        for decl in CLASS_DECL_RE.finditer(text):
            name = decl.group(1)
            open_at = decl.end() - 1
            spans.append((name, decl.start(), _brace_end(text, open_at)))
            self.classes.add(name)
            for base in (decl.group(2) or "").split(","):
                base = re.sub(r"<.*", "", base.strip()).split(".")[-1].strip()
                base = re.sub(r"\bwhere\b.*", "", base).strip()
                if base:
                    self.bases.setdefault(name, set()).add(base)
                    self.implementers.setdefault(base, set()).add(name)

        def owner_of(pos: int) -> str | None:
            best, owner = -1, None
            for cls, start, end in spans:
                if start < pos <= end and start > best:
                    best, owner = start, cls
            return owner

        for match in METH_RE.finditer(text):
            name = match.group(1)
            if name in NOT_METHODS:
                continue
            paren = match.end() - 1
            close = _paren_end(text, paren)
            if close < 0:
                continue
            after = text[close + 1:close + 200]
            m_body = re.match(r"\s*(?:where\s[^{;=]*)?(\{|=>)", after)
            if not m_body:
                continue
            head = text[match.start():paren]
            # a call statement (x = Foo(...) {) is not a declaration: a declaration has a type or modifier before the name
            if not re.search(r"(?:^|\s)[\w.<>\[\],?]+\s+" + re.escape(name) + r"\s*(?:<[^>()]*>)?\s*$", head) \
                    and not re.match(r"\s*(?:public|private|protected|internal|static)\b", head) \
                    and not (owner_of(match.start()) == name):
                continue
            if re.search(r"[=(,]\s*$", text[max(0, match.start() - 3):match.start()]):
                continue
            if m_body.group(1) == "{":
                open_at = close + 1 + m_body.start(1)
                end = _brace_end(text, open_at)
                body = text[open_at:end + 1]
                body_at = open_at
            else:
                start = close + 1 + m_body.end(1)
                end = text.find(";", start)
                body = text[start:end + 1]
                body_at = start
            owner = owner_of(match.start())
            if owner is None:
                continue
            method = Method(owner, name, rel, match.start(), body_at, body, text)
            self.methods.setdefault((owner, name), []).append(method)
            self.by_name.setdefault(name, []).append(method)
        # static IFoo Name => _x ??= new Foo();   static Foo Name { get; } = new Foo();
        for match in re.finditer(
                r"\bstatic\s+([A-Za-z_][\w.<>]*)\s+([A-Z][A-Za-z0-9_]*)\s*(?:=>|\{[^}]*\}\s*=)\s*[^;]*?new\s+([A-Za-z_]\w*)",
                text):
            owner = owner_of(match.start())
            if owner:
                self.props.setdefault((owner, match.group(2)), set()).update({match.group(3), match.group(1)})
        # fields and locals with a declared type: Foo x = ... / private Foo _x; / var x = new Foo(
        for match in re.finditer(r"\b([A-Z][A-Za-z0-9_]*)(?:<[^>()]*>)?\s+([a-z_][A-Za-z0-9_]*)\s*(?:[=;),])", text):
            owner = owner_of(match.start())
            if owner and match.group(1) not in ("Task", "List", "Dictionary", "HashSet", "JObject", "JToken"):
                self.field_types.setdefault((owner, match.group(2)), match.group(1))
        for match in re.finditer(r"\bvar\s+([a-z_][A-Za-z0-9_]*)\s*=\s*new\s+([A-Z][A-Za-z0-9_]*)", text):
            owner = owner_of(match.start())
            if owner:
                self.field_types.setdefault((owner, match.group(1)), match.group(2))

    def in_class(self, cls: str, name: str) -> list[Method]:
        """Methods named name on cls, its partial parts, and its base classes."""
        found = list(self.methods.get((cls, name), []))
        seen = {cls}
        queue = list(self.bases.get(cls, ()))
        while queue and not found:
            base = queue.pop(0)
            if base in seen:
                continue
            seen.add(base)
            found = list(self.methods.get((base, name), []))
            queue.extend(self.bases.get(base, ()))
        return found

    def on_type(self, type_name: str, name: str) -> list[Method]:
        """A call on a type: the type itself, or every class that implements the interface."""
        found = self.in_class(type_name, name)
        if found:
            return found
        out = []
        for impl in sorted(self.implementers.get(type_name, ())):
            out.extend(self.in_class(impl, name))
        return out


CALL_RE = re.compile(
    r"(?:\b([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*([A-Z][A-Za-z0-9_]*)\s*(?:<[^>()]*>)?\s*\(|"
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\?)?\.\s*([A-Z][A-Za-z0-9_]*)\s*(?:<[^>()]*>)?\s*\(|"
    r"(?<![\w.])([A-Z][A-Za-z0-9_]*)\s*(?:<[^>()]*>)?\s*\(|"
    r"\bnew\s+([A-Z][A-Za-z0-9_]*)\s*(?:<[^>()]*>)?\s*[({]|"
    r"\+=\s*([A-Z][A-Za-z0-9_]*)\s*;)"
)


def _calls(index: Index, method_cls: str | None, chunk: str) -> list[tuple[int, list[Method]]]:
    """(offset in chunk, the project methods that call can reach)."""
    out = []
    for m in CALL_RE.finditer(chunk):
        targets: list[Method] = []
        if m.group(3):
            a, b, name = m.group(1), m.group(2), m.group(3)
            types = index.props.get((a, b)) or ({index.field_types.get((a, b))} - {None})
            for type_name in sorted(types):
                targets.extend(index.on_type(type_name, name))
            if not targets and a in index.classes:
                targets = []
        elif m.group(5):
            recv, name = m.group(4), m.group(5)
            if recv in ("this", "base") and method_cls:
                targets = index.in_class(method_cls, name)
            elif recv in index.classes:
                targets = index.on_type(recv, name)
            else:
                types = set()
                if method_cls and (method_cls, recv) in index.field_types:
                    types.add(index.field_types[(method_cls, recv)])
                if method_cls and (method_cls, recv) in index.props:
                    types |= index.props[(method_cls, recv)]
                for type_name in sorted(types):
                    targets.extend(index.on_type(type_name, name))
                if not targets and recv[:1].islower() and name not in COMMON:
                    cands = index.by_name.get(name, [])
                    owners = {c.cls for c in cands}
                    if 1 <= len(owners) <= 2 and len(name) >= 6:
                        targets = list(cands)
        elif m.group(6):
            name = m.group(6)
            if method_cls:
                targets = index.in_class(method_cls, name)
            if not targets and name not in COMMON and len(name) >= 8:
                cands = index.by_name.get(name, [])
                if len({c.cls for c in cands}) == 1:
                    targets = list(cands)
        elif m.group(7):
            name = m.group(7)
            targets = index.in_class(name, name)
        elif m.group(8):
            name = m.group(8)
            if method_cls:
                targets = index.in_class(method_cls, name)
        if targets:
            out.append((m.start(), targets))
    return out


def _conditions_at(text: str, pos: int, lo: int, hi: int) -> list[str]:
    """if conditions of the blocks around pos, between lo and hi (one method body). else blocks give not (cond)."""
    conds = []
    for m in re.finditer(r"\b(else\s+)?if\s*\(", text[lo:hi]):
        start = lo + m.end() - 1
        close = _paren_end(text, start)
        if close < 0 or close > pos:
            continue
        cond = " ".join(text[start + 1:close].split())
        rest = text[close + 1:close + 3]
        j = close + 1
        while j < hi and text[j] in " \t\r\n":
            j += 1
        if j < hi and text[j] == "{":
            end = _brace_end(text, j)
        else:
            end = text.find(";", j)
        if close < pos <= end:
            conds.append(cond)
            continue
        # else branch
        k = end + 1
        while k < hi and text[k] in " \t\r\n":
            k += 1
        if text.startswith("else", k) and not re.match(r"else\s+if\b", text[k:k + 12]):
            k += 4
            while k < hi and text[k] in " \t\r\n":
                k += 1
            if k < hi and text[k] == "{":
                e2 = _brace_end(text, k)
            else:
                e2 = text.find(";", k)
            if k <= pos <= e2:
                conds.append("not (" + cond + ")")
        del rest
    return conds


def _norm(name: str) -> str:
    return name.replace("_", "").lower()


def _when_params(conds: list[str], params: list[str], aliases: dict[str, str]) -> list[dict]:
    """The operation's own arguments named in the conditions, and whether the effect needs them true or false."""
    wanted = {_norm(p): p for p in params}
    out = []
    for cond in conds:
        negated_block = cond.startswith("not (")
        inner = cond[5:-1] if negated_block else cond
        if "||" in inner:
            continue
        for part in inner.split("&&"):
            part = part.strip()
            while part.startswith("(") and part.endswith(")") and _paren_end(part, 0) == len(part) - 1:
                part = part[1:-1].strip()
            eq = (re.fullmatch(r"(!)?\s*string\.Equals\(\s*([A-Za-z_]\w*)\s*,\s*\"([^\"]*)\"[^)]*\)", part)
                  or re.fullmatch(r"()([A-Za-z_]\w*)\s*==\s*\"([^\"]*)\"", part)
                  # an enum the tool parsed from the argument: mode == TestMode.PlayMode
                  or re.fullmatch(r"()([A-Za-z_]\w*)\s*==\s*[A-Z]\w*\.([A-Za-z_]\w*)", part))
            if eq and _norm(aliases.get(eq.group(2), eq.group(2))) in wanted:
                out.append({"param": wanted[_norm(aliases.get(eq.group(2), eq.group(2)))],
                            "truthy": not (bool(eq.group(1)) ^ negated_block), "equals": eq.group(3), "cond": cond})
                continue
            # presence: !string.IsNullOrEmpty(x), x != null, x.HasValue, x != "text" (and their negations)
            pres = (re.fullmatch(r"(!)?\s*string\.IsNullOr(?:Empty|WhiteSpace)\(\s*([A-Za-z_]\w*)\s*\)", part)
                    or re.fullmatch(r"()([A-Za-z_]\w*)\s*(==|!=)\s*null", part)
                    or re.fullmatch(r"(!)?\s*([A-Za-z_]\w*)\.HasValue", part)
                    or re.fullmatch(r"()([A-Za-z_]\w*)\s*(!=)\s*\"[^\"]*\"", part))
            if pres and _norm(aliases.get(pres.group(2), pres.group(2))) in wanted:
                if "IsNullOr" in part:
                    present = bool(pres.group(1))
                elif "null" in part or "\"" in part:
                    present = pres.group(3) == "!="
                else:
                    present = not pres.group(1)
                out.append({"param": wanted[_norm(aliases.get(pres.group(2), pres.group(2)))],
                            "truthy": present ^ negated_block, "cond": cond})
                continue
            m = re.fullmatch(r"(!)?\s*([A-Za-z_][A-Za-z0-9_]*)(?:\s*==\s*(true|false))?", part)
            if not m:
                m2 = re.search(r"@?params\s*\[\s*\"([A-Za-z_]+)\"\s*\]", part)
                if m2 and _norm(m2.group(1)) in wanted:
                    out.append({"param": wanted[_norm(m2.group(1))], "truthy": not negated_block, "cond": cond})
                continue
            var = m.group(2)
            key = _norm(aliases.get(var, var))
            if key not in wanted:
                continue
            truthy = not bool(m.group(1))
            if m.group(3) == "false":
                truthy = not truthy
            if negated_block:
                truthy = not truthy
            out.append({"param": wanted[key], "truthy": truthy, "cond": cond})
    return out


def _aliases(text: str) -> dict[str, str]:
    """local variable -> the JSON argument it was read from (bool overwrite = @params["overwrite"]...)."""
    out = {}
    for m in re.finditer(
            r"\b([a-z_][A-Za-z0-9_]*)\s*=\s*[^;\n]*?(?:@?params|p|parameters|args)\s*\??\s*"
            r"(?:\[\s*\"([A-Za-z_][A-Za-z0-9_]*)\"\s*\]|\.(?:Get\w*|TryGet\w*)\s*\(\s*\"([A-Za-z_][A-Za-z0-9_]*)\")",
            text):
        out[m.group(1)] = m.group(2) or m.group(3)
    return out


def _labels(action: str | None) -> list[str]:
    """The case labels a sub-dispatch can use for this action: the action, then the action without its prefix
    (animator_get_parameter is dispatched as get_parameter after Substring)."""
    if not action:
        return []
    parts = action.split("_")
    return ["_".join(parts[i:]) for i in range(len(parts))]


def _switch_exclusions(text: str, lo: int, hi: int, labels: list[str]) -> list[tuple[int, int]]:
    """Spans inside [lo, hi) that do not run for this action: in a switch over an action variable, every case
    except the one for this action (or the default when no case matches)."""
    if not labels:
        return []
    spans = []
    for m in re.finditer(r"switch\s*\(\s*(\w*[Aa]ction\w*)(?:\s*\.\s*ToLower\w*\s*\(\s*\))?\s*\)\s*\{",
                         text[lo:hi]):
        open_at = lo + m.end() - 1
        end = _brace_end(text, open_at)
        if end > hi:
            continue
        cases = [(c.start() + open_at, c.group(1)) for c in
                 re.finditer(r"(?:case\s+\"([^\"]+)\"|default)\s*:", text[open_at:end])]
        if not cases:
            continue
        names = [name for _pos, name in cases if name]
        keep = next((label for label in labels if label in names), None)
        for i, (pos, name) in enumerate(cases):
            stop = cases[i + 1][0] if i + 1 < len(cases) else end
            if keep is not None and name == keep:
                continue
            if keep is None and name is None:
                continue
            spans.append((pos, stop))
    return spans


def walk(index: Index, start: list[tuple[str | None, str, int, int, str]], params: list[str],
         limit_nodes: int = 600, limit_depth: int = 10, action: str | None = None) -> list[dict]:
    """Effect sites reachable from the start chunks.

    start rows: (owning class, file, lo, hi, label) — an offset range in that file's text.
    """
    sites: dict[tuple[str, str], dict] = {}
    seen: set[tuple[str, str, int]] = set()
    queue: list[tuple[str | None, str, int, int, list[str], list[str], int]] = [
        (cls, file, lo, hi, [label], [], 0) for cls, file, lo, hi, label in start]
    nodes = 0
    while queue and nodes < limit_nodes:
        cls, file, lo, hi, via, conds, depth = queue.pop(0)
        nodes += 1
        text = index.files[file]
        chunk = text[lo:hi]
        aliases = _aliases(chunk)
        skip = _switch_exclusions(text, lo, hi, _labels(action))

        def skipped(pos: int) -> bool:
            return any(a <= pos < b for a, b in skip)

        for kind, rx in KIND_RE.items():
            for m in rx.finditer(chunk):
                pos = lo + m.start()
                if skipped(pos):
                    continue
                here = conds + _conditions_at(text, pos, lo, hi)
                line = text.count("\n", 0, pos) + 1
                key = (kind, f"{file}:{line}")
                open_at = text.find("(", lo + m.start(), lo + m.end() + 1)
                arg = ""
                if open_at >= 0:
                    close = _paren_end(text, open_at)
                    if close > open_at:
                        depth, first = 0, ""
                        for ch in text[open_at + 1:close]:
                            if ch in "([{":
                                depth += 1
                            elif ch in ")]}":
                                depth -= 1
                            if ch == "," and depth == 0:
                                break
                            first += ch
                        arg = " ".join(first.split())[:60]
                row = {"kind": kind, "api": " ".join(m.group(0).split()).rstrip("(<").strip(),
                       "at": f"{file}:{line}", "via": via[:], "when": here,
                       "when_params": _when_params(here, params, aliases), "arg": arg,
                       "scratch": bool((kind == "delete_file" and SCRATCH_ARG.match(arg or ""))
                                       or (kind == "destroy_object" and SCRATCH_OBJECT.match(arg or "")))}
                old = sites.get(key)
                if old is None or len(here) < len(old["when"]):
                    sites[key] = row
        if depth >= limit_depth:
            continue
        for offset, targets in _calls(index, cls, chunk):
            pos = lo + offset
            if skipped(pos):
                continue
            here = conds + _conditions_at(text, pos, lo, hi)
            for target in targets:
                key = (target.cls, target.file, target.start)
                if key in seen:
                    continue
                seen.add(key)
                queue.append((target.cls, target.file, target.body_at, target.body_at + len(target.body),
                              via + [f"{target.cls}.{target.name}"], here, depth + 1))
    return sorted(sites.values(), key=lambda r: (list(KINDS).index(r["kind"]), r["at"]))


def _handler_file(index: Index, tool: str) -> str | None:
    for file, text in index.files.items():
        if re.search(r'\[McpForUnityTool\(\s*"' + re.escape(tool) + r'"', text):
            return file
    return None


def _class_at(index: Index, file: str, pos: int) -> str | None:
    text = index.files[file]
    best, owner = -1, None
    for decl in CLASS_DECL_RE.finditer(text):
        end = _brace_end(text, decl.end() - 1)
        if decl.start() < pos <= end and decl.start() > best:
            best, owner = decl.start(), decl.group(1)
    return owner


def entry_chunks(index: Index, tool: str, action: str | None, cases: dict) -> tuple[list, str]:
    """Where the editor starts for this tool and action: the action's case, an Is<Action>Action block, a
    Handle<Action> method, else the whole HandleCommand (every action's effects, marked unresolved)."""
    file = _handler_file(index, tool)
    if file is None:
        return [], "no C# handler"
    text = index.files[file]
    handle = None
    for (cls, name), rows in index.methods.items():
        for row in rows:
            if row.file == file and name == "HandleCommand":
                handle = row
    rows = []
    if handle is not None:
        # the code before the action dispatch runs for every action
        body = handle.body
        cut = re.search(r"switch\s*\(|\bif\s*\(\s*Is\w+Action\s*\(|return\s+\w+\s*switch|\baction\s*==", body)
        pre_hi = handle.body_at + (cut.start() if cut else len(body))
        rows.append((handle.cls, file, handle.body_at, pre_hi, f"{handle.cls}.HandleCommand"))
    if action is None:
        if handle is None:
            return [], "no HandleCommand"
        return [(handle.cls, file, handle.body_at, handle.body_at + len(handle.body),
                 f"{handle.cls}.HandleCommand")], "HandleCommand"
    if action in cases:
        # The case text came from the file with comments; this text has them blanked. Comment blanking keeps
        # offsets, so the case is found at its own line (several cases can start with the same words).
        chunk = _strip_comments(cases[action]["text"])
        line_at = 0
        for _ in range(max(0, int(cases[action]["line"]) - 1)):
            line_at = text.find("\n", line_at) + 1
        pos = text.find(chunk.strip()[:80], line_at) if chunk.strip() else -1
        if pos >= 0:
            rows.append((_class_at(index, file, pos), file, pos, pos + len(chunk.strip()),
                         f"case {action}"))
            return rows, f"{file}:{cases[action]['line']}"
    # if (IsCreateAction(action)) { ... }
    for m in re.finditer(r"\bif\s*\(\s*Is(\w+)Action\s*\(\s*action\s*\)\s*\)", text):
        if _norm(m.group(1)) == _norm(action):
            j = m.end()
            while text[j] in " \t\r\n":
                j += 1
            end = _brace_end(text, j) if text[j] == "{" else text.find(";", j)
            rows.append((_class_at(index, file, m.start()), file, j, end + 1, f"if Is{m.group(1)}Action"))
            return rows, f"{file}:{text.count(chr(10), 0, m.start()) + 1}"
    want = _norm(action)
    for (cls, name), found in index.methods.items():
        for row in found:
            if row.file != file:
                continue
            short = _norm(name)
            for prefix in ("handle", "do", "execute", ""):
                if short == prefix + want or short == prefix + want + "async":
                    rows.append((cls, file, row.body_at, row.body_at + len(row.body), f"{cls}.{name}"))
                    return rows, f"{file}:{row.line}"
    if handle is not None:
        return [(handle.cls, file, handle.body_at, handle.body_at + len(handle.body),
                 f"{handle.cls}.HandleCommand (action not resolved: every action's effects)")], "unresolved"
    return [], "no entry"


def effects_for(root: Path, ops: list[dict], handlers: dict, py_tools: dict) -> dict[str, dict]:
    """op key -> {"effects": [...], "entry": evidence}."""
    index = Index(root)
    out: dict[str, dict] = {}
    for op in ops:
        tool = op["unity_target"] or op["tool"]
        cases = (handlers.get(tool) or handlers.get(op["tool"]) or {}).get("cases") or {}
        start, entry = entry_chunks(index, tool, op["action"], cases)
        effects = walk(index, start, op["params"], action=op["action"]) if start else []
        body = (py_tools.get(op["tool"]) or {}).get("module", "")
        if not start and body and PY_SEND_RE.search(body):
            effects.append({"kind": "send", "api": PY_SEND_RE.search(body).group(0),
                            "at": (py_tools.get(op["tool"]) or {}).get("py_file", ""), "via": [op["tool"]],
                            "when": [], "when_params": [], "arg": "", "scratch": False})
        out[op["key"]] = {"effects": effects, "entry": entry}
    return out


def compact_effect(row: dict) -> dict:
    """The table row the bridge loads: the chain keeps its first and last two methods."""
    via = row["via"]
    if len(via) > 3:
        via = [via[0], "…"] + via[-2:]
    return {
        "kind": row["kind"],
        "api": row["api"][:80],
        "at": row["at"].replace("MCPForUnity/", ""),
        "via": via,
        "when": [cond[:80] for cond in row["when"][:2]],
        "when_params": [dict({"param": item["param"], "truthy": item["truthy"]},
                             **({"equals": item["equals"]} if "equals" in item else {})) for item in row["when_params"]],
        "arg": row.get("arg", ""),
        "scratch": row.get("scratch", False),
    }


def compact_effects(rows: list[dict], keep: int = 3) -> list[dict]:
    """At most keep sites per effect kind: one for each distinct argument gate first (an ungated site sorts
    first, so a kind that also happens with no gate is never shown as gated), then the least conditioned.
    "more" counts the sites left out."""
    by_kind: dict[str, list[dict]] = {}
    for row in rows:
        by_kind.setdefault(row["kind"], []).append(compact_effect(row))
    out = []
    for kind in KINDS:
        group = by_kind.get(kind) or []
        if not group:
            continue
        group.sort(key=lambda r: (r["scratch"], len(r["when_params"]), len(r["when"]), r["at"]))
        chosen, gates = [], set()
        for row in group:
            sig = (row["scratch"],) + tuple(sorted((g["param"], g["truthy"], g.get("equals", ""))
                                                   for g in row["when_params"]))
            if sig not in gates:
                gates.add(sig)
                chosen.append(row)
        for row in group:
            if len(chosen) >= max(keep, len(gates)):
                break
            if row not in chosen:
                chosen.append(row)
        if len(group) > len(chosen):
            chosen[-1] = dict(chosen[-1], more=len(group) - len(chosen))
        out.extend(chosen)
    return out


# H7 cases from the 10/21 audits. The extractor exits non-zero when one of them drifts.
EFFECT_CHECKS = (
    ("run_tests", "save_scene", "TestRunnerService.cs", None),
    ("manage_build.build", "save_scene", "BuildRunner.cs", None),
    ("manage_scriptable_object.create", "delete_file", "ManageScriptableObject.cs", ("overwrite", True)),
    ("manage_scriptable_object.create", "write_file", "ManageScriptableObject.cs", None),
    ("manage_gameobject.create", "instantiate", "GameObjectCreate.cs", None),
    ("manage_gameobject.create", "write_file", "GameObjectCreate.cs", ("save_as_prefab", True)),
    ("manage_editor.play", "enter_play", "ManageEditor.cs", None),
    ("manage_editor.stop", "exit_play", "ManageEditor.cs", None),
    ("manage_asset.search", "load_asset", "ManageAsset.cs", None),
    ("manage_prefabs.get_info", "load_asset", "ManagePrefabs.cs", None),
    ("manage_scene.create", "scene_switch", "ManageScene.cs", None),
    ("manage_asset.delete", "delete_file", "ManageAsset.cs", None),
    ("execute_code.execute", "compile_run", "", None),
    ("execute_menu_item", "menu_item", "", None),
    ("manage_gameobject.delete", "destroy_object", "GameObjectDelete.cs", None),
    ("manage_physics.simulate_step", "simulate", "", None),
    ("refresh_unity", "import_compile", "RefreshUnity.cs", ("compile", True)),
)


def effects_self_check(ops: list[dict]) -> list[str]:
    by_key = {op["key"]: op for op in ops}
    problems = []
    for key, kind, file, gate in EFFECT_CHECKS:
        op = by_key.get(key)
        if op is None:
            problems.append(f"effects: {key} missing")
            continue
        rows = [row for row in op.get("effects") or [] if row["kind"] == kind and file in row["at"]]
        if not rows:
            problems.append(f"effects: {key} has no {kind} in {file or 'any file'}")
            continue
        if gate is None:
            continue
        param, truthy = gate
        if not any(any(g["param"] == param and g["truthy"] == truthy for g in row["when_params"]) for row in rows):
            problems.append(f"effects: {key} {kind} is not gated by {param}={truthy}")
    # A gated write never shows up as unconditional: manage_gameobject.create with prefab_path places the prefab.
    create = by_key.get("manage_gameobject.create") or {}
    ungated = [row for row in create.get("effects") or []
               if row["kind"] in ("write_file", "delete_file") and not row["when_params"]]
    if ungated:
        problems.append("effects: manage_gameobject.create writes or deletes with no argument gate: "
                        + ", ".join(row["at"] for row in ungated))
    return problems


def table_markdown(bundles: dict) -> str:
    lines = [
        "# What each operation does inside (upstream 10.3.0)",
        "",
        "Made by tools/extract_side_effects.py from the MCPForUnity C# source. One row per effect site: the Unity "
        "call, where it is, the chain from the operation to it, and the arguments that gate it. The bridge decides "
        "the plan text, the second question, and the state fingerprint from these rows.",
        "",
        "| op | effect | call | at | gated by | via |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for _bundle, slot in bundles.items():
        for key, op in slot["ops"].items():
            rows = op.get("effects") or []
            if not rows:
                lines.append(f"| {key} | none found | - | - | - | {op.get('entry') or '-'} |")
                continue
            for row in rows:
                gate = ", ".join(("" if item["truthy"] else "not ") + item["param"] for item in row["when_params"])
                lines.append(f"| {key} | {row['kind']} | `{row['api']}` | {row['at']} | {gate or '-'} | "
                             f"{' > '.join(row['via'])} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    index = Index(root)
    print(f"classes {len(index.classes)} methods {sum(len(v) for v in index.methods.values())} "
          f"service properties {len(index.props)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
