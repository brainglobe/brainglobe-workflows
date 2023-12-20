import json
import logging
import re
from pathlib import Path

import pytest

# from brainglobe_workflows.cellfinder_core.cellfinder import (
#     # CellfinderConfig,
#     add_signal_and_background_files,
#     read_cellfinder_config,
#     run_workflow_from_cellfinder_run,
#     setup_workflow,
# )
# from brainglobe_workflows.cellfinder_core.cellfinder import
# setup as setup_full
from brainglobe_workflows.utils import (
    DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
    setup_logger,
)


def test_read_cellfinder_config():
    """Test for reading a cellfinder config file default

    Parameters
    ----------
    input_config : str
        Name of input config json file
    input_configs_dir : Path
        Test data directory path
    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        read_cellfinder_config,
    )

    input_config_path = DEFAULT_JSON_CONFIG_PATH_CELLFINDER
    # request.getfixturevalue(input_config)

    # read json as Cellfinder config
    config = read_cellfinder_config(input_config_path)

    # read json as dict
    with open(input_config_path) as cfg:
        config_dict = json.load(cfg)

    # check keys of dictionary are a subset of Cellfinder config attributes
    assert all(
        [ky in config.__dataclass_fields__.keys() for ky in config_dict.keys()]
    )


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
    "input_config, message",
    [
        (DEFAULT_JSON_CONFIG_PATH_CELLFINDER, "Using default config file"),
        # ("config_GIN", "Input config read from"),
    ],
)
def test_setup_workflow(
    input_config: str,
    message: str,
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
    from brainglobe_workflows.cellfinder_core.cellfinder import setup_workflow

    # setup logger
    _ = setup_logger()

    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    # monkeypatch.chdir(tmp_path)

    # setup workflow
    config = setup_workflow(
        input_config
    )  # request.getfixturevalue(input_config))

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

    # check output file path
    assert (
        Path(config._detected_cells_path)
        == Path(config.output_path) / config.detected_cells_filename
    )


@pytest.mark.parametrize(
    "input_config",
    [
        DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
        # "input_config_fetch_GIN",
        # "input_config_fetch_local",
    ],
)
def test_setup(
    input_config: str,
    custom_logger_name: str,
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
        setup as setup_full,
    )

    # Monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    # monkeypatch.chdir(tmp_path)
    # run setup on default configuration
    cfg = setup_full(input_config)  # (request.getfixturevalue(input_config))

    # check logger exists
    logger = logging.getLogger(custom_logger_name)
    assert logger.level == logging.DEBUG
    assert logger.hasHandlers()

    # check config is CellfinderConfig
    assert isinstance(cfg, CellfinderConfig)


@pytest.mark.parametrize(
    "input_config",
    [
        DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
        # "input_config_fetch_GIN",
        # "input_config_fetch_local",
    ],
)
def test_run_workflow_from_cellfinder_run(
    input_config: str,
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
        setup as setup_full,
    )

    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    # monkeypatch.chdir(tmp_path)
    # run setup
    cfg = setup_full(
        input_config
    )  # str(request.getfixturevalue(input_config)))

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files are those expected?
    assert Path(cfg._detected_cells_path).is_file()
