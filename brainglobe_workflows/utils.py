# import argparse
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

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


def config_parser(
    default_config: str,
    argv_: Optional[list[str]] = None,
) -> argparse.Namespace:
    """Define argument parser for a workflow script.

    The only CLI argument defined in the parser is
    the input config file. The default config to use if
    no config is passed must be passed as an input to this
    function. The list of input arguments `arg_v` can be
    an empty list or None.

    Parameters
    ----------
    default_config : str
        _description_
    argv_ : Optional[list[str]], optional
        _description_, by default None

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
    if not argv_:
        argv_ = []
    args = parser.parse_args(argv_)

    return args
