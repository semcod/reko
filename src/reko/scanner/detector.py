"""Wykrywanie hardkodowanych wartości w kodzie Python."""
import ast
import fnmatch
import hashlib
import re
from collections import defaultdict
from pathlib import Path

from reko.config import RekoConfig, ScanConfig, load_config
from reko.models import Finding, FindingKind, ScanReport

_URL_PATTERN = re.compile(r"^https?://")
_PATH_PATTERN = re.compile(r"^(/|[A-Za-z]:\\|\./|\../)")
_ENV_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+$")
def _should_exclude(path: Path, root: Path, patterns: list[str]) -> bool:
    rel = str(path.relative_to(root)).replace("\\", "/")
    name = path.name
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern):
            return True
    return False
def _is_magic_number(value: int | float, config: ScanConfig) -> bool:
    if value in config.allowed_numbers:
        return False
    if abs(value) < config.number_threshold:
        return False
    if value in {24, 60, 3600, 86400}:
        return False
    if isinstance(value, int) and value > 0 and (value & (value - 1)) == 0:
        return False
    return True
def _suggest_constant_name(value: str | int | float, kind: FindingKind) -> str:
    if kind == FindingKind.MAGIC_NUMBER:
        return f"VALUE_{str(value).replace('.', '_').replace('-', 'NEG_')}"

    text = str(value)
    if _URL_PATTERN.match(text):
        host = text.split("//", 1)[-1].split("/", 1)[0].replace(".", "_").upper()
        return f"URL_{host}"[:48]
    if _PATH_PATTERN.match(text):
        stem = Path(text).stem.replace(".", "_").replace("-", "_").upper()
        return f"PATH_{stem or 'ROOT'}"[:48]
    if _ENV_PATTERN.match(text):
        return text

    words = re.findall(r"[A-Za-z0-9]+", text)
    if not words:
        return "HARDCODED_VALUE"
    name = "_".join(word.upper() for word in words[:5])
    if kind == FindingKind.STRING_LITERAL:
        return f"STR_{name}"[:48]
    return name[:48]
def _literal_size(node: ast.AST) -> int:
    if isinstance(node, ast.Dict):
        return len(node.keys)
    if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
        return len(node.elts)
    return 0
def _get_source_segment(source: str, node: ast.AST) -> str | None:
    if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
        return None
    lines = source.splitlines()
    start = node.lineno - 1
    end = (node.end_lineno or node.lineno) - 1
    if start < 0 or end >= len(lines):
        return None
    if start == end:
        line = lines[start]
        col = getattr(node, "col_offset", 0)
        end_col = getattr(node, "end_col_offset", len(line))
        return line[col:end_col]
    chunk = lines[start : end + 1]
    chunk[0] = chunk[0][getattr(node, "col_offset", 0) :]
    chunk[-1] = chunk[-1][: getattr(node, "end_col_offset", len(chunk[-1]))]
    return "\n".join(chunk)


class _HardcodeVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str, config: ScanConfig) -> None:
        self.path = path
        self.source = source
        self.config = config
        self.findings: list[Finding] = []
        self._scope_depth = 0
        self._module_assignments: set[str] = set()
        self._joined_str_constants: set[int] = set()

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        for value in node.values:
            if isinstance(value, ast.Constant):
                self._joined_str_constants.add(id(value))
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        self._module_assignments.add(target.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scope_depth += 1
        self.generic_visit(node)
        self._scope_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._scope_depth += 1
        self.generic_visit(node)
        self._scope_depth -= 1

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope_depth += 1
        self.generic_visit(node)
        self._scope_depth -= 1

    def visit_Constant(self, node: ast.Constant) -> None:
        if self._scope_depth == 0 or id(node) in self._joined_str_constants:
            return
        if isinstance(node.value, bool) or node.value is None:
            return
        if isinstance(node.value, (int, float)) and _is_magic_number(node.value, self.config):
            self.findings.append(
                Finding(
                    kind=FindingKind.MAGIC_NUMBER,
                    file=self.path,
                    line=node.lineno,
                    col=node.col_offset,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    end_col=getattr(node, "end_col_offset", None),
                    value_repr=str(node.value),
                    message=f"Magic number: {node.value}",
                    suggested_name=_suggest_constant_name(node.value, FindingKind.MAGIC_NUMBER),
                )
            )
        elif isinstance(node.value, str) and len(node.value) >= self.config.min_string_length:
            self.findings.append(
                Finding(
                    kind=FindingKind.STRING_LITERAL,
                    file=self.path,
                    line=node.lineno,
                    col=node.col_offset,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    end_col=getattr(node, "end_col_offset", None),
                    value_repr=repr(node.value),
                    message=f"Hardcoded string ({len(node.value)} chars)",
                    suggested_name=_suggest_constant_name(node.value, FindingKind.STRING_LITERAL),
                    context=_get_source_segment(self.source, node),
                )
            )

    def visit_Dict(self, node: ast.Dict) -> None:
        size = _literal_size(node)
        if size >= self.config.min_dict_keys:
            segment = _get_source_segment(self.source, node) or "{...}"
            self.findings.append(
                Finding(
                    kind=FindingKind.DICT_LITERAL,
                    file=self.path,
                    line=node.lineno,
                    col=node.col_offset,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    end_col=getattr(node, "end_col_offset", None),
                    value_repr=f"{segment[:120]}{'...' if len(segment) > 120 else ''}",
                    message=f"Inline dict with {size} keys",
                    suggested_name="CONFIG_DICT",
                    metadata={"keys": size},
                )
            )
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:
        size = _literal_size(node)
        if size >= self.config.min_list_items:
            self.findings.append(
                Finding(
                    kind=FindingKind.LIST_LITERAL,
                    file=self.path,
                    line=node.lineno,
                    col=node.col_offset,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    end_col=getattr(node, "end_col_offset", None),
                    value_repr=f"[... {size} items ...]",
                    message=f"Inline list with {size} items",
                    suggested_name="ITEMS_LIST",
                    metadata={"items": size},
                )
            )
        self.generic_visit(node)


def scan_file(path: Path, config: RekoConfig | None = None) -> list[Finding]:
    config = config or RekoConfig()
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    visitor = _HardcodeVisitor(path, source, config.scan)
    visitor.visit(tree)
    return visitor.findings


def _collect_literal_hashes(findings: list[Finding]) -> dict[str, list[Finding]]:
    buckets: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        if finding.kind in {
            FindingKind.STRING_LITERAL,
            FindingKind.MAGIC_NUMBER,
        }:
            key = hashlib.sha256(finding.value_repr.encode()).hexdigest()[:16]
            buckets[key].append(finding)
    return buckets


def scan_project(root: Path, config: RekoConfig | None = None) -> ScanReport:
    root = root.resolve()
    config = config or load_config(root)
    report = ScanReport(root=root)

    all_findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in config.scan.extensions:
            continue
        if _should_exclude(path, root, config.scan.exclude):
            continue
        report.files_scanned += 1
        all_findings.extend(scan_file(path, config))

    if config.scan.detect_repeated:
        for group in _collect_literal_hashes(all_findings).values():
            if len(group) >= config.scan.min_repeat_count:
                for finding in group:
                    repeated = finding.model_copy(
                        update={
                            "kind": FindingKind.REPEATED_LITERAL,
                            "message": f"Repeated literal ({len(group)} occurrences)",
                            "metadata": {**finding.metadata, "repeat_count": len(group)},
                        }
                    )
                    all_findings.append(repeated)

    report.findings = all_findings
    return report
