import json
from pathlib import Path

import pytest

from pythonscad_stl_generator.presets import Preset, PresetError, load_presets, preset_path_for


def test_preset_path_for_uses_design_stem(tmp_path: Path) -> None:
    assert preset_path_for(tmp_path / "gear.py") == tmp_path / "gear.json"


def test_load_presets_reads_parameter_sets(tmp_path: Path) -> None:
    preset_file = tmp_path / "box.json"
    preset_file.write_text(
        json.dumps(
            {
                "parameterSets": {
                    "small": {"width": "10"},
                    "large": {"width": "50"},
                },
                "fileFormatVersion": "1",
            }
        ),
        encoding="utf-8",
    )

    assert load_presets(preset_file) == [
        Preset("small", {"width": "10"}),
        Preset("large", {"width": "50"}),
    ]


def test_load_presets_requires_parameter_sets_object(tmp_path: Path) -> None:
    preset_file = tmp_path / "box.json"
    preset_file.write_text("{}", encoding="utf-8")

    with pytest.raises(PresetError, match="parameterSets"):
        load_presets(preset_file)
