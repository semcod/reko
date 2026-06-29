"""CLI dla reko."""

import json
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from reko.config import load_config
from reko.models import FindingKind, RefactorAction, RefactorChange, RefactorPlan
from reko.refactor.engine import apply_plan
from reko.refactor.extract import extract_constants
from reko.refactor.move import move_constants
from reko.refactor.remove import remove_unused_constants
from reko.refactor.split import split_structures
from reko.reporters.json_reporter import write_report
from reko.scanner.detector import scan_project

app = typer.Typer(
    name="reko",
    help="reko — refaktoryzacja hardkodowanych wartości i struktur w kodzie Python.",
    add_completion=False,
)
console = Console()

_MAX_TABLE_ROWS = 200


def _require_python_file(path: Path) -> Path:
    try:
        from reko.refactor._utils import require_python_file

        return require_python_file(path)
    except FileNotFoundError as exc:
        console.print(f"[red]Błąd:[/red] {exc}")
        console.print(
            "[dim]Podaj istniejący plik .py, np. po `reko extract` utworzysz constants.py "
            "albo użyj pliku z examples/03-unused-constants/before.py[/dim]"
        )
        raise typer.Exit(code=1) from exc
    except (IsADirectoryError, ValueError) as exc:
        console.print(f"[red]Błąd:[/red] {exc}")
        raise typer.Exit(code=1) from exc


def _print_findings(report) -> None:
    table = Table(title="Hardcoded findings")
    table.add_column("Kind")
    table.add_column("File")
    table.add_column("Line")
    table.add_column("Message")
    for finding in report.findings[:_MAX_TABLE_ROWS]:
        rel = finding.file
        try:
            rel = finding.file.relative_to(report.root)
        except ValueError:
            pass
        table.add_row(finding.kind.value, str(rel), str(finding.line), finding.message)
    console.print(table)
    if len(report.findings) > _MAX_TABLE_ROWS:
        console.print(f"[dim]... and {len(report.findings) - _MAX_TABLE_ROWS} more[/dim]")
    console.print(
        f"\nScanned {report.files_scanned} files, found {len(report.findings)} issues."
    )
    if report.by_kind:
        console.print("By kind:", report.by_kind)


@app.command()
def scan(
    path: Path = typer.Argument(Path("."), help="Katalog projektu do skanowania."),
    format: str = typer.Option("table", "--format", "-f", help="table | json | yaml"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Plik wyjściowy."),
) -> None:
    """Wykryj hardkodowane wartości i struktury."""
    config = load_config(path)
    report = scan_project(path.resolve(), config)
    if format == "table" and output is None:
        _print_findings(report)
        return
    fmt = "yaml" if format == "yaml" else "json"
    if output is None:
        console.print_json(json.dumps(report.model_dump(mode="json"), default=str))
        return
    write_report(report, output, fmt=fmt)
    console.print(f"Report saved to {output}")


@app.command()
def extract(
    path: Path = typer.Argument(..., help="Plik źródłowy."),
    target: Path | None = typer.Option(None, "--target", "-t", help="Moduł docelowy stałych."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Tylko podgląd / zapis."),
) -> None:
    """Wyciągnij hardkod do modułu stałych."""
    path = _require_python_file(path)
    config = load_config(path.parent)
    result = extract_constants(path, target=target, config=config, dry_run=dry_run)
    console.print(result.model_dump(mode="json"))
    if dry_run:
        console.print("[yellow]Dry run — użyj --apply aby zapisać zmiany[/yellow]")


@app.command()
def split(
    path: Path = typer.Argument(..., help="Plik ze strukturami inline."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Tylko podgląd / zapis."),
) -> None:
    """Rozbij duże dict/list na mniejsze stałe."""
    path = _require_python_file(path)
    result = split_structures(path, dry_run=dry_run)
    console.print(result.model_dump(mode="json"))
    if dry_run:
        console.print("[yellow]Dry run — użyj --apply aby zapisać zmiany[/yellow]")


@app.command("move")
def move_cmd(
    source: Path = typer.Argument(..., help="Plik źródłowy."),
    target: Path = typer.Argument(..., help="Moduł docelowy."),
    names: str = typer.Option(..., "--names", "-n", help="Lista nazw stałych po przecinku."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Tylko podgląd / zapis."),
) -> None:
    """Przenieś stałe między modułami."""
    source = _require_python_file(source)
    name_set = {part.strip() for part in names.split(",") if part.strip()}
    result = move_constants(source, target, names=name_set, dry_run=dry_run)
    console.print(result.model_dump(mode="json"))


@app.command()
def remove(
    path: Path = typer.Argument(..., help="Plik ze stałymi."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Tylko podgląd / zapis."),
) -> None:
    """Usuń nieużywane stałe modułowe."""
    path = _require_python_file(path)
    result = remove_unused_constants(path, dry_run=dry_run)
    console.print(result.model_dump(mode="json"))


@app.command()
def apply(
    plan: Path = typer.Argument(..., help="Plik planu YAML/JSON."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Tylko podgląd / zapis."),
) -> None:
    """Zastosuj plan refaktoryzacji."""
    result = apply_plan(plan, dry_run=dry_run)
    console.print(result.model_dump(mode="json"))


@app.command("plan")
def plan_cmd(
    path: Path = typer.Argument(Path("."), help="Katalog projektu."),
    output: Path = typer.Option(Path("reko-plan.yaml"), "--output", "-o"),
) -> None:
    """Wygeneruj plan refaktoryzacji na podstawie skanu."""
    config = load_config(path)
    report = scan_project(path.resolve(), config)
    changes: list[RefactorChange] = []
    seen_files: set[Path] = set()
    for finding in report.findings:
        if finding.kind in {FindingKind.MAGIC_NUMBER, FindingKind.STRING_LITERAL}:
            if finding.file not in seen_files:
                seen_files.add(finding.file)
                changes.append(
                    RefactorChange(
                        action=RefactorAction.EXTRACT,
                        file=finding.file,
                        description=f"Extract hardcoded values from {finding.file.name}",
                    )
                )
        elif finding.kind in {FindingKind.DICT_LITERAL, FindingKind.LIST_LITERAL}:
            changes.append(
                RefactorChange(
                    action=RefactorAction.SPLIT,
                    file=finding.file,
                    line=finding.line,
                    description=f"Split inline structure at line {finding.line}",
                )
            )
    plan = RefactorPlan(root=path.resolve(), changes=changes, dry_run=True)
    output.write_text(
        yaml.safe_dump(plan.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    console.print(f"Plan saved to {output} ({len(changes)} changes)")


if __name__ == "__main__":
    app()
