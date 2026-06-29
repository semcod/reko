"""Usuwanie nieużywanych stałych modułowych."""
import ast
from pathlib import Path

from reko.models import RefactorAction, RefactorChange, RefactorPlan, RefactorResult
from reko.refactor._utils import (
    collect_name_usages,
    ensure_trailing_newline,
    module_level_names,
    read_module,
    write_module,
)


def remove_unused_constants(
    source: Path,
    *,
    dry_run: bool = True,
) -> RefactorResult:
    source_text, tree = read_module(source)
    names = module_level_names(tree)
    if not names:
        return RefactorResult(plan=RefactorPlan(root=source.parent, dry_run=dry_run))

    assigned: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)

    used = collect_name_usages(tree, assigned)
    unused = assigned - used
    if not unused:
        return RefactorResult(plan=RefactorPlan(root=source.parent, dry_run=dry_run))

    lines = source_text.splitlines(keepends=True)
    remove_ranges: list[tuple[int, int]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in unused:
                remove_ranges.append((node.lineno - 1, (node.end_lineno or node.lineno) - 1))

    for start, end in sorted(remove_ranges, reverse=True):
        del lines[start : end + 1]

    write_module(source, ensure_trailing_newline("".join(lines)), dry_run)

    return RefactorResult(
        plan=RefactorPlan(
            root=source.parent,
            dry_run=dry_run,
            changes=[
                RefactorChange(
                    action=RefactorAction.REMOVE,
                    file=source,
                    description=f"Remove unused constants: {', '.join(sorted(unused))}",
                )
            ],
        ),
        modified_files=[source],
        skipped=[],
    )
