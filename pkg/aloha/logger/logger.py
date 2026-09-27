import http
import json
import logging
import os
import socket
import traceback
from copy import copy
from datetime import datetime
from os.path import join as pjoin
from typing import TextIO

from .handler import MultiProcessSafeDailyRotatingFileHandler

DEFAULT_LOG_FORMAT = "%(levelprefix)s %(asctime)s %(source)s %(message)s"
DEFAULT_ACCESS_LOG_FORMAT = "%(levelprefix)s %(message)s"
LEVEL_COLORS = {
    5: "34",
    logging.DEBUG: "36",
    logging.INFO: "32",
    logging.WARNING: "33",
    logging.ERROR: "31",
    logging.CRITICAL: "91",
}
LOG_RECORD_FIELDS = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "levelprefix",
    "source",
}


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="milliseconds")


def _get_extra_fields(record: logging.LogRecord) -> dict:
    return {key: value for key, value in record.__dict__.items() if key not in LOG_RECORD_FIELDS}


class PlainFormatter(logging.Formatter):
    """Format plain logs with an optional Uvicorn-style colored level prefix."""

    def __init__(self, fmt: str, use_colors: bool = False, include_source: bool = True):
        super().__init__(fmt)
        self.use_colors = use_colors
        self.include_source = include_source

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        level_name = record_copy.levelname
        if self.use_colors and record_copy.levelno in LEVEL_COLORS:
            level_name = f"\x1b[{LEVEL_COLORS[record_copy.levelno]}m{level_name}\x1b[0m"
        record_copy.__dict__["levelprefix"] = f"{level_name}:{' ' * (8 - len(record_copy.levelname))}"
        if self.include_source:
            record_copy.__dict__["source"] = f"{record_copy.filename}:{record_copy.lineno}"
        else:
            if isinstance(record_copy.args, tuple) and len(record_copy.args) == 5:
                client_addr, method, full_path, http_version, status_code = record_copy.args
                try:
                    status_phrase = http.HTTPStatus(int(status_code)).phrase
                except ValueError:
                    status_phrase = ""
                status = f"{status_code} {status_phrase}".rstrip()
                request_line = f"{method} {full_path} HTTP/{http_version}"
                if self.use_colors:
                    request_line = f"\x1b[1m{request_line}\x1b[0m"
                    color_status = {
                        1: "97",
                        2: "32",
                        3: "33",
                        4: "31",
                        5: "91",
                    }.get(int(status_code) // 100)
                    if color_status:
                        status = f"\x1b[{color_status}m{status}\x1b[0m"
                record_copy.msg = f'{client_addr} - "{request_line}" {status}'
                record_copy.args = ()
                record_copy.message = record_copy.msg
            fields_extra = _get_extra_fields(record_copy)
            fields_extra.pop("logger", None)
            if fields_extra:
                msg_access = record_copy.getMessage()
                fields_access = json.dumps(fields_extra, ensure_ascii=False, default=str)
                record_copy.msg = f"{msg_access} {fields_access}"
                record_copy.args = ()
                record_copy.message = record_copy.msg
        return super().formatMessage(record_copy)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        return _format_timestamp(record.created)


class JsonFormatter(logging.Formatter):
    """Format log records as JSON objects."""

    def __init__(self, include_source: bool = True, include_logger: bool = True, include_extra: bool = False):
        super().__init__()
        self.include_source = include_source
        self.include_logger = include_logger
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": _format_timestamp(record.created),
            "level": record.levelname,
        }
        if self.include_logger:
            payload["logger"] = record.name
        payload["message"] = record.getMessage()
        if self.include_source:
            payload["source"] = f"{record.filename}:{record.lineno}"
        if self.include_extra:
            for key, value in _get_extra_fields(record).items():
                if key not in payload and (self.include_logger or key != "logger"):
                    payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info and record.levelno > logging.INFO:
            payload["stack_info"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class StackInfoFilter(logging.Filter):
    """Capture the calling stack for records above INFO when it was not supplied."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno > logging.INFO and not record.stack_info:
            frames = traceback.extract_stack()
            callsite = next(
                (
                    index
                    for index in range(len(frames) - 1, -1, -1)
                    if frames[index].filename == record.pathname and frames[index].lineno == record.lineno
                ),
                None,
            )
            if callsite is not None:
                frames = frames[: callsite + 1]
            else:
                frames = frames[:-1]
            record.stack_info = "Stack (most recent call last):\n" + "".join(traceback.format_list(frames))
        return True


def get_formatter(
    log_format: str = "plain",
    formatter_str: str | None = None,
    use_colors: bool = False,
    access_log: bool = False,
) -> logging.Formatter:
    """Build a formatter from a predefined name or a custom format string."""
    if formatter_str:
        return logging.Formatter(formatter_str)
    if log_format == "plain":
        format_log = DEFAULT_ACCESS_LOG_FORMAT if access_log else DEFAULT_LOG_FORMAT
        return PlainFormatter(format_log, use_colors=use_colors, include_source=not access_log)
    if log_format == "json":
        return JsonFormatter(include_source=not access_log, include_logger=not access_log, include_extra=access_log)
    raise ValueError(f"Unsupported log format: {log_format!r}. Choose 'plain' or 'json'.")


def setup_logger(
    logger: logging.Logger,
    level: int = logging.DEBUG,
    logger_name: str | None = None,
    module: str | None = None,
    formatter_str: str | None = None,
    log_format: str | None = None,
    log_format_file: str = "json",
    log_format_stream: str = "plain",
    stream: TextIO | None = None,
    access_log: bool = False,
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
    :param log_format: Deprecated format override for both file and stream
    :param log_format_file: Predefined format for the file handler
    :param log_format_stream: Predefined format for the console handler
    :param stream: Console output stream (defaults to stderr)
    :param access_log: Use the access-log format and omit the source location
    """
    if not logger.handlers:
        if log_format is not None:
            log_format_file = log_format
            log_format_stream = log_format

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
        file_handler.setFormatter(
            get_formatter(log_format=log_format_file, formatter_str=formatter_str, access_log=access_log)
        )
        file_handler.addFilter(StackInfoFilter())
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(stream)
        stream_formatter = get_formatter(
            log_format=log_format_stream,
            formatter_str=formatter_str,
            use_colors=stream_handler.stream.isatty(),
            access_log=access_log,
        )
        stream_handler.setFormatter(stream_formatter)
        stream_handler.addFilter(StackInfoFilter())
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
