"""Pytest fixtures shared across unit and integration tests"""

from pathlib import Path

import pooch
import pytest

from brainglobe_workflows.cellfinder import read_cellfinder_config


@pytest.fixture()
def input_configs_dir() -> Path:
    """Return the directory path to the input configs
    used for testing

    Returns
    -------
    Path
        Test data directory path
    """
    return Path(__file__).parent / "data"


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
def input_config_fetch_GIN(input_configs_dir: Path) -> Path:
    """
    Return the cellfinder config json file that is configured to fetch from GIN

    Parameters
    ----------
    input_configs_dir : Path
        Path to the directory holding the test config files.

    Returns
    -------
    Path
        Path to the config json file for fetching data from GIN
    """
    return input_configs_dir / "input_data_GIN.json"


@pytest.fixture()
def input_config_fetch_local(
    input_configs_dir: Path,
    cellfinder_GIN_data: dict,
) -> Path:
    """
    Download the cellfinder data locally and return the config json
    file configured to fetch local data.

    The data is downloaded to a directory under the current working
    directory (that is, to a directory under the directory from where
    pytest is launched).

    Parameters
    ----------
    input_configs_dir : Path
        Path to the directory holding the test config files.
    cellfinder_GIN_data : dict
        URL and hash of the GIN repository with the cellfinder test data

    Returns
    -------
    Path
        Path to the config json file for fetching data locally
    """
    # read local config
    input_config_path = input_configs_dir / "input_data_locally.json"
    config = read_cellfinder_config(input_config_path)

    # fetch data from GIN and download locally
    pooch.retrieve(
        url=cellfinder_GIN_data["url"],
        known_hash=cellfinder_GIN_data["hash"],
        path=config.install_path,  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir=config.data_dir_relative
            # path to unzipped dir, *relative*  to 'path'
        ),
    )

    return input_config_path
