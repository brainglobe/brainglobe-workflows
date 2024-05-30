import os

import pytest
import torch
from cellfinder.core.tools.system import force_cpu


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
