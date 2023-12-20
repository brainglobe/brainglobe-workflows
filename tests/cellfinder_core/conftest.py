"""Pytest fixtures shared across unit and integration tests"""

import json
from pathlib import Path

import pooch
import pytest


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
def config_GIN(cellfinder_GIN_data):
    """
    Return a config pointing to the location where GIN would be by default
    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        read_cellfinder_config,
    )
    from brainglobe_workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER

    # fetch data from GIN and download locally
    # if it exists, pooch doesnt download again
    pooch.retrieve(
        url=cellfinder_GIN_data["url"],
        known_hash=cellfinder_GIN_data["hash"],
        path=Path.home(),  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir="cellfinder_test_data"
            # path to unzipped dir, *relative*  to 'path'
        ),
    )

    return read_cellfinder_config(DEFAULT_JSON_CONFIG_PATH_CELLFINDER)
    # read_cellfinder_config(input_configs_dir / "input_data_GIN.json")


@pytest.fixture()
def config_local(cellfinder_GIN_data):
    """ """

    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )
    from brainglobe_workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER

    # read default config as dict
    # as dict because some paths are computed derived from input_data_dir
    with open(DEFAULT_JSON_CONFIG_PATH_CELLFINDER) as cfg:
        config_dict = json.load(cfg)

    # modify location of data?
    # - remove url
    # - remove data hash
    # - add input_data_dir
    config_dict["data_url"] = None
    config_dict["data_hash"] = None
    config_dict["input_data_dir"] = Path.home() / "local_data"

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
