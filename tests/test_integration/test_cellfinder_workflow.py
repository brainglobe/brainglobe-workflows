import json
import logging
import os
from pathlib import Path, PosixPath

import pytest

from brainglobe_workflows.cellfinder.cellfinder_main import (
    run_workflow_from_cellfinder_run,
    setup_workflow,
)


@pytest.fixture(autouse=True)
def cellfinder_cache_dir(tmp_path):
    # use pytest's tmp_path fixture so that all is cleared after the test
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

    return os.environ["CELLFINDER_CONFIG_PATH"]


class TestsCellfinderWorkflow:
    # def test_run_with_default_config(self, caplog):
    # --this would generate files in ~/.cellfinder_benchmark!
    #     caplog.set_level(logging.INFO)
    #     cfg = setup_workflow()
    #     run_workflow_from_cellfinder_run(cfg)

    #     assert 'Using default configuration' in caplog.text

    def test_run_with_predefined_default_config(
        self, config_from_dict, caplog
    ):
        caplog.set_level(logging.INFO)
        cfg = setup_workflow(config_from_dict)
        run_workflow_from_cellfinder_run(cfg)

        assert "Using default configuration" in caplog.text

    def test_run_with_env_var_defined_config(
        self, config_from_env_var, caplog
    ):
        caplog.set_level(logging.INFO)
        cfg = setup_workflow()
        run_workflow_from_cellfinder_run(cfg)
        assert "BRAINGLOBE_REGISTRATION_CONFIG_PATH" in os.environ.keys()
        assert (
            "Configuration retrieved from "
            f'{os.environ["CELLFINDER_CONFIG_PATH"]}' in caplog.text
        )
