import json
import logging
import re
from pathlib import Path

import pytest
import pooch
from brainglobe_workflows.utils import setup_logger


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



@pytest.mark.skip(reason="focus of PR62")
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
    ],
)
def test_add_input_paths(
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

    # instantiate custom logger
    _ = setup_logger()

    # read json as Cellfinder config
    # ---> change so that the fixture is the config object!
    # config = read_cellfinder_config(input_configs_dir / input_config)
    _ = request.getfixturevalue(input_config_dict)

    # check log messages
    assert len(caplog.messages) > 0
    out = re.fullmatch(message_pattern, caplog.messages[-1])
    assert out is not None
    assert out.group() is not None


@pytest.mark.parametrize(
    "input_config_path, message",
    [
        ("default_input_config_cellfinder", "Using default config file"),
        # ("config_GIN", "Input config read from"),
    ],
)
def test_read_cellfinder_config(
    input_config_path: str,
    message: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    request: pytest.FixtureRequest,
):
    """Test setup steps for the cellfinder workflow, using the default config
    and passing a specific config file.

    These setup steps include:
    - instantiating a CellfinderConfig object using the input json file,
    - add the signal and background files to the config if these are not
      defined,
    - create a timestamped directory for the output of the workflow if
      it doesn't exist and add its path to the config

    Parameters
    ----------
    input_config : str
        Name of input config json file
    message : str
        Expected log message
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    caplog : pytest.LogCaptureFixture
        Pytest fixture to capture the logs during testing
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        setup,
        DEFAULT_JSON_CONFIG_PATH_CELLFINDER
    )

    # setup logger
    _ = setup_logger()

    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    # monkeypatch.chdir(tmp_path)

    # setup workflow
    config = setup(DEFAULT_JSON_CONFIG_PATH_CELLFINDER)

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
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        CellfinderConfig,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        setup as setup_full,
    )

    # run setup on default configuration
    cfg = setup_full(str(request.getfixturevalue(input_config)))

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
    ],
)
def test_run_workflow_from_cellfinder_run(
    input_config: str,
    request: pytest.FixtureRequest,
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
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        run_workflow_from_cellfinder_run,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        setup as setup_full,
    )

    # run setup
    cfg = setup_full(str(request.getfixturevalue(input_config)))

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()
