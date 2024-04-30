"""This script reproduces the most common cellfinder workflow

It receives as an (optional) command line input the path to a configuration
json file, that holds the values of the required parameters for the workflow.

If no input json file is passed as a configuration, the default
configuration defined at brainglobe_workflows/cellfinder/default_config.json
is used.

Example usage:
 - to pass a custom configuration, run (from the cellfinder_main.py
   parent directory):
    python cellfinder_core.py --config path/to/input/config.json
 - to use the default configuration, run
    python cellfinder_core.py


"""

import json
import logging
import os
from typing import Union

from brainglobe_utils.IO.cells import save_cells
from cellfinder.core.main import main as cellfinder_run
from cellfinder.core.tools.IO import read_with_dask

from brainglobe_workflows.cellfinder_core.config import CellfinderConfig
from brainglobe_workflows.utils import (
    DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
    setup_logger,
)
from brainglobe_workflows.utils import __name__ as LOGGER_NAME

Pathlike = Union[str, os.PathLike]


def setup() -> CellfinderConfig:
    # setup logger
    _ = setup_logger()

    # read config
    cfg = setup_config()

    return cfg


def setup_config(log_on: bool = False) -> CellfinderConfig:
    """Instantiate a CellfinderConfig from the input json file.

    Assumes config is json serializable.

    Parameters
    ----------
    input_config_path : Path
        Absolute path to a cellfinder config file
    log_on : bool, optional
        whether to log the info messages from reading the config
        to the logger, by default False

    Returns
    -------
    CellfinderConfig:
        The cellfinder config object, populated with data from the input
    """

    # read input config: environment variable if it exists, else default
    input_config_path = os.getenv(
        "CELLFINDER_CONFIG_PATH",
        default=str(DEFAULT_JSON_CONFIG_PATH_CELLFINDER),
    )

    # read as dict
    with open(input_config_path) as cfg:
        config_dict = json.load(cfg)

    # pass dict to class
    config = CellfinderConfig(
        **config_dict
    )  # config is a dataclass but not an instance? why?

    # print config's origin to log if required
    if log_on:
        logger = logging.getLogger(LOGGER_NAME)
        logger.info(f"Input config read from {input_config_path}")
        if input_config_path == DEFAULT_JSON_CONFIG_PATH_CELLFINDER:
            logger.info("Using default config file")

    return config


def run_workflow(cfg: CellfinderConfig):
    """Run workflow based on the cellfinder.core.main.main()
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
    cfg : dict
        a dictionary with the required setup methods and parameters for
        the cellfinder workflow
    """
    # Read input data as Dask arrays
    signal_array = read_with_dask(str(cfg._signal_dir_path))
    background_array = read_with_dask(str(cfg._background_dir_path))

    # Run main analysis using `cellfinder_run`
    detected_cells = cellfinder_run(
        signal_array,
        background_array,
        cfg.voxel_sizes,
        cfg.start_plane,
        cfg.end_plane,
        cfg.trained_model,
        cfg.model_weights,
        cfg.model,
        cfg.batch_size,
        cfg.n_free_cpus,
        cfg.network_voxel_sizes,
        cfg.soma_diameter,
        cfg.ball_xy_size,
        cfg.ball_z_size,
        cfg.ball_overlap_fraction,
        cfg.log_sigma_size,
        cfg.n_sds_above_mean_thresh,
        cfg.soma_spread_factor,
        cfg.max_cluster_size,
        cfg.cube_width,
        cfg.cube_height,
        cfg.cube_depth,
        cfg.network_depth,
    )

    # Save results to xml file
    save_cells(
        detected_cells,
        cfg._detected_cells_path,
    )


def main() -> CellfinderConfig:
    """Setup and run cellfinder workflow.

    This function runs the setup steps required
    to run the cellfinder workflow, and the
    workflow itself. Note that only the workflow
    will be benchmarked.

    Returns
    -------
    cfg : CellfinderConfig
        a class with the required setup methods and parameters for
        the cellfinder workflow
    """

    # run setup
    # use environment variable CELLFINDER_CONFIG_PATH if exists,
    # otherwise use default
    # log which one is used
    cfg = setup()

    # run full workflow
    run_workflow(cfg)  # only this will be benchmarked

    return cfg


if __name__ == "__main__":
    # run setup and workflow
    _ = main()
