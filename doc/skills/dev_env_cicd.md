# Development Environment and CI/CD Management Skill

This skill outlines the conventions and tools used within the `aloha-python` boilerplate for managing the development environment and CI/CD processes. It focuses on leveraging Docker and Docker Compose for a consistent and reproducible development workflow.

## 1. Containerized Development Environment

The `aloha-python` boilerplate provides a fully containerized development environment using Docker and Docker Compose. This ensures that all developers work with the same dependencies and configurations, minimizing "it works on my machine" issues.

### Quick Start with `run-dev.sh`

The primary script for managing the development environment is `./tool/cicd/run-dev.sh`. This script simplifies common Docker operations.

**To launch the development environment:**

```bash
./tool/cicd/run-dev.sh up
```

This command performs the following actions:
-   **Port Availability Check**: Verifies that required ports (dynamically assigned based on user ID to avoid conflicts) are free.
-   **Docker Image Build**: If the image doesn't exist, it builds it using `tool/dev-demo.Dockerfile` and `tool/cicd/docker-compose.app-demo.DEV.yml`. The build process includes installing Node.js (pnpm), Python with JupyterLab, project dependencies, and PostgreSQL client tools.
-   **Container Start**: Starts the Docker container with volume mounts (e.g., `doc/`, `notebook/`, `src/` are mounted to `/root/app/doc`, `/root/app/notebook`, `/root/app/src` respectively) and port forwarding.

**To enter the development container:**

```bash
./tool/cicd/run-dev.sh enter
```

This command provides an interactive bash shell inside the running container, with the working directory set to `/root/app`.

### `run-dev.sh` Commands

The `run-dev.sh` script supports the following commands for environment management:

| Command                          | Description                                 |
| :------------------------------- | :------------------------------------------ |
| `./tool/cicd/run-dev.sh up`      | Starts or creates the development environment. |
| `./tool/cicd/run-dev.sh restart` | Restarts the running container.             |
| `./tool/cicd/run-dev.sh logs`    | Views and follows container logs.           |
| `./tool/cicd/run-dev.sh enter`   | Accesses the container's bash shell.        |
| `./tool/cicd/run-dev.sh down`    | Stops and removes the container.            |

## 2. Dockerfile and Docker Compose Configuration

-   **`tool/dev-demo.Dockerfile`**: This Dockerfile defines the base image for the development container. It includes installations for `pnpm`, `jupyterlab`, Python dependencies, and database clients.
-   **`tool/cicd/docker-compose.app-demo.DEV.yml`**: This Docker Compose file orchestrates the development environment. It specifies how the Docker image is built, environment variables (including `PYTHONPATH` for easy imports from `pkg/` and `src/`), exposed ports, and volume mounts to enable live code changes.

## 3. Building Docker Images for Deployment

The `tool/tool.sh` script provides utilities for building and managing Docker images for deployment.

**To build a Docker image for your application:**

```bash
source tool/tool.sh
build_image app_common latest tool/app-demo.Dockerfile
```

This command uses `tool/app-demo.Dockerfile` to build a production-ready Docker image for your application.

## 4. Developing Documentation Locally

To develop and preview documentation locally, the project uses MkDocs.

**To serve the documentation locally:**

```bash
mkdocs serve -f mkdocs.yml -a 0.0.0.0:3000
```

This command starts a local web server, allowing you to view changes to your Markdown documentation in real-time. The main configuration files are `doc/mkdocs.yml` (for English) and `doc/mkdocs.zh.yml` (for Chinese).
