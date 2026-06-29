"""Reporter JSON/YAML dla wyników skanowania."""
import json
from pathlib import Path

import yaml

from reko.models import ScanReport
def report_to_dict(report: ScanReport) -> dict:
    return {
        "root": str(report.root),
        "files_scanned": report.files_scanned,
        "total_findings": len(report.findings),
        "by_kind": report.by_kind,
        "findings": [
            {
                "kind": finding.kind.value,
                "file": str(finding.file),
                "line": finding.line,
                "col": finding.col,
                "message": finding.message,
                "value_repr": finding.value_repr,
                "suggested_name": finding.suggested_name,
                "severity": finding.severity,
            }
            for finding in report.findings
        ],
    }
def write_report(report: ScanReport, output: Path, fmt: str = "json") -> None:
    payload = report_to_dict(report)
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "yaml":
        output.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
