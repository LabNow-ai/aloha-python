# Aloha Package Usage and API Development Skill

This skill provides guidance on how to effectively use the `aloha` Python package for developing applications, particularly focusing on API creation and service management within the `aloha-python` boilerplate structure.

## 1. Importing and Using the `aloha` Package

The `aloha` package is designed to be easily integrated into your Python projects. Once installed (e.g., `pip install aloha[all]`), you can import its modules as needed.

### Example: Basic API Handler

To create a simple API endpoint, you typically define a handler class that inherits from `aloha.service.api.v0.APIHandler` and expose it via a `default_handlers` list. This is demonstrated in `src/app_common/api/api_multipart.py`:

```python
from aloha.logger import LOG
from aloha.service.api.v0 import APIHandler

class MultipartHandler(APIHandler):
    def response(self):
        LOG.info("Handling multipart request")
        # Your business logic here
        return {"status": "success", "message": "Multipart request processed"}

default_handlers = [
    (r"/api_internal/multipart", MultipartHandler),
]
```

In this example:
- `aloha.logger.LOG` provides a pre-configured logger instance.
- `APIHandler` provides the base functionality for handling API requests.
- The `response` method contains the core logic for your API endpoint.
- `default_handlers` is a list of tuples, where each tuple defines a URL pattern (regex) and its corresponding handler class.

## 2. Application Configuration

`aloha` applications are configured using HOCON files, typically located in `src/resource/config/`. The `aloha.config.paths` module helps in discovering these configuration files.

### Specifying Modules to Load

To integrate your API handlers into the `aloha` application, you need to specify them in your configuration file (e.g., `src/resource/config/main.conf`). The `service.modules` key lists the Python modules containing your `default_handlers`:

```hocon
service {
    # List of Python modules containing default_handlers for the service
    modules = [
        "app_common.api.api_multipart",
        "app_common.api.api_common_sys_info"
    ]
    # Other service configurations like port, number of processes, etc.
    port = 8080
    num_process = 1
}
```

## 3. Starting the `aloha` Application

The `aloha.service.app.Application` class is responsible for bootstrapping and running your `aloha`-based service.

### Example: Application Entry Point

A typical entry point for an `aloha` application, as seen in `src/app_common/main.py`, involves creating an `Application` instance and calling its `start()` method:

```python
def main():
    from aloha.service.app import Application
    # The Application class automatically loads configurations and handlers
    app = Application()
    app.start() # This will start the web server and listen for requests
```

### Running the Application

To run your `aloha` application, you can use the `src/main.py` script, which acts as a generic module runner:

```bash
python3 src/main.py app_common.main
```

This command tells `src/main.py` to find and execute the `main()` function within the `app_common.main` module.

## 4. Advanced Usage and Best Practices

-   **Configuration Management**: Leverage `aloha.config.paths` and HOCON files for environment-specific configurations (e.g., `deploy-DEV.conf`).
-   **Database Integration**: Utilize `aloha.db` modules (e.g., `aloha.db.postgres`) for seamless database interactions, as demonstrated in `src/app_common/api/api_common_query_postgres.py`.
-   **Logging**: Use `aloha.logger.LOG` for consistent and configurable logging across your application.
-   **Testing**: Employ `aloha.testing` utilities for unit and integration tests.
