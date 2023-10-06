"""A script reproducing the main cellfinder workflow

It assumes an environment variable called "CELLFINDER_CONFIG_PATH" exists,
which points to a json file with the required parameters. If the environment
variable does not exist, the default configuration parameters (defined in
DEFAULT_CONFIG_DICT below) are used

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
    Define input and output data locations, and parameters for
    preprocessing steps.
    """

    # cellfinder benchmarks cache directory
    install_path: Pathlike

    # origin of data to download (if required)
    data_url: Optional[str]
    data_hash: Optional[str]

    # cached subdirectory to save data to
    extract_relative_dir: Pathlike
    signal_parent_dir: str
    background_parent_dir: str
    output_path_basename: Pathlike
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

    list_signal_files: Optional[list] = None
    list_background_files: Optional[list] = None
    output_path: Optional[Pathlike] = None


# logger --- make this a function ?
def setup_logger():
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter("%(name)s %(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)
    logger = logging.getLogger(
        __name__
    )  # if imported as a module, the logger is named after the module
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger


def run_workflow_from_cellfinder_run(cfg):
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

    We plan to time each of the steps in the workflow individually,
    as well as the full workflow.

    Parameters
    ----------
    cfg : CellfinderConfig
        a class with the required setup methods and parameters for
        the cellfinder workflow
    """
    # Read input data as Dask arrays
    signal_array = read_with_dask(cfg.signal_parent_dir)
    background_array = read_with_dask(cfg.background_parent_dir)

    # Run main analysis using `cellfinder_run`
    detected_cells = cellfinder_run(
        signal_array, background_array, cfg.voxel_sizes
    )

    # Save results to xml file
    save_cells(detected_cells, cfg.output_path / cfg.detected_cells_filename)


def setup_workflow(input_config_path):
    """Prepare configuration to run workflow

    This includes
    - instantiating the config dictionary,
    - checking if the input data exists locally, and fetching from
      GIN repository otherwise,
    - creating a timestamped directory for the output of the workflow if
      it doesn't exist and adding it to the config


    Parameters
    ----------
    input_config_path : Path
        _description_

    Returns
    -------
    config : CellfinderConfig
        a class with the required setup methods and parameters for
        the cellfinder workflow
    """

    # Define config
    assert input_config_path.exists()

    # read config into dict
    # (assumes config is json serializable)
    with open(input_config_path) as cfg:
        config_dict = json.load(cfg)

    config = CellfinderConfig(**config_dict)

    logger.info(f"Input config read from {input_config_path}")
    if input_config_path == DEFAULT_JSON_CONFIG_PATH:
        logger.info("Using default config file")

    # Retrieve and add lists of input data to config if neither are defined
    if not (config.list_signal_files and config.list_signal_files):
        config = retrieve_input_data(config)

    # Create output directory if it doesn't exist, timestamped
    timestamp = datetime.datetime.now()
    timestamp_formatted = timestamp.strftime("%Y%m%d_%H%M%S")
    output_path_timestamped = Path(
        str(config.output_path_basename) + timestamp_formatted
    )
    output_path_timestamped.mkdir(parents=True, exist_ok=True)
    # add to config
    config.output_path = output_path_timestamped

    return config


def retrieve_input_data(config):
    """
    Adds the lists of input data files (signal and background) to the config.

    It first checks if the input data exists locally.
    - If both directories (signal and background) exist, the lists of signal
      and background files are added to the relevant config attributes
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
        Path(config.signal_parent_dir).exists()
        and Path(config.background_parent_dir).exists()
    ):
        logger.info("Fetching input data from the local directories")

        config.list_signal_files = [
            f for f in Path(config.signal_parent_dir).iterdir() if f.is_file()
        ]
        config.list_background_files = [
            f
            for f in Path(config.background_parent_dir).iterdir()
            if f.is_file()
        ]

    # If exactly one of the input data directories is missing, print error
    elif (
        Path(config.signal_parent_dir).exists()
        or Path(config.background_parent_dir).exists()
    ):
        if not Path(config.signal_parent_dir).exists():
            logger.error(
                f"The directory {config.signal_parent_dir} does not exist"
            )
        else:
            logger.error(
                f"The directory {config.background_parent_dir} does not exist"
            )

    # If neither of them exist, retrieve data from GIN repository
    else:
        if (not config.data_url) or (not config.data_hash):
            logger.error(
                "Input data not found locally, and URL/hash to "
                "GIN repository not provided"
            )

        else:
            # get list of files in GIN archive with retrieve
            list_files_archive = pooch.retrieve(
                url=config.data_url,
                known_hash=config.data_hash,
                path=config.install_path,  # path to download zip to
                progressbar=True,
                processor=pooch.Unzip(
                    extract_dir=config.extract_relative_dir
                    # path to unzipped dir, *relative*  to 'path'
                ),
            )
            logger.info("Fetching input data from the provided GIN repository")

            # check signal and background parent directories exist now
            assert Path(config.signal_parent_dir).exists()
            assert Path(config.background_parent_dir).exists()

            # add signal files to config
            config.list_signal_files = [
                f
                for f in list_files_archive
                if f.startswith(config.signal_parent_dir)
            ]

            # add background files to config
            config.list_background_files = [
                f
                for f in list_files_archive
                if f.startswith(config.background_parent_dir)
            ]

    return config


def parse_cli_arguments():
    # initialise argument parser
    parser = argparse.ArgumentParser(
        description=(
            "To launch the workflow with "
            "a desired set of input parameters, run:"
            " `python cellfinder_main path/to/input/config.json` "
            " where path/to/input/config.json is the json file "
            "containing the workflow parameters."
        )
    )
    # add required arguments
    # add --config?
    parser.add_argument(
        "-c",
        "--config",
        default=str(DEFAULT_JSON_CONFIG_PATH),
        type=str,
        metavar="CONFIG",  # a name for usage messages
        help="",
    )
    # build parser object
    args = parser.parse_args()

    # error if required arguments not provided
    if not args.config:
        logger.error("Paths to input config not provided.")
        parser.print_help()

    return args


if __name__ == "__main__":
    # setup logger
    logger = setup_logger()

    # parse command line arguments
    args = parse_cli_arguments()

    # run workflow
    cfg = setup_workflow(Path(args.config))
    run_workflow_from_cellfinder_run(cfg)  # only this will be benchmarked
