import io
import json
import logging
from datetime import datetime, timezone

import pytest
from aloha.logger.logger import JsonFormatter, StackInfoFilter, get_formatter, get_logger


def test_plain_formatter_matches_uvicorn_default_format():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello", (), None)
    record.created = datetime(2026, 9, 27, 13, 25, 45, 547000, tzinfo=timezone.utc).timestamp()

    output = get_formatter().format(record)

    assert output.startswith("INFO:     2026-09-27T13:25:45.547Z ")
    assert output.endswith("worker.py:7 hello")
    assert "\x1b[" not in output


def test_plain_formatter_colors_level_prefix_when_enabled():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello", (), None)

    output = get_formatter(use_colors=True).format(record)

    assert output.startswith("\x1b[32mINFO\x1b[0m:     ")
    assert output.endswith("worker.py:7 hello")


def test_access_formatter_uses_uvicorn_style_without_source():
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "h11_impl.py",
        477,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1:50430", "GET", "/", "1.1", 404),
        None,
    )

    output = get_formatter(access_log=True).format(record)

    assert output == 'INFO:     127.0.0.1:50430 - "GET / HTTP/1.1" 404 Not Found'
    assert "h11_impl.py" not in output


def test_json_formatter_outputs_structured_record():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello %s", ("world",), None)
    record.created = datetime(2026, 9, 27, 13, 25, 45, 547000, tzinfo=timezone.utc).timestamp()

    payload = json.loads(JsonFormatter().format(record))

    assert payload["timestamp"] == "2026-09-27T13:25:45.547Z"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "worker"
    assert payload["source"] == "worker.py:7"
    assert "module" not in payload
    assert "line" not in payload
    assert payload["message"] == "hello world"


def test_json_access_formatter_omits_source():
    record = logging.LogRecord("uvicorn.access", logging.INFO, "h11_impl.py", 477, "GET / 404", (), None)

    payload = json.loads(get_formatter(log_format="json", access_log=True).format(record))

    assert payload["message"] == "GET / 404"
    assert "source" not in payload


def test_warning_logs_include_stack_info():
    logger = logging.getLogger("warning_stack_test")
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(logging.WARNING)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(get_formatter())
    handler.addFilter(StackInfoFilter())
    logger.addHandler(handler)

    logger.warning("warning")

    output = stream.getvalue()
    assert "Stack (most recent call last):" in output
    assert "test_warning_logs_include_stack_info" in output

    logger.removeHandler(handler)


def test_setup_logger_routes_console_output_to_requested_stream(monkeypatch, tmp_path):
    from aloha.logger.logger import setup_logger

    stream = io.StringIO()
    logger = logging.getLogger("requested_stream_test")
    logger.handlers.clear()
    monkeypatch.setenv("DIR_LOG", str(tmp_path))

    setup_logger(
        logger,
        logger_name="requested_stream_test",
        module="test",
        stream=stream,
        log_format_file="json",
        log_format_stream="plain",
    )
    logger.info("hello")

    assert stream.getvalue().startswith("INFO:     ")
    assert stream.getvalue().endswith("hello\n")
    files_log = list(tmp_path.glob("test_requested_stream_test_*.log"))
    assert len(files_log) == 1
    payload = json.loads(files_log[0].read_text().splitlines()[0])
    assert payload["message"] == "hello"
    assert payload["source"].startswith("test_logger.py:")

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


def test_ordinary_loggers_share_file_and_keep_stream_format_separate(monkeypatch, tmp_path):
    stream_ordinary = io.StringIO()
    stream_access = io.StringIO()
    monkeypatch.setenv("DIR_LOG", str(tmp_path))
    logger_ordinary = get_logger(
        "ordinary_format_test",
        module="app",
        stream=stream_ordinary,
        log_format_file="json",
        log_format_stream="plain",
    )
    logger_uvicorn = logging.getLogger("ordinary_format_test.uvicorn")
    logger_uvicorn.setLevel(logging.DEBUG)
    logger_uvicorn.propagate = True
    logger_access = get_logger(
        "access_format_test",
        module="access_app",
        stream=stream_access,
        access_log=True,
        log_format_file="json",
        log_format_stream="plain",
    )
    logger_access.propagate = False

    try:
        logger_ordinary.info("aloha ordinary")
        logger_uvicorn.warning("uvicorn ordinary")
        logger_access.info('%s - "%s %s HTTP/%s" %d', "127.0.0.1:1", "GET", "/", "1.1", 200)

        files_log = list(tmp_path.glob("*.log"))
        assert len(files_log) == 2
        records_log = [json.loads(line) for path in files_log for line in path.read_text().splitlines()]
        assert len(records_log) == 3
        assert {record["message"] for record in records_log} == {
            "aloha ordinary",
            "uvicorn ordinary",
            '127.0.0.1:1 - "GET / HTTP/1.1" 200',
        }
        assert "aloha ordinary" in stream_ordinary.getvalue()
        assert "uvicorn ordinary" in stream_ordinary.getvalue()
        assert "GET / HTTP/1.1" in stream_access.getvalue()
        assert "source" not in next(record for record in records_log if record["logger"] == "access_format_test")
    finally:
        for logger in (logger_ordinary, logger_access):
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()
        logger_uvicorn.propagate = False


def test_json_warning_records_include_stack_info():
    record = logging.LogRecord("worker", logging.WARNING, "worker.py", 7, "warning", (), None)

    StackInfoFilter().filter(record)
    payload = json.loads(JsonFormatter().format(record))

    assert "Stack (most recent call last):" in payload["stack_info"]


def test_custom_formatter_takes_precedence():
    formatter = get_formatter(log_format="json", formatter_str="%(message)s")

    assert formatter.format(logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello", (), None)) == "hello"


def test_unknown_formatter_is_rejected():
    with pytest.raises(ValueError, match="Unsupported log format"):
        get_formatter("xml")