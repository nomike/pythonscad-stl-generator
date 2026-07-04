# PythonSCAD STL Generator

PythonSCAD STL Generator is a small command line tool for batch-rendering
PythonSCAD design files. It scans a directory for Python files that import
`pythonscad`, renders each design with the `pythonscad` executable from
`PATH`, and optionally renders once per customizer preset from a sibling JSON
file.

## Installation

Install the published package with `pipx`:

```sh
pipx install pythonscad-stl-generator
```

Or install it into an existing environment with `pip`:

```sh
python -m pip install pythonscad-stl-generator
```

For development:

```sh
git clone https://github.com/nomike/pythonscad-stl-generator.git
cd pythonscad-stl-generator
python -m pip install -e ".[dev]"
```

PythonSCAD itself is not bundled. The tool expects a `pythonscad` executable to
be available on `PATH`, or you can point to it explicitly with
`--pythonscad=/path/to/pythonscad`.

## Usage

From a directory containing PythonSCAD designs:

```sh
generate-pythonscad-stls
```

The command writes STL files to `output/` by default. A Python file is treated
as a design when it imports `pythonscad`, for example:

```python
from pythonscad import *

width = add_parameter("width", 20)
cube([width, width, width]).show()
```

Useful options:

```sh
generate-pythonscad-stls --output-dir stls
generate-pythonscad-stls --pythonscad ~/bin/pythonscad
generate-pythonscad-stls --format 3mf
generate-pythonscad-stls --dry-run --verbose
generate-pythonscad-stls --recursive
```

The generated PythonSCAD command includes `--trust-python`, because PythonSCAD
requires that flag for command-line execution of Python input files.

## Customizer Presets

If `box.py` has a sibling `box.json`, the tool reads its top-level
`parameterSets` object and renders once per preset:

```json
{
  "parameterSets": {
    "small": {
      "width": "10"
    },
    "large": {
      "width": "50"
    }
  },
  "fileFormatVersion": "1"
}
```

This produces files like:

```text
output/box-small.stl
output/box-large.stl
```

Without a sibling preset file, the design renders once to `output/box.stl`.

## Up-To-Date Checks

Existing output files are skipped when they are newer than their inputs. For a
plain design, the input is the `.py` file. For preset renders, both the `.py`
file and the sibling `.json` preset file must be older than the output.

Use `--force` to render everything regardless of timestamps.

## Development

Run tests:

```sh
python -m pytest
```

Run linting and formatting:

```sh
ruff check .
ruff format .
```

Run all pre-commit hooks:

```sh
pre-commit run --all-files
```

## License

This project is licensed under the MIT License. See `LICENSE`.
