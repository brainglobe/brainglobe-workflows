import logging
import sys
from pathlib import Path

DEFAULT_JSON_CONFIGS_PATH = Path(__file__).resolve().parent / "configs"

DEFAULT_JSON_CONFIG_PATH_CELLFINDER = (
    DEFAULT_JSON_CONFIGS_PATH / "cellfinder.json"
)


def setup_logger() -> logging.Logger:
    """Setup a logger for workflow runs

    The logger's level is set to DEBUG, and it
    is linked to a handler that writes to the
    console. This utility function helps run
    workflows, and test their logs, in a
    consistent way.

    Returns
    -------
    logging.Logger
        a logger object configured for workflow runs
    """
    # define handler that writes to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter("%(name)s %(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)
    console_handler.set_name("console_handler")

    # define logger and link to handler
    logger = logging.getLogger(
        __name__
    )  # if imported as a module, the logger is named after the module
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger
