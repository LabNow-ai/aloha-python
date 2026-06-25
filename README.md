# Aloha

[![License](https://img.shields.io/github/license/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LabNow-ai/aloha-python/build.yml?branch=main)](https://github.com/LabNow-ai/aloha-python/actions)
[![PyPI version](https://img.shields.io/pypi/v/aloha)](https://pypi.python.org/pypi/aloha/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/aloha)](https://pepy.tech/badge/aloha/)
[![Code Activity](https://img.shields.io/github/commit-activity/m/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/pulse)
[![Recent Code Update](https://img.shields.io/github/last-commit/LabNow-ai/aloha-python.svg)](https://github.com/LabNow-ai/aloha-python/stargazers)

`aloha-python` is a modern project template (boilerplate) and a versatile utility library (`aloha` package) designed to build robust, containerized microservices in Python.

---

Please generously STAR★ our project or donate to us!
[![GitHub Starts](https://img.shields.io/github/stars/LabNow-ai/aloha-python.svg?label=Stars&style=social)](https://github.com/LabNow-ai/aloha-python/stargazers)

- To understand the package, read the [📚docs](https://aloha-python.readthedocs.io/) or [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/LabNow-ai/lab-foundation)

- To contribute or talk to a human: [![Open an Issue on GitHub](https://img.shields.io/github/issues/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/issues) [![Join the Discord Chat](https://img.shields.io/badge/Discuss_on-Discord-green)](https://discord.gg/kHUzgQxgbJ) [![Join the Gitter Chat](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/LabNow-ai/)

---

## 🚀 Key Features

- **Configuration Management (`aloha.config`)**: Lazy-loaded settings (`SETTINGS`) using HOCON (Human-Optimized Config Object Notation), supporting environment profile overrides (`ENV_PROFILE` / `FILES_CONFIG`) and environment variable injection.
- **Concurrent-Safe Logging (`aloha.logger`)**: Multi-process safe daily rotating log file handler, console output, and automatic log paths configuration.
- **Database Operators (`aloha.db`)**: Pre-built SQLAlchemy-backed connections for PostgreSQL, MySQL, SQLite, DuckDB, MongoDB, Redis, Elasticsearch, and Kafka, with password resolution via a secure `PasswordVault` wrapper.
- **Encryption & Utilities (`aloha.encrypt`)**: Fast helpers for AES (ECB/CBC) encryption, RSA asymmetric key-pair generation/signatures, JWT encoding/decoding, and Base62 hashing.
- **Testing Harness (`aloha.testing`)**: Extended `UnitTestCase` and integration `ServiceTestCase` structures for testing HTTP endpoints.
- **Binary Code Protection (`aloha compile`)**: Utility compiler using Cython to package python source files (`.py`) into platform-native compiled dynamic libraries (`.so`/`.pyd`), protecting intellectual property.

---

## 📁 Repository Layout

- **[`src/`](src)**: Application-specific codebase, configuration files (`src/resource/config/`), and unit/integration tests (`src/tests/`).
- **[`pkg/`](pkg)**: The core `aloha` utility library source code.
- **[`tool/`](tool)**: Local CI/CD files and setup helpers (e.g. docker-compose configurations, lifecycle scripts).
- **[`doc/`](doc)**: Documentation files and AI Agent Skills.
- **[`notebook/`](notebook)**: Jupyter notebooks for interactive analysis.

---

## 🛠️ Local Development Quick Start

Local development is fully containerized using Docker & Docker Compose to maintain environment consistency.

### 1. Launch Dev Container

Run the lifecycle helper script:

```bash
# Check port availability and spin up the development container
./tool/cicd/run-dev.sh up

# Open an interactive terminal inside the container
./tool/cicd/run-dev.sh enter
```

_Note: Development ports (`PORT_APP` and `PORT_WEB`) are dynamically computed based on your User ID (`UID`) to avoid conflicts on shared servers._

### 2. Run Tests

Inside the running container terminal:

```bash
# Execute pytest suite
pytest src/

# Run tests with code coverage report
pytest --cov=src src/
```

### 3. Production Packaging

To build a production-ready Docker image with optional binary compilation enabled:

```bash
source tool/tool.sh
build_image app_common latest src/app-demo.Dockerfile
```

---

## ✍️ Coding Guidelines

When developing in this project, variables should place their **type or primary characteristics/role prefix first**:

- _Correct_: `name_service`, `port_service`, `svc_ingress`, `cfg_postgres`.
- _Incorrect_: `service_name`, `service_port`, `ingress_service`, `postgres_config`.

For details on local setups, CI/CD specifications, and sub-module APIs, inspect our agent instruction files:

- **[Aloha Python Skills Guide](doc/skills/aloha_python/SKILL.md)**
- **[Aloha CI/CD & Scaffolding Guide](doc/skills/aloha_cicd/SKILL.md)**
