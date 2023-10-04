import json
import logging
import os
from pathlib import Path

import pytest

from brainglobe_workflows.cellfinder.cellfinder_main import (
    default_config_dict,
    run_workflow_from_cellfinder_run,
    setup_workflow,
)


@pytest.fixture(autouse=True, scope="session")
def logger_str():
    logging.root.setLevel(logging.DEBUG)
    logger_str = "brainglobe_workflows.cellfinder.cellfinder_main"
    return logger_str


@pytest.fixture(autouse=True, scope="function")
def cellfinder_cache_dir(tmp_path):
    # use pytest's tmp_path fixture so that all is cleared after the test
    # a new temporary directory is created every function call
    return Path(tmp_path) / ".cellfinder_benchmarks"


@pytest.fixture()
def config_from_env_var(tmp_path, cellfinder_cache_dir):
    # dump config from fixture into a json file
    # ensure all Paths are JSON serializable
    def prep_json(obj):
        if isinstance(obj, Path):
            return str(obj)
        else:
            return json.JSONEncoder.default(obj)

    # create a temp json file to dump config data
    input_config_path = tmp_path / "input_config.json"

    # alter config if required by the test
    # - missing signal directory
    # - missing background directory
    config_dict = default_config_dict(cellfinder_cache_dir)

    # dump config into json
    with open(input_config_path, "w") as js:
        json.dump(config_dict, js, default=prep_json)

    # define environment variable pointing to this json file
    os.environ["CELLFINDER_CONFIG_PATH"] = str(input_config_path)

    yield os.environ["CELLFINDER_CONFIG_PATH"]
    # teardown for this fixture
    del os.environ["CELLFINDER_CONFIG_PATH"]


def test_run_with_env_var_config(config_from_env_var, caplog, logger_str):
    # check environment variable exists
    assert "CELLFINDER_CONFIG_PATH" in os.environ.keys()

    # run setup and workflow
    with caplog.at_level(logging.DEBUG, logger=logger_str):
        cfg = setup_workflow()
        run_workflow_from_cellfinder_run(cfg)

    # check log
    assert (
        "Configuration retrieved from "
        f'{os.environ["CELLFINDER_CONFIG_PATH"]}' in caplog.messages
    )
    assert (
        "Fetching input data from the "
        "provided GIN repository" in caplog.messages
    )

    # check output directory and output file exist
    assert Path(cfg.output_path).exists()
    assert (Path(cfg.output_path) / cfg.detected_cells_filename).is_file()


def test_run_with_default_config(cellfinder_cache_dir, caplog, logger_str):
    # check environment var is not defined
    assert "CELLFINDER_CONFIG_PATH" not in os.environ.keys()

    # run setup and workflow
    with caplog.at_level(logging.DEBUG, logger=logger_str):
        cfg = setup_workflow(cellfinder_cache_dir)
        run_workflow_from_cellfinder_run(cfg)

    # check log
    assert "Using default configuration" in caplog.messages
    assert (
        "Fetching input data from the "
        "provided GIN repository" in caplog.messages
    )

    # check output directory and output file exist
    assert Path(cfg.output_path).exists()
    assert (Path(cfg.output_path) / cfg.detected_cells_filename).is_file()


# test running on local data?
# def test_run_with_default_config_local(
#     caplog, logger_str
# ):
#     # check environment var is not defined
#     assert "CELLFINDER_CONFIG_PATH" not in os.environ.keys()

#     # run setup and workflow
#     # do not pass a cellfinder_cache_dir location to use default
#     with caplog.at_level(
#         logging.DEBUG, logger=logger_str
#     ):
#         cfg = setup_workflow()
#         run_workflow_from_cellfinder_run(cfg)

#     # check log
#     assert "Using default configuration" in caplog.messages
#     assert (
#         "Fetching input data from the "
#         "local directories" in caplog.messages
#     )
