# Aloha Package Usage and API Development Skill

This skill provides guidance on how to effectively use the `aloha` Python package for developing applications within the `aloha-python` boilerplate structure.

## 1. Importing and Using the `aloha` Package

The `aloha` package is designed to be easily integrated into your Python projects. Once installed (e.g., `pip install aloha[all]`), you can import its modules as needed.

### Example: Basic `aloha` Module Usage

To use `aloha` modules, you simply import them and use their functionalities. For example, using `aloha.logger`:

```python
from aloha.logger import LOG

def my_function():
    LOG.info("This is an informational message from aloha logger.")
    return "Function executed successfully"
```

In this example:
- `aloha.logger.LOG` provides a pre-configured logger instance.

## 2. Application Configuration with HOCON

`aloha` applications are configured using HOCON (Human-Optimized Config Object Notation) files, typically located in `src/resource/config/`. The `aloha.config.paths` module helps in discovering these configuration files.

### Configuration File Location and Structure

By default, `aloha` looks for configuration files in the `src/resource/config/` directory. The primary configuration file is `main.conf`.

HOCON allows for hierarchical, modular, and human-readable configurations. You can include other configuration files, which is useful for modularizing your settings (e.g., separating development, staging, and production configurations).

**Example `main.conf`:**

```hocon
include "deploy-DEV.conf"

app_name = "MyAlohaApp"

server {
    host = "0.0.0.0"
    port = 8080
}

database {
    type = "postgresql"
    connection_string = "${?DB_CONNECTION_STRING}" # Environment variable override
}
```

In this example:
- `include "deploy-DEV.conf"` brings in settings from another file, allowing for environment-specific overrides.
- `app_name` and `server` define application-specific settings.
- `database.connection_string = "${?DB_CONNECTION_STRING}"` demonstrates how to use environment variables to override configuration values, making it flexible for different deployment environments.

### Accessing Configuration in Code

You can access configuration values in your Python code via `aloha.settings.SETTINGS.config`:

```python
from aloha.settings import SETTINGS

app_name = SETTINGS.config.get("app_name")
server_port = SETTINGS.config.get("server.port")

print(f"Application Name: {app_name}")
print(f"Server Port: {server_port}")
```

This approach ensures that your application remains configurable and adaptable to various deployment scenarios.

## 3. Running Your `aloha`-based Application

To run your `aloha`-based application, you can use the `src/main.py` script, which acts as a generic module runner:

### Example: Application Entry Point

Your application's main entry point should be a function (e.g., `main()`) within a module in your `src/` directory. For example, in `src/my_app/main.py`:

```python
def main():
    # Your application's startup logic here
    print("My Aloha application is starting...")
    # Integrate with FastAPI or other frameworks here
```

### Running the Application

To execute your application, use the `src/main.py` script:

```bash
python3 src/main.py my_app.main
```

This command tells `src/main.py` to find and execute the `main()` function within your specified module (e.g., `my_app.main`).

## 4. Advanced Usage and Best Practices

-   **Configuration Management**: Leverage `aloha.config.paths` and HOCON files for environment-specific configurations (e.g., `deploy-DEV.conf`). This allows for modular and flexible management of settings across different environments.
-   **HOCON Configuration Details**: For a comprehensive understanding of HOCON configuration, refer to the "Configuration with HOCON" section in the `README-get-start.md` documentation.
-   **Database Integration**: Utilize `aloha.db` modules (e.g., `aloha.db.postgres`) for seamless database interactions, as demonstrated in `src/app_common/api/api_common_query_postgres.py`.
-   **Logging**: Use `aloha.logger.LOG` for consistent and configurable logging across your application.
-   **Testing**: Employ `aloha.testing` utilities for unit and integration tests.
