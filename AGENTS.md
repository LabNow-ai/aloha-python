# Aloha — Contributor Guidelines

Welcome, AI Coding Agents (`agy`, `Claude Code`, `GitHub Copilot`, etc.)! This document serves as your central instruction entry point. Please read this file and the referenced skills before making any modifications to the codebase.

## 1. Project Context

`aloha-python` is a modern project template (boilerplate) and a versatile utility library (`aloha` package) designed to build robust, containerized microservices in Python.

### Repository Structure

- `src/`: Application-specific codebase, configuration resources, and tests.
  - `src/resource/config/`: Configuration files (`main.conf`, settings, profiles).
  - `src/tests/`: Unit and integration tests.
- `pkg/`: Core `aloha` utility library package source code.
- `tool/`: Helper scripts, build files, and Docker/Docker Compose configs for local CI/CD.
- `doc/`: Documentation files and AI Agent Skills.
  - `doc/skill`: The folder to store all project skill files -- all other agent-specific skill folders (e.g.: `.claude/skills`, `.agent/skills`) point to this folder using symlinks.
- `notebook/`: Jupyter notebooks for interactive analysis.
- `.agents/`: Local customization folder for AI agents containing the `skills` symlink setup.

## 2. Working Rules

When writing code or configurations for this project, you **MUST** strictly adhere to the following rules:

### A. Python Coding & Naming Standards

- **Primary Type/First-Class Identity Prefix**: Place the variable's type, role, or primary characteristics first in its name.
  - _Correct_: `name_service`, `port_service`, `svc_ingress`, `cfg_postgres`, `db_mysql`.
  - _Incorrect_: `service_name`, `service_port`, `ingress_service`, `postgres_config`, `mysql_db`.
- **Logger Naming**: Use lowercase with underscores for logger names, e.g., `db_sync`, `api_router`.
- **Import Conventions**: Use relative imports if possible, especially inside a package.

### B. Configuration & Security

- **HOCON Configuration**: Always use HOCON configuration via `aloha.config` (`SETTINGS` object). Maintain configurations in modular files and import them using the HOCON `include` directive in `main.conf`.
- **No Hardcoded Credentials**: Never write plaintext passwords or secrets in configuration files. Configure secrets to resolve dynamically at runtime using the `PasswordVault`.

### C. Logging & Concurrency

- **Safe Multi-Process Logging**: Do not instantiate default Python `FileHandler` inside concurrent or multi-process tasks. Use `aloha.logger.LOG` or named loggers from `get_logger()` to ensure safe concurrent log writing.

### D. Testing Guidelines

- **Framework**: Use `pytest` for all unit and integration testing.
- **Harness**: Subclass `UnitTestCase` or `ServiceTestCase` from `aloha.testing` to leverage pre-configured settings, DB connections, and loggers.

## 3. Skills

We have defined explicit skills to guide specific development tasks. Refer to the corresponding instruction files before editing relevant code:

- **[Aloha Python Skill](doc/skills/aloha_python/SKILL.md)**
  - Covers Python naming standards, sub-modules usage (`aloha.config`, `aloha.logger`, `aloha.encrypt`, `aloha.db`, `aloha.testing`), and the Cython binary compilation process.
- **[Aloha CI/CD & Scaffolding Skill](doc/skills/aloha_cicd/SKILL.md)**
  - Covers project structure layout, local containerized development environments via `./tool/cicd/run-dev.sh`, user-specific port calculations, and production Docker builds.

## 4. Runtime Environment

Note: It is always advised to develop/debug/test code inside a container environment by using the method specified in `Local Container Lifecycle`.

To execute scripts, run tests, or compile code, work within the containerized local development environment:

### A. Local Container Lifecycle

Management is driven by `./tool/cicd/run-dev.sh`:

```bash
# Start the development container in the background
./tool/cicd/run-dev.sh up

# Open an interactive shell inside the container
./tool/cicd/run-dev.sh enter

# Stop the development container
./tool/cicd/run-dev.sh down
```

> [!NOTE]
> The helper script dynamically assigns `PORT_APP` and `PORT_WEB` based on your system `UID` to prevent port collisions on shared servers.

### B. Module Execution

To run application entry points, use the generic module runner:

```bash
cd src

# Execute within the dev container
python3 main.py <module_path>.<function_name>

# Example
python3 main.py app_common.main
```

### C. Running Tests

Run tests from the root directory _inside the container terminal_:

```bash
cd src

# Run pytest on application source code
pytest ./

# Run tests and output test coverage
pytest --cov=./ ./
```

### D. Binary Compilation & Packaging

To compile code using Cython and build production images:

```bash
# Source tool utilities and build the Docker image
source tool/tool.sh
build_image app_common latest src/app-demo.Dockerfile
```

## 5. Extension Metadata

This configuration allows AI coding assistants to load this project's custom definitions automatically.

### Agent Skill Mapping

- **Config file**: `.agents/skills`
- **Path mapping**: Pointing to `../doc/skills`. Enables `codex`, `claude`, `agy`, etc. to resolve all workspace-scoped skills defined under `doc/skills/`.
