import pytest


@pytest.fixture()
def default_input_config_cellfinder():
    from brainglobe_workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER

    return DEFAULT_JSON_CONFIG_PATH_CELLFINDER


@pytest.fixture()
def custom_logger_name():
    from brainglobe_workflows.utils import __name__ as LOGGER_NAME

    return LOGGER_NAME
