from pathlib import Path

from reko.models import FindingKind
from reko.refactor.extract import extract_constants
from reko.refactor.move import move_constants
from reko.refactor.remove import remove_unused_constants
from reko.refactor.split import split_structures


def _copy_fixture(tmp_path: Path, name: str = "sample.py") -> Path:
    source = Path(__file__).parent / "fixtures" / name
    target = tmp_path / name
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def test_extract_constants_dry_run(tmp_path: Path) -> None:
    sample = _copy_fixture(tmp_path)
    result = extract_constants(sample, dry_run=True)
    assert result.plan.changes
    assert sample.read_text(encoding="utf-8") == (Path(__file__).parent / "fixtures" / "sample.py").read_text(
        encoding="utf-8"
    )


def test_extract_constants_apply(tmp_path: Path) -> None:
    sample = _copy_fixture(tmp_path)
    target = tmp_path / "constants.py"
    result = extract_constants(
        sample,
        target=target,
        kinds={FindingKind.MAGIC_NUMBER},
        dry_run=False,
    )
    updated = sample.read_text(encoding="utf-8")
    assert "VALUE_42" in updated or "42" not in updated.split("if value >")[1][:20]
    assert result.modified_files


def test_split_structures_apply(tmp_path: Path) -> None:
    sample = _copy_fixture(tmp_path)
    result = split_structures(sample, dry_run=False)
    text = sample.read_text(encoding="utf-8")
    assert "PART_" in text or result.plan.changes == []
    assert result.modified_files == [sample] or not result.plan.changes


def test_remove_unused_constants(tmp_path: Path) -> None:
    sample = _copy_fixture(tmp_path)
    result = remove_unused_constants(sample, dry_run=False)
    text = sample.read_text(encoding="utf-8")
    assert "UNUSED" not in text
    assert "USED" in text
    assert result.modified_files == [sample]


def test_move_constants(tmp_path: Path) -> None:
    sample = _copy_fixture(tmp_path)
    target = tmp_path / "moved.py"
    result = move_constants(sample, target, names={"USED"}, dry_run=False)
    assert target.exists()
    assert "USED" in target.read_text(encoding="utf-8")
    assert "from moved import USED" in sample.read_text(encoding="utf-8")
    assert not result.errors
