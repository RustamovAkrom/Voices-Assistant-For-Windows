import logging
from logging.handlers import RotatingFileHandler
from core import settings


logger = logging.getLogger("VoiceAsistant")
if settings.LOGGER_ACTIVE:
    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(
        settings.LOGGER_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
