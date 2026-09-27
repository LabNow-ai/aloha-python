# Getting Started with Aloha

This guide covers two ways to use Aloha:

1. Install the `aloha` Python library in an existing application.
2. Use the `aloha-python` repository as a Docker-based microservice template.

## 1. Install the Python Library

Aloha supports Python 3.10 and later. Install the base package:

```bash
python -m pip install aloha
```

Install extras for optional capabilities:

```bash
python -m pip install "aloha[service]"  # FastAPI and Uvicorn support
python -m pip install "aloha[db]"       # Database integrations
python -m pip install "aloha[all]"      # All optional dependencies
```

Other extras include `aio` for asynchronous database drivers, `build` for Cython compilation, `stream` for Kafka clients, `data` and `report` for data/reporting tools, and `test` and `docs` for development.

Verify the installation:

```bash
aloha info
```

## 2. Use Aloha in an Application

Import only the modules your application needs. For example, the shared logger is available from `aloha.logger`:

```python
from aloha.logger import LOG

LOG.info("Application started")
```

To use HOCON settings, provide a resource configuration directory and load values from `SETTINGS`:

```python
from aloha.settings import SETTINGS

config_settings = SETTINGS.config
```

By default, Aloha looks for configuration under `resource/config/` relative to the current working directory. `PROFILE_ENV`, `FILES_CONFIG`, `DIR_RESOURCE`, and `DIR_CONFIG` can be used to select profiles and locations. See the [configuration guide](README-config.md) for details.

The `aloha start` command can run a module whose `main()` function starts your application:

```bash
aloha start your_package.main
```

## 3. Start from the Microservice Template

Clone the repository and enter the project:

```bash
git clone https://github.com/LabNow-ai/aloha-python.git
cd aloha-python
```

Start and enter the containerized development environment:

```bash
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

From the container shell, run the sample FastAPI/Uvicorn service and tests:

```bash
cd /workspace/src
python3 main.py app_common.main
pytest ./
```

The sample application lives in `src/app_common/`; service configuration and profiles live in `src/resource/config/`. Adapt these to your application. See the [development guide](README-develop.md) for container commands and [configuration guide](README-config.md) for HOCON setup.

## 4. Build a Production Image

From the repository root, build the example Docker image:

```bash
source tool/tool.sh
build_image app_common latest src/app-demo.Dockerfile
```

The Docker build can compile selected application modules with Cython. See the [CLI guide](README-cli.md) and [compilation reference](../skills/aloha_python/references/compile.md).

## Next Steps

- Browse the [API reference](api/index.md).
- Learn about [structured logging](api/logging.md), [database integrations](api/db.md), and [HOCON configuration](README-config.md).
- Review the [12-Factor application guide](README-12factor.md) for deployment practices.
