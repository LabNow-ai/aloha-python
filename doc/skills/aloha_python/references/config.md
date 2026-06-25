# Configuration Management Module (`aloha.config`)

The `aloha.config` subpackage provides tools for discovering, loading, and parsing application configurations written in HOCON (Human-Optimized Config Object Notation). The configuration process is highly driven by Operating System Environment Variables.

---

## 1. Operating System Environment Variables

The configuration and startup behavior of an `aloha` application can be customized using the following environment variables:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENV_PROFILE` | `None` (undefined) | Specifies the running profile (e.g., `DEV`, `STG`, `PRD`). Determines the configuration entry file (`main-${ENV_PROFILE}.conf`). |
| `ENTRYPOINT` | `None` (undefined) | Specifies the default Python module entry point when running `aloha start`. The module must contain a `main()` function. |
| `APP_MODULE` | `default` | Identifies the application/module name. Mapped to configuration key `APP_MODULE` and used as a prefix for the log file names. |
| `DIR_LOG` | `logs` | The directory where log files are stored. |
| `DIR_RESOURCE` | `resource` (under CWD) | Root directory containing non-code resources (e.g. assets, static data). |
| `DIR_CONFIG` | `${DIR_RESOURCE}/config` | Directory where configuration files are located. |
| `FILES_CONFIG` | `None` (undefined) | Comma-separated list of configuration filenames to load (e.g., `db.conf,server.conf`). If defined, it overrides `ENV_PROFILE`. |

---

## 2. Path Discovery (`aloha.config.paths`)

This module resolves paths for config directories, resource directories, and active configuration files.

### Key Functions
- `get_resource_dir(*args) -> str`: Resolves the absolute path to the resource directory. Relies on the `DIR_RESOURCE` environment variable.
- `get_config_dir(*args) -> str`: Resolves the absolute path to the configuration directory. Relies on the `DIR_CONFIG` environment variable.
- `get_config_files() -> list`: Determines which HOCON configuration files should be loaded.
  - If `FILES_CONFIG` environment variable is defined, it splits the list by comma and resolves their paths.
  - If `FILES_CONFIG` is not defined but `ENV_PROFILE` is defined, it resolves `main-${ENV_PROFILE}.conf`.
  - Otherwise, it defaults to `main.conf`.
- `get_project_base_dir(file_caller: str) -> str`: Traverses directories upwards from `file_caller` (typically passed as `__file__`) until it finds a directory containing no `__init__.py`, marking the project base root.

---

## 3. HOCON Loading (`aloha.config.hocon`)

This module uses the `pyhocon` library to parse configurations.

### Key Functions
- `load_config_from_hocon(config_file: str) -> dict`: Parses a single HOCON file into a plain ordered dictionary.
- `load_config_from_hocon_files(config_files: list, base_dir: str) -> AttrDict`: Generates a string containing HOCON `include required("<file>")` directives for each configuration file, parses it within the context of `base_dir`, and returns the merged configuration as an `AttrDict` object. This enables attribute-style dot access.

---

## 4. Settings Interface (`aloha.settings`)

The `aloha.settings` module exports a global, pre-instantiated singleton `SETTINGS` of class `Settings`, which manages lazy loading of config files.

### Usage Example
```python
from aloha.settings import SETTINGS

# Access the global configuration (loads configuration lazily on first access)
config = SETTINGS.config

# Dot-style attribute access (since config is an AttrDict)
app_name = config.app_name
db_host = config.database.host

# Or retrieve specific paths as dictionary keys
port = config.get("server.port", 8080)
```
