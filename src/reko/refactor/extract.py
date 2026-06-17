"""Wyciąganie hardkodowanych wartości do modułu stałych."""

from __future__ import annotations

import ast
from pathlib import Path

from reko.config import RekoConfig, load_config
from reko.models import FindingKind, RefactorAction, RefactorChange, RefactorPlan, RefactorResult
from reko.refactor._ast_extract import build_extraction_plan, insert_import, transform_source
from reko.refactor._utils import ensure_trailing_newline, read_module, write_module


def _group_target_path(source: Path, target: Path | None, config: RekoConfig) -> Path:
    if target is not None:
        return target
    return source.parent / config.extract.target


def extract_constants(
    source: Path,
    *,
    target: Path | None = None,
    kinds: set[FindingKind] | None = None,
    config: RekoConfig | None = None,
    dry_run: bool = True,
) -> RefactorResult:
    config = config or load_config(source.parent)
    kinds = kinds or {FindingKind.MAGIC_NUMBER, FindingKind.STRING_LITERAL}
    target_path = _group_target_path(source, target, config)

    source_text, tree = read_module(source)
    existing_target_names: set[str] = set()
    target_text = ""
    if target_path.exists():
        target_text, target_tree = read_module(target_path)
        existing_target_names = {
            node.targets[0].id
            for node in target_tree.body
            if isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
        }

    plan = build_extraction_plan(tree, config.scan, existing_names=existing_target_names, kinds=kinds)
    if not plan.constants:
        return RefactorResult(plan=RefactorPlan(root=source.parent, dry_run=dry_run))

    updated_source = transform_source(source_text, plan, tree)
    if config.extract.add_import and target_path != source:
        updated_source = insert_import(updated_source, target_path.stem, [name for name, _ in plan.constants])

    new_constants = "".join(f"{name} = {value_repr}\n" for name, value_repr in plan.constants)
    updated_target = ensure_trailing_newline(target_text + new_constants)

    write_module(source, updated_source, dry_run)
    write_module(target_path, updated_target, dry_run)

    created = [target_path] if not target_path.exists() and not dry_run else []

    return RefactorResult(
        plan=RefactorPlan(
            root=source.parent,
            dry_run=dry_run,
            changes=[
                RefactorChange(
                    action=RefactorAction.EXTRACT,
                    file=source,
                    description=f"Extract {len(plan.constants)} hardcoded values to {target_path.name}",
                )
            ],
        ),
        modified_files=[source, target_path],
        created_files=created,
    )
