"""Pytest fixtures shared across unit and integration tests"""


import json
from pathlib import Path

import pooch
import pytest


@pytest.fixture(autouse=True)
def mock_home_directory(monkeypatch: pytest.MonkeyPatch):
    # define mock home path
    home_path = Path.home()  # actual home path
    mock_home_path = home_path / ".brainglobe-tests"

    # create directory if it doesn't exist
    if not mock_home_path.exists():
        mock_home_path.mkdir()

    # monkeypatch Path.home() to point to the mock home
    def mock_home():
        return mock_home_path

    monkeypatch.setattr(Path, "home", mock_home)


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
def config_local_dict(
    cellfinder_GIN_data: dict, default_input_config_cellfinder: Path
) -> dict:
    """
    Return a config pointing to a local dataset,
    and ensure the data is downloaded there
    """

    # read default config as dict
    with open(default_input_config_cellfinder) as cfg:
        config_dict = json.load(cfg)

    # modify dict
    # - remove url
    # - remove data hash
    # - point to a local directory under home in input_data_dir
    config_dict["data_url"] = None
    config_dict["data_hash"] = None
    config_dict["input_data_dir"] = str(Path.home() / "local_cellfinder_data")

    # fetch data from GIN and download to the local location
    pooch.retrieve(
        url=cellfinder_GIN_data["url"],
        known_hash=cellfinder_GIN_data["hash"],
        path=Path(
            config_dict["input_data_dir"]
        ).parent,  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir=Path(config_dict["input_data_dir"]).stem
            # path to unzipped dir, *relative*  to 'path'
        ),
    )
    return config_dict


@pytest.fixture()
def config_GIN_dict(
    cellfinder_GIN_data: dict, default_input_config_cellfinder: Path
) -> dict:
    """
    Return a config pointing to the location where GIN would be by default,
    and download the data
    """

    # read default config as a dictionary
    with open(default_input_config_cellfinder) as cfg:
        config_dict = json.load(cfg)

    # modify
    # - add url
    # - add data hash
    # - remove input_data_dir if present
    config_dict["data_url"] = cellfinder_GIN_data["url"]
    config_dict["data_hash"] = cellfinder_GIN_data["hash"]
    if "input_data_dir" in config_dict.keys():
        del config_dict["input_data_dir"]

    # download GIN data to default location for GIN
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

    return config_dict


@pytest.fixture()
def config_local_json(config_local_dict: dict, tmp_path: Path) -> Path:
    # define location of input config file
    config_file_path = tmp_path / "input_config.json"

    # write config dict to that location
    with open(config_file_path, "w") as js:
        json.dump(config_local_dict, js)

    return config_file_path


@pytest.fixture()
def config_GIN_json(config_GIN_dict: dict, tmp_path: Path) -> Path:
    # define location of input config file
    config_file_path = tmp_path / "input_config.json"

    # write config dict to that location
    with open(config_file_path, "w") as js:
        json.dump(config_GIN_dict, js)

    return config_file_path
