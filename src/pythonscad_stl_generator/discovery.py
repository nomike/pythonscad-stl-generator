"""Discover PythonSCAD design scripts."""

from __future__ import annotations

import ast
import logging
from collections.abc import Iterable
from pathlib import Path

LOG = logging.getLogger(__name__)


def imports_pythonscad(path: Path) -> bool:
    """Return whether *path* imports the public PythonSCAD module."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as error:
        LOG.debug("Skipping %s: cannot parse as Python (%s)", path, error)
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                alias.name == "pythonscad" or alias.name.startswith("pythonscad.")
                for alias in node.names
            ):
                return True
        elif isinstance(node, ast.ImportFrom) and (
            node.module == "pythonscad" or (node.module or "").startswith("pythonscad.")
        ):
            return True

    return False


def discover_designs(directory: Path, *, recursive: bool = False) -> list[Path]:
    """Find Python files in *directory* that import ``pythonscad``."""
    pattern = "**/*.py" if recursive else "*.py"
    candidates: Iterable[Path] = directory.glob(pattern)
    designs = [path for path in sorted(candidates) if path.is_file() and imports_pythonscad(path)]
    LOG.debug("Discovered %d PythonSCAD design(s) in %s", len(designs), directory)
    return designs
