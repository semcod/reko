"""AST-based extraction of hardcoded literals."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

from reko.config import ScanConfig
from reko.models import FindingKind
from reko.refactor._utils import to_upper_snake, unique_name
from reko.scanner.detector import _is_magic_number, _suggest_constant_name


@dataclass
class ExtractableNode:
    node: ast.Constant
    kind: FindingKind
    value_repr: str


@dataclass
class ExtractionPlan:
    replacements: dict[int, str] = field(default_factory=dict)
    constants: list[tuple[str, str]] = field(default_factory=list)


class _InsideJoinedStr(ast.NodeVisitor):
    def __init__(self) -> None:
        self.ids: set[int] = set()

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        for value in node.values:
            if isinstance(value, ast.Constant):
                self.ids.add(id(value))
        self.generic_visit(node)


class _ExtractCollector(ast.NodeVisitor):
    def __init__(self, config: ScanConfig, skip_ids: set[int]) -> None:
        self.config = config
        self.skip_ids = skip_ids
        self.items: list[ExtractableNode] = []
        self._scope_depth = 0

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
        if self._scope_depth == 0 or id(node) in self.skip_ids:
            return
        if isinstance(node.value, bool) or node.value is None:
            return
        if isinstance(node.value, (int, float)) and _is_magic_number(node.value, self.config):
            self.items.append(
                ExtractableNode(node, FindingKind.MAGIC_NUMBER, repr(node.value))
            )
        elif isinstance(node.value, str) and len(node.value) >= self.config.min_string_length:
            self.items.append(
                ExtractableNode(node, FindingKind.STRING_LITERAL, repr(node.value))
            )


class _ExtractTransformer(ast.NodeTransformer):
    def __init__(self, replacements: dict[int, str]) -> None:
        self.replacements = replacements

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        name = self.replacements.get(id(node))
        if name:
            return ast.Name(id=name, ctx=ast.Load())
        return node


def build_extraction_plan(
    tree: ast.Module,
    config: ScanConfig,
    *,
    existing_names: set[str],
    kinds: set[FindingKind] | None = None,
) -> ExtractionPlan:
    kinds = kinds or {FindingKind.MAGIC_NUMBER, FindingKind.STRING_LITERAL}
    joined = _InsideJoinedStr()
    joined.visit(tree)

    collector = _ExtractCollector(config, joined.ids)
    collector.visit(tree)

    plan = ExtractionPlan()
    used_names = set(existing_names)
    value_to_name: dict[str, str] = {}

    for item in collector.items:
        if item.kind not in kinds:
            continue
        if item.value_repr in value_to_name:
            plan.replacements[id(item.node)] = value_to_name[item.value_repr]
            continue
        base = _suggest_constant_name(
            ast.literal_eval(item.value_repr)
            if item.kind == FindingKind.STRING_LITERAL
            else item.node.value,
            item.kind,
        )
        name = unique_name(to_upper_snake(base), used_names)
        used_names.add(name)
        value_to_name[item.value_repr] = name
        plan.replacements[id(item.node)] = name
        plan.constants.append((name, item.value_repr))

    return plan


def transform_module(tree: ast.Module, plan: ExtractionPlan) -> str:
    transformed = _ExtractTransformer(plan.replacements).visit(tree)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed) + "\n"


def transform_source(source: str, plan: ExtractionPlan, tree: ast.Module | None = None) -> str:
    module = tree or ast.parse(source)
    return transform_module(module, plan)


def insert_import(source: str, module: str, names: list[str]) -> str:
    if not names:
        return source
    import_line = f"from {module} import {', '.join(names)}\n"
    if import_line in source:
        return source

    tree = ast.parse(source)
    insert_at = 0
    for index, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            insert_at = index + 1
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(
            node.value.value, str
        ):
            insert_at = index + 1
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            insert_at = index + 1
            continue
        break

    lines = source.splitlines(keepends=True)
    offset = 0
    for index, node in enumerate(tree.body[:insert_at]):
        if hasattr(node, "end_lineno") and node.end_lineno:
            line_idx = node.end_lineno
            offset = sum(len(lines[i]) for i in range(line_idx))
    return source[:offset] + import_line + source[offset:]
