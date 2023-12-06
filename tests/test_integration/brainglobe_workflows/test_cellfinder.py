import logging
import subprocess
import sys
from pathlib import Path

from brainglobe_workflows.cellfinder import (
    CellfinderConfig,
    main,
    run_workflow_from_cellfinder_run,
)
from brainglobe_workflows.cellfinder import (
    setup as setup_all,  # --->why do I need setup_all??
)


def test_setup(
    default_input_config_cellfinder, custom_logger_name, monkeypatch, tmp_path
):
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run setup on default configuration
    cfg = setup_all(default_input_config_cellfinder)

    # check logger exists
    logger = logging.getLogger(custom_logger_name)
    assert logger.level == logging.DEBUG
    assert logger.hasHandlers()

    # check config is CellfinderConfig
    assert isinstance(cfg, CellfinderConfig)


def test_run_workflow_from_cellfinder_run(
    default_input_config_cellfinder, monkeypatch, tmp_path
):
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run setup --- have as a fixture for these two test instead?
    cfg = setup_all(default_input_config_cellfinder)

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files are those expected?
    assert (cfg.detected_cells_path).is_file()


# TODO: test main with default and custom json?
def test_main(monkeypatch, tmp_path):
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    cfg = main()

    # check output files are those expected?
    assert (cfg.detected_cells_path).is_file()


# TODO: test main CLI with default and custom json?
def test_app_wrapper(monkeypatch, tmp_path):
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
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


def test_main_entry_point(monkeypatch, tmp_path):
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
