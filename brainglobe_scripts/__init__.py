from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("brainglobe-scripts")
except PackageNotFoundError:
    # package is not installed
    pass
