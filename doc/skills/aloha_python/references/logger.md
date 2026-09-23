# Logging Module (`aloha.logger`)

The `aloha.logger` subpackage provides a pre-configured, multi-process safe logging framework.

## 1. Global Logger (`LOG`)

The module exports a global pre-configured logger named `LOG`. It reads log levels from settings under `deploy.log_level` (falling back to `logging.DEBUG` if unset) and selects a predefined format from `deploy.log_format` (falling back to `plain`).

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
    log_format = "json"
}
```

Supported values are:

- `plain`: the default format, `LEVEL> timestamp> module:line> message`.
- `json`: one JSON object per line with `timestamp`, `level`, `logger`, `module`, `line`, and `message` fields. Exception and stack information are included when available.

The `formatter_str` argument remains available for loggers that need a custom format. It takes precedence over `log_format`.

- **Safe Concurrent File Writes**: Utilizes `MultiProcessSafeDailyRotatingFileHandler` to avoid lock conflicts or log corruption when multiple parallel processes write logs concurrently.
- **Log Location**: Writes logs to the directory specified by the `DIR_LOG` environment variable (defaults to `logs/`).
- **File Naming Format**: Log file names include:
  - Application module (`APP_MODULE`)
  - Logger name
  - Hostname
  - PID (Process ID)

  Example: `app_module_default_hostname_p12345.log`
