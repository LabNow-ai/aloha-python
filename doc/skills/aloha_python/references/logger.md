# Logging Module (`aloha.logger`)

The `aloha.logger` subpackage provides a pre-configured, multi-process safe logging framework.

## 1. Global Logger (`LOG`)

The module exports a global pre-configured logger named `LOG`. It reads log levels from settings under `deploy.log_level` (falling back to `logging.DEBUG` if unset). File and console formats are configured independently with `deploy.log_format_file` and `deploy.log_format_stream`; these default to `json` and `plain`, respectively.

### Usage Example

```python
from aloha.logger import LOG

def run_task():
    LOG.debug("Starting task processing...")
    try:
        # Task implementation
        LOG.info("Task completed successfully.")
    except Exception as e:
        LOG.error(f"Task failed: {e}", exc_info=True)
```

---

## 2. Dynamic Logger Creation (`get_logger`)

You can create named loggers dynamically with customized levels.

### Key Functions

- `get_logger(logger_name: str | None = None, level=logging.DEBUG, **kwargs) -> logging.Logger`: Retrieves and configures a logger.
- `getLogger`: An alias to `get_logger`.

### Usage Example

```python
from aloha.logger import get_logger

logger_custom = get_logger("database_sync", level="INFO")
logger_custom.info("Custom sync logger initialized.")
```

---

## 3. Implementation Details

### Predefined formats

Configure the format in HOCON:

```hocon
deploy = {
    log_level = "INFO"
    log_format_file = "json"
    log_format_stream = "plain"
}
```

Supported values are:

- `plain`: the default format, with an aligned level prefix, ISO 8601 timestamp with millisecond precision and the host's configured local UTC offset (the same representation as the JSON `timestamp` field), `filename:lineno` source location, and message. The console handler colors the level prefix by severity when its stream is a terminal; log files remain uncolored.
- `json`: one JSON object per line with `timestamp`, `level`, `logger`, `pid`, `hostname`, `source` (`filename:lineno`), and `message` fields. `pid` and `hostname` identify the current Python process and runtime host. Exception information is included when available. WARNING and higher records also include a captured calling stack in `stack_info`.

The file format defaults to `json`; the console format defaults to `plain`. The console formatter adds colors when its output stream is a terminal. The deprecated `log_format` argument to `setup_logger` and `get_logger` remains available as an explicit override for both handlers. `formatter_str`, when provided, takes precedence over the selected formats for both handlers.

- Aloha and FastAPI/Uvicorn ordinary logs share the root logger's stderr handler and one ordinary log file. Ordinary Uvicorn loggers propagate to the root instead of creating duplicate files.
- Uvicorn access logs write to stdout and a separate `<APP_MODULE>_<YYYY-MMDD>.access.log` file. Their file/console formats use the same independent settings; in plain mode they use Uvicorn's access format without a source location and append `pid`, `hostname`, and additional `LogRecord` fields as a JSON object. In JSON mode the `source` and `logger` fields are omitted, while `pid`, `hostname`, and additional `LogRecord` fields are included.

### Parsing timestamps

Log timestamps are ISO 8601 strings with the runtime host's UTC offset, for example `2026-09-27T23:20:41.353+08:00`. Parse them as timezone-aware values to preserve the represented instant.

In Python, `datetime.fromisoformat()` parses the offset into an aware `datetime`:

```python
from datetime import datetime

timestamp_log = datetime.fromisoformat("2026-09-27T23:20:41.353+08:00")
```

In DuckDB, cast the string to `TIMESTAMPTZ`:

```sql
SELECT CAST('2026-09-27T23:20:41.353+08:00' AS TIMESTAMPTZ) AS timestamp_log;
```

- **Safe Concurrent File Writes**: Utilizes `MultiProcessSafeDailyRotatingFileHandler` to avoid lock conflicts or log corruption when multiple parallel processes write logs concurrently.
- **Log Location**: Writes logs to the directory specified by the `DIR_LOG` environment variable (defaults to `logs/`).
- **File Naming Format**: Ordinary log files use `<APP_MODULE>_<YYYY-MMDD>.log`; access log files use `<APP_MODULE>_<YYYY-MMDD>.access.log`. If `APP_MODULE` is unset or empty, `default` is used. For example: `Aloha_2026-0927.log` and `Aloha_2026-0927.access.log`.
