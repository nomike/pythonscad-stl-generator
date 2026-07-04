import json
from pathlib import Path

import pythonscad_stl_generator.cli as cli


def test_cli_dry_run_renders_discovered_design(tmp_path: Path, capsys) -> None:
    (tmp_path / "box.py").write_text("from pythonscad import *\n", encoding="utf-8")

    exit_code = cli.main(["--directory", str(tmp_path), "--dry-run"])

    assert exit_code == 0
    assert "--trust-python" in capsys.readouterr().out


def test_cli_recursive_dry_run_preserves_relative_output_paths(tmp_path: Path, capsys) -> None:
    parts_dir = tmp_path / "parts"
    fixtures_dir = tmp_path / "fixtures"
    parts_dir.mkdir()
    fixtures_dir.mkdir()
    (parts_dir / "box.py").write_text("from pythonscad import *\n", encoding="utf-8")
    (fixtures_dir / "box.py").write_text("from pythonscad import *\n", encoding="utf-8")

    exit_code = cli.main(["--directory", str(tmp_path), "--dry-run", "--recursive"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert str(tmp_path / "output/parts/box.stl") in output
    assert str(tmp_path / "output/fixtures/box.stl") in output


def test_cli_returns_error_for_malformed_preset_file(tmp_path: Path) -> None:
    (tmp_path / "box.py").write_text("from pythonscad import *\n", encoding="utf-8")
    (tmp_path / "box.json").write_text(json.dumps({"notParameterSets": {}}), encoding="utf-8")

    assert cli.main(["--directory", str(tmp_path), "--dry-run"]) == 2


def test_cli_returns_success_when_no_designs_are_found(tmp_path: Path) -> None:
    (tmp_path / "utility.py").write_text("import json\n", encoding="utf-8")

    assert cli.main(["--directory", str(tmp_path), "--dry-run"]) == 0
