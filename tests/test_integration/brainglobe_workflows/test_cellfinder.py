import logging

from brainglobe_workflows.cellfinder import (
    CellfinderConfig,
    run_workflow_from_cellfinder_run,
)
from brainglobe_workflows.cellfinder import (
    setup as setup_all,  # why do I need setup_all??
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

    # run setup
    cfg = setup_all(default_input_config_cellfinder)

    # run workflow
    run_workflow_from_cellfinder_run(cfg)

    # check output files are those expected?
    assert (cfg.detected_cells_path).is_file()


# def test_main
