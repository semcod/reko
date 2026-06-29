"""Konfiguracja reko."""
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]
class ScanConfig(BaseModel):
    extensions: list[str] = Field(default_factory=lambda: [".py"])
    exclude: list[str] = Field(
        default_factory=lambda: [
            "**/__pycache__/**",
            "**/.venv/**",
            "**/venv/**",
            "**/node_modules/**",
            "**/.git/**",
            "**/_work/**",
            "**/tests/**",
            "**/*_test.py",
            "**/test_*.py",
        ]
    )
    min_string_length: int = 8
    min_dict_keys: int = 4
    min_list_items: int = 5
    min_structure_lines: int = 3
    allowed_numbers: list[int | float] = Field(
        default_factory=lambda: [0, 1, -1, 2, 10, 100, 1000]
    )
    number_threshold: int = 10
    detect_repeated: bool = True
    min_repeat_count: int = 2
class ExtractConfig(BaseModel):
    target: str = "constants.py"
    naming: str = "upper_snake"
    group_by: str = "file"
    add_import: bool = True
class SplitConfig(BaseModel):
    min_keys: int = 4
    min_items: int = 5
    prefix: str = "PART_"
class MoveConfig(BaseModel):
    update_imports: bool = True
    remove_from_source: bool = True
class RekoConfig(BaseModel):
    scan: ScanConfig = Field(default_factory=ScanConfig)
    extract: ExtractConfig = Field(default_factory=ExtractConfig)
    split: SplitConfig = Field(default_factory=SplitConfig)
    move: MoveConfig = Field(default_factory=MoveConfig)
def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return {}
    return data
def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    tool = data.get("tool", {})
    if isinstance(tool, dict):
        reko = tool.get("reko", {})
        if isinstance(reko, dict):
            return reko
    return {}
def load_config(root: Path | None = None) -> RekoConfig:
    root = root or Path(".")
    candidates = [
        root / "reko.yaml",
        root / "reko.yml",
        root / ".reko.yaml",
        root / "pyproject.toml",
    ]
    merged: dict[str, Any] = {}
    for candidate in candidates:
        if not candidate.exists():
            continue
        if candidate.suffix == ".toml":
            merged.update(_load_toml(candidate))
        else:
            merged.update(_load_yaml(candidate))
    return RekoConfig.model_validate(merged)
