# import argparse
import logging
import sys
from pathlib import Path

DEFAULT_JSON_CONFIGS_PATH = Path(__file__).resolve().parent / "configs"

DEFAULT_JSON_CONFIG_PATH_CELLFINDER = (
    DEFAULT_JSON_CONFIGS_PATH / "cellfinder.json"
)


def setup_logger() -> logging.Logger:
    """Setup a logger for this script

    The logger's level is set to DEBUG, and it
    is linked to a handler that writes to the
    console

    Returns
    -------
    logging.Logger
        a logger object
    """
    # define handler that writes to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter("%(name)s %(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)

    # define logger and link to handler
    logger = logging.getLogger(
        __name__
    )  # if imported as a module, the logger is named after the module
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger
