# Development Docs

## Quick Start Development Environment

The project provides a containerized development environment using Docker and Docker Compose. It sets up a complete development workspace with all necessary dependencies pre-installed.

### Launch the Development Environment

Run this command in your terminal:

```bash
./tool/cicd/run-dev.sh up
```

This will build the Docker image and start the container. Your local code directories are mounted into the container, enabling live development.

### Enter the Development Container

Once the environment is running, execute:

```bash
./tool/cicd/run-dev.sh enter
```

You will be attached to the running container with a bash shell.

### Manage the Environment

The `run-dev.sh` script provides several commands to manage your development environment:

| Command                          | Description                                 |
| -------------------------------- | ------------------------------------------- |
| `./tool/cicd/run-dev.sh up`      | Start or create the development environment |
| `./tool/cicd/run-dev.sh restart` | Restart the running container               |
| `./tool/cicd/run-dev.sh logs`    | View and follow container logs              |
| `./tool/cicd/run-dev.sh enter`   | Access the container's bash shell           |
| `./tool/cicd/run-dev.sh down`    | Stop and remove the container               |

## Live debug source code with Docker

If you prefer to run a single container for debugging:

```bash
# First, cd to project root, then run:
docker run -it \
  -v $(pwd):/root/app/ \
  -w /root/app/src \
  --name="app-$(whoami)" \
  -p 8080:80 \
  quay.io/labnow/base:latest bash

python3 main.py app_common.debug
```

## Build Docker image

```bash
source tool/tool.sh
build_image app_common latest tool/app-demo.Dockerfile
```

## Develop docs

```bash
mkdocs serve -f mkdocs.yml -a 0.0.0.0:3000
```
