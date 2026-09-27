import json
import logging
from datetime import datetime, timezone

import pytest
from aloha.logger.logger import JsonFormatter, get_formatter


def test_plain_formatter_matches_uvicorn_default_format():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello", (), None)
    record.created = datetime(2026, 9, 27, 13, 25, 45, 547000, tzinfo=timezone.utc).timestamp()

    output = get_formatter().format(record)

    assert output.startswith("INFO:     2026-09-27T13:25:45.547Z ")
    assert output.endswith("worker 7 hello")
    assert "\x1b[" not in output


def test_plain_formatter_colors_level_prefix_when_enabled():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello", (), None)

    output = get_formatter(use_colors=True).format(record)

    assert output.startswith("\x1b[32mINFO\x1b[0m:     ")
    assert output.endswith("worker 7 hello")


def test_json_formatter_outputs_structured_record():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello %s", ("world",), None)
    record.created = datetime(2026, 9, 27, 13, 25, 45, 547000, tzinfo=timezone.utc).timestamp()

    payload = json.loads(JsonFormatter().format(record))

    assert payload["timestamp"] == "2026-09-27T13:25:45.547Z"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "worker"
    assert payload["module"] == "worker"
    assert payload["line"] == 7
    assert payload["message"] == "hello world"
    assert payload["timestamp"].endswith("Z")


def test_custom_formatter_takes_precedence():
    formatter = get_formatter(log_format="json", formatter_str="%(message)s")

    assert formatter.format(logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello", (), None)) == "hello"


def test_unknown_formatter_is_rejected():
    with pytest.raises(ValueError, match="Unsupported log format"):
        get_formatter("xml")