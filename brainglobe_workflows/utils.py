# import argparse
import argparse
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
    console_handler.set_name("console_handler")

    # define logger and link to handler
    logger = logging.getLogger(
        __name__
    )  # if imported as a module, the logger is named after the module
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger


def config_parser(argv_: list[str], default_config: str) -> argparse.Namespace:
    """Define argument parser for cellfinder
    workflow script.

    It expects a path to a json file with the
    parameters required to run the workflow.
    If none is provided, the default

    Parameters
    ----------
    argv_ : list[str]
        List of strings to parse
    default_config : str
        path to default config if none is passed as a CLI argument

    Returns
    -------
    args : argparse.Namespace
        command line input arguments parsed
    """

    # initialise argument parser
    parser = argparse.ArgumentParser(
        description=(
            "To launch the workflow with "
            "a specific set of input parameters, run: "
            "`python brainglobe_workflows/cellfinder.py "
            "--config path/to/config.json`"
            "where path/to/input/config.json is the json file "
            "containing the workflow parameters."
        )
    )
    # add arguments
    parser.add_argument(
        "-c",
        "--config",
        default=default_config,
        type=str,
        metavar="CONFIG",  # a name for usage messages
        help="",
    )

    # build parser object
    args = parser.parse_args(argv_)

    return args
