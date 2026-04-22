# Getting Started

## Step 1. Install the Python package

```title="Install aloha with all extra requirements"
pip install aloha[all]
```

## Step 2. Use this repository as a boilerplate

The `app/` folder in this repository is a boilerplate/template project built on top of `aloha`.
It gives you a ready-to-use application layout, development scripts, and containerized tooling so you can start building instead of assembling the project skeleton yourself.

### What this template gives you

- A containerized development environment based on Docker and Docker Compose
- Pre-installed Python and project dependencies
- An application entry point you can extend directly
- A conventional layout for source code, documentation, notebooks, and tooling

### Recommended workflow

1. Clone this repository.
2. Open the `app/` directory to inspect the starter application structure.
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

- `app/`: application code and entry points
- `src/`: the `aloha` library source code
- `doc/`: documentation source files
- `notebook/`: Jupyter notebooks for experimentation
- `tool/`: scripts and Docker assets for development and CI/CD

[:octicons-mark-github-16: Go to Template Project](https://github.com/LabNow-ai/aloha-python/tree/main/app){ .md-button }
