"""This script reproduces the most common cellfinder workflow

It receives as an (optional) command line input the path to a configuration
json file, that holds the values of the required parameters for the workflow.

If no input json file is passed as a configuration, the default
configuration defined at brainglobe_workflows/cellfinder/default_config.json
is used.

Example usage:
 - to pass a custom configuration, run (from the cellfinder_main.py
   parent directory):
    python cellfinder_main.py --config path/to/input/config.json
 - to use the default configuration, run
    python cellfinder_main.py


"""

import argparse
import datetime
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

import pooch
from brainglobe_utils.IO.cells import save_cells
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask
from cellfinder_core.train.train_yml import depth_type

Pathlike = Union[str, os.PathLike]

DEFAULT_JSON_CONFIG_PATH = (
    Path(__file__).resolve().parent / "default_config.json"
)


@dataclass
class CellfinderConfig:
    """
    Define input and output data locations, and the parameters for
    the cellfinder preprocessing steps.
    """

    # cellfinder workflows cache directory
    install_path: Pathlike

    # cached subdirectory to save data to
    extract_dir_relative: Pathlike
    signal_subdir: str
    background_subdir: str
    output_path_basename_relative: Pathlike
    detected_cells_filename: Pathlike

    # preprocessing parameters
    voxel_sizes: Tuple[float, float, float]
    start_plane: int
    end_plane: int
    trained_model: Optional[
        os.PathLike
    ]  # if None, it will use a default model
    model_weights: Optional[os.PathLike]
    model: str
    batch_size: int
    n_free_cpus: int
    network_voxel_sizes: Tuple[int, int, int]
    soma_diameter: int
    ball_xy_size: int
    ball_z_size: int
    ball_overlap_fraction: float
    log_sigma_size: float
    n_sds_above_mean_thresh: int
    soma_spread_factor: float
    max_cluster_size: int
    cube_width: int
    cube_height: int
    cube_depth: int
    network_depth: depth_type

    # origin of data to download (if required)
    data_url: Optional[str] = None
    data_hash: Optional[str] = None

    # The following attributes are added
    # during the setup phase of the workflow
    list_signal_files: Optional[list] = None
    list_background_files: Optional[list] = None
    output_path: Pathlike = ""
    signal_dir_path: Pathlike = ""
    background_dir_path: Pathlike = ""
    detected_cells_path: Pathlike = ""


def setup(argv=None) -> CellfinderConfig:
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
            default=str(DEFAULT_JSON_CONFIG_PATH),
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

    def setup_workflow(input_config_path: Path) -> CellfinderConfig:
        """Run setup steps prior to executing the workflow

        These setup steps include:
        - instantiating a CellfinderConfig object with the required parameters,
        - checking if the input data exists locally, and fetching from
        GIN repository otherwise,
        - adding the path to the input data files to the config, and
        - creating a timestamped directory for the output of the workflow if
        it doesn't exist and adding its path to the config

        Parameters
        ----------
        input_config_path : Path
            path to the input config file

        Returns
        -------
        config : CellfinderConfig
            a dataclass whose attributes are the parameters
            for running cellfinder.
        """

        # Check config file exists
        assert input_config_path.exists()

        # Instantiate a CellfinderConfig from the input json file
        # (assumes config is json serializable)
        with open(input_config_path) as cfg:
            config_dict = json.load(cfg)
        config = CellfinderConfig(**config_dict)

        # Print info logs for status
        logger.info(f"Input config read from {input_config_path}")
        if input_config_path == DEFAULT_JSON_CONFIG_PATH:
            logger.info("Using default config file")

        # Retrieve and add lists of input data to the config,
        # if these are defined yet
        if not (config.list_signal_files and config.list_signal_files):
            # build fullpaths to inputs
            config.signal_dir_path = str(
                Path(config.install_path)
                / config.extract_dir_relative
                / config.signal_subdir
            )
            config.background_dir_path = str(
                Path(config.install_path)
                / config.extract_dir_relative
                / config.background_subdir
            )
            # retrieve data
            config = retrieve_input_data(config)

        # Create timestamped output directory if it doesn't exist
        timestamp = datetime.datetime.now()
        timestamp_formatted = timestamp.strftime("%Y%m%d_%H%M%S")
        output_path_timestamped = Path(config.install_path) / (
            str(config.output_path_basename_relative) + timestamp_formatted
        )
        output_path_timestamped.mkdir(parents=True, exist_ok=True)

        # Add output path and output file path to config
        config.output_path = output_path_timestamped
        config.detected_cells_path = (
            config.output_path / config.detected_cells_filename
        )

        return config

    def retrieve_input_data(config: CellfinderConfig) -> CellfinderConfig:
        """
        Adds the lists of input data files (signal and background)
        to the config.

        It first checks if the input data exists locally.
        - If both directories (signal and background) exist, the lists of
        signal and background files are added to the config.
        - If exactly one of the input data directories is missing, an error
        message is logged.
        - If neither of them exist, the data is retrieved from the provided GIN
        repository. If no URL or hash to GIN is provided, an error is shown.

        Parameters
        ----------
        config : CellfinderConfig
            a dataclass whose attributes are the parameters
            for running cellfinder.

        Returns
        -------
        config : CellfinderConfig
            a dataclass whose attributes are the parameters
            for running cellfinder.
        """
        # Check if input data (signal and background) exist locally.
        # If both directories exist, get list of signal and background files
        if (
            Path(config.signal_dir_path).exists()
            and Path(config.background_dir_path).exists()
        ):
            logger.info("Fetching input data from the local directories")

            config.list_signal_files = [
                f
                for f in Path(config.signal_dir_path).resolve().iterdir()
                if f.is_file()
            ]
            config.list_background_files = [
                f
                for f in Path(config.background_dir_path).resolve().iterdir()
                if f.is_file()
            ]

        # If exactly one of the input data directories is missing, print error
        elif (
            Path(config.signal_dir_path).resolve().exists()
            or Path(config.background_dir_path).resolve().exists()
        ):
            if not Path(config.signal_dir_path).resolve().exists():
                logger.error(
                    f"The directory {config.signal_dir_path} does not exist"
                )
            else:
                logger.error(
                    f"The directory {config.background_dir_path} "
                    "does not exist"
                )

        # If neither of them exist, retrieve data from GIN repository
        else:
            # check if GIN URL and hash are defined (log error otherwise)
            if (not config.data_url) or (not config.data_hash):
                logger.error(
                    "Input data not found locally, and URL/hash to "
                    "GIN repository not provided"
                )

            else:
                # get list of files in GIN archive with pooch.retrieve
                list_files_archive = pooch.retrieve(
                    url=config.data_url,
                    known_hash=config.data_hash,
                    path=config.install_path,  # zip will be downloaded here
                    progressbar=True,
                    processor=pooch.Unzip(
                        extract_dir=config.extract_dir_relative
                        # path to unzipped dir,
                        # *relative* to the path set in 'path'
                    ),
                )
                logger.info(
                    "Fetching input data from the provided GIN repository"
                )

                # Check signal and background parent directories exist now
                assert Path(config.signal_dir_path).resolve().exists()
                assert Path(config.background_dir_path).resolve().exists()

                # Add signal files to config
                config.list_signal_files = [
                    f
                    for f in list_files_archive
                    if f.startswith(
                        str(Path(config.signal_dir_path).resolve())
                    )  # if str(config.signal_dir_path) in f
                ]

                # Add background files to config
                config.list_background_files = [
                    f
                    for f in list_files_archive
                    if f.startswith(
                        str(Path(config.background_dir_path).resolve())
                    )  # if str(config.background_dir_path) in f
                ]

        return config

    # parse command line input arguments:
    # sys.argv in most cases except for testing
    # see https://paiml.com/docs/home/books/testing-in-python/chapter08-monkeypatching/#the-simplest-monkeypatching
    argv = argv or sys.argv[1:]
    args = parse_cli_arguments(argv)

    # setup logger
    logger = setup_logger()

    # run setup steps and return config
    cfg = setup_workflow(Path(args.config))

    return cfg


def run_workflow_from_cellfinder_run(cfg: CellfinderConfig):
    """
    Run workflow based on the cellfinder_core.main.main()
    function.

    The steps are:
    1. Read the input signal and background data as two separate
       Dask arrays.
    2. Run the main cellfinder pipeline on the input Dask arrays,
       with the parameters defined in the input configuration (cfg).
    3. Save the detected cells as an xml file to the location specified in
       the input configuration (cfg).

    Parameters
    ----------
    cfg : CellfinderConfig
        a class with the required setup methods and parameters for
        the cellfinder workflow
    """
    # Read input data as Dask arrays
    signal_array = read_with_dask(cfg.signal_dir_path)
    background_array = read_with_dask(cfg.background_dir_path)

    # Run main analysis using `cellfinder_run`
    detected_cells = cellfinder_run(
        signal_array, background_array, cfg.voxel_sizes
    )

    # Save results to xml file
    save_cells(
        detected_cells,
        cfg.detected_cells_path,
    )


if __name__ == "__main__":
    # run setup
    cfg = setup()

    # run workflow
    run_workflow_from_cellfinder_run(cfg)  # only this will be benchmarked
