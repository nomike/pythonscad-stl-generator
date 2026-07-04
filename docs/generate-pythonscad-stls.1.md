# generate-pythonscad-stls(1)

## Name

generate-pythonscad-stls - render PythonSCAD designs and customizer presets

## Synopsis

```text
generate-pythonscad-stls [--directory=<dir>] [--output-dir=<dir>]
                         [--pythonscad=<path>] [--format=<ext>]
                         [--force] [--dry-run] [--recursive]
                         [-v | --verbose]
generate-pythonscad-stls -h | --help
generate-pythonscad-stls --version
```

## Description

`generate-pythonscad-stls` scans a directory for Python files that import
`pythonscad` and renders each detected design by invoking the PythonSCAD
command line application. It passes `--trust-python` automatically.

When a design has a sibling JSON file with a top-level `parameterSets` object,
the design is rendered once for each named preset using PythonSCAD's `-p` and
`-P` customizer options.

## Options

`-h`, `--help`
: Show help text.

`--version`
: Show the program version.

`--directory=<dir>`
: Directory to scan for PythonSCAD designs. Defaults to the current directory.

`--output-dir=<dir>`
: Directory for generated output files. Relative paths are resolved below the
scan directory. Defaults to `output`.

`--pythonscad=<path>`
: PythonSCAD executable to run. Defaults to `pythonscad` from `PATH`.

`--format=<ext>`
: Output file extension and PythonSCAD export format. Defaults to `stl`.

`--force`
: Render even when output files are newer than their inputs.

`--dry-run`
: Print render commands without executing them.

`--recursive`
: Search for designs recursively below the scan directory.

`-v`, `--verbose`
: Enable debug logging.

## Files

`<design>.py`
: PythonSCAD design script. The file is detected as a design when it imports
`pythonscad`.

`<design>.json`
: Optional customizer preset file with a top-level `parameterSets` object.

## Examples

Render designs in the current directory:

```sh
generate-pythonscad-stls
```

Preview the commands that would be run:

```sh
generate-pythonscad-stls --dry-run --verbose
```

Use a specific PythonSCAD binary and output directory:

```sh
generate-pythonscad-stls --pythonscad ~/bin/pythonscad --output-dir stls
```

## Exit Status

`0`
: All requested renders completed successfully, or no designs were found.

`2`
: Command line input, scan directory, or preset JSON was invalid.

Any other non-zero status from `pythonscad`
: At least one render command failed; the PythonSCAD exit code is returned.
