import json
import logging

import pytest

from aloha.logger.logger import JsonFormatter, get_formatter


def test_json_formatter_outputs_structured_record():
    record = logging.LogRecord("worker", logging.INFO, "worker.py", 7, "hello %s", ("world",), None)

    payload = json.loads(JsonFormatter().format(record))

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