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

- `plain`: the default format, with an aligned level prefix, UTC ISO 8601 timestamp with millisecond precision (the same representation as the JSON `timestamp` field), `filename:lineno` source location, and message. The console handler colors the level prefix by severity when its stream is a terminal; log files remain uncolored.
- `json`: one JSON object per line with `timestamp`, `level`, `logger`, `source` (`filename:lineno`), and `message` fields. Exception information is included when available. WARNING and higher records also include a captured calling stack in `stack_info`.

The file format defaults to `json`; the console format defaults to `plain`. The console formatter adds colors when its output stream is a terminal. The deprecated `log_format` argument to `setup_logger` and `get_logger` remains available as an explicit override for both handlers. `formatter_str`, when provided, takes precedence over the selected formats for both handlers.

- Aloha and FastAPI/Uvicorn ordinary logs share the root logger's stderr handler and one ordinary log file. Ordinary Uvicorn loggers propagate to the root instead of creating duplicate files.
- Uvicorn access logs write to stdout and a separate `access_<APP_MODULE>_...log` file. Their file/console formats use the same independent settings; in plain mode they use Uvicorn's access format without a source location, and in JSON mode the `source` field is omitted.

- **Safe Concurrent File Writes**: Utilizes `MultiProcessSafeDailyRotatingFileHandler` to avoid lock conflicts or log corruption when multiple parallel processes write logs concurrently.
- **Log Location**: Writes logs to the directory specified by the `DIR_LOG` environment variable (defaults to `logs/`).
- **File Naming Format**: Log file names include:
  - Application module (`APP_MODULE`)
  - Logger name
  - Hostname
  - PID (Process ID)

  Example: `app_module_default_hostname_p12345.log`
