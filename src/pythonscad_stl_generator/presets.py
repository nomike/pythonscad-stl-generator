"""Read PythonSCAD/OpenSCAD customizer preset files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class PresetError(ValueError):
    """Raised when a preset file is present but malformed."""


@dataclass(frozen=True)
class Preset:
    """One named customizer parameter set."""

    name: str
    values: dict[str, Any]


def preset_path_for(design_path: Path) -> Path:
    """Return the conventional sibling customizer JSON path for a design."""
    return design_path.with_suffix(".json")


def load_presets(path: Path) -> list[Preset]:
    """Load named presets from an OpenSCAD/PythonSCAD customizer JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PresetError(f"{path}: invalid JSON: {error}") from error
    except OSError as error:
        raise PresetError(f"{path}: cannot read preset file: {error}") from error

    parameter_sets = data.get("parameterSets")
    if not isinstance(parameter_sets, dict):
        raise PresetError(f"{path}: expected top-level 'parameterSets' object")

    presets: list[Preset] = []
    for name, values in parameter_sets.items():
        if not isinstance(values, dict):
            raise PresetError(f"{path}: preset {name!r} must be an object")
        presets.append(Preset(str(name), values))

    return presets
