# Aloha: Python Microservice Library and Project Template

**Aloha is an open-source Python utility library and microservice boilerplate for building containerized services.** The `aloha` package brings together HOCON configuration, structured logging, database operators, encryption utilities, FastAPI/Uvicorn service helpers, and testing support.

Use Aloha as a dependency in an existing Python application, or use the `aloha-python` repository as a Docker-ready starting point for a new microservice.

[![PyPI version](https://img.shields.io/pypi/v/aloha)](https://pypi.org/project/aloha/)
[![Build](https://img.shields.io/github/actions/workflow/status/LabNow-ai/aloha-python/build.yml?branch=main)](https://github.com/LabNow-ai/aloha-python/actions)
[![License](https://img.shields.io/github/license/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/blob/main/LICENSE)

## What Aloha Provides

- **HOCON configuration** — Load modular configuration files and select profiles with environment variables.
- **Service-ready logging** — Emit plain or JSON logs to the console and daily rotating files, including process and host metadata.
- **Database connectivity** — Reusable operators and helpers for PostgreSQL, MySQL, SQLite, DuckDB, MongoDB, Redis, Elasticsearch, Oracle, and Kafka.
- **Security utilities** — AES and RSA operations, JWT helpers, hashing, and password-vault integrations.
- **Python web services** — FastAPI/Uvicorn application helpers and reusable HTTP service components.
- **Testing and packaging tools** — Test helpers and an optional Cython-based command for building selected modules as native extensions.
- **Containerized template** — A sample application, Dockerfiles, Docker Compose development environment, and CI/CD scripts.

## Install the Python Package

Aloha requires Python 3.10 or later. Install the base package with pip:

```bash
python -m pip install aloha
```

Optional integrations are grouped as extras. Install only what your application needs:

```bash
python -m pip install "aloha[service]"  # FastAPI and Uvicorn
python -m pip install "aloha[db]"       # Database integrations
python -m pip install "aloha[all]"      # All optional integrations and tools
```

See [Installation and first steps](README-get-start.md) for more extras and a minimal usage example.

## Choose Your Path

### Add Aloha to an Existing Python Project

Install the package, configure settings with HOCON, and import the modules you need:

```python
from aloha.logger import LOG

LOG.info("Service is ready")
```

The global logger reads its level and file/console formats from the `deploy` HOCON settings. See the [configuration guide](README-config.md) and [logging reference](api/logging.md).

### Start from the Microservice Template

Clone the repository and start its development container:

```bash
git clone https://github.com/LabNow-ai/aloha-python.git
cd aloha-python
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

Inside the container:

```bash
cd /workspace/src
python3 main.py app_common.main
pytest ./
```

The `src/app_common/` application is an example to adapt for your service. Follow the [Getting Started guide](README-get-start.md) for setup and project structure.

## Documentation

- [Getting Started](README-get-start.md)
- [Configuration and HOCON profiles](README-config.md)
- [CLI commands](README-cli.md)
- [12-Factor application guide](README-12factor.md)
- [Development and Docker guide](README-develop.md)
- [API reference](api/index.md)

## Project and Community

- [Source code on GitHub](https://github.com/LabNow-ai/aloha-python)
- [PyPI package](https://pypi.org/project/aloha/)
- [Report a bug or request a feature](https://github.com/LabNow-ai/aloha-python/issues)
