import logging

from workflows.utils import setup_logger


def test_setup_logger():
    logger = setup_logger()

    assert logger.level == logging.DEBUG
    assert logger.name == "workflows.utils"
    assert logger.hasHandlers()
    assert len(logger.handlers) == 1
    assert logger.handlers[0].name == "console_handler"
