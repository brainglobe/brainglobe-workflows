import json
from pathlib import Path

import pooch
import pytest

from brainglobe_workflows.cellfinder.cellfinder_main import CellfinderConfig


def make_config_dict_local(cellfinder_cache_dir: Path):
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
        "signal_parent_dir": str(
            cellfinder_cache_dir / "cellfinder_test_data" / "signal"
        ),
        "background_parent_dir": str(
            cellfinder_cache_dir / "cellfinder_test_data" / "background"
        ),
        "output_path_basename": cellfinder_cache_dir / "cellfinder_output_",
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
    cellfinder_cache_dir: Path, data_url, data_hash
):
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

    Returns
    -------
    dict
        dictionary with the required parameters for the workflow
    """

    config = make_config_dict_local(cellfinder_cache_dir)
    config["data_url"] = data_url
    config["data_hash"] = data_hash

    return config


def prep_json(obj):
    """
    Returns a JSON encodable version of the object.

    It uses the JSON default encoder for all objects
    except those of type Path.

    Parameters
    ----------
    obj : _type_
        _description_

    Returns
    -------
    _type_
        JSON serializable version of input object
    """
    if isinstance(obj, Path):
        return str(obj)
    else:
        return json.JSONEncoder.default(obj)


@pytest.fixture(autouse=True)
def cellfinder_cache_dir(tmp_path: Path):
    """Create a .cellfinder_workflows directory
    under a temporary pytest directory and return
    its path.

    The temporary directory is available via pytest's tmp_path
    fixture. A new temporary directory is created every function call

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
def data_url():
    return "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip"


@pytest.fixture(scope="session")
def data_hash():
    return "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914"


@pytest.fixture()
def path_to_config_fetch_GIN(
    tmp_path: Path, cellfinder_cache_dir: Path, data_url, data_hash
):
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
    tmp_path: Path, cellfinder_cache_dir: Path, data_url, data_hash
):
    """Create an input config that points to local data and
    return its path.

    The process is analogous to creating a config that
    fetches data from GIN, except that here we download the data
    from GIN prior to running the workflow.

    Parameters
    ----------
    path_to_config_fetch_GIN : Path
        path to a config file that fetches data from GIN

    Returns
    -------
    path_to_config_fetch_GIN : Path
        path to a config file that fetches data from GIN
    """

    # instantiate basic config (assumes data is local)
    config_dict = make_config_dict_local(cellfinder_cache_dir)
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
