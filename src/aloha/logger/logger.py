import logging
import os
import socket
from os.path import join as pjoin

from .handler import MultiProcessSafeDailyRotatingFileHandler


def setup_logger(
    logger: logging.Logger,
    level: int = logging.DEBUG,
    logger_name: str | None = None,
    module: str | None = None,
    formatter_str: str | None = None,
):
    """
    Set up a logger with file and stream handlers.

    Configures the logger with:
    - A multi-process safe daily rotating file handler
    - A console stream handler
    - A standard log format

    :param logger: Logger instance to set up
    :param level: Logging level (default: DEBUG)
    :param logger_name: Name of the logger (optional)
    :param module: Module name for log file naming (optional)
    :param formatter_str: Custom log format string (optional)
    """
    if not logger.handlers:
        formatter = logging.Formatter(formatter_str or "%(levelname)s> %(asctime)s> %(module)s:%(lineno)s> %(message)s")

        folder = os.environ.get("DIR_LOG", "logs")
        os.makedirs(folder, exist_ok=True)

        if module is None:
            from ..settings import SETTINGS

            module = SETTINGS.config.get("APP_MODULE") or os.environ.get("APP_MODULE", None)

        if logger_name is not None and len(logger_name) > 0:
            logger_name = logger_name.strip().replace(" ", "_")

        path_file = [module, logger_name, socket.gethostname(), "p%s" % os.getpid()]  # module, logger_name, hostname, pid
        path_file = "_".join(str(i) for i in path_file if i is not None and len(str(i)) > 0)
        path_file = pjoin(folder, "%s.log" % path_file)

        file_handler = MultiProcessSafeDailyRotatingFileHandler(path_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        logger.setLevel(level)


def get_logger(logger_name: str | None = None, level=logging.DEBUG, **kwargs) -> logging.Logger:
    """
    Get a configured logger instance.

    Creates or retrieves a logger by name and sets it up with file and stream handlers.
    Accepts both string and integer log levels.

    :param level: Logging level (int or str, default: DEBUG)
    :param logger_name: Name of the logger (default: 'default')
    :param args: Additional arguments passed to setup_logger
    :param kwargs: Additional keyword arguments passed to setup_logger
    :return: Configured logger instance
    """

    logger = logging.getLogger(logger_name)

    if isinstance(level, str):
        level = getattr(logging, str(level).upper(), 10)

    setup_logger(logger, level=level, logger_name=logger_name, **kwargs)
    return logger


getLogger = get_logger
