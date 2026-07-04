"""Tools for batch-rendering PythonSCAD designs."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pythonscad-stl-generator")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
