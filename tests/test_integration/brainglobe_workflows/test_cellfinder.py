import logging
import subprocess
import sys
from pathlib import Path

import pytest

# --->why do I need setup_all??
from pytest import MonkeyPatch

from brainglobe_workflows.cellfinder import (
    CellfinderConfig,
    main,
    run_workflow_from_cellfinder_run,
)
from brainglobe_workflows.cellfinder import (
    setup as setup_full,
)


# should this be unit test?
def test_setup(
    default_input_config_cellfinder: Path,
    custom_logger_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test full setup for cellfinder workflow

    Parameters
    ----------
    default_input_config_cellfinder : Path
        Default input config file
    custom_logger_name : str
        Name of custom logger
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run setup on default configuration
    cfg = setup_full(str(default_input_config_cellfinder))

    # check logger exists
    logger = logging.getLogger(custom_logger_name)
    assert logger.level == logging.DEBUG
    assert logger.hasHandlers()

    # check config is CellfinderConfig
    assert isinstance(cfg, CellfinderConfig)


# should this be unit test?
def test_run_workflow_from_cellfinder_run(
    default_input_config_cellfinder: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test running cellfinder workflow

    Parameters
    ----------
    default_input_config_cellfinder : Path
        Default input config file
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run setup --- have as a fixture for these two test instead?
    cfg = setup_full(str(default_input_config_cellfinder))

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files are those expected?
    assert Path(cfg.detected_cells_path).is_file()


# TODO: test main with default and custom json?
def test_main(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Test main function for setting up and running cellfinder workflow

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    cfg = main()

    # check output files are those expected?
    assert (cfg.detected_cells_path).is_file()


# TODO: test main CLI with default and specific json?
def test_app_wrapper(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Test running the cellfinder worklfow from the command line

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[3]
            / "brainglobe_workflows"
            / "cellfinder.py",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0


# TODO: test main CLI with default and specific json?
def test_main_entry_point(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Test running the cellfinder workflow via the predefined entry point

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    #  monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        ["cellfinder-workflow"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0
