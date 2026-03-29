"""BinaryByte — Infrastructure layer for AI coding agents."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("binarybyte")
except PackageNotFoundError:
    __version__ = "0.3.0"
