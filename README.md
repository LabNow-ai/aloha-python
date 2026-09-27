# Aloha: Python Utilities and Microservice Boilerplate

[![License](https://img.shields.io/github/license/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/blob/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/LabNow-ai/aloha-python/build.yml?branch=main)](https://github.com/LabNow-ai/aloha-python/actions)
[![PyPI version](https://img.shields.io/pypi/v/aloha)](https://pypi.org/project/aloha/)
[![PyPI downloads](https://img.shields.io/pypi/dm/aloha)](https://pypi.org/project/aloha/)
[![GitHub stars](https://img.shields.io/github/stars/LabNow-ai/aloha-python.svg?label=Stars&style=social)](https://github.com/LabNow-ai/aloha-python/stargazers)

**Aloha is an open-source Python utility library and microservice project template.** It helps Python teams build containerized services with HOCON configuration, structured and multi-process-safe logging, database integrations, encryption utilities, and pytest testing helpers.

Use the installable **`aloha` package** to add common service-building utilities to an existing Python project, or use this repository as a **FastAPI/Uvicorn-oriented microservice boilerplate** with Docker-based development and deployment examples.

- **Documentation:** [English](https://aloha-python.readthedocs.io/en/latest/) · [中文](https://aloha-python.readthedocs.io/zh/latest/)
- **PyPI:** [aloha](https://pypi.org/project/aloha/)
- **Issues and feature requests:** [GitHub Issues](https://github.com/LabNow-ai/aloha-python/issues)

## Why Aloha?

- **One library for common service foundations:** configuration, logging, database access, encryption, HTTP service helpers, and tests live in the `aloha` package.
- **Configuration that fits deployments:** load modular HOCON files and apply environment-specific settings through `PROFILE_ENV`, `FILES_CONFIG`, and environment substitutions.
- **Logs built for services:** write plain or JSON logs to console and daily rotating files, with a multi-process-safe file handler.
- **Database integrations:** use SQLAlchemy-backed operators and helpers for PostgreSQL, MySQL, SQLite, DuckDB, MongoDB, Redis, Elasticsearch, Oracle, and Kafka.
- **A practical microservice starting point:** the repository includes FastAPI/Uvicorn service examples, Dockerfiles, Docker Compose development setup, and pytest examples.
- **Optional binary builds:** compile Python modules to native extensions with the `aloha compile` command and Cython.

## Install

The base package supports Python 3.10 and later:

```bash
python -m pip install aloha
```

Install optional dependency groups for the capabilities you need:

```bash
python -m pip install "aloha[service]"  # FastAPI and Uvicorn helpers
python -m pip install "aloha[db]"       # Database integrations
python -m pip install "aloha[all]"      # All optional integrations and tools
```

## Quick Start

Check the installed library version:

```python
from aloha import __version__

print(__version__)
```

Use the shared application logger after configuring the service's HOCON settings:

```python
from aloha.logger import LOG

LOG.info("Service is ready")
```

The global logger reads `deploy.log_level`, `deploy.log_format_file`, and `deploy.log_format_stream` from the loaded configuration. File logs default to JSON; console logs default to plain text. See the [logging guide](doc/skills/aloha_python/references/logger.md) for formats, fields, timestamps, and configuration details.

## What Is Included?

| Module          | What it helps with                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------------------ |
| `aloha.config`  | Load HOCON settings, profiles, and environment-based configuration.                                    |
| `aloha.logger`  | Configure global and named loggers, JSON/plain output, and daily rotating logs.                        |
| `aloha.db`      | Connect to supported SQL and service databases with reusable operators and password-vault integration. |
| `aloha.encrypt` | Use AES, RSA, JWT, hashing, and password-vault helpers.                                                |
| `aloha.service` | Build FastAPI/Uvicorn services and reusable HTTP API handlers.                                         |
| `aloha.testing` | Test utilities for unit tests and service API tests.                                                   |
| `aloha compile` | Build selected Python modules as native extensions using Cython.                                       |

Explore the [API documentation](https://aloha-python.readthedocs.io/en/main/api/) or the detailed [Aloha Python Skill guide](doc/skills/aloha_python/SKILL.md).

## Use This Repository as a Service Template

The repository includes a runnable application example under `src/`, modular configuration under `src/resource/config/`, and Docker-based development helpers.

Start the development container from the repository root:

```bash
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

Inside the container, run the example service and tests:

```bash
cd /workspace/src
python3 main.py app_common.main
pytest ./
```

To build a production Docker image from the repository root:

```bash
source tool/tool.sh
build_image app_common latest src/app-demo.Dockerfile
```

See the [development and scaffolding guide](doc/skills/aloha_cicd/SKILL.md) for container lifecycle, configuration, ports, and production builds.

## Repository Layout

- `pkg/` — source code and packaging metadata for the installable `aloha` library.
- `src/` — example application, HOCON configuration, and tests.
- `tool/` — Docker, Compose, and development lifecycle scripts.
- `doc/` — user documentation, API references, and contributor skills.
- `notebook/` — notebooks for interactive examples and experiments.

## Contributing

Before changing code, review the repository [contributor guidelines](AGENTS.md) for coding, configuration, logging, and testing standards. See the [Aloha Python Skill](doc/skills/aloha_python/SKILL.md) for package development and the [Aloha CI/CD & Scaffolding Skill](doc/skills/aloha_cicd/SKILL.md) for local development and builds.

Contributions, bug reports, and feature requests are welcome via [GitHub Issues](https://github.com/LabNow-ai/aloha-python/issues).
