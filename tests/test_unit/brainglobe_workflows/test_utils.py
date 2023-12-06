import logging

from brainglobe_workflows.utils import setup_logger


def test_setup_logger(custom_logger_name):
    logger = setup_logger()

    assert logger.level == logging.DEBUG
    assert logger.name == custom_logger_name
    assert logger.hasHandlers()
    assert len(logger.handlers) == 1
    assert logger.handlers[0].name == "console_handler"
