import json
import logging
import re
from pathlib import Path

import pytest

from brainglobe_workflows.utils import setup_logger


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
    Test reading a cellfinder config

    Parameters
    ----------
    input_config_path : str
        path to input config file
    message : str
        Expected message in the log
    caplog : pytest.LogCaptureFixture
        Pytest fixture to capture the logs during testing
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name

    """
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        setup_config,
    )

    # instantiate custom logger
    _ = setup_logger()

    # read Cellfinder config
    config = setup_config(log_on=True)

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
    assert Path(config._output_path).resolve().is_dir()

    # check output directory name has correct format
    out = re.fullmatch(
        str(config.output_dir_basename) + "\\d{8}_\\d{6}$",
        Path(config._output_path).stem,
    )
    assert out is not None
    assert out.group() is not None

    # check output file path is as expected
    assert (
        Path(config._detected_cells_path)
        == Path(config._output_path) / config.detected_cells_filename
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
    """
    Test the full setup for the cellfinder workflow.

    Parameters
    ----------
    input_config : str
        Path to input config file
    custom_logger_name : str
        Name of custom logger
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        CellfinderConfig,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        setup as setup_workflow,
    )

    # run setup on default configuration
    cfg = setup_workflow()

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
    """
    Test running cellfinder workflow

    Parameters
    ----------
    input_config : str
        Path to input config json file
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        run_workflow,
    )
    from brainglobe_workflows.cellfinder_core.cellfinder_core import (
        setup as setup_workflow,
    )

    # run setup
    cfg = setup_workflow()

    # run workflow
    run_workflow(cfg)

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()
