---
name: aloha-cicd
description: Guides on project scaffolding, multi-agent setup, local containerized development via run-dev.sh, and building Docker images for production.
---

# Aloha Project Scaffolding and Docker CI/CD Skill

This skill outlines the process for setting up boilerplate codebases, orchestrating containerized local development environments, and building production Docker images.

---

## 1. Project Scaffolding & Multi-Agent setup

To set up your project folders and ensure consistent AI assistant behaviors (across Antigravity, Claude Code, and Copilot), refer to the **[Project Scaffolding & Multi-Agent Setup reference](file:///home/haobibo/dev/dev-labnow/aloha-python/doc/skills/aloha_cicd/references/scaffolding.md)**. This guide covers:
- Core directory layout conventions (`src/`, `doc/`, `notebook/`, `tool/`).
- Handing library isolation (excluding `pkg/` from new app template repositories).
- Centralized rules (`AGENTS.md`) and centralized skills (`doc/skills/`) configuration via symlinks.

---

## 2. Local Development Environment

To start, run, and enter the development container with auto-allocated user ports and volume mappings, refer to the **[Local Development Container & Compose reference](file:///home/haobibo/dev/dev-labnow/aloha-python/doc/skills/aloha_cicd/references/dev_env.md)**. This guide covers:
- Lifecycle management using `./tool/cicd/run-dev.sh` (`up`, `enter`, `logs`, `restart`, `down`).
- User-specific dynamic port calculation (`PORT_APP` and `PORT_WEB`).
- Mounting credentials and setting the `PYTHONPATH`.
- Specs for `dev-demo.Dockerfile` and shared DB compose configurations.

---

## 3. Production Compilation & Packaging

To compile your code into binary extension libraries (`.so` files) and package them into a lightweight container image:

1. **Production Dockerfile ([src/app-demo.Dockerfile](file:///home/haobibo/dev/dev-labnow/aloha-python/src/app-demo.Dockerfile))**:
   - Uses a two-stage build layout.
   - Converts normal Python `.py` files into binary dynamic libraries inside the builder stage (using `aloha compile`) if `ENABLE_CODE_BUILD="true"`.
   - Packs compiled assets into a clean minimal environment, exposing `PORT_SVC` (default 80) and launching via `aloha start`.
2. **Build Trigger Command**:
   ```bash
   source tool/tool.sh
   build_image app_common latest src/app-demo.Dockerfile
   ```

---

## 4. Running Tests & Code Coverage

Tests are executed using `pytest` inside the running dev container:

1. Start and enter the development container:
   ```bash
   ./tool/cicd/run-dev.sh up
   ./tool/cicd/run-dev.sh enter
   ```
2. Run your tests from the root directory:
   ```bash
   # Run all unit and integration tests
   pytest src/

   # Run tests with code coverage report
   pytest --cov=src src/
   ```
