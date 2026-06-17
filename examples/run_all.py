#!/usr/bin/env python3
"""Uruchom workflow reko na przykładach w examples/."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

EXAMPLES = Path(__file__).parent
WORK = EXAMPLES / "_work"


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or EXAMPLES, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result


def prepare_workdir() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    for name in ("01-hardcoded-api", "02-inline-config", "03-unused-constants"):
        shutil.copytree(EXAMPLES / name, WORK / name)


def main() -> int:
    prepare_workdir()

    steps = [
        ["reko", "scan", str(WORK), "--format", "json", "-o", str(WORK / "scan.json")],
        ["reko", "plan", str(WORK), "-o", str(WORK / "plan.yaml")],
        [
            "reko",
            "extract",
            str(WORK / "01-hardcoded-api" / "before.py"),
            "--target",
            str(WORK / "01-hardcoded-api" / "constants.py"),
            "--apply",
        ],
        ["reko", "split", str(WORK / "02-inline-config" / "before.py"), "--apply"],
        ["reko", "remove", str(WORK / "03-unused-constants" / "before.py"), "--apply"],
    ]

    for cmd in steps:
        result = run(cmd)
        if result.returncode != 0:
            print(f"FAILED: {' '.join(cmd)}", file=sys.stderr)
            return result.returncode

    print("\n=== Wyniki ===")
    for path in sorted(WORK.rglob("*.py")):
        rel = path.relative_to(WORK)
        print(f"\n--- {rel} ---")
        print(path.read_text(encoding="utf-8"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
