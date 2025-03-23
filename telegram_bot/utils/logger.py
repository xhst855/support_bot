import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("support_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler = RotatingFileHandler("logs/bot.log", maxBytes=2_000_000, backupCount=5)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
