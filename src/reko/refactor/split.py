"""Rozbijanie dużych struktur inline na mniejsze stałe."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from reko.config import RekoConfig, load_config
from reko.models import RefactorAction, RefactorChange, RefactorPlan, RefactorResult
from reko.refactor._utils import ensure_trailing_newline, read_module, to_upper_snake, unique_name, write_module


@dataclass
class _SplitTarget:
    node: ast.Dict | ast.List
    scope: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef
    insert_at: int


def _parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _contains_node(parent: ast.AST, child: ast.AST) -> bool:
    for node in ast.walk(parent):
        if node is child:
            return True
    return False


def _literal_size(node: ast.AST) -> int:
    if isinstance(node, ast.Dict):
        return len(node.keys)
    if isinstance(node, ast.List):
        return len(node.elts)
    return 0


class _SplitFinder(ast.NodeVisitor):
    def __init__(self, config: RekoConfig) -> None:
        self.config = config
        self.scope: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef = None  # type: ignore[assignment]
        self.all_nodes: list[ast.Dict | ast.List] = []
        self.targets: list[_SplitTarget] = []
        self._parents: dict[ast.AST, ast.AST] = {}

    def visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self._parents[child] = node
        super().visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        self.scope = node
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        previous = self.scope
        self.scope = node
        self.generic_visit(node)
        self.scope = previous

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        previous = self.scope
        self.scope = node
        self.generic_visit(node)
        self.scope = previous

    def visit_Dict(self, node: ast.Dict) -> None:
        if len(node.keys) >= self.config.split.min_keys:
            self.all_nodes.append(node)
            self.targets.append(_SplitTarget(node=node, scope=self.scope, insert_at=self._insert_at(node)))
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:
        if len(node.elts) >= self.config.split.min_items:
            self.all_nodes.append(node)
            self.targets.append(_SplitTarget(node=node, scope=self.scope, insert_at=self._insert_at(node)))
        self.generic_visit(node)

    def _insert_at(self, node: ast.AST) -> int:
        current: ast.AST | None = node
        while current is not None and current is not self.scope:
            parent = self._parents.get(current)
            if isinstance(parent, ast.stmt) and parent in self.scope.body:
                return self.scope.body.index(parent)
            current = parent
        return _insert_index(self.scope)

    def finalize(self) -> None:
        nested_ids = set()
        for outer in self.all_nodes:
            for inner in self.all_nodes:
                if outer is not inner and _contains_node(outer, inner):
                    nested_ids.add(id(inner))
        self.targets = [target for target in self.targets if id(target.node) not in nested_ids]


def _key_name(key: ast.AST | None, index: int) -> str:
    if isinstance(key, ast.Constant) and isinstance(key.value, str):
        return key.value
    return f"KEY_{index}"


def _make_assign(name: str, value: ast.AST) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=value)


def _split_dict_node(node: ast.Dict, prefix: str, used: set[str]) -> tuple[ast.Dict, list[ast.Assign]]:
    keys: list[ast.AST | None] = []
    values: list[ast.AST] = []
    assignments: list[ast.Assign] = []

    for index, (key, value) in enumerate(zip(node.keys, node.values, strict=False)):
        if value is None:
            continue
        part_name = unique_name(to_upper_snake(f"{prefix}{_key_name(key, index)}"), used)
        used.add(part_name)
        assignments.append(_make_assign(part_name, value))
        keys.append(key)
        values.append(ast.Name(id=part_name, ctx=ast.Load()))

    return ast.Dict(keys=keys, values=values), assignments


def _split_list_node(node: ast.List, prefix: str, used: set[str]) -> tuple[ast.List, list[ast.Assign]]:
    names: list[ast.AST] = []
    assignments: list[ast.Assign] = []
    for index, elt in enumerate(node.elts):
        part_name = unique_name(to_upper_snake(f"{prefix}ITEM_{index}"), used)
        used.add(part_name)
        assignments.append(_make_assign(part_name, elt))
        names.append(ast.Name(id=part_name, ctx=ast.Load()))
    return ast.List(elts=names, ctx=ast.Load()), assignments


def _insert_index(scope: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    for index, stmt in enumerate(scope.body):
        if isinstance(stmt, ast.Return):
            return index
    return len(scope.body)


def split_structures(
    source: Path,
    *,
    config: RekoConfig | None = None,
    dry_run: bool = True,
) -> RefactorResult:
    config = config or load_config(source.parent)
    source_text, tree = read_module(source)

    finder = _SplitFinder(config)
    finder.visit(tree)
    finder.finalize()
    if not finder.targets:
        return RefactorResult(plan=RefactorPlan(root=source.parent, dry_run=dry_run))

    used: set[str] = set()
    scope_inserts: dict[int, list[ast.Assign]] = {}

    for target in sorted(finder.targets, key=lambda item: item.node.lineno, reverse=True):
        if isinstance(target.node, ast.Dict):
            replacement, assignments = _split_dict_node(target.node, config.split.prefix, used)
        else:
            replacement, assignments = _split_list_node(target.node, config.split.prefix, used)

        parents = _parent_map(tree)
        parent = parents.get(target.node)
        if parent is None:
            continue
        replaced = False
        for field, value in ast.iter_fields(parent):
            if value is target.node:
                setattr(parent, field, replacement)
                replaced = True
                break
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    if item is target.node:
                        value[idx] = replacement
                        replaced = True
                        break
            if replaced:
                break

        scope_id = id(target.scope)
        scope_inserts.setdefault(scope_id, []).append((target.insert_at, assignments))

    for scope in _iter_scopes(tree):
        inserts = scope_inserts.get(id(scope), [])
        for insert_at, assignments in sorted(inserts, key=lambda item: item[0], reverse=True):
            scope.body[insert_at:insert_at] = assignments

    ast.fix_missing_locations(tree)
    final_source = ast.unparse(tree) + "\n"
    write_module(source, ensure_trailing_newline(final_source), dry_run)

    return RefactorResult(
        plan=RefactorPlan(
            root=source.parent,
            dry_run=dry_run,
            changes=[
                RefactorChange(
                    action=RefactorAction.SPLIT,
                    file=source,
                    description=f"Split {len(finder.targets)} inline structures",
                )
            ],
        ),
        modified_files=[source],
    )


def _iter_scopes(tree: ast.Module) -> list[ast.Module | ast.FunctionDef | ast.AsyncFunctionDef]:
    scopes: list[ast.Module | ast.FunctionDef | ast.AsyncFunctionDef] = [tree]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append(node)
    return scopes
