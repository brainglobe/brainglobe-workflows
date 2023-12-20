import json
from pathlib import Path

import pooch
import pytest

from brainglobe_workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER


@pytest.fixture()
def custom_logger_name() -> str:
    """Return name of custom logger created in workflow utils

    Returns
    -------
    str
        Name of custom logger
    """
    from brainglobe_workflows.utils import __name__ as logger_name

    return logger_name


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
def config_GIN_dict(cellfinder_GIN_data):
    """
    Return a config pointing to the location where GIN would be by default
    """

    # read default config as dict
    with open(DEFAULT_JSON_CONFIG_PATH_CELLFINDER) as cfg:
        config_dict = json.load(cfg)

    # modify / ensure
    # - add url
    # - add data hash
    # - remove input_data_dir
    config_dict["data_url"] = cellfinder_GIN_data["url"]
    config_dict["data_hash"] = cellfinder_GIN_data["hash"]
    if "input_data_dir" in config_dict.keys():
        del config_dict["input_data_dir"]

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

    return config_dict


@pytest.fixture()
def config_force_GIN_dict(cellfinder_GIN_data, tmp_path):
    """
    Return a config pointing to the location where GIN would be by default
    """
    # read default config as dict
    with open(DEFAULT_JSON_CONFIG_PATH_CELLFINDER) as cfg:
        config_dict = json.load(cfg)

    # modify
    config_dict["data_url"] = cellfinder_GIN_data["url"]
    config_dict["data_hash"] = cellfinder_GIN_data["hash"]
    config_dict["input_data_dir"] = tmp_path
    # since the input_data_dir does not exist, it will
    # download the GIN data there

    return config_dict


@pytest.fixture()
def config_local_dict(cellfinder_GIN_data):
    """ """

    # read default config as dict
    # as dict because some paths are computed derived from input_data_dir
    with open(DEFAULT_JSON_CONFIG_PATH_CELLFINDER) as cfg:
        config_dict = json.load(cfg)

    # modify dict
    # - remove url
    # - remove data hash
    # - add input_data_dir
    config_dict["data_url"] = None
    config_dict["data_hash"] = None
    config_dict["input_data_dir"] = Path.home() / "local_cellfinder_data"

    # fetch data from GIN and download locally to local location?
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
def config_missing_signal_dict(config_local_dict):
    config_dict = config_local_dict.copy()
    config_dict["signal_subdir"] = "_"

    return config_dict


@pytest.fixture()
def config_missing_background_dict(config_local_dict):
    config_dict = config_local_dict.copy()
    config_dict["background_subdir"] = "_"

    return config_dict


@pytest.fixture()
def config_not_GIN_nor_local_dict(config_local_dict):
    config_dict = config_local_dict.copy()
    config_dict["input_data_dir"] = "_"

    return config_dict
