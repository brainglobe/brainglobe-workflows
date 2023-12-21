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


import datetime
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import pooch
from brainglobe_utils.IO.cells import save_cells
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask
from cellfinder_core.train.train_yml import depth_type

from brainglobe_workflows.utils import (
    DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
    config_parser,
    setup_logger,
)
from brainglobe_workflows.utils import __name__ as LOGGER_NAME

Pathlike = Union[str, os.PathLike]


@dataclass
class CellfinderConfig:
    """Define input and output data locations, and the parameters for
    the cellfinder preprocessing steps.

    We distinguish three types of fields:
    - required fields: must be provided, they do not have a default value
    - optional fields: they have a default value
    - internal fields: their names start with _ indicating these are private.
      Any functionality to update them is moved to a method of
      CellfinderConfig.

    Notes on optional parameters:
    - input data path: if not specified, the are assumed to be "signal" and
      "background" dirs under _install_path/cellfinder_test_data/
      (see __post_init__ method).
    - output data path: if not specified, it is assumed to be under
      _install_path/output_dir_basename (see __post_init__ method).
    - data_url, data_hash: source of data to download. If not specified
      in JSON, it is set to None.
    """

    # Required parameters
    voxel_sizes: tuple[float, float, float]
    start_plane: int
    end_plane: int
    trained_model: Optional[os.PathLike]
    model_weights: Optional[os.PathLike]
    model: str
    batch_size: int
    n_free_cpus: int
    network_voxel_sizes: tuple[int, int, int]
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

    # Optional parameters
    # they have a default value if not specified in json

    # install path: default path for downloaded and output data
    _install_path: Pathlike = (
        Path.home() / ".brainglobe" / "workflows" / "cellfinder_core"
    )

    # input data path:
    # if not specified, the are assumed to be "signal" and
    # "background" dirs under _install_path/cellfinder_test_data/
    # (see __post_init__ method)
    input_data_dir: Optional[Pathlike] = None
    signal_subdir: Pathlike = "signal"
    background_subdir: Pathlike = "background"

    # output data path:
    # if not specified, it is assumed to be under
    # _install_path/output_dir_basename
    # (see __post_init__ method)
    output_dir_basename: str = "cellfinder_output_"
    detected_cells_filename: str = "detected_cells.xml"
    output_parent_dir: Optional[Pathlike] = None

    # source of data to download
    # if not specified in JSON, it is set to None
    data_url: Optional[str] = None
    data_hash: Optional[str] = None

    # Internal parameters
    # even though these are optional we don't expect users to
    # change them
    _signal_dir_path: Optional[Pathlike] = None
    _background_dir_path: Optional[Pathlike] = None
    _list_signal_files: Optional[list] = None
    _list_background_files: Optional[list] = None
    _detected_cells_path: Pathlike = ""

    def __post_init__(self: "CellfinderConfig"):
        """Executed after __init__ function.

        We use it to define attributes as a function of other
        attributes. See https://peps.python.org/pep-0557/#post-init-processing

        The following attributes are set:
        - input_data_dir is set to a default value if not set in __init__
        - _signal_dir_path: full path to the directory holding the signal files
        - _background_dir_path: full path to the directory holding the
          background files
        In 'add_signal_and_background_files':
        - _list_signal_files: list of signal files
        - _list_background_files: list of background files
        In 'add_output_timestamped':
        - output_parent_dir

        Parameters
        ----------
        self : CellfinderConfig
            a CellfinderConfig instance
        """

        # Fill in input data directory if not specified
        if self.input_data_dir is None:
            self.input_data_dir = (
                Path(self._install_path) / "cellfinder_test_data"
            )

        # Add input data paths that are derived from 'input_data_dir'
        self._signal_dir_path: Pathlike = self.input_data_dir / Path(
            self.signal_subdir
        )
        self._background_dir_path: Pathlike = self.input_data_dir / Path(
            self.background_subdir
        )

        # Add signal and background files to config
        self.add_signal_and_background_files()

        # Fill in output directory if not specified
        if self.output_parent_dir is None:
            self.output_parent_dir = (
                Path(self._install_path) / self.output_dir_basename
            )

        # Add output paths that are derived from 'output_parent_dir'
        self.add_output_timestamped()

    def add_output_timestamped(self):
        """Adds output paths to the cellfinder config

        Specifically it adds:
        - output_path: a path to a timestamped output directory
        - _detected_cells_path: the full path to the output file
          (under output_path).

        Parameters
        ----------
        config : CellfinderConfig
            a cellfinder config
        """

        # output directory and file
        timestamp = datetime.datetime.now()
        timestamp_formatted = timestamp.strftime("%Y%m%d_%H%M%S")
        output_path_timestamped = Path(self.output_parent_dir) / (
            str(self.output_dir_basename) + timestamp_formatted
        )
        output_path_timestamped.mkdir(
            parents=True,  # create any missing parents
            exist_ok=True,  # ignore FileExistsError exceptions
        )

        # Add paths to output directory and file to config
        self.output_path = output_path_timestamped
        self._detected_cells_path = (
            self.output_path / self.detected_cells_filename
        )

    def add_signal_and_background_files(self):
        """Adds the lists of input data files (signal and background)
        to the config.

        These files are first searched locally at the given location.
        If not found, we attempt to download them from GIN and place
        them at the specified location.

        Specifically:
        - If both parent data directories (signal and background) exist
        locally, the lists of signal and background files are added to
        the config.
        - If exactly one of the parent data directories is missing, an error
        message is logged.
        - If neither of them exist, the data is retrieved from the provided GIN
        repository. If no URL or hash to GIN is provided, an error is thrown.

        Parameters
        ----------
        config : CellfinderConfig
            a cellfinder config with input data files to be validated

        """
        # Fetch logger
        logger = logging.getLogger(LOGGER_NAME)

        # Check if input data directories (signal and background) exist
        # locally.
        # If both directories exist, get list of signal and background files
        if (
            Path(self._signal_dir_path).exists()
            and Path(self._background_dir_path).exists()
        ):
            logger.info("Fetching input data from the local directories")

            self._list_signal_files = [
                f
                for f in Path(self._signal_dir_path).resolve().iterdir()
                if f.is_file()
            ]
            self._list_background_files = [
                f
                for f in Path(self._background_dir_path).resolve().iterdir()
                if f.is_file()
            ]

        # If exactly one of the input data directories is missing, print error
        elif (
            Path(self._signal_dir_path).resolve().exists()
            or Path(self._background_dir_path).resolve().exists()
        ):
            if not Path(self._signal_dir_path).resolve().exists():
                logger.error(
                    f"The directory {self._signal_dir_path} does not exist",
                )
            else:
                logger.error(
                    f"The directory {self._background_dir_path} "
                    "does not exist",
                )

        # If neither of the input data directories exist,
        # retrieve data from GIN repository and add list of files to config
        else:
            # Check if GIN URL and hash are defined (log error otherwise)
            if self.data_url and self.data_hash:
                # get list of files in GIN archive with pooch.retrieve
                list_files_archive = pooch.retrieve(
                    url=self.data_url,
                    known_hash=self.data_hash,
                    path=Path(
                        self.input_data_dir
                    ).parent,  # zip will be downloaded here
                    progressbar=True,
                    processor=pooch.Unzip(
                        extract_dir=Path(self.input_data_dir).stem,
                        # files are unpacked here, a dir
                        # *relative* to the path set in 'path'
                    ),
                )
                logger.info(
                    "Fetching input data from the provided GIN repository"
                )

                # Check signal and background parent directories exist now
                assert Path(self._signal_dir_path).resolve().exists()
                assert Path(self._background_dir_path).resolve().exists()

                # Add signal files to config
                self._list_signal_files = [
                    f
                    for f in list_files_archive
                    if f.startswith(
                        str(Path(self._signal_dir_path).resolve()),
                    )
                ]

                # Add background files to config
                self._list_background_files = [
                    f
                    for f in list_files_archive
                    if f.startswith(
                        str(Path(self._background_dir_path).resolve()),
                    )
                ]
            # If one of URL/hash to GIN repo not defined, throw an error
            else:
                logger.error(
                    "Input data not found locally, and URL/hash to "
                    "GIN repository not provided",
                )


def read_cellfinder_config(
    input_config_path: str, log_on: bool = False
) -> CellfinderConfig:
    """Instantiate a CellfinderConfig from the input json file.

    Assumes config is json serializable.

    Parameters
    ----------
    input_config_path : str
        Absolute path to a cellfinder config file

    Returns
    -------
    CellfinderConfig:
        The cellfinder config object, populated with data from the input
    """
    logger = logging.getLogger(LOGGER_NAME)

    # read input config
    with open(input_config_path) as cfg:
        config_dict = json.load(cfg)
    config = CellfinderConfig(**config_dict)

    # log config origin
    if log_on:
        logger = logging.getLogger(LOGGER_NAME)
        logger.info(f"Input config read from {input_config_path}")
        if input_config_path == DEFAULT_JSON_CONFIG_PATH_CELLFINDER:
            logger.info("Using default config file")

    return config


def setup(input_config_path: str) -> CellfinderConfig:
    """Run setup steps prior to executing the workflow

    Parameters
    ----------
    input_config_path : str
        path to the input config file

    Returns
    -------
    CellfinderConfig
        a dataclass whose attributes are the parameters
        for running cellfinder.
    """
    assert Path(input_config_path).exists()

    # setup logger
    _ = setup_logger()

    # read config
    cfg = read_cellfinder_config(input_config_path)

    return cfg


def run_workflow_from_cellfinder_run(cfg: CellfinderConfig):
    """Run workflow based on the cellfinder_core.main.main()
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


def main(
    input_config: str = str(DEFAULT_JSON_CONFIG_PATH_CELLFINDER),
) -> CellfinderConfig:
    """Setup and run cellfinder workflow.

    This function runs the setup steps required
    to run the cellfinder workflow, and the
    workflow itself. Note that only the workflow
    will be benchmarked.

    Parameters
    ----------
    input_config : str, optional
        Absolute path to input config file,
        by default str(DEFAULT_JSON_CONFIG_PATH_CELLFINDER)

    Returns
    -------
    cfg : CellfinderConfig
        a class with the required setup methods and parameters for
        the cellfinder workflow
    """
    # run setup
    cfg = setup(input_config)

    # run workflow
    run_workflow_from_cellfinder_run(cfg)  # only this will be benchmarked

    return cfg


def main_app_wrapper():
    """Parse command line arguments and
    run cellfinder setup and workflow

    This function is used to define an entry-point,
    that allows the user to run the cellfinder workflow
    for a given input config file as:
    `cellfinder-workflow --config <path-to-input-config>`.

    If no input config file is provided, the default is used.

    """
    # parse CLI arguments
    args = config_parser(
        sys.argv[1:],  # sys.argv[0] is the script name
        str(DEFAULT_JSON_CONFIG_PATH_CELLFINDER),
    )

    # run setup and workflow
    _ = main(args.config)


if __name__ == "__main__":
    main_app_wrapper()
