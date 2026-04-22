# Introduction

Aloha! Thanks for your interest in this Python package.

[![License](https://img.shields.io/github/license/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LabNow-ai/aloha-python/build.yml?branch=main)](https://github.com/LabNow-ai/aloha-python/actions)
[![Join the Gitter Chat](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/LabNow-ai/)
[![PyPI version](https://img.shields.io/pypi/v/aloha)](https://pypi.python.org/pypi/aloha/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/aloha)](https://pepy.tech/badge/aloha/)
[![Code Activity](https://img.shields.io/github/commit-activity/m/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/pulse)
[![Recent Code Update](https://img.shields.io/github/last-commit/LabNow-ai/aloha-python.svg)](https://github.com/LabNow-ai/aloha-python/stargazers)

Please generously STAR our project or donate to us! [![GitHub Stars](https://img.shields.io/github/stars/LabNow-ai/aloha-python.svg?label=Stars&style=social)](https://github.com/LabNow-ai/aloha-python/stargazers)

The Python package `aloha` is a versatile toolkit for building Python microservices.
It encapsulates commonly used components and features, such as:

- Rapidly creating RESTful APIs and starting services
- Logging utilities
- Managing environments, configuration files, and resource files
- Connecting to popular databases
- Detecting and monitoring runtime environments

## Installation

```title="Install aloha with extra requirements"
pip install aloha[all]
```

Notice that `[all]` after the package name is a set of extra requirements that enable additional features.

These extras include:

- `all`: includes everything listed below
- `service`: packages used to build RESTful APIs (`aloha` uses Tornado for services)
- `build`: compile Python code into binary files, useful for source code protection
- `db`: connect to popular databases, such as MySQL / PostgreSQL / Redis
- `stream`: process stream data using `confluent_kafka`
- `data`: process data or do data science tasks using packages like `pandas`
- `report`: export data and reports to Excel files
- `test`: unit test utilities
- `docs`: documentation build utilities
