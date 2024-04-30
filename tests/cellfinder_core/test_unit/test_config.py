import re
from pathlib import Path

import pytest

from brainglobe_workflows.utils import setup_logger


@pytest.fixture()
def config_force_GIN_dict(
    config_GIN_dict: dict,
    tmp_path: Path,
    GIN_default_location: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> dict:
    """
    Fixture returning a config as a dictionary, which has a
    Pytest-generated temporary directory as input data location,
    and that monkeypatches pooch.retrieve()

    Since there is no data at the input_data_dir location, the GIN download
    will be triggered, but the monkeypatched pooch.retrieve() will copy the
    files rather than download them.

    Parameters
    ----------
    config_GIN_dict : dict
        dictionary with the config for a workflow that uses the downloaded
        GIN data
    tmp_path : Path
        path to pytest-generated temporary directory
    GIN_default_location : Path
        path to the default location where to download GIN data
    monkeypatch : pytest.MonkeyPatch
        a monkeypatch fixture

    Returns
    -------
    dict
        dictionary with the config for a workflow that triggers the downloaded
        GIN data
    """

    import shutil

    import pooch

    # read GIN config as dict
    config_dict = config_GIN_dict.copy()

    # point to a temporary directory in input_data_dir
    config_dict["input_data_dir"] = str(tmp_path)

    # monkeypatch pooch.retrieve()
    # when called copy GIN downloaded data, instead of downloading it
    def mock_pooch_download(
        url="", known_hash="", path="", progressbar="", processor=""
    ):
        # Copy destination
        GIN_copy_destination = tmp_path

        # copy only relevant subdirectories
        for subdir in ["signal", "background"]:
            shutil.copytree(
                GIN_default_location / subdir,  # src
                GIN_copy_destination / subdir,  # dest
                dirs_exist_ok=True,
            )

        # List of files in destination
        list_of_files = [
            str(f) for f in GIN_copy_destination.glob("**/*") if f.is_file()
        ]
        list_of_files.sort()

        return list_of_files

    # monkeypatch pooch.retreive with mock_pooch_download()
    monkeypatch.setattr(pooch, "retrieve", mock_pooch_download)

    return config_dict


@pytest.fixture()
def config_missing_signal_dict(config_local_dict: dict) -> dict:
    """
    Fixture that returns a config as a dictionary, pointing to a local dataset,
    whose signal directory does not exist

    Parameters
    ----------
    config_local_dict : _type_
        dictionary with the config for a workflow that uses local data

    Returns
    -------
    dict
        dictionary with the config for a workflow that uses local data, but
        whose signal directory does not exist.
    """
    config_dict = config_local_dict.copy()
    config_dict["signal_subdir"] = "_"

    return config_dict


@pytest.fixture()
def config_missing_background_dict(config_local_dict: dict) -> dict:
    """
    Fixture that returns a config as a dictionary, pointing to a local dataset,
    whose background directory does not exist

    Parameters
    ----------
    config_local_dict : dict
        dictionary with the config for a workflow that uses local data

    Returns
    -------
    dict
        dictionary with the config for a workflow that uses local data, but
        whose background directory does not exist.
    """
    config_dict = config_local_dict.copy()
    config_dict["background_subdir"] = "_"

    return config_dict


@pytest.fixture()
def config_not_GIN_nor_local_dict(config_local_dict: dict) -> dict:
    """
    Fixture that returns a config as a dictionary, whose input_data_dir
    directory does not exist and with no references to a GIN dataset.

    Parameters
    ----------
    config_local_dict : dict
        dictionary with the config for a workflow that uses local data

    Returns
    -------
    dict
        dictionary with the config for a workflow that uses local data, but
        whose input_data_dir directory does not exist and with no references
        to a GIN dataset.
    """
    config_dict = config_local_dict.copy()
    config_dict["input_data_dir"] = "_"

    config_dict["data_url"] = None
    config_dict["data_hash"] = None

    return config_dict


@pytest.mark.parametrize(
    "input_config_dict, message_pattern",
    [
        (
            "config_force_GIN_dict",
            "Fetching input data from the provided GIN repository",
        ),
        (
            "config_local_dict",
            "Fetching input data from the local directories",
        ),
        (
            "config_missing_signal_dict",
            "The directory .+ does not exist$",
        ),
        ("config_missing_background_dict", "The directory .+ does not exist$"),
        (
            "config_not_GIN_nor_local_dict",
            "Input data not found locally, and URL/hash to "
            "GIN repository not provided",
        ),
    ],
)
def test_add_input_paths(
    caplog: pytest.LogCaptureFixture,
    input_config_dict: dict,
    message_pattern: str,
    request: pytest.FixtureRequest,
):
    """
    Test the addition of signal and background files to the cellfinder config

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Pytest fixture to capture the logs during testing
    input_config_dict : dict
        input config as a dict
    message_pattern : str
        Expected pattern in the log
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """

    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        CellfinderConfig,
    )

    # instantiate custom logger
    _ = setup_logger()

    # instantiate config object
    _ = CellfinderConfig(**request.getfixturevalue(input_config_dict))

    # check log messages
    assert len(caplog.messages) > 0
    out = re.fullmatch(message_pattern, caplog.messages[-1])
    assert out is not None
    assert out.group() is not None
