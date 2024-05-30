import os
import pathlib
import sys

import pytest
import torch
from brainglobe_utils.general.config import get_config_obj
from cellfinder.core.download.cli import main as cellfinder_download
from cellfinder.core.tools.system import force_cpu

test_data_dir = pathlib.Path(__file__) / ".." / ".." / "data"
data_dir = test_data_dir / "brain"
test_output_dir = test_data_dir / "registration_output"

TEST_ATLAS = "allen_2017_100um"


@pytest.fixture(scope="session", autouse=True)
def set_device_arm_macos_ci():
    """
    Ensure that the device is set to CPU when running on arm based macOS
    GitHub runners. This is to avoid the following error:
    https://discuss.pytorch.org/t/mps-back-end-out-of-memory-on-github-action/189773/5
    """
    if (
        os.getenv("GITHUB_ACTIONS") == "true"
        and torch.backends.mps.is_available()
    ):
        force_cpu()


def download_atlas(directory):
    download_args = [
        "cellfinder_download",
        "--atlas",
        TEST_ATLAS,
        "--install-path",
        directory,
        "--no-amend-config",
        "--no-models",
    ]
    sys.argv = download_args
    cellfinder_download()
    return directory


def generate_test_config(atlas_dir):
    config = test_data_dir / "config" / "test.conf"
    config_obj = get_config_obj(config)
    atlas_conf = config_obj["atlas"]
    orig_base_directory = atlas_conf["base_folder"]

    with open(config, "r") as in_conf:
        data = in_conf.readlines()
    for i, line in enumerate(data):
        data[i] = line.replace(
            f"base_folder = '{orig_base_directory}",
            f"base_folder = '{atlas_dir / 'atlas' / TEST_ATLAS}",
        )
    test_config = atlas_dir / "config.conf"
    with open(test_config, "w") as out_conf:
        out_conf.writelines(data)

    return test_config


@pytest.fixture()
def test_config_path(tmpdir):
    print("fixture")
    atlas_directory = str(tmpdir)
    download_atlas(atlas_directory)
    test_config = generate_test_config(atlas_directory)
    return test_config
