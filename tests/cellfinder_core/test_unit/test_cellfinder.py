import json
import logging
import re
from pathlib import Path

import pooch
import pytest

from brainglobe_workflows.utils import (
    setup_logger,
)


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
def config_force_GIN_dict(
    cellfinder_GIN_data: dict,
    default_input_config_cellfinder: Path,
    tmp_path: Path,
) -> dict:
    """
    Return a config pointing to a temporary directory where to download GIN
    data, without downloading the data first.

    Since there is no data at the input_data_dir location, the GIN download
    will be triggered
    """
    # read default config as dict
    with open(default_input_config_cellfinder) as cfg:
        config_dict = json.load(cfg)

    # modify
    # - add url
    # - add data hash
    # - point to a temporary directory in input_data_dir
    config_dict["data_url"] = cellfinder_GIN_data["url"]
    config_dict["data_hash"] = cellfinder_GIN_data["hash"]
    config_dict["input_data_dir"] = str(tmp_path)

    return config_dict


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


@pytest.mark.parametrize(
    "input_config_dict, message_pattern",
    [
        pytest.param(
            "config_force_GIN_dict",
            "Fetching input data from the provided GIN repository",
            marks=pytest.mark.slow,
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
