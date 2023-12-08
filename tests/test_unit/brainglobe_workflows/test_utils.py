import logging
from typing import List

import pytest

from brainglobe_workflows.utils import (
    DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
    config_parser,
    setup_logger,
)


def test_setup_logger(custom_logger_name: str):
    """Test custom logger is correctly created

    Parameters
    ----------
    custom_logger_name : str
        Pytest fixture for the custom logger name
    """
    logger = setup_logger()

    assert logger.level == logging.DEBUG
    assert logger.name == custom_logger_name
    assert logger.hasHandlers()
    assert logger.handlers[0].name == "console_handler"


@pytest.mark.parametrize(
    "list_input_args",
    [[], ["--config", str(DEFAULT_JSON_CONFIG_PATH_CELLFINDER)]],
)
def test_config_parser(list_input_args: List[str]):
    args = config_parser(
        list_input_args,
        str(DEFAULT_JSON_CONFIG_PATH_CELLFINDER),
    )

    assert args.config
