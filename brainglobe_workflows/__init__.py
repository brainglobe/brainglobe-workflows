from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("brainglobe-workflows")
except PackageNotFoundError:
    # package is not installed
    pass
