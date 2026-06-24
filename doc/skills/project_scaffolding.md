# Project Scaffolding and Conventions Skill

This skill provides guidelines for understanding and utilizing the `aloha-python` repository as a boilerplate for new Python projects. It outlines the project structure, the purpose of key directories, and how to leverage the `aloha` package within this framework.

## 1. Project Structure Overview

The `aloha-python` repository is organized into several top-level directories, each serving a specific purpose:

- **`doc/`**: This directory contains all project documentation, including guides, API references, and these AI Agent Skills. When creating new documentation, it should be placed here, typically organized by language (e.g., `doc/en`, `doc/zh`).

- **`pkg/`**: This directory stores the source code for the `aloha` Python package that is intended for publication to PyPI. It is the correct place to modify when the task is to work on this library itself. When using this repository as a boilerplate for a new application project, developers or agents should not include this directory unless they explicitly intend to create and publish a new package to PyPI.

- **`src/`**: This directory is designed for application-specific code and tests that consume the `aloha` package. It serves as a boilerplate example (`app_common`) for how to structure a project using `aloha`. New projects based on this boilerplate should place their primary application logic, modules, and tests here.

- **`notebook/`**: This directory is for Jupyter notebooks, which can be used for experimentation, data analysis, or interactive development related to the project.

- **`tool/`**: This directory contains development and CI/CD related scripts and Docker assets. This includes scripts for setting up the development environment, building Docker images, and managing the project lifecycle.

## 2. Using the Repository as a Boilerplate

To initiate a new project using `aloha-python` as a boilerplate, follow these steps:

1.  **Clone the Repository**: Begin by cloning the `aloha-python` repository to your local machine.
2.  **Inspect `src/`**: Review the `src/` directory to understand the example application structure (`app_common`) and how it integrates with the `aloha` package.
3.  **Develop Your Application**: Place your application-specific code within the `src/` directory, following the established patterns for modularity and `aloha` integration.
4.  **Utilize `tool/cicd/`**: Leverage the scripts provided in `tool/cicd/` for managing your development environment, as detailed in the "Development Environment and CI/CD Management Skill".

## 3. Key Conventions for Boilerplate Projects

-   **`src/` for Application Logic**: All primary application code, including API handlers, business logic, and utility modules, should reside within `src/`. The `src/main.py` script acts as a generic entry point for running Python modules within the `src/` directory. Your application's main function should be callable via `python3 src/main.py your_module.main`.
-   **`pkg/` is not part of a new boilerplate app**: If the goal is to build a new application project from this repository, do not carry over `pkg/` unless the user specifically wants to create and publish a separate package. Application code should live in `src/` instead.
-   **`resource/config/` for Configuration**: Application configuration files (e.g., `main.conf`, `deploy-DEV.conf`) should be placed under `src/resource/config/`. The `aloha` package's `aloha.config.paths` module handles the discovery and loading of these configuration files. For detailed information on HOCON configuration, refer to the "Configuration with HOCON" section in the `aloha_package_usage.md` skill.
-   **Tests Placement**: All test-related code (including unit tests, integration tests, and test resources) must be placed inside the `src/` directory, typically organized under a `src/tests/` subdirectory. Test files should follow standard naming conventions such as `test_*.py`.
-   **Executing Tests**: Tests should be run using `pytest` inside the containerized development environment:
    1. Launch and enter the development container:
       ```bash
       ./tool/cicd/run-dev.sh up
       ./tool/cicd/run-dev.sh enter
       ```
    2. Run tests under the `src/` directory:
       ```bash
       pytest src/
       ```
    3. To run tests with code coverage analysis:
       ```bash
       pytest --cov=src src/
       ```

By adhering to these conventions, AI agents can effectively understand, navigate, and contribute to projects built upon the `aloha-python` framework.
