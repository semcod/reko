"""Przenoszenie stałych między modułami."""

from __future__ import annotations

import ast
from pathlib import Path

from reko.config import RekoConfig, load_config
from reko.models import RefactorAction, RefactorChange, RefactorPlan, RefactorResult
from reko.refactor._utils import ensure_trailing_newline, read_module, write_module


def _assignment_lines(source: str, tree: ast.Module, names: set[str]) -> dict[str, str]:
    lines = source.splitlines()
    result: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                start = node.lineno - 1
                end = (node.end_lineno or node.lineno) - 1
                block = "\n".join(lines[start : end + 1])
                result[target.id] = block
    return result


def _remove_assignments(source: str, tree: ast.Module, names: set[str]) -> str:
    lines = source.splitlines(keepends=True)
    remove_ranges: list[tuple[int, int]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                remove_ranges.append((node.lineno - 1, (node.end_lineno or node.lineno) - 1))
    for start, end in sorted(remove_ranges, reverse=True):
        del lines[start : end + 1]
    return "".join(lines)


def _ensure_import(source: str, module: str, names: set[str]) -> str:
    import_line = f"from {module} import {', '.join(sorted(names))}"
    if import_line in source:
        return source
    lines = source.splitlines(keepends=True)
    insert_at = 0
    for index, line in enumerate(lines):
        if line.startswith(("import ", "from ")):
            insert_at = index + 1
    lines.insert(insert_at, import_line + "\n")
    return "".join(lines)


def move_constants(
    source: Path,
    target: Path,
    *,
    names: set[str],
    config: RekoConfig | None = None,
    dry_run: bool = True,
) -> RefactorResult:
    config = config or load_config(source.parent)
    source_text, source_tree = read_module(source)
    blocks = _assignment_lines(source_text, source_tree, names)
    missing = names - set(blocks)
    if missing:
        return RefactorResult(
            plan=RefactorPlan(root=source.parent, dry_run=dry_run),
            errors=[f"Constants not found in {source}: {', '.join(sorted(missing))}"],
        )

    target_text = target.read_text(encoding="utf-8") if target.exists() else ""
    moved_block = "\n\n".join(blocks[name] for name in sorted(names)) + "\n"
    updated_target = ensure_trailing_newline(target_text + "\n" + moved_block)

    updated_source = _remove_assignments(source_text, source_tree, names)
    if config.move.update_imports:
        module = target.stem
        if source.parent != target.parent:
            rel = target.relative_to(source.parent)
            module = ".".join(rel.with_suffix("").parts)
        updated_source = _ensure_import(updated_source, module, names)

    write_module(target, updated_target, dry_run)
    write_module(source, ensure_trailing_newline(updated_source), dry_run)

    return RefactorResult(
        plan=RefactorPlan(
            root=source.parent,
            dry_run=dry_run,
            changes=[
                RefactorChange(
                    action=RefactorAction.MOVE,
                    file=source,
                    description=f"Move {len(names)} constants to {target}",
                    metadata={"target": str(target), "names": sorted(names)},
                )
            ],
        ),
        modified_files=[source, target],
        created_files=[] if target.exists() else [target],
    )
