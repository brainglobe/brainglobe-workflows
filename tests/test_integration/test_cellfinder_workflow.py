import json
import logging
import os
from pathlib import Path, PosixPath

import pytest

from brainglobe_workflows.cellfinder.cellfinder_main import (
    run_workflow_from_cellfinder_run,
    setup_workflow,
)

# logger_str = 'brainglobe_workflows.cellfinder.cellfinder_main'


@pytest.fixture(autouse=True, scope="session")
def logger_setup():
    logging.root.setLevel(logging.DEBUG)


@pytest.fixture(autouse=True, scope="function")
def cellfinder_cache_dir(tmp_path):
    # use pytest's tmp_path fixture so that all is cleared after the test
    # a new temporary directory is created every function call
    return Path(tmp_path) / ".cellfinder_benchmarks"


@pytest.fixture()
def config_from_dict(cellfinder_cache_dir):
    DATA_URL = "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip"
    DATA_HASH = (
        "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914"
    )
    CELLFINDER_CACHE_DIR = cellfinder_cache_dir

    workflow_config = {
        "install_path": CELLFINDER_CACHE_DIR,
        "data_url": DATA_URL,
        "data_hash": DATA_HASH,
        "local_path": CELLFINDER_CACHE_DIR / "cellfinder_test_data",
        "signal_parent_dir": str(
            CELLFINDER_CACHE_DIR / "cellfinder_test_data" / "signal"
        ),
        "background_parent_dir": str(
            CELLFINDER_CACHE_DIR / "cellfinder_test_data" / "background"
        ),
        "output_path": CELLFINDER_CACHE_DIR / "cellfinder_output",
        "detected_cells_filepath": (
            CELLFINDER_CACHE_DIR / "cellfinder_output" / "detected_cells.xml"
        ),
        "voxel_sizes": [5, 2, 2],  # microns
        "start_plane": 0,
        "end_plane": -1,
        "trained_model": None,  # if None, it will use a default model
        "model_weights": None,
        "model": "resnet50_tv",
        "batch_size": 32,
        "n_free_cpus": 2,
        "network_voxel_sizes": [5, 1, 1],
        "soma_diameter": 16,
        "ball_xy_size": 6,
        "ball_z_size": 15,
        "ball_overlap_fraction": 0.6,
        "log_sigma_size": 0.2,
        "n_sds_above_mean_thresh": 10,
        "soma_spread_factor": 1.4,
        "max_cluster_size": 100000,
        "cube_width": 50,
        "cube_height": 50,
        "cube_depth": 20,
        "network_depth": "50",
    }
    return workflow_config


@pytest.fixture()
def config_from_env_var(tmp_path, config_from_dict):
    # create a temp json file to dump config data
    input_config_path = tmp_path / "input_config.json"

    # dump config from fixture into a json file
    # ensure all Paths are JSON serializable
    def prep_json(obj):
        if isinstance(obj, PosixPath):
            return str(obj)
        else:
            return json.JSONEncoder.default(obj)

    with open(input_config_path, "w") as js:
        json.dump(config_from_dict, js, default=prep_json)

    # define environment variable pointing to this json file
    # --- should be cleared after this test!!
    os.environ["CELLFINDER_CONFIG_PATH"] = str(input_config_path)

    yield os.environ["CELLFINDER_CONFIG_PATH"]
    # teardown for this fixture
    del os.environ["CELLFINDER_CONFIG_PATH"]


def test_run_with_predefined_default_config(config_from_dict, caplog):
    # run setup and workflow
    with caplog.at_level(
        logging.DEBUG, logger="brainglobe_workflows.cellfinder.cellfinder_main"
    ):  # temporarily sets the log level for the given logger
        cfg = setup_workflow(config_from_dict)
        run_workflow_from_cellfinder_run(cfg)

    # check log
    assert "Using default configuration" in caplog.messages


def test_run_with_env_var_defined_config(config_from_env_var, caplog):
    # check environment variable exists
    assert "CELLFINDER_CONFIG_PATH" in os.environ.keys()

    # run setup and workflow
    with caplog.at_level(
        logging.DEBUG, logger="brainglobe_workflows.cellfinder.cellfinder_main"
    ):
        cfg = setup_workflow()
        run_workflow_from_cellfinder_run(cfg)

    # check log
    assert (
        "Configuration retrieved from "
        f'{os.environ["CELLFINDER_CONFIG_PATH"]}' in caplog.messages
    )


def test_setup_with_missing_signal_data(config_from_dict, caplog):
    # check neither signal or background data exist locally,
    assert not Path(config_from_dict["signal_parent_dir"]).exists()
    assert not Path(config_from_dict["background_parent_dir"]).exists()

    # create a directory for the background only
    Path(config_from_dict["background_parent_dir"]).mkdir(
        parents=True, exist_ok=True
    )

    # run setup
    # context manager temporarily sets the log level for the given logger
    with caplog.at_level(
        logging.DEBUG, logger="brainglobe_workflows.cellfinder.cellfinder_main"
    ):
        cfg = setup_workflow(config_from_dict)

    # check log-- when run as a suite, both directories exist already?
    assert (
        f"The directory {cfg.signal_parent_dir} "
        "does not exist" in caplog.messages
    )


def test_setup_with_missing_background_data(config_from_dict, caplog):
    # check neither signal or background data exist locally,
    assert not Path(config_from_dict["signal_parent_dir"]).exists()
    assert not Path(config_from_dict["background_parent_dir"]).exists()

    # create a directory for the signal, but not for the background
    Path(config_from_dict["signal_parent_dir"]).mkdir(
        parents=True, exist_ok=True
    )

    # run setup
    with caplog.at_level(
        logging.DEBUG, logger="brainglobe_workflows.cellfinder.cellfinder_main"
    ):
        cfg = setup_workflow(config_from_dict)

    # check log
    assert (
        f"The directory {cfg.background_parent_dir} "
        "does not exist" in caplog.messages
    )


def test_setup_fetching_from_GIN(config_from_dict, caplog):
    # check neither signal or background data exist locally before setup
    assert not Path(config_from_dict["signal_parent_dir"]).exists()
    assert not Path(config_from_dict["background_parent_dir"]).exists()

    # run setup
    with caplog.at_level(
        logging.DEBUG, logger="brainglobe_workflows.cellfinder.cellfinder_main"
    ):
        setup_workflow(config_from_dict)

    # check log
    assert (
        "Fetching input data from the "
        "provided GIN repository" in caplog.messages
    )
