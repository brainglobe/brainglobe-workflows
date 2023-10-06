import json
import subprocess
import sys
from pathlib import Path

import pooch
import pytest

from brainglobe_workflows.cellfinder.cellfinder_main import (
    DEFAULT_JSON_CONFIG_PATH,
    CellfinderConfig,
)


## Utils
def make_config_dict_fetch_from_GIN(cellfinder_cache_dir):
    """Generate a config dictionary with the required parameters
    for the workflow

    The input data is fetched from GIN and downloaded to
    the location provided by cellfinder_cache_dir. The results are
    also saved in a timestamped output subdirectory under cellfinder_cache_dir

    Parameters
    ----------
    cellfinder_cache_dir : _type_
        _description_

    Returns
    -------
    dict
        dictionary with the required parameters for the workflow
    """
    return {
        "install_path": cellfinder_cache_dir,
        "data_url": "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip",
        "data_hash": (
            "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914"
        ),
        "extract_relative_dir": "cellfinder_test_data",  # relative path
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


# ensure all Paths are JSON serializable
def prep_json(obj):
    if isinstance(obj, Path):
        return str(obj)
    else:
        return json.JSONEncoder.default(obj)


def assert_outputs(path_to_config, parent_dir=""):
    # load input config
    # ATT! config.output_path is only defined after the workflow
    # setup, because its name is timestamped
    with open(path_to_config) as cfg:
        config_dict = json.load(cfg)
    config = CellfinderConfig(**config_dict)

    # check one output directory exists and
    # it has expected output file inside it
    output_path_timestamped = [
        x
        for x in (Path(parent_dir) / config.output_path_basename).parent.glob(
            "*"
        )
        if x.is_dir()
        and x.name.startswith(Path(config.output_path_basename).name)
    ]

    assert len(output_path_timestamped) == 1
    assert (output_path_timestamped[0]).exists()
    assert (
        output_path_timestamped[0] / config.detected_cells_filename
    ).is_file()


### Fixtures
@pytest.fixture(autouse=True)
def cellfinder_cache_dir(tmp_path):
    """Create a .cellfinder_workflows directory
    under a temporary pytest directory.

    It uses pytest's tmp_path fixture so that all is cleared after the test.
    A new temporary directory is created every function call (scope="function"
    by default)

    Parameters
    ----------
    tmp_path : _type_
        _description_

    Returns
    -------
    Path
        path to the created cache directory
    """

    return Path(tmp_path) / ".cellfinder_workflows"


@pytest.fixture()
def path_to_config_fetch_GIN(tmp_path, cellfinder_cache_dir):
    """Create an input config that fetches data from GIN and
    return its path

    Parameters
    ----------
    tmp_path : _type_
        _description_
    cellfinder_cache_dir : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # create config dict
    config_dict = make_config_dict_fetch_from_GIN(cellfinder_cache_dir)

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
def path_to_config_fetch_local(path_to_config_fetch_GIN):
    # create config that fetches data from GIN
    # path_to_config_fetch_GIN

    # read into config class
    with open(path_to_config_fetch_GIN) as cfg:
        config_dict = json.load(cfg)
    config = CellfinderConfig(**config_dict)

    # Download GIN data
    pooch.retrieve(
        url=config.data_url,
        known_hash=config.data_hash,
        path=config.install_path,  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir=config.extract_relative_dir
            # path to unzipped dir, *relative*  to 'path'
        ),
    )

    # return path to config json
    return path_to_config_fetch_GIN


### Tests
def test_run_with_default_config(tmp_path):
    # run workflow with CLI and capture log
    # with cwd = pytest tmp_path <-------
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
            / "brainglobe_workflows"
            / "cellfinder"
            / "cellfinder_main.py",
        ],
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs
    assert "Using default config file" in subprocess_output.stdout

    # Check one output directory exists and has expected
    # output file inside it
    assert_outputs(DEFAULT_JSON_CONFIG_PATH, tmp_path)


def test_run_with_config_GIN(
    path_to_config_fetch_GIN,
):
    # run workflow with CLI and capture log
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
            / "brainglobe_workflows"
            / "cellfinder"
            / "cellfinder_main.py",
            "--config",
            str(path_to_config_fetch_GIN),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs
    assert (
        f"Input config read from {str(path_to_config_fetch_GIN)}"
        in subprocess_output.stdout
    )
    assert (
        "Fetching input data from the provided GIN repository"
        in subprocess_output.stdout
    )

    # check output directory
    # check one output directory exists and has expected output file inside it
    assert_outputs(path_to_config_fetch_GIN)


def test_run_with_config_local(
    path_to_config_fetch_local,
):
    # run workflow with CLI and capture log
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
            / "brainglobe_workflows"
            / "cellfinder"
            / "cellfinder_main.py",
            "--config",
            str(path_to_config_fetch_local),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs
    assert (
        f"Input config read from {str(path_to_config_fetch_local)}"
        in subprocess_output.stdout
    )
    assert (
        "Fetching input data from the local directories"
        in subprocess_output.stdout
    )

    # check output directory
    # check one output directory exists and has expected output file inside it
    assert_outputs(path_to_config_fetch_local)
