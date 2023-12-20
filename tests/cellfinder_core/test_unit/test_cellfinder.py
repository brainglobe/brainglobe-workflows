import json
import logging
import re
from pathlib import Path

import pooch
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


@pytest.mark.parametrize(
    "input_config",
    [
        "input_data_GIN.json",
        "input_data_locally.json",
        "input_data_missing_background.json",
        "input_data_missing_signal.json",
        "input_data_not_locally_or_GIN.json",
    ],
)
def test_read_cellfinder_config(input_config: str, input_configs_dir: Path):
    """Test for reading a cellfinder config file

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

    # path to config json file
    input_config_path = input_configs_dir / input_config

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
    "input_config, message_pattern",
    [
        (
            "input_data_GIN.json",
            "Fetching input data from the provided GIN repository",
        ),
        (
            "input_data_locally.json",
            "Fetching input data from the local directories",
        ),
        (
            "input_data_missing_background.json",
            "The directory .+ does not exist$",
        ),
        ("input_data_missing_signal.json", "The directory .+ does not exist$"),
        (
            "input_data_not_locally_or_GIN.json",
            "Input data not found locally, and URL/hash to "
            "GIN repository not provided",
        ),
    ],
)
def test_add_signal_and_background_files(
    mock_home_directory,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    cellfinder_GIN_data: dict,
    input_configs_dir: Path,
    input_config: str,
    message_pattern: str,
):
    """Test signal and background files addition to the cellfinder config

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Pytest fixture to capture the logs during testing
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    cellfinder_GIN_data : dict
        Dict holding the URL and hash of the cellfinder test data in GIN
    input_configs_dir : Path
        Test data directory path
    input_config : str
        Name of input config json file
    message_pattern : str
        Expected pattern in the log
    """
    # mock_home_directory

    # import after mocking home dir!
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        add_signal_and_background_files,
        read_cellfinder_config,
    )

    # instantiate our custom logger
    _ = setup_logger()

    # read json as Cellfinder config
    config = read_cellfinder_config(input_configs_dir / input_config)

    # monkeypatch cellfinder config:
    # set install_path to pytest temporary directory
    # config._install_path =
    # Path.home() / ".brainglobe" / "workflows" / "cellfinder_core"
    # config._install_path = tmp_path / config._install_path

    # check lists of signal and background files are not defined
    assert not (config._list_signal_files and config._list_background_files)

    # monkeypatch cellfinder config:
    # if config is "local" or "signal/background missing":
    # ensure signal and background data from GIN are downloaded locally
    if input_config in [
        "input_data_locally.json",
        "input_data_missing_signal.json",
        "input_data_missing_background.json",
    ]:
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

    # add signal and background files lists to config
    add_signal_and_background_files(config)

    # check log messages
    assert len(caplog.messages) > 0
    out = re.fullmatch(message_pattern, caplog.messages[-1])
    assert out is not None
    assert out.group() is not None


@pytest.mark.parametrize(
    "input_config, message",
    [
        ("default_input_config_cellfinder", "Using default config file"),
        ("input_config_fetch_GIN", "Input config read from"),
    ],
)
def test_setup_workflow(
    input_config: str,
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
    from brainglobe_workflows.cellfinder_core.cellfinder import setup_workflow

    # setup logger
    _ = setup_logger()

    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # setup workflow
    config = setup_workflow(request.getfixturevalue(input_config))

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
        "default_input_config_cellfinder",
        "input_config_fetch_GIN",
        "input_config_fetch_local",
    ],
)
def test_setup(
    input_config: str,
    custom_logger_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
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
    monkeypatch.chdir(tmp_path)

    # run setup on default configuration
    cfg = setup_full(request.getfixturevalue(input_config))

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
        "input_config_fetch_GIN",
        "input_config_fetch_local",
    ],
)
def test_run_workflow_from_cellfinder_run(
    input_config: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
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
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        run_workflow_from_cellfinder_run,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        setup as setup_full,
    )

    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run setup
    cfg = setup_full(str(request.getfixturevalue(input_config)))

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files are those expected?
    assert Path(cfg._detected_cells_path).is_file()
