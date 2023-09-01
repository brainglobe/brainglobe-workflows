from importlib.metadata import metadata

__version__ = metadata("brainglobe_workflows")["version"]
__author__ = metadata("brainglobe_workflows")["author-email"]
__license__ = metadata("brainglobe_workflows")["license"]

del metadata
