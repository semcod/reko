"""Silnik stosujący plany refaktoryzacji."""
from pathlib import Path

import yaml

from reko.models import RefactorAction, RefactorPlan, RefactorResult
from reko.refactor.extract import extract_constants
from reko.refactor.move import move_constants
from reko.refactor.remove import remove_unused_constants
from reko.refactor.split import split_structures
def apply_plan(plan_path: Path, *, dry_run: bool = True) -> RefactorResult:
    raw = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    plan = RefactorPlan.model_validate(raw)
    plan.dry_run = dry_run

    aggregate = RefactorResult(plan=plan)
    for change in plan.changes:
        try:
            if change.action == RefactorAction.EXTRACT:
                result = extract_constants(change.file, dry_run=dry_run)
            elif change.action == RefactorAction.SPLIT:
                result = split_structures(change.file, dry_run=dry_run)
            elif change.action == RefactorAction.REMOVE:
                result = remove_unused_constants(change.file, dry_run=dry_run)
            elif change.action == RefactorAction.MOVE:
                target = Path(change.metadata["target"])
                names = set(change.metadata.get("names", []))
                result = move_constants(change.file, target, names=names, dry_run=dry_run)
            else:
                aggregate.skipped.append(f"Unsupported action: {change.action}")
                continue
            aggregate.modified_files.extend(result.modified_files)
            aggregate.created_files.extend(result.created_files)
            aggregate.errors.extend(result.errors)
        except Exception as exc:  # pragma: no cover - defensive
            aggregate.errors.append(f"{change.action} on {change.file}: {exc}")

    aggregate.modified_files = sorted(set(aggregate.modified_files))
    aggregate.created_files = sorted(set(aggregate.created_files))
    return aggregate
