from pathlib import Path

from reko.models import FindingKind
from reko.scanner.detector import scan_file, scan_project


FIXTURES = Path(__file__).parent / "fixtures"


def test_scan_file_detects_magic_number_and_string() -> None:
    findings = scan_file(FIXTURES / "sample.py")
    kinds = {finding.kind for finding in findings}
    assert FindingKind.MAGIC_NUMBER in kinds
    assert FindingKind.STRING_LITERAL in kinds


def test_scan_file_detects_inline_dict_and_list() -> None:
    findings = scan_file(FIXTURES / "sample.py")
    kinds = {finding.kind for finding in findings}
    assert FindingKind.DICT_LITERAL in kinds
    assert FindingKind.LIST_LITERAL in kinds


def test_scan_project_returns_report() -> None:
    report = scan_project(FIXTURES)
    assert report.files_scanned >= 1
    assert len(report.findings) > 0
    assert report.by_kind
