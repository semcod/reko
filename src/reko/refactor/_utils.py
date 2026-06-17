"""Pomocnicze narzędzia do transformacji kodu."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Replacement:
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    new_text: str


def _line_offsets(source: str) -> list[int]:
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _position_to_index(source: str, line: int, col: int) -> int:
    lines = source.splitlines(keepends=True)
    if line < 1 or line > len(lines):
        return len(source)
    return sum(len(lines[i]) for i in range(line - 1)) + col


def apply_replacements(source: str, replacements: Iterable[Replacement]) -> str:
    ordered = sorted(
        replacements,
        key=lambda item: (item.start_line, item.start_col),
        reverse=True,
    )
    result = source
    for repl in ordered:
        start = _position_to_index(result, repl.start_line, repl.start_col)
        end = _position_to_index(result, repl.end_line, repl.end_col)
        result = result[:start] + repl.new_text + result[end:]
    return result


def unique_name(base: str, existing: set[str]) -> str:
    if base not in existing:
        return base
    index = 2
    while f"{base}_{index}" in existing:
        index += 1
    return f"{base}_{index}"


def to_upper_snake(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.strip("_").upper() or "CONSTANT"


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def require_python_file(path: Path) -> Path:
    """Validate that path points to an existing Python source file."""
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        msg = f"Plik nie istnieje: {path}"
        raise FileNotFoundError(msg)
    if not resolved.is_file():
        msg = f"Oczekiwano pliku Python, nie katalogu: {path}"
        raise IsADirectoryError(msg)
    if resolved.suffix != ".py":
        msg = f"Oczekiwano pliku .py: {path}"
        raise ValueError(msg)
    return resolved


def read_module(path: Path) -> tuple[str, ast.Module]:
    resolved = require_python_file(path)
    source = resolved.read_text(encoding="utf-8")
    return source, ast.parse(source)


def write_module(path: Path, source: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ensure_trailing_newline(source), encoding="utf-8")


def module_level_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def collect_name_usages(tree: ast.AST, names: set[str]) -> set[str]:
    used: set[str] = set()

    class Visitor(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Load) and node.id in names:
                used.add(node.id)

    Visitor().visit(tree)
    return used
