import json
import logging
import re
from pathlib import Path

import pytest

from brainglobe_workflows.utils import setup_logger


@pytest.fixture()
def config_force_GIN_dict(
    config_GIN_dict: dict, tmp_path: Path, monkeypatch
) -> dict:
    """
    Return a config pointing to a temporary directory where to download GIN
    data, without downloading the data first.

    Since there is no data at the input_data_dir location, the GIN download
    will be triggered
    """
    import shutil

    import pooch

    # read GIN config as dict
    config_dict = config_GIN_dict.copy()

    # point to a temporary directory in input_data_dir
    config_dict["input_data_dir"] = str(tmp_path)

    # monkeypatch pooch.retrieve
    # when called: copy GIN downloaded data, instead of re-downloading
    def mock_pooch_download(
        url="", known_hash="", path="", progressbar="", processor=""
    ):
        # GIN downloaded data default location
        GIN_default_location = (
            Path.home()
            / ".brainglobe"
            / "workflows"
            / "cellfinder_core"
            / "cellfinder_test_data"
        )

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
    Return a config pointing to a local dataset, whose signal directory
    does not exist

    Parameters
    ----------
    config_local_dict : _type_
        _description_

    Returns
    -------
    dict
        _description_
    """
    config_dict = config_local_dict.copy()
    config_dict["signal_subdir"] = "_"

    return config_dict


@pytest.fixture()
def config_missing_background_dict(config_local_dict):
    """Return a config pointing to a local dataset, whose background directory
    does not exist

    Parameters
    ----------
    config_local_dict : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    config_dict = config_local_dict.copy()
    config_dict["background_subdir"] = "_"

    return config_dict


@pytest.fixture()
def config_not_GIN_nor_local_dict(config_local_dict):
    """Return a config pointing to a local dataset whose input_data_dir
    directory does not exist, and with no references to a GIN dataset.

    Parameters
    ----------
    config_local_dict : _type_
        _description_

    Returns
    -------
    _type_
        _description_
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
def test_add_signal_and_background_files(
    caplog: pytest.LogCaptureFixture,
    input_config_dict: dict,
    message_pattern: str,
    request: pytest.FixtureRequest,
):
    """Test signal and background files addition to the cellfinder config

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Pytest fixture to capture the logs during testing
    input_config_dict : dicy
        input config as a dict
    message_pattern : str
        Expected pattern in the log
    """

    from brainglobe_workflows.cellfinder_core.cellfinder import (
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


@pytest.mark.parametrize(
    "input_config_path, message",
    [
        ("default_input_config_cellfinder", "Using default config file"),
        ("config_local_json", "Input config read from"),
    ],
)
def test_read_cellfinder_config(
    input_config_path: str,
    message: str,
    caplog: pytest.LogCaptureFixture,
    request: pytest.FixtureRequest,
):
    """
    Test for reading a cellfinder config file default

    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        read_cellfinder_config,
    )

    # instantiate custom logger
    _ = setup_logger()

    # read Cellfinder config
    config = read_cellfinder_config(
        request.getfixturevalue(input_config_path), log_on=True
    )

    # read json as dict
    with open(request.getfixturevalue(input_config_path)) as cfg:
        config_dict = json.load(cfg)

    # check keys of dictionary are a subset of Cellfinder config attributes
    assert all(
        [ky in config.__dataclass_fields__.keys() for ky in config_dict.keys()]
    )

    # check logs
    assert message in caplog.text

    # check all signal files exist
    assert config._list_signal_files
    assert all([Path(f).is_file() for f in config._list_signal_files])

    # check all background files exist
    assert config._list_background_files
    assert all([Path(f).is_file() for f in config._list_background_files])

    # check output directory exists
    assert Path(config.output_path).resolve().is_dir()

    # check output directory name has correct format
    out = re.fullmatch(
        str(config.output_dir_basename) + "\\d{8}_\\d{6}$",
        Path(config.output_path).stem,
    )
    assert out is not None
    assert out.group() is not None

    # check output file path is as expected
    assert (
        Path(config._detected_cells_path)
        == Path(config.output_path) / config.detected_cells_filename
    )


@pytest.mark.parametrize(
    "input_config",
    [
        "default_input_config_cellfinder",
        "config_local_json",
        "config_GIN_json",
    ],
)
def test_setup(
    input_config: str, custom_logger_name: str, request: pytest.FixtureRequest
):
    """Test full setup for cellfinder workflow, using the default config
    and passing a specific config file.

    Parameters
    ----------
    input_config : str
        Path to input config file
    custom_logger_name : str
        Name of custom logger
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        CellfinderConfig,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        setup as setup_workflow,
    )

    # run setup on default configuration
    cfg = setup_workflow(str(request.getfixturevalue(input_config)))

    # check logger exists
    logger = logging.getLogger(custom_logger_name)
    assert logger.level == logging.DEBUG
    assert logger.hasHandlers()

    # check config is CellfinderConfig
    assert isinstance(cfg, CellfinderConfig)


@pytest.mark.parametrize(
    "input_config",
    [
        "default_input_config_cellfinder",
        "config_local_json",
        "config_GIN_json",
    ],
)
def test_run_workflow_from_cellfinder_run(
    input_config: str, request: pytest.FixtureRequest
):
    """Test running cellfinder workflow with default input config
    (fetches data from GIN) and local input config

    Parameters
    ----------
    input_config : str
        Path to input config json file
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        run_workflow_from_cellfinder_run,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        setup as setup_workflow,
    )

    # run setup
    cfg = setup_workflow(str(request.getfixturevalue(input_config)))

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()
