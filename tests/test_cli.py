from pathlib import Path
from typer.testing import CliRunner

from reko.cli.main import app


runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_scan_table():
    result = runner.invoke(app, ["scan", str(FIXTURES)])
    assert result.exit_code == 0
    assert "Hardcoded findings" in result.stdout


def test_cli_remove_missing_file():
    result = runner.invoke(app, ["remove", "src/constants.py", "--dry-run"])
    assert result.exit_code == 1
    assert "Plik nie istnieje" in result.stdout


def test_cli_plan(tmp_path):
    output = tmp_path / "plan.yaml"
    result = runner.invoke(app, ["plan", str(FIXTURES), "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()
    assert "extract" in output.read_text(encoding="utf-8").lower() or "split" in output.read_text(
        encoding="utf-8"
    ).lower()
