# 12-Factor Implementation Guide for Aloha

This guide uses [The Twelve-Factor App](https://12factor.net/) and its [Simplified Chinese translation](https://12factor.net/zh_cn/) as the reference standard. It explains how to use the `aloha` Python package and this repository’s boilerplate structure to build services that are reproducible, configurable, deployable, and operable. “Satisfy” has two meanings here: **capabilities already provided by Aloha**, and **engineering constraints that every application using Aloha must still implement**. Aloha supplies reusable mechanisms; it does not automatically choose deployment topology, manage secrets, orchestrate processes, or collect logs.

> The central 12-Factor idea is that one codebase can produce many deploys, while explicit dependencies, environment-based configuration, replaceable attached resources, and a simple process model make delivery and operations repeatable.[1] [2]

## 1. Overall assessment

`aloha-python` already provides a strong foundation for 12-Factor applications. The source is managed by Git; `pkg/pyproject.toml` explicitly declares the Python version, core dependencies, and optional dependency groups; `aloha.config` discovers configuration through environment variables and composes HOCON files with `include required(...)`; `src/app-demo.Dockerfile` demonstrates multi-stage builds, dependency installation, health checks, and image-based execution; `aloha.logger` provides a common logging entry point; and the `aloha` CLI provides startup, compilation, and other script capabilities.

However, **12-Factor compliance depends on how an application uses these capabilities**. A production application should treat this repository as a single application codebase and template, keep business code, Docker build definitions, tests, and CI in the same version line, inject deployment-specific values through environment variables or platform Secrets, treat databases and external services as replaceable attached resources, separate build/release/run, and delegate process management, restarts, scaling, log forwarding, and rolling releases to the execution platform.

| Area | Foundation provided by Aloha | Application-level requirement |
| --- | --- | --- |
| Code and dependencies | Git repository, `pyproject.toml`, `aloha[all]` dependency group | One primary codebase per application; pin dependencies and verify them in CI |
| Configuration | `ENV_PROFILE`, `FILES_CONFIG`, `DIR_CONFIG`, and related environment variables; HOCON composition | Keep secrets out of Git; inject deploy-specific values with environment variables or Secrets; use HOCON for non-secret structure and defaults |
| Build and runtime | Multi-stage Dockerfile; `aloha compile` can compile source into extensions | Build immutable images; bind configuration at release time; never modify code or install dependencies at runtime |
| Services and data | `aloha.db` integrations for several databases, caches, and search services | Connect through URLs, credentials, or resource handles; never persist business state in the container filesystem |
| Operations | `aloha.logger`, CLI, and Docker `HEALTHCHECK` example | Emit event streams to standard output; let the platform collect them; implement graceful shutdown, migrations, and one-off admin commands |

## 2. Requirements and Aloha practices by factor

### I. Codebase — one codebase, many deploys

**12-Factor requirement.** An application should correspond to one codebase tracked in version control. Development, test, staging, and production are deploys of that same codebase and may run different commits or release versions. When multiple applications share code, extract that code into a library installed through the dependency manager rather than copying or implicitly sharing source.[1]

**Aloha practice.** Treat `LabNow-ai/aloha-python`, or an application repository created from it, as the single source of truth. Keep application code, `pyproject.toml`, Dockerfiles, configuration templates, tests, and CI definitions in one repository. If multiple applications use Aloha, depend on the `aloha` package through `pip` or a built artifact instead of copying `pkg/aloha` into each application. Identify every deploy by a Git commit and image digest, allowing development, staging, and production to point to different releases of the same codebase.

**Acceptance criteria.** A clean checkout can be built with a deterministic command; the application does not depend on local paths, uncommitted directories, or manually copied libraries; and every deploy is traceable to a Git commit and image digest.

### II. Dependencies — explicitly declare and isolate dependencies

**12-Factor requirement.** An application must not depend on packages or commands that happen to exist on the host. Every library must be declared completely in a dependency manifest and used in an isolated environment in both development and production.[3]

**Aloha practice.** Use `pkg/pyproject.toml` to declare core dependencies and optional groups for `service`, `db`, `stream`, `data`, `report`, `docs`, and `test`. Declare application-specific dependencies in the application’s own `pyproject.toml` and pin or lock versions. CI and Docker builds must consume the same manifest. Install with `pip` or `uv pip install --system -r pyproject.toml` during the build stage; the runtime stage should use only the already-built image.

System tools must also be explicit. A Dockerfile should install and version tools such as `curl`, database clients, or other binaries instead of assuming they exist on the host. `src/app-demo.Dockerfile` shows the pattern for installing Python dependencies inside the image; production projects should additionally pin the base image by tag or digest and run dependency and image vulnerability scans in CI.

### III. Config — store configuration in the environment

**12-Factor requirement.** Configuration includes everything likely to vary between deploys, such as database handles, external-service credentials, and deploy hostnames. It must be strictly separated from code and represented by individually manageable, orthogonal environment variables rather than inseparable environment groups.[4]

**Aloha practice.** `aloha.config.paths` supports configuration discovery through `DIR_RESOURCE`, `DIR_CONFIG`, `ENV_PROFILE`, and `FILES_CONFIG`. `aloha.config.hocon` parses HOCON and combines multiple files through `include required(...)`. Use the pattern **“structure in HOCON, deploy values in environment variables”**:

```text
src/resource/config/
├── main.conf                 # Stable, non-secret structure and safe defaults
├── database.conf             # Database structure; never commit real passwords
├── service.conf              # External-service structure
└── deploy-local.conf         # Local-development example overrides
```

```hocon
# main.conf: safe to keep in version control
include required("database.conf")
include required("service.conf")

app_name = "my-aloha-service"
database.url = ${?DATABASE_URL}
database.password = ${?DATABASE_PASSWORD}
service.api_key = ${?SERVICE_API_KEY}
```

Production should inject `DATABASE_PASSWORD`, `SERVICE_API_KEY`, and similar values through a Secret manager, container platform, or CI/CD Secret. Never place real credentials in HOCON, Dockerfiles, notebooks, logs, or Git history. `ENV_PROFILE` may select an entry file, but it should not become a collection of hard-coded, inseparable deployment environments. When selecting files explicitly, prefer `FILES_CONFIG` and ensure those files contain no secrets.

### IV. Backing services — treat them as attached resources

**12-Factor requirement.** Databases, caches, queues, SMTP, object storage, metrics services, and external APIs are backing services accessed over the network. Code should not distinguish between local and third-party services; it should use URLs, resource handles, and credentials from configuration. Resources must be attachable, detachable, and replaceable without code changes.[5]

**Aloha practice.** `aloha.db` provides modules for PostgreSQL, MySQL, SQLite, MongoDB, Redis, Elasticsearch, DuckDB, Oracle, Kafka, and other resources. `aloha.encrypt.vault` can be used for secure password or key resolution. Define each resource independently, for example `DATABASE_URL`, `REDIS_URL`, and `KAFKA_BOOTSTRAP_SERVERS`, and let connection factories create clients from those handles. Do not hard-code hostnames, ports, or credentials, or introduce a local-only code path. Local, staging, and production should use the same service types and compatible versions whenever possible.

### V. Build, release, run — strictly separate the stages

**12-Factor requirement.** The build stage transforms source and dependencies into an executable bundle; the release stage combines that bundle with the current deploy configuration; and the run stage starts the selected release. Each release needs a unique identifier and must be immutable. Rollback means selecting an older release, not editing the current one.[6]

**Aloha practice.** Use the multi-stage flow in `src/app-demo.Dockerfile` as a reference. The builder stage copies source, installs build dependencies, and can run `aloha compile`; the runtime stage copies build output and installs only runtime dependencies. A CI pipeline should follow this sequence:

```text
Git commit → build/test/scan → push immutable image:<commit-or-version>
          → release: inject environment and Secrets; select image digest
          → run: start the image without editing it
```

Use immutable tags or digests. Do not run `git pull`, `pip install`, source compilation, or release-file rewrites when the container starts. Configuration changes should create a new release record even when the image is unchanged; code changes must create a new image. Docker build arguments may control the build, but must not carry secrets because build history may expose them.

### VI. Processes — run as stateless processes

**12-Factor requirement.** Processes should be stateless and share-nothing. Memory and the local filesystem may be used only as short-lived transaction caches. Persistent data belongs in a database, object store, queue, or other backing service. The application must not rely on sticky sessions or a cache local to one process.[7]

**Aloha practice.** Use `src/main.py` or `aloha start` as an explicit process entry point, and separate HTTP services, workers, and scheduled jobs into independently scalable process types. Store sessions, task state, uploaded files, and business results in Redis, databases, or object storage. The container’s `logs/` directory must not become business storage. Aloha’s database and service modules help keep state external, but the application must still avoid mutable module-global state, cross-request temporary files, and local sessions.

### VII. Port binding — export services through ports

**12-Factor requirement.** The application is a self-contained service that exports HTTP or other protocols by binding to a port. The port should be configurable, and the service must listen on an address reachable from the container or platform.[8]

**Aloha practice.** Read the port from `PORT` or the project’s `PORT_SVC` convention and listen on `0.0.0.0`. Use `EXPOSE` in the Dockerfile to document a default port; let the platform perform the actual mapping. `src/app-demo.Dockerfile` demonstrates `PORT_SVC`, `EXPOSE`, and an HTTP `HEALTHCHECK`. Do not bind production services only to the developer’s `localhost`, and do not require a pre-installed Nginx or Apache merely to start the application; gateways, TLS, and reverse proxies may remain platform concerns.

### VIII. Concurrency — scale out through the process model

**12-Factor requirement.** Processes are first-class resources. Different workloads should be represented by different process types, and capacity should be increased by adding processes. Processes should not daemonize themselves or write PID files; the operating system or execution platform should manage them.[9]

**Aloha practice.** Define separate startup commands for web APIs, asynchronous workers, batch jobs, and admin tasks. Configure replica counts, resource limits, and rolling policies independently in Docker Compose, Kubernetes, or another platform. Threads and async execution inside one process are valid, but vertical scaling must not be the only scaling strategy. A production container should keep its service as the foreground process; it should not use `tail -f` as the service entry point. The `tail -f /dev/null` command in `src/dev-demo.Dockerfile` is only a development-container keepalive pattern.

### IX. Disposability — maximize robustness with fast startup and graceful shutdown

**12-Factor requirement.** Processes should start and stop at short notice, start quickly, and respond to `SIGTERM` by stopping new work, completing current work, and exiting. Workers should safely return unfinished jobs to the queue and tolerate sudden termination.[10]

**Aloha practice.** Load only necessary configuration and establish connection pools during startup; do not hide uncontrolled long-running tasks or migrations in startup hooks. HTTP services should handle `SIGTERM` by closing listeners, pools, and worker threads. Workers should use retryable, idempotent, or transactional processing and allow the queue to redeliver work after disconnection. A Docker `HEALTHCHECK` detects service health but does not replace graceful shutdown. Configure an appropriate termination grace period and test recovery after forced process termination.

### X. Dev/prod parity — keep environments as similar as possible

**12-Factor requirement.** Minimize the time gap between code and production, the personnel gap between authors and deployers, and the tools gap between development and production. Development, staging, and production should use the same runtime and compatible types and versions of databases, queues, and caches.[11]

**Aloha practice.** Use the scripts and Docker Compose resources under `tool/cicd/` for a containerized development environment. Reuse the same Python version, dependency manifest, entry points, and Docker build flow in development, CI, and production. Use HOCON `include` to organize configuration structure and environment variables to inject deploy-specific values. Development may use smaller resource limits, but SQLite, in-memory caches, or mock queues should not be the only test path. Run integration tests in CI against real or compatible PostgreSQL, Redis, Kafka, and other services, and apply the same startup checks to local and production images.

### XI. Logs — treat logs as event streams

**12-Factor requirement.** The application should produce a time-ordered event stream and should not manage log routing, retention, or archival. Processes should write unbuffered logs to `stdout`/`stderr`; the execution environment should collect, aggregate, search, and alert on them.[12]

**Aloha practice.** `aloha.logger` provides a common logger, log-level configuration, and a multi-process-safe file handler. For a 12-Factor production deployment, prefer a console handler and send logs to standard output; let Docker, Kubernetes, Fluent Bit, or a cloud logging service collect them. If a file handler is required for compliance, treat it as a platform or sidecar capability. Business logic must not depend on local log files, and `logs/` must not be shared application state. Include timestamps, levels, service name, release ID, and request or correlation IDs, while never printing passwords, tokens, credentials, or sensitive personal data.

### XII. Admin processes — run management tasks as one-off processes

**12-Factor requirement.** Database migrations, REPL sessions, data repairs, and one-time scripts should run as one-off processes using exactly the same code, dependencies, release, and configuration as long-running processes.[13]

**Aloha practice.** Commit migration, index-rebuild, repair, and diagnostic scripts to the application repository and provide an explicit CLI entry point for each. Run each task inside the production release container using the same image digest, environment variables, and dependency environment. For example, an application may invoke `python -m your_app.admin.migrate` or a project-defined `aloha` subcommand. Tasks should be auditable, idempotent or safely retryable, and should record the release, operator, and scope before and after execution.

## 3. Recommended Aloha layout and release convention

```text
my-aloha-service/
├── src/
│   ├── my_app/                 # Business packages and process-type entries
│   ├── resource/config/
│   │   ├── main.conf           # Non-secret configuration structure
│   │   └── database.conf       # Include-able module configuration
│   ├── pyproject.toml           # Application dependencies, tests, and entries
│   └── Dockerfile               # Build and runtime image definition
├── tests/                      # Unit, integration, and startup checks
├── tool/cicd/                  # Local and CI/CD scripts
├── doc/                        # User, developer, and operations documentation
└── .github/workflows/          # Build, test, scan, and release workflows
```

Release commands should preserve the principles of the same code, explicit dependencies, immutable images, and runtime configuration injection. The following is illustrative; the application’s own `pyproject.toml` and Dockerfile remain authoritative:

```bash
# Local verification
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest

# Build an immutable image
export RELEASE_ID="$(git rev-parse --short=12 HEAD)"
docker build -f src/Dockerfile -t registry.example/my-aloha-service:"$RELEASE_ID" .
docker push registry.example/my-aloha-service:"$RELEASE_ID"

# Inject configuration at runtime; do not edit code or install dependencies
# inside the container
docker run --rm \
  -e ENV_PROFILE=PRD \
  -e FILES_CONFIG=main.conf,database.conf \
  -e DATABASE_URL \
  -e DATABASE_PASSWORD \
  -p 8080:8080 \
  registry.example/my-aloha-service:"$RELEASE_ID"
```

## 4. Pre-release acceptance checklist

| Check | Pass condition |
| --- | --- |
| Codebase | All application source and build definitions come from one Git codebase; deploys are traceable to commits |
| Dependencies | `pyproject.toml` explicitly declares dependencies; build and runtime environments are isolated and reproducible |
| Config | Credentials are absent from the repository, image, and logs; deploy-specific values are injected through environment variables or Secrets |
| Backing services | Databases, caches, queues, and external APIs are connected through resource handles and can be replaced without code changes |
| Build/release/run | The stages are separate; images and releases are immutable; rollback is supported |
| Processes/concurrency | Processes are stateless; web, worker, and admin entries are separate; replicas can scale horizontally |
| Port/health | The service listens on `0.0.0.0`; the port is configurable; health checks do not rely on host-only paths |
| Shutdown/recovery | `SIGTERM` is graceful; jobs are idempotent or retryable; forced termination does not lose persistent state |
| Dev/prod parity | Runtime, dependencies, and major backing-service types are aligned; integration tests cover real connection paths |
| Logs | Production logs go to `stdout`/`stderr`; the platform collects them; sensitive data is excluded |
| Admin processes | Migrations and repairs ship with application code and use the same image, configuration, and dependencies |

## References

[1]: https://12factor.net/codebase "The Twelve-Factor App — Codebase"
[2]: https://12factor.net/zh_cn/codebase "The Twelve-Factor App（简体中文）— 基准代码"
[3]: https://12factor.net/dependencies "The Twelve-Factor App — Dependencies"
[4]: https://12factor.net/config "The Twelve-Factor App — Config"
[5]: https://12factor.net/backing-services "The Twelve-Factor App — Backing services"
[6]: https://12factor.net/build-release-run "The Twelve-Factor App — Build, release, run"
[7]: https://12factor.net/processes "The Twelve-Factor App — Processes"
[8]: https://12factor.net/port-binding "The Twelve-Factor App — Port binding"
[9]: https://12factor.net/concurrency "The Twelve-Factor App — Concurrency"
[10]: https://12factor.net/disposability "The Twelve-Factor App — Disposability"
[11]: https://12factor.net/dev-prod-parity "The Twelve-Factor App — Dev/prod parity"
[12]: https://12factor.net/logs "The Twelve-Factor App — Logs"
[13]: https://12factor.net/admin-processes "The Twelve-Factor App — Admin processes"
