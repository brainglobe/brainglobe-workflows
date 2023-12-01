import argparse
import logging
import sys
from pathlib import Path

DEFAULT_JSON_CONFIGS_PATH = Path(__file__).resolve().parent / "configs"

DEFAULT_JSON_CONFIG_PATH_CELLFINDER = (
    DEFAULT_JSON_CONFIGS_PATH / "cellfinder.json"
)


def setup_logger_and_parse_cli_arguments(argv):
    def setup_logger() -> logging.Logger:
        """Setup a logger for this script

        The logger's level is set to DEBUG, and it
        is linked to a handler that writes to the
        console and whose level is

        Returns
        -------
        logging.Logger
            a logger object
        """
        # define handler that writes to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(
            "%(name)s %(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_format)

        # define logger and link to handler
        logger = logging.getLogger(
            __name__
        )  # if imported as a module, the logger is named after the module
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
        return logger

    def parse_cli_arguments(argv_) -> argparse.Namespace:
        """Define argument parser for cellfinder
        workflow script.

        It expects a path to a json file with the
        parameters required to run the workflow.
        If none is provided, the default

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
                "`python cellfinder_main.py --config path/to/config.json`"
                "where path/to/input/config.json is the json file "
                "containing the workflow parameters."
            )
        )
        # add arguments
        parser.add_argument(
            "-c",
            "--config",
            default=str(
                DEFAULT_JSON_CONFIG_PATH_CELLFINDER
            ),  # can I do argv_[0]? --- TODO use typer!
            type=str,
            metavar="CONFIG",  # a name for usage messages
            help="",
        )

        # build parser object
        args = parser.parse_args(argv_)

        # print error if required arguments not provided
        if not args.config:
            logger.error("Paths to input config not provided.")
            parser.print_help()

        return args

    # setup logger
    logger = setup_logger()

    # parse command line arguments
    args = parse_cli_arguments(argv)

    return args, logger
