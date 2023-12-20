"""Pytest fixtures shared across unit and integration tests"""

import json
from pathlib import Path

import pooch
import pytest


@pytest.fixture()
def default_input_config_cellfinder() -> Path:
    """Return path to default input config for cellfinder workflow

    Returns
    -------
    Path
        Path to default input config

    """
    from brainglobe_workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER

    return DEFAULT_JSON_CONFIG_PATH_CELLFINDER


@pytest.fixture(autouse=True)
def mock_home_directory(monkeypatch: pytest.MonkeyPatch):
    # define mock home path
    home_path = Path.home()  # actual home path
    mock_home_path = home_path / ".brainglobe-tests"  # tmp_path  #

    # create dir if it doesn't exist
    if not mock_home_path.exists():
        mock_home_path.mkdir()

    # monkeypatch Path.home() to point to the mock home
    def mock_home():
        return mock_home_path

    monkeypatch.setattr(Path, "home", mock_home)


@pytest.fixture()  # Do I need this?
def input_configs_dir() -> Path:
    """Return the directory path to the input configs
    used for testing

    Returns
    -------
    Path
        Test data directory path
    """
    return Path(__file__).parents[1] / "data"


@pytest.fixture(scope="session")
def cellfinder_GIN_data() -> dict:
    """Return the URL and hash to the GIN repository with the input data

    Returns
    -------
    dict
        URL and hash of the GIN repository with the cellfinder test data
    """
    return {
        "url": "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip",
        "hash": "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914",  # noqa
    }


@pytest.fixture()
def config_GIN(cellfinder_GIN_data, default_input_config_cellfinder):
    """
    Return a config pointing to the location where GIN would be by default
    """

    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )

    # download data to default location for GIN
    pooch.retrieve(
        url=cellfinder_GIN_data["url"],
        known_hash=cellfinder_GIN_data["hash"],
        path=Path.home()
        / ".brainglobe"
        / "workflows"
        / "cellfinder_core",  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(extract_dir="cellfinder_test_data"),
    )

    # read default config as dict
    with open(default_input_config_cellfinder) as cfg:
        config_dict = json.load(cfg)

    # modify / ensure
    # - add url
    # - add data hash
    # - add input_data_dir
    config_dict["data_url"] = cellfinder_GIN_data["url"]
    config_dict["data_hash"] = cellfinder_GIN_data["hash"]
    if "input_data_dir" in config_dict.keys():
        del config_dict["input_data_dir"]

    # instantiate object
    config = CellfinderConfig(**config_dict)

    return config


@pytest.fixture()
def config_force_GIN(config_GIN, tmp_path):
    """
    Return a config pointing to the location where GIN would be by default
    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )

    # ensure neither signal or background dir exist!
    config_dict = config_GIN.__dict__
    config_dict["input_data_dir"] = tmp_path
    # since the input_data_dir does not exist, it will
    # download the GIN data there

    # instantiate object
    config = CellfinderConfig(**config_dict)

    # ensure neither signal or background dir exist, to force GIN case
    assert not Path(config._signal_dir_path).exists()
    assert not Path(config._background_dir_path).exists()

    return config


@pytest.fixture()
def config_local(cellfinder_GIN_data, default_input_config_cellfinder):
    """ """

    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )

    # read default config as dict
    # as dict because some paths are computed derived from input_data_dir
    with open(default_input_config_cellfinder) as cfg:
        config_dict = json.load(cfg)

    # modify location of data?
    # - remove url
    # - remove data hash
    # - add input_data_dir
    config_dict["data_url"] = None
    config_dict["data_hash"] = None
    config_dict["input_data_dir"] = Path.home() / "local_cellfinder_data"

    # instantiate object
    config = CellfinderConfig(**config_dict)

    # fetch data from GIN and download locally to local location?
    pooch.retrieve(
        url=cellfinder_GIN_data["url"],
        known_hash=cellfinder_GIN_data["hash"],
        path=Path(config.input_data_dir).parent,  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir=Path(config.input_data_dir).stem
            # path to unzipped dir, *relative*  to 'path'
        ),
    )
    return config


@pytest.fixture()
def config_missing_signal(config_local):
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )

    config_dict = config_local.__dict__
    config_dict["signal_subdir"] = "_"

    # update rest of the paths
    config = CellfinderConfig(**config_dict)

    return config


@pytest.fixture()
def config_missing_background(config_local):
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )

    config_dict = config_local.__dict__
    config_dict["background_subdir"] = "_"

    # update rest of the paths
    config = CellfinderConfig(**config_dict)
    return config


@pytest.fixture()
def config_not_GIN_or_local(config_local):
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )

    config_dict = config_local.__dict__
    config_dict["input_data_dir"] = "_"

    # update rest of the paths
    config = CellfinderConfig(**config_dict)
    return config
