# App Demo

Using `aloha` to develop your project - a boilerplate/template project.

## Overview

This project provides a containerized development environment using Docker and Docker Compose. It sets up a complete development workspace with all necessary dependencies pre-installed, allowing you to focus on writing code rather than configuring your environment.

### Key Components

- **Docker**: Containerization platform that packages applications with all their dependencies
- **Docker Compose**: Tool for defining and running multi-container Docker applications
- **Development Container**: A pre-configured environment with Python, Node.js, and database clients

## How to quickly setup and start DEV environment

### Prerequisites

Before getting started, ensure you have the following installed:

- Docker Engine
- Docker Compose
- Git (for cloning the repository)

You can verify Docker installation by running:

```bash
docker --version
docker-compose --version
```

### Step 1: Launch the Development Environment

Run this command in your terminal:

```bash
./tool/cicd/run-dev.sh up
```

**What happens when you run this command:**

1. **Port Availability Check**: The script first verifies that the required ports are not already in use on your system. The ports are dynamically assigned based on your user ID (UID) to avoid conflicts with other developers.

2. **Docker Image Build**: If the Docker image doesn't exist yet, Docker Compose will build it using:
   - `tool/cicd/docker-compose.app-demo.DEV.yml`: Defines the container configuration
   - `tool/dev-demo.Dockerfile`: Specifies how to build the Docker image

   The build process includes:
   - Installing Node.js package manager (pnpm)
   - Setting up Python with JupyterLab
   - Installing project dependencies from `app/requirements.txt`
   - Adding PostgreSQL database client tools

3. **Container Start**: Docker Compose starts the container with the following features:
   - **Volume Mounts**: Your local code directories are mounted into the container, enabling live development (changes on your host are immediately visible in the container):
     - `doc/` → `/root/doc`
     - `notebook/` → `/root/notebook`
     - `src/` → `/root/src`
     - `app/` → `/root/app`
   - **Port Forwarding**: Exposes ports for your application and web interface
   - **Persistent Process**: The container runs `tail -f /dev/null` to stay active

### Step 2: Enter the Development Container

Once the environment is running, execute:

```bash
./tool/cicd/run-dev.sh enter
```

**What this command does:**

- Uses `docker exec -it` to create an interactive terminal session
- Attaches you to the running container with a bash shell
- You'll be logged in as the root user inside the container
- Your working directory will be `/root`

**What you can do inside the container:**

- Run Python scripts and applications
- Use JupyterLab for interactive development
- Install additional packages with pip or npm
- Access the PostgreSQL database using the client tools
- Edit files (changes will be reflected on your host machine)

### Step 3: Manage the Environment

The `run-dev.sh` script provides several commands to manage your development environment:

| Command                          | Description                                 |
| -------------------------------- | ------------------------------------------- |
| `./tool/cicd/run-dev.sh up`      | Start or create the development environment |
| `./tool/cicd/run-dev.sh restart` | Restart the running container               |
| `./tool/cicd/run-dev.sh logs`    | View and follow container logs              |
| `./tool/cicd/run-dev.sh enter`   | Access the container's bash shell           |
| `./tool/cicd/run-dev.sh down`    | Stop and remove the container               |

### Understanding the Port Assignment

The script dynamically assigns ports to avoid conflicts:

- **Base App Port**: 30000 (as specified in the `run-dev.sh`)+ your UID
- **Base Web Port**: 33000 (as specified in the `run-dev.sh`)+ your UID

Your specific ports will be displayed when you run any `run-dev.sh` command:

```
----------------------------------------
User:            yourusername (UID: 1000)
Project Name:    dev-app-demo-yourusername
Container:       dev-app-demo-yourusername
App Port Expose: 31000
Web Port Expose: 34000
Action:          up
Compose:         /path/to/docker-compose.app-demo.DEV.yml
----------------------------------------
```

### Tearing Down the Environment

When you're done working, you can stop and remove the container:

```bash
./tool/cicd/run-dev.sh down
```

**Note:** This command only removes the container, not the Docker image. If you want to reclaim disk space by removing the image as well, run:

```bash
docker rmi $(docker images | grep dev-app-demo | awk '{print $3}')
```

## Project Structure

```
aloha-python/
├── app/                    # Application code
│   ├── main.py            # Main application entry point
│   ├── requirements.txt   # Python dependencies
│   └── app_common/        # Common application utilities
├── src/                    # Source code for the aloha library
├── doc/                    # Documentation files
├── notebook/               # Jupyter notebooks
└── tool/                   # Development tools
    ├── cicd/              # CI/CD scripts and configs
    │   ├── run-dev.sh     # Main development environment script
    │   └── docker-compose.app-demo.DEV.yml
    ├── dev-demo.Dockerfile
    └── app-demo.Dockerfile
```

## Troubleshooting

### "Port is already in use" error

If you see this error, another process is using the assigned ports. You can:

1. Identify and stop the conflicting process
2. Work with a system administrator to free up the ports

### Container won't start

- Check Docker logs: `./tool/cicd/run-dev.sh logs`
- Ensure Docker service is running: `systemctl status docker` (Linux) or check Docker Desktop (Windows/macOS)

### Changes not reflecting

- Verify your files are in the mounted directories
- Check that you're editing files on your host machine (not just inside the container)
- Restart any running services inside the container if needed

## Next Steps

Once inside the container, you can:

1. Explore the `app/` directory to understand the application structure
2. Check out the Jupyter notebooks in the `notebook/` directory
3. Review the documentation in the `doc/` directory
4. Start developing your application!
