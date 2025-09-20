import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=7, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def setup_logging(debug: bool) -> None:
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        handlers=[InterceptHandler(level=log_level)], level=log_level, force=True
    )
    logger.configure(handlers=[{"sink": sys.stderr, "level": log_level}])
