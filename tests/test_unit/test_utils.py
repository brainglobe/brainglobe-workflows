import logging

from workflows.utils import setup_logger


def test_setup_logger():
    logger = setup_logger()
    assert logger.level == logging.DEBUG
