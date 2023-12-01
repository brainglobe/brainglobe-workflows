import json
from pathlib import Path
from typing import Any

import pooch
import pytest

from workflows.cellfinder import CellfinderConfig


def make_config_dict_fetch_from_local(cellfinder_cache_dir: Path) -> dict:
    """Generate a config dictionary with the required parameters
    for the workflow

    The input data is assumed to be locally at cellfinder_cache_dir.
    The results are saved in a timestamped output subdirectory under
    cellfinder_cache_dir

    Parameters
    ----------
    cellfinder_cache_dir : Path
        Path to the directory where the downloaded input data will be unzipped,
        and the output will be saved

    Returns
    -------
    dict
        dictionary with the required parameters for the workflow
    """
    return {
        "install_path": cellfinder_cache_dir,
        "extract_dir_relative": "cellfinder_test_data",  # relative path
        "signal_subdir": "signal",
        "background_subdir": "background",
        "output_path_basename_relative": "cellfinder_output_",
        "detected_cells_filename": "detected_cells.xml",
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


def make_config_dict_fetch_from_GIN(
    cellfinder_cache_dir: Path,
    data_url: str,
    data_hash: str,
) -> dict:
    """Generate a config dictionary with the required parameters
    for the workflow

    The input data is fetched from GIN and downloaded to cellfinder_cache_dir.
    The results are also saved in a timestamped output subdirectory under
    cellfinder_cache_dir

    Parameters
    ----------
    cellfinder_cache_dir : Path
        Path to the directory where the downloaded input data will be unzipped,
        and the output will be saved
    data_url: str
        URL to the GIN repository with the data to download
    data_hash: str
        Hash of the data to download

    Returns
    -------
    dict
        dictionary with the required parameters for the workflow
    """

    config = make_config_dict_fetch_from_local(cellfinder_cache_dir)
    config["data_url"] = data_url
    config["data_hash"] = data_hash

    return config


def prep_json(obj: Any) -> Any:
    """
    Returns a JSON encodable version of the input object.

    It uses the JSON default encoder for all objects
    except those of type `Path`.


    Parameters
    ----------
    obj : Any
        _description_

    Returns
    -------
    Any
        JSON serializable version of input object
    """
    if isinstance(obj, Path):
        return str(obj)
    else:
        json_decoder = json.JSONEncoder()
        return json_decoder.default(obj)


@pytest.fixture(autouse=True)
def cellfinder_cache_dir(tmp_path: Path) -> Path:
    """Create a .cellfinder_workflows directory
    under a temporary pytest directory and return
    its path.

    The temporary directory is available via pytest's tmp_path
    fixture. A new temporary directory is created every function call
    (i.e., scope="function")

    Parameters
    ----------
    tmp_path : Path
        path to pytest-generated temporary directory

    Returns
    -------
    Path
        path to the created cellfinder_workflows cache directory
    """

    return Path(tmp_path) / ".cellfinder_workflows"


@pytest.fixture(scope="session")
def data_url() -> str:
    """Return the URL to the GIN repository with the input data

    Returns
    -------
    str
        URL to the GIN repository with the input data
    """
    return "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip"


@pytest.fixture(scope="session")
def data_hash() -> str:
    """Return the hash of the GIN input data

    Returns
    -------
    str
        Hash to the GIN input data
    """
    return "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914"


@pytest.fixture(scope="session")
def default_json_config_path() -> Path:
    """Return the path to the json file
    with the default config parameters for cellfinder

    Returns
    -------
    Path
        path to the json file with the default config parameters
    """
    from workflows.utils import (
        DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
    )

    return DEFAULT_JSON_CONFIG_PATH_CELLFINDER


@pytest.fixture()
def path_to_config_fetch_GIN(
    tmp_path: Path, cellfinder_cache_dir: Path, data_url: str, data_hash: str
) -> Path:
    """Create an input config that fetches data from GIN and
    return its path

    Parameters
    ----------
    tmp_path : Path
        path to a fresh pytest-generated temporary directory. The
        generated config is saved here.

    cellfinder_cache_dir : Path
        path to the cellfinder cache directory, where the paths
        in the config should point to.

    data_url: str
        URL to the GIN repository with the input data

    data_hash: str
        hash to the GIN input data

    Returns
    -------
    input_config_path : Path
        path to config file that fetches data from GIN
    """
    # create config dict
    config_dict = make_config_dict_fetch_from_GIN(
        cellfinder_cache_dir, data_url, data_hash
    )

    # create a temp json file to dump config data
    input_config_path = (
        tmp_path / "input_config.json"
    )  # save it in a temp dir separate from cellfinder_cache_dir

    # save config data to json file
    with open(input_config_path, "w") as js:
        json.dump(config_dict, js, default=prep_json)

    # check json file exists
    assert Path(input_config_path).is_file()

    return input_config_path


@pytest.fixture()
def path_to_config_fetch_local(
    tmp_path: Path, cellfinder_cache_dir: Path, data_url: str, data_hash: str
) -> Path:
    """Create an input config that points to local data and
    return its path.

    The local data is downloaded from GIN, but no reference
    to the GIN repository is included in the config.

    Parameters
    ----------
    tmp_path : Path
        path to a fresh pytest-generated temporary directory. The
        generated config is saved here.

    cellfinder_cache_dir : Path
        path to the cellfinder cache directory, where the paths
        in the config should point to.

    data_url: str
        URL to the GIN repository with the input data

    data_hash: str
        hash to the GIN input data

    Returns
    -------
    path_to_config_fetch_GIN : Path
        path to a config file that fetches data from GIN
    """

    # instantiate basic config (assumes data is local)
    config_dict = make_config_dict_fetch_from_local(cellfinder_cache_dir)
    config = CellfinderConfig(**config_dict)

    # download GIN data to specified local directory
    pooch.retrieve(
        url=data_url,
        known_hash=data_hash,
        path=config.install_path,  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir=config.extract_dir_relative
            # path to unzipped dir, *relative*  to 'path'
        ),
    )

    # save config to json
    input_config_path = tmp_path / "input_config.json"
    with open(input_config_path, "w") as js:
        json.dump(config_dict, js, default=prep_json)

    # check json file exists
    assert Path(input_config_path).is_file()

    return input_config_path
