import json
import logging
import os
import socket
from copy import copy
from datetime import datetime, timezone
from os.path import join as pjoin

from .handler import MultiProcessSafeDailyRotatingFileHandler

DEFAULT_LOG_FORMAT = "%(levelprefix)s %(asctime)s %(module)s %(lineno)s %(message)s"
LEVEL_COLORS = {
    5: "34",
    logging.DEBUG: "36",
    logging.INFO: "32",
    logging.WARNING: "33",
    logging.ERROR: "31",
    logging.CRITICAL: "91",
}


def _format_timestamp(timestamp: float) -> str:
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


class PlainFormatter(logging.Formatter):
    """Format plain logs with an optional Uvicorn-style colored level prefix."""

    def __init__(self, fmt: str, use_colors: bool = False):
        super().__init__(fmt)
        self.use_colors = use_colors

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        level_name = record_copy.levelname
        if self.use_colors and record_copy.levelno in LEVEL_COLORS:
            level_name = f"\x1b[{LEVEL_COLORS[record_copy.levelno]}m{level_name}\x1b[0m"
        record_copy.__dict__["levelprefix"] = f"{level_name}:{' ' * (8 - len(record_copy.levelname))}"
        return super().formatMessage(record_copy)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        return _format_timestamp(record.created)


class JsonFormatter(logging.Formatter):
    """Format log records as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": _format_timestamp(record.created),
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


def get_formatter(
    log_format: str = "plain",
    formatter_str: str | None = None,
    use_colors: bool = False,
) -> logging.Formatter:
    """Build a formatter from a predefined name or a custom format string."""
    if formatter_str:
        return logging.Formatter(formatter_str)
    if log_format == "plain":
        return PlainFormatter(DEFAULT_LOG_FORMAT, use_colors=use_colors)
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
        stream_formatter = get_formatter(
            log_format=log_format,
            formatter_str=formatter_str,
            use_colors=stream_handler.stream.isatty(),
        )
        stream_handler.setFormatter(stream_formatter)
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
