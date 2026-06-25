# Local Development Container & Docker Compose

This sub-module guides you through setting up and using the containerized local development environment via `docker-compose` and the `run-dev.sh` lifecycle helper.

---

## 1. Local Development Containerization (`run-dev.sh`)

To guarantee environment consistency, local development is fully containerized. The `./tool/cicd/run-dev.sh` script manages this container.

### Commands

| Command | Action |
| :--- | :--- |
| `./tool/cicd/run-dev.sh up` | Checks port availability and starts the development container in detached mode. |
| `./tool/cicd/run-dev.sh enter` | Spawns an interactive bash terminal inside the running container. |
| `./tool/cicd/run-dev.sh logs` | Tails and streams container logs to stdout. |
| `./tool/cicd/run-dev.sh restart` | Restarts the development container. |
| `./tool/cicd/run-dev.sh down` | Stops and removes the development container. |

### Configuration Details

- **User-Specific Port Mapping**: To prevent port clashes on shared, multi-user systems, host ports are computed dynamically using the user's numeric ID (`UID`):
  - **Application Port (`PORT_APP`)**: `30000 + UID` (exposes port 9000).
  - **Web Port (`PORT_WEB`)**: `33000 + UID` (exposes port 3000).
- **Import Environments**: The container mounts the project root to `/root/app:rw` and automatically sets `PYTHONPATH=/root/app/pkg:/root/app/src:/root/app/notebook` for clean imports.
- **Agent Credentials Mounts**: Volume-mounts local config directories (`~/.gemini`, `~/.claude`, `~/.copilot`) to keep credential cache and auth profiles active.

---

## 2. Docker Compose & Dockerfiles Specs

- **Development Dockerfile ([src/dev-demo.Dockerfile](file:///home/haobibo/dev/dev-labnow/aloha-python/src/dev-demo.Dockerfile))**:
  - Defines the base environment for development.
  - Installs Node.js (`pnpm`), Python (`jupyterlab`), package requirements from `src/requirements.txt`, and PostgreSQL client CLI.
- **Development Compose ([tool/cicd/docker-compose.app-demo.DEV.yml](file:///home/haobibo/dev/dev-labnow/aloha-python/tool/cicd/docker-compose.app-demo.DEV.yml))**:
  - Configures the development service container, exposing computed ports, mounting workspace files, and setting environment variables.
- **Common Database Server ([tool/cicd/docker-compose.db.yml](file:///home/haobibo/dev/dev-labnow/aloha-python/tool/cicd/docker-compose.db.yml))**:
  - Launches a shared PostgreSQL 17 database service (`db-postgres-common`) on port 5432.
  - Preloaded with database extensions: `pg_duckdb`, `pg_search`, `pg_cron`.
