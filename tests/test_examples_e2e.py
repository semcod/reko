"""Testy e2e na examples/."""

import shutil
import subprocess
import sys
from pathlib import Path

EXAMPLES = Path(__file__).parent.parent / "examples"
WORK = EXAMPLES / "_work"

# Wywołuj CLI przez bieżący interpreter, aby nie zależeć od skryptu `reko` na PATH
# (np. gdy testy biegną przez .venv/bin/python -m pytest bez aktywowanego venv).
REKO = [sys.executable, "-m", "reko"]


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=EXAMPLES, text=True, capture_output=True)


def setup_module() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    for name in ("01-hardcoded-api", "02-inline-config", "03-unused-constants"):
        shutil.copytree(EXAMPLES / name, WORK / name)


def test_examples_workflow_produces_valid_python() -> None:
    setup_module()
    steps = [
        [*REKO, "extract", str(WORK / "01-hardcoded-api" / "before.py"),
         "--target", str(WORK / "01-hardcoded-api" / "constants.py"), "--apply"],
        [*REKO, "split", str(WORK / "02-inline-config" / "before.py"), "--apply"],
        [*REKO, "remove", str(WORK / "03-unused-constants" / "before.py"), "--apply"],
    ]
    for cmd in steps:
        result = _run(cmd)
        assert result.returncode == 0, result.stderr or result.stdout

    api = (WORK / "01-hardcoded-api" / "before.py").read_text(encoding="utf-8")
    assert "https://api.example.com" not in api
    assert "import httpx" in api
    assert "limit=50" in api  # f-string pozostaje nienaruszony

    config = (WORK / "02-inline-config" / "before.py").read_text(encoding="utf-8")
    assert "PART_" in config
    assert "db.internal.local" in config

    unused = (WORK / "03-unused-constants" / "before.py").read_text(encoding="utf-8")
    assert "UNUSED_ENDPOINT" not in unused
    assert "LEGACY_TIMEOUT" not in unused
    assert "ACTIVE_BASE" in unused

    for path in WORK.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
