import pytest


@pytest.fixture()
def custom_logger_name() -> str:
    """Return name of custom logger created in workflow utils

    Returns
    -------
    str
        Name of custom logger
    """
    from brainglobe_workflows.utils import __name__ as LOGGER_NAME

    return LOGGER_NAME
