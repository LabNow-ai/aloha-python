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

1. **Define API Handlers**: Create your API handlers by extending `APIHandler` from `aloha.service.api.v0`. For example, in `src/app_common/api/api_multipart.py`:

```python
from aloha.logger import LOG
from aloha.service.api.v0 import APIHandler

class MultipartHandler(APIHandler):
    def response(self):
        LOG.info("Handling multipart request")
        return {"status": "success"}

default_handlers = [
    (r"/api_internal/multipart", MultipartHandler),
]
```

2. **Configure the Application**: Define your application configuration in `src/resource/config/main.conf`. Specify the modules to load:

```hocon
service {
    modules = [
        "app_common.api.api_multipart"
    ]
}
```

3. **Start the Application**: Use the `Application` class from `aloha.service.app` to start your service. For example, in `src/app_common/main.py`:

```python
def main():
    from aloha.service.app import Application
    app = Application()
    app.start()
```

You can run the application using the provided `main.py` script:

```bash
python3 src/main.py app_common.main
```

[:octicons-mark-github-16: Go to Template Project](https://github.com/LabNow-ai/aloha-python/tree/main/src){ .md-button }
