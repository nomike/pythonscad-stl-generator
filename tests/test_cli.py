import json
from pathlib import Path

import pythonscad_stl_generator.cli as cli


def test_cli_dry_run_renders_discovered_design(tmp_path: Path, capsys) -> None:
    (tmp_path / "box.py").write_text("from pythonscad import *\n", encoding="utf-8")

    exit_code = cli.main(["--directory", str(tmp_path), "--dry-run"])

    assert exit_code == 0
    assert "--trust-python" in capsys.readouterr().out


def test_cli_returns_error_for_malformed_preset_file(tmp_path: Path) -> None:
    (tmp_path / "box.py").write_text("from pythonscad import *\n", encoding="utf-8")
    (tmp_path / "box.json").write_text(json.dumps({"notParameterSets": {}}), encoding="utf-8")

    assert cli.main(["--directory", str(tmp_path), "--dry-run"]) == 2


def test_cli_returns_success_when_no_designs_are_found(tmp_path: Path) -> None:
    (tmp_path / "utility.py").write_text("import json\n", encoding="utf-8")

    assert cli.main(["--directory", str(tmp_path), "--dry-run"]) == 0
