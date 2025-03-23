import logging
import sys

_logger = None


def setup_logger():
    global _logger
    if _logger:
        return _logger

    _logger = logging.getLogger("telegram_bot")

    if not _logger.handlers:
        _logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
        _logger.propagate = False

    return _logger
