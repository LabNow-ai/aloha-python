import json
import logging
import os
import socket
from datetime import datetime, timezone
from os.path import join as pjoin

from .handler import MultiProcessSafeDailyRotatingFileHandler

DEFAULT_LOG_FORMAT = "%(levelname)s> %(asctime)s> %(module)s:%(lineno)s> %(message)s"


class JsonFormatter(logging.Formatter):
    """Format log records as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            ),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False)


def get_formatter(log_format: str = "plain", formatter_str: str | None = None) -> logging.Formatter:
    """Build a formatter from a predefined name or a custom format string."""
    if formatter_str:
        return logging.Formatter(formatter_str)
    if log_format == "plain":
        return logging.Formatter(DEFAULT_LOG_FORMAT)
    if log_format == "json":
        return JsonFormatter()
    raise ValueError(f"Unsupported log format: {log_format!r}. Choose 'plain' or 'json'.")


def setup_logger(
    logger: logging.Logger,
    level: int = logging.DEBUG,
    logger_name: str | None = None,
    module: str | None = None,
    formatter_str: str | None = None,
    log_format: str = "plain",
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
    :param log_format: Predefined format name, either ``plain`` or ``json``
    """
    if not logger.handlers:
        formatter = get_formatter(log_format=log_format, formatter_str=formatter_str)

        folder = os.environ.get("DIR_LOG", "logs")
        os.makedirs(folder, exist_ok=True)

        if module is None:
            from ..settings import SETTINGS

            module = SETTINGS.config.get("APP_MODULE") or os.environ.get("APP_MODULE", None)

        if logger_name is not None and len(logger_name) > 0:
            logger_name = logger_name.strip().replace(" ", "_")

        path_file = [module, logger_name, socket.gethostname(), f"p{os.getpid()}"]  # module, logger_name, hostname, pid
        path_file = "_".join(str(i) for i in path_file if i is not None and len(str(i)) > 0)
        path_file = pjoin(folder, f"{path_file}.log")

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
