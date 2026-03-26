"""FociPy — automated kinetics analysis of DNA repair protein recruitment."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("focipy")
except PackageNotFoundError:
    __version__ = "0.3.0"
