from pathlib import Path

from pythonscad_stl_generator.discovery import discover_designs, imports_pythonscad


def write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_imports_pythonscad_accepts_supported_import_forms(tmp_path: Path) -> None:
    import_forms = [
        "from pythonscad import *\n",
        "import pythonscad\n",
        "import pythonscad as ps\n",
        "from pythonscad import cube, show\n",
        "from pythonscad.extras import gear\n",
    ]

    for index, source in enumerate(import_forms):
        assert imports_pythonscad(write(tmp_path / f"design_{index}.py", source))


def test_imports_pythonscad_rejects_arbitrary_python(tmp_path: Path) -> None:
    script = write(tmp_path / "script.py", "import json\nprint(json.dumps({'ok': True}))\n")

    assert not imports_pythonscad(script)


def test_discover_designs_finds_only_current_directory_by_default(tmp_path: Path) -> None:
    design = write(tmp_path / "box.py", "from pythonscad import *\n")
    write(tmp_path / "utility.py", "import pathlib\n")
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    write(nested_dir / "nested_design.py", "import pythonscad\n")

    assert discover_designs(tmp_path) == [design]


def test_discover_designs_can_search_recursively(tmp_path: Path) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    nested_design = write(nested_dir / "nested_design.py", "import pythonscad\n")

    assert discover_designs(tmp_path, recursive=True) == [nested_design]
