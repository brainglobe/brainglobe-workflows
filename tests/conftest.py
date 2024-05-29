import os

import torch.backends.mps


def pytest_sessionstart(session):
    """
    Ensure that the device is set to CPU when running on arm based macOS
    GitHub runners. This is to avoid the following error:
    https://discuss.pytorch.org/t/mps-back-end-out-of-memory-on-github-action/189773/5
    """
    os.environ["KERAS_BACKEND"] = "torch"

    if (
        os.getenv("GITHUB_ACTIONS") == "true"
        and torch.backends.mps.is_available()
    ):
        import keras.src.backend.common.global_state

        keras.src.backend.common.global_state.set_global_attribute(
            "torch_device", "cpu"
        )
