"""Plan and execute PythonSCAD renders."""

from __future__ import annotations

import logging
import re
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .presets import Preset, load_presets, preset_path_for

LOG = logging.getLogger(__name__)

RunResult = subprocess.CompletedProcess[str]
Runner = Callable[[Sequence[str]], RunResult]


@dataclass(frozen=True)
class RenderJob:
    """A single PythonSCAD export command."""

    design_path: Path
    output_path: Path
    command: tuple[str, ...]
    preset_path: Path | None = None
    preset_name: str | None = None

    @property
    def dependencies(self) -> tuple[Path, ...]:
        """Inputs that make this job stale when newer than the output."""
        if self.preset_path is None:
            return (self.design_path,)
        return (self.design_path, self.preset_path)


def sanitize_filename_part(value: str) -> str:
    """Replace characters that are awkward or unsafe in output filenames."""
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return sanitized or "preset"


def output_path_for(
    design_path: Path,
    output_dir: Path,
    output_format: str,
    preset_name: str | None,
) -> Path:
    """Build an output path for a design and optional preset."""
    extension = output_format.lstrip(".")
    stem = sanitize_filename_part(design_path.stem)
    if preset_name:
        stem = f"{stem}-{sanitize_filename_part(preset_name)}"
    return output_dir / f"{stem}.{extension}"


def build_command(
    *,
    pythonscad: str,
    design_path: Path,
    output_path: Path,
    preset_path: Path | None = None,
    preset_name: str | None = None,
) -> tuple[str, ...]:
    """Construct the PythonSCAD CLI invocation for one render."""
    command = [pythonscad, "-o", str(output_path), "--trust-python"]
    if preset_path is not None and preset_name is not None:
        command.extend(["-p", str(preset_path), "-P", preset_name])
    command.append(str(design_path))
    return tuple(command)


def is_up_to_date(output_path: Path, dependencies: Sequence[Path]) -> bool:
    """Return whether *output_path* is newer than all dependency paths."""
    if not output_path.exists():
        return False
    output_mtime = output_path.stat().st_mtime
    return all(dependency.stat().st_mtime <= output_mtime for dependency in dependencies)


def plan_jobs(
    designs: Sequence[Path],
    *,
    output_dir: Path,
    output_format: str,
    pythonscad: str,
) -> list[RenderJob]:
    """Create render jobs for designs and their optional customizer presets."""
    jobs: list[RenderJob] = []
    for design_path in designs:
        preset_path = preset_path_for(design_path)
        if preset_path.exists():
            presets = load_presets(preset_path)
            for preset in presets:
                jobs.append(
                    _job_for_preset(
                        design_path=design_path,
                        output_dir=output_dir,
                        output_format=output_format,
                        pythonscad=pythonscad,
                        preset_path=preset_path,
                        preset=preset,
                    )
                )
        else:
            output_path = output_path_for(design_path, output_dir, output_format, None)
            jobs.append(
                RenderJob(
                    design_path=design_path,
                    output_path=output_path,
                    command=build_command(
                        pythonscad=pythonscad,
                        design_path=design_path,
                        output_path=output_path,
                    ),
                )
            )
    return jobs


def run_jobs(
    jobs: Sequence[RenderJob],
    *,
    force: bool = False,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> int:
    """Execute planned render jobs and return a process-style exit code."""
    actual_runner = runner or _default_runner
    exit_code = 0

    for job in jobs:
        if not force and is_up_to_date(job.output_path, job.dependencies):
            LOG.info("%s is up to date", job.output_path)
            continue

        job.output_path.parent.mkdir(parents=True, exist_ok=True)
        LOG.info("Rendering %s", job.output_path)
        LOG.debug("Running command: %r", list(job.command))
        if dry_run:
            print(" ".join(job.command))
            continue

        result = actual_runner(job.command)
        if result.returncode != 0:
            exit_code = result.returncode
            LOG.error(
                "PythonSCAD failed for %s with exit code %s",
                job.design_path,
                result.returncode,
            )

    return exit_code


def _job_for_preset(
    *,
    design_path: Path,
    output_dir: Path,
    output_format: str,
    pythonscad: str,
    preset_path: Path,
    preset: Preset,
) -> RenderJob:
    output_path = output_path_for(design_path, output_dir, output_format, preset.name)
    return RenderJob(
        design_path=design_path,
        output_path=output_path,
        command=build_command(
            pythonscad=pythonscad,
            design_path=design_path,
            output_path=output_path,
            preset_path=preset_path,
            preset_name=preset.name,
        ),
        preset_path=preset_path,
        preset_name=preset.name,
    )


def _default_runner(command: Sequence[str]) -> RunResult:
    return subprocess.run(command, check=False)
