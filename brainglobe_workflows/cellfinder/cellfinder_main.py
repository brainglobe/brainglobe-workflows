import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

import pooch
from brainglobe_utils.IO.cells import save_cells
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask
from cellfinder_core.train.train_yml import depth_type

Pathlike = Union[str, os.PathLike]

# logger
# if imported as a module, the logger is named after the module
logger = logging.getLogger(__name__)

# Default config
DATA_URL = "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip"
DATA_HASH = "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914"
CELLFINDER_CACHE_DIR = Path.home() / ".cellfinder_benchmarks"

default_config_dict = {
    "install_path": CELLFINDER_CACHE_DIR,
    "data_url": DATA_URL,
    "data_hash": DATA_HASH,
    "local_path": CELLFINDER_CACHE_DIR / "cellfinder_test_data",
    "signal_parent_dir": str(
        CELLFINDER_CACHE_DIR / "cellfinder_test_data" / "signal"
    ),
    "background_parent_dir": str(
        CELLFINDER_CACHE_DIR / "cellfinder_test_data" / "background"
    ),
    "output_path": CELLFINDER_CACHE_DIR / "cellfinder_output",
    "detected_cells_filepath": (
        CELLFINDER_CACHE_DIR / "cellfinder_output" / "detected_cells.xml"
    ),
    "voxel_sizes": [5, 2, 2],  # microns
    "start_plane": 0,
    "end_plane": -1,
    "trained_model": None,  # if None, it will use a default model
    "model_weights": None,
    "model": "resnet50_tv",
    "batch_size": 32,
    "n_free_cpus": 2,
    "network_voxel_sizes": [5, 1, 1],
    "soma_diameter": 16,
    "ball_xy_size": 6,
    "ball_z_size": 15,
    "ball_overlap_fraction": 0.6,
    "log_sigma_size": 0.2,
    "n_sds_above_mean_thresh": 10,
    "soma_spread_factor": 1.4,
    "max_cluster_size": 100000,
    "cube_width": 50,
    "cube_height": 50,
    "cube_depth": 20,
    "network_depth": "50",
}


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
    local_path: Pathlike
    signal_parent_dir: str
    background_parent_dir: str
    output_path: Pathlike
    detected_cells_filepath: Pathlike

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


def example_cellfinder_script():
    cfg = setup_workflow()
    run_workflow_from_cellfinder_run(cfg)


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
    save_cells(detected_cells, cfg.detected_cells_filepath)


def setup_workflow(default_config_dict: dict = default_config_dict):
    """Prepare configuration to run workflow

    This includes
    - instantiating the config dictionary,
    - checking if the input data exists locally, and fetching from
      GIN repository otherwise,
    - creating the directory for the output of the workflow if it doesn't exist

    To instantiate the config dictionary, we first check if an environment
    variable "CELLFINDER_CONFIG_PATH" pointing to a config json file exists.
    If not, the default config is used.

    Parameters
    ----------
    default_config_dict : dict
        a dictionary with the default config parameters

    Returns
    -------
    _type_
        _description_
    """

    # Define config
    if "CELLFINDER_CONFIG_PATH" in os.environ.keys():
        input_config_path = Path(os.environ["CELLFINDER_CONFIG_PATH"])
        assert input_config_path.exists()

        # read config into dict
        # (assumes config is json serializable)
        with open(input_config_path) as cfg:
            config_dict = json.load(cfg)

        config = CellfinderConfig(**config_dict)

        logger.info(
            "Configuration retrieved from "
            f'{os.environ["CELLFINDER_CONFIG_PATH"]}'
        )

    else:
        config = CellfinderConfig(**default_config_dict)
        logger.info("Using default configuration")

    # Retrieve and add lists of input data to config if neither are defined
    if not (config.list_signal_files and config.list_signal_files):
        config = retrieve_input_data(config)

    # Create output directory if it doesn't exist
    # TODO: should I check if it exists and has data in it?
    # it will be overwritten
    Path(config.output_path).mkdir(parents=True, exist_ok=True)

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
                    extract_dir=config.local_path  # path to unzipped dir
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


if __name__ == "__main__":
    example_cellfinder_script()
