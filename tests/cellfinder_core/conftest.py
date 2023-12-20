"""Pytest fixtures shared across unit and integration tests"""

from pathlib import Path

import pooch
import pytest

# from brainglobe_workflows.cellfinder_core.cellfinder import (
#     read_cellfinder_config,
# )


@pytest.fixture(autouse=True)
def mock_home_directory(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """_summary_

    from https://github.com/brainglobe/brainrender-napari/blob/52673db58df247261b1ad43c52135e5a26f88d1e/tests/conftest.py#L10

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        _description_

    Returns
    -------
    _type_
        _description_
    """

    # define mock home path
    # home_path = Path.home()  # actual home path
    mock_home_path = tmp_path  # home_path / ".brainglobe-tests"

    # create dir if it doesn't exist
    if not mock_home_path.exists():
        mock_home_path.mkdir()

    # monkeypatch Path.home() to point to the mock home
    def mock_home():
        return mock_home_path

    monkeypatch.setattr(Path, "home", mock_home)


@pytest.fixture()
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
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        read_cellfinder_config,
    )

    # read local config
    input_config_path = input_configs_dir / "input_data_locally.json"
    config = read_cellfinder_config(input_config_path)

    # fetch data from GIN and download locally
    pooch.retrieve(
        url=cellfinder_GIN_data["url"],
        known_hash=cellfinder_GIN_data["hash"],
        path=config._install_path,  # path to download zip to
        progressbar=True,
        processor=pooch.Unzip(
            extract_dir=Path(config.input_data_dir).stem
            # path to unzipped dir, *relative*  to 'path'
        ),
    )

    return input_config_path
