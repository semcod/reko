"""Modele danych dla reko."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class FindingKind(str, Enum):
    MAGIC_NUMBER = "magic_number"
    STRING_LITERAL = "string_literal"
    DICT_LITERAL = "dict_literal"
    LIST_LITERAL = "list_literal"
    SET_LITERAL = "set_literal"
    TUPLE_LITERAL = "tuple_literal"
    REPEATED_LITERAL = "repeated_literal"
    UNUSED_CONSTANT = "unused_constant"
    INLINE_STRUCTURE = "inline_structure"


class RefactorAction(str, Enum):
    EXTRACT = "extract"
    SPLIT = "split"
    MOVE = "move"
    REMOVE = "remove"
    INLINE = "inline"
    REPLACE = "replace"


class Finding(BaseModel):
    kind: FindingKind
    file: Path
    line: int
    col: int = 0
    end_line: int | None = None
    end_col: int | None = None
    value_repr: str
    message: str
    suggested_name: str | None = None
    severity: str = "info"
    context: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class ScanReport(BaseModel):
    root: Path
    findings: list[Finding] = Field(default_factory=list)
    files_scanned: int = 0

    @property
    def by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.kind.value] = counts.get(finding.kind.value, 0) + 1
        return counts


class RefactorChange(BaseModel):
    action: RefactorAction
    file: Path
    description: str
    line: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RefactorPlan(BaseModel):
    root: Path = Path(".")
    changes: list[RefactorChange] = Field(default_factory=list)
    dry_run: bool = True


class RefactorResult(BaseModel):
    plan: RefactorPlan
    modified_files: list[Path] = Field(default_factory=list)
    created_files: list[Path] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
