"""Command line interface for PythonSCAD STL generation."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import NoReturn

from docopt import docopt

from . import __version__
from .discovery import discover_designs
from .presets import PresetError
from .render import plan_jobs, run_jobs

USAGE = """PythonSCAD STL Generator.

Usage:
  generate-pythonscad-stls [--directory=<dir>] [--output-dir=<dir>]
                           [--pythonscad=<path>] [--format=<ext>]
                           [--force] [--dry-run] [--recursive]
                           [-v | --verbose]
  generate-pythonscad-stls -h | --help
  generate-pythonscad-stls --version

Options:
  -h --help                 Show this screen.
  --version                 Show the version.
  --directory=<dir>         Directory to scan for PythonSCAD designs [default: .].
  --output-dir=<dir>        Directory to save generated files to [default: output].
  --pythonscad=<path>       PythonSCAD executable to run [default: pythonscad].
  --format=<ext>            Output file extension/export format [default: stl].
  --force                   Render even when output files are up to date.
  --dry-run                 Print commands without executing them.
  --recursive               Search for designs recursively below the scan directory.
  -v --verbose              Show debug messages.
"""


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process-style exit code."""
    arguments = docopt(USAGE, argv=argv, version=f"generate-pythonscad-stls {__version__}")
    _configure_logging(verbose=bool(arguments["--verbose"]))

    directory = Path(str(arguments["--directory"])).resolve()
    output_dir = Path(str(arguments["--output-dir"]))
    if not output_dir.is_absolute():
        output_dir = directory / output_dir

    if not directory.is_dir():
        logging.error("%s is not a directory", directory)
        return 2

    try:
        designs = discover_designs(directory, recursive=bool(arguments["--recursive"]))
        if not designs:
            logging.info("No PythonSCAD designs found in %s", directory)
            return 0

        jobs = plan_jobs(
            designs,
            output_dir=output_dir,
            output_format=str(arguments["--format"]),
            pythonscad=str(arguments["--pythonscad"]),
        )
    except PresetError as error:
        logging.error("%s", error)
        return 2

    logging.info("Planned %d render job(s) from %d design(s)", len(jobs), len(designs))
    return run_jobs(
        jobs,
        force=bool(arguments["--force"]),
        dry_run=bool(arguments["--dry-run"]),
    )


def _configure_logging(*, verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def _entrypoint() -> NoReturn:
    raise SystemExit(main())


if __name__ == "__main__":
    sys.exit(main())
