from importlib.metadata import PackageNotFoundError, metadata

try:
    __version__ = metadata("brainglobe_workflows")["version"]
    __author__ = metadata("brainglobe_workflows")["author-email"]
    __license__ = metadata("brainglobe_workflows")["license"]
except PackageNotFoundError:
    # Package not installed
    pass

del metadata
