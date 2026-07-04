import json
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from pythonscad_stl_generator.render import (
    RenderJob,
    build_command,
    is_up_to_date,
    output_path_for,
    plan_jobs,
    run_jobs,
    sanitize_filename_part,
)


def test_sanitize_filename_part_replaces_unsafe_characters() -> None:
    assert sanitize_filename_part("Size/Large: 20 mm") == "Size_Large_20_mm"
    assert sanitize_filename_part("...") == "preset"


def test_output_path_for_adds_preset_name_when_present(tmp_path: Path) -> None:
    assert (
        output_path_for(tmp_path / "box.py", tmp_path / "out", "stl", None)
        == tmp_path / "out/box.stl"
    )
    assert (
        output_path_for(tmp_path / "box.py", tmp_path / "out", ".3mf", "Size/Large")
        == tmp_path / "out/box-Size_Large.3mf"
    )


def test_build_command_includes_trust_python_and_presets(tmp_path: Path) -> None:
    command = build_command(
        pythonscad="/usr/bin/pythonscad",
        design_path=tmp_path / "box.py",
        output_path=tmp_path / "out/box-large.stl",
        preset_path=tmp_path / "box.json",
        preset_name="large",
    )

    assert command == (
        "/usr/bin/pythonscad",
        "-o",
        str(tmp_path / "out/box-large.stl"),
        "--trust-python",
        "-p",
        str(tmp_path / "box.json"),
        "-P",
        "large",
        str(tmp_path / "box.py"),
    )


def test_plan_jobs_uses_sibling_parameter_sets(tmp_path: Path) -> None:
    design = tmp_path / "box.py"
    design.write_text("from pythonscad import *\n", encoding="utf-8")
    (tmp_path / "box.json").write_text(
        json.dumps({"parameterSets": {"small": {"width": "10"}, "large": {"width": "20"}}}),
        encoding="utf-8",
    )

    jobs = plan_jobs(
        [design],
        output_dir=tmp_path / "out",
        output_format="stl",
        pythonscad="pythonscad",
    )

    assert [job.preset_name for job in jobs] == ["small", "large"]
    assert [job.output_path.name for job in jobs] == ["box-small.stl", "box-large.stl"]


def test_is_up_to_date_compares_all_dependencies(tmp_path: Path) -> None:
    design = tmp_path / "box.py"
    preset = tmp_path / "box.json"
    output = tmp_path / "out.stl"
    for path in (design, preset, output):
        path.write_text("", encoding="utf-8")

    os.utime(design, (10, 10))
    os.utime(preset, (20, 20))
    os.utime(output, (30, 30))
    assert is_up_to_date(output, [design, preset])

    os.utime(preset, (40, 40))
    assert not is_up_to_date(output, [design, preset])


def test_run_jobs_dry_run_prints_command_without_runner(tmp_path: Path, capsys) -> None:
    job = RenderJob(
        design_path=tmp_path / "box.py",
        output_path=tmp_path / "out/box.stl",
        command=(
            "pythonscad",
            "-o",
            str(tmp_path / "out/box.stl"),
            "--trust-python",
            str(tmp_path / "box.py"),
        ),
    )

    exit_code = run_jobs([job], dry_run=True, runner=_failing_runner)

    assert exit_code == 0
    assert "pythonscad -o" in capsys.readouterr().out


def test_run_jobs_skips_up_to_date_outputs(tmp_path: Path) -> None:
    design = tmp_path / "box.py"
    output = tmp_path / "out/box.stl"
    output.parent.mkdir()
    design.write_text("", encoding="utf-8")
    output.write_text("", encoding="utf-8")
    os.utime(design, (10, 10))
    os.utime(output, (20, 20))
    calls: list[Sequence[str]] = []
    job = RenderJob(design_path=design, output_path=output, command=("pythonscad", str(design)))

    exit_code = run_jobs([job], runner=lambda command: _recording_runner(command, calls))

    assert exit_code == 0
    assert calls == []


def test_run_jobs_propagates_nonzero_exit_code(tmp_path: Path) -> None:
    design = tmp_path / "box.py"
    design.write_text("", encoding="utf-8")
    job = RenderJob(
        design_path=design,
        output_path=tmp_path / "out/box.stl",
        command=("pythonscad", str(design)),
    )

    assert run_jobs([job], runner=_failing_runner) == 7


def _recording_runner(
    command: Sequence[str],
    calls: list[Sequence[str]],
) -> subprocess.CompletedProcess[str]:
    calls.append(tuple(command))
    return subprocess.CompletedProcess(command, 0)


def _failing_runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, 7)
