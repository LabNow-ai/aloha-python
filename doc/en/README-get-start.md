# Getting Started

## Step 1. Install the Python package

```title="Install aloha with all extra requirements"
pip install aloha[all]
```

## Step 2. Use this repository as a boilerplate

This repository serves as a boilerplate/template project built on top of `aloha`.
It gives you a ready-to-use application layout, development scripts, and containerized tooling so you can start building instead of assembling the project skeleton yourself.

### What this template gives you

- A containerized development environment based on Docker and Docker Compose
- Pre-installed Python and project dependencies
- An application entry point you can extend directly
- A conventional layout for source code, documentation, notebooks, and tooling

### Recommended workflow

1. Clone this repository.
2. Inspect the starter application structure.
3. Use the scripts under `tool/cicd/` to start the development container when you want a reproducible environment.
4. Put your own application code in the template structure and grow from there.

### Launch the development environment

If you want the full boilerplate experience, start the containerized DEV environment:

```bash
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

The `up` command creates or starts the development container. The `enter` command opens an interactive shell inside that container.

### Project structure

The template is organized around a few common folders:

- `doc/`: Documentation source files. You can place your project's documentation here.
- `src/`: Application code and entry points. This is where your business logic goes. It contains a demo application (`app_common`) showing how to use `aloha`.
- `tool/`: Scripts and Docker assets for development and CI/CD.

### How to use `aloha` in your project

The `src/` directory contains a demo application that demonstrates how to use the `aloha` package. Here is a brief overview of how to import and use `aloha` for regular Python project development:

1. **Import `aloha` modules**: Import the necessary `aloha` modules for your application logic. For example, `aloha.logger` for logging, `aloha.config` for configuration, or `aloha.db` for database interactions.

2. **Configure your application**: Define your application configuration in `src/resource/config/main.conf`.

3. **Implement your application logic**: Write your Python code using the imported `aloha` modules.

4. **Run your application**: You can run your application using the provided `main.py` script:

```bash
python3 src/main.py your_module.main
```

This command tells `src/main.py` to find and execute the `main()` function within your specified module (e.g., `your_module.main`).

## Configuration with HOCON

`aloha` uses the HOCON (Human-Optimized Config Object Notation) format for its configuration files. This allows for hierarchical, modular, and human-readable configurations.

### Configuration File Location

By default, `aloha` looks for configuration files in the `src/resource/config/` directory. The primary configuration file is `main.conf`.

### Modular Configuration

HOCON supports including other configuration files, which is useful for modularizing your settings (e.g., separating development, staging, and production configurations).

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

[:octicons-mark-github-16: Go to Template Project](https://github.com/LabNow-ai/aloha-python/tree/main/src){ .md-button }
