# Aloha 项目的 12-Factor 落地指南

本文以 [The Twelve-Factor App](https://12factor.net/) 的英文原文及其[简体中文译本](https://12factor.net/zh_cn/)为依据，说明如何使用 `aloha` Python 包及本仓库的 boilerplate 结构构建可重复、可配置、可发布和可运维的服务。本文中的“满足”分为两类：**Aloha 已提供的能力**，以及**使用 Aloha 的应用仍必须完成的工程约束**。Aloha 提供通用机制，但不会自动替应用决定部署拓扑、密钥管理、进程编排或日志采集策略。

> 12-Factor 的核心是让同一份代码库能够形成多个部署，并通过显式依赖、环境配置、可替换的外部服务和简单的进程模型，实现可重复交付与可运维运行。[1] [2]

## 一、总体落地结论

`aloha-python` 已经具备较好的 12-Factor 基础：源码由 Git 管理；`pkg/pyproject.toml` 显式声明 Python 版本、核心依赖和可选依赖组；`aloha.config` 支持通过环境变量发现配置，并使用 HOCON 的 `include required(...)` 组合配置；`src/app-demo.Dockerfile` 展示了多阶段构建、依赖安装、健康检查和镜像化运行；`aloha.logger` 提供统一日志入口；`aloha` CLI 提供启动、编译和其他脚本能力。

但是，**是否真正符合 12-Factor 取决于应用项目的使用方式**。生产应用应将本仓库作为单一应用代码库和模板，将业务代码、Docker 构建定义、测试和文档放在同一版本线；将每个部署会变化的值放到环境变量或部署平台的 Secret 中；把数据库、缓存、消息队列和外部 API 当作可替换的附加资源；把构建、发布和运行拆开；并由容器编排平台管理进程、重启、扩缩容、日志转发及滚动发布。

| 维度 | Aloha 当前提供的基础 | 应用项目的落地要求 |
| --- | --- | --- |
| 代码与依赖 | Git 仓库、`pyproject.toml`、`aloha[all]` 依赖组 | 一个应用使用一个主代码库；锁定依赖版本并在 CI 中验证 |
| 配置 | `ENV_PROFILE`、`FILES_CONFIG`、`DIR_CONFIG` 等环境变量；HOCON 合并加载 | 秘密不入库；部署差异使用环境变量或 Secret 注入；HOCON 仅承载非秘密结构和默认值 |
| 构建与运行 | 多阶段 Dockerfile；`aloha compile` 可将源码编译为扩展 | 构建不可变镜像；发布时绑定配置；运行时不修改代码或安装依赖 |
| 服务与数据 | `aloha.db` 支持多种数据库/缓存/搜索客户端；服务层支持 API | 通过 URL、凭据或资源句柄连接外部服务；持久状态不得写入容器本地磁盘 |
| 运维 | `aloha.logger`、CLI、Docker `HEALTHCHECK` 示例 | 输出标准输出事件流；平台负责采集；实现优雅停止、迁移和一次性管理命令 |

## 二、逐项要求与 Aloha 实践

### I. 基准代码（Codebase）——一份代码库，多份部署

**12-Factor 要求。** 一个应用应对应一个由版本控制系统跟踪的基准代码。开发、测试、预发布和生产是同一代码库的不同部署，可以运行不同的提交或发布版本；多个应用共享代码时，应把共享部分拆成可由依赖管理器安装的库，而不是复制或隐式共享代码。[1]

**Aloha 的落地方式。** 将 `LabNow-ai/aloha-python` 或基于它创建的应用仓库作为唯一源代码来源。应用代码、`pyproject.toml`、Dockerfile、配置模板、测试和 CI 定义应在同一仓库中维护。若多个应用都使用 `aloha`，应通过 `pip`/构建产物依赖 `aloha`，而不是复制 `pkg/aloha` 到各应用中。每一次部署使用 Git commit 或镜像 digest 标识，并允许开发、staging、production 分别指向同一代码库的不同 release。

**验收标准。** 能从任意干净 checkout 通过固定命令构建；应用代码未通过本地路径、未提交目录或人工拷贝依赖运行；每个部署均能追溯到 Git commit 和镜像 digest。

### II. 依赖（Dependencies）——显式声明并隔离依赖

**12-Factor 要求。** 不得依赖系统中“碰巧存在”的包或命令。所有库必须在依赖清单中完整声明，并在开发和生产中使用隔离环境。[3]

**Aloha 的落地方式。** 使用 `pkg/pyproject.toml` 的 `[project].dependencies` 声明核心依赖，按 `service`、`db`、`stream`、`data`、`report`、`docs` 和 `test` 划分可选依赖组。应用自己的依赖应在应用 `pyproject.toml` 中继续声明并锁定版本；CI 和 Docker 构建应使用同一份清单。推荐在构建阶段执行 `pip install` 或 `uv pip install --system -r pyproject.toml`，在运行阶段只使用已经构建好的镜像。

对于系统工具，Dockerfile 应明确安装并固定版本，不能假设运行环境已有 `curl`、数据库客户端或其他二进制。`src/app-demo.Dockerfile` 已展示在镜像内安装 Python 依赖的模式；应用应进一步固定基础镜像 tag 或 digest，并在 CI 中执行安装、测试和漏洞扫描。

### III. 配置（Config）——在环境中存储配置

**12-Factor 要求。** 配置是所有可能随部署变化的值，包括数据库句柄、外部服务凭据和部署域名；它必须与代码严格分离，且应使用彼此正交、可单独管理的环境变量，而不是把 `development`、`staging`、`production` 固化成一组不可拆分的环境名称。[4]

**Aloha 的落地方式。** `aloha.config.paths` 支持通过 `DIR_RESOURCE`、`DIR_CONFIG`、`ENV_PROFILE` 和 `FILES_CONFIG` 发现配置；`aloha.config.hocon` 使用 HOCON 解析配置，并通过 `include required(...)` 将多个文件合并为一个配置对象。推荐采用“**结构在 HOCON，部署值在环境变量**”的分层方式：

```text
src/resource/config/
├── main.conf                 # 非秘密的稳定结构和安全默认值
├── database.conf             # 数据库配置结构，禁止提交真实密码
├── service.conf              # 外部服务结构
└── deploy-local.conf         # 仅用于本地开发的示例覆盖
```

```hocon
# main.conf：可以进入版本库的结构
include required("database.conf")
include required("service.conf")

app_name = "my-aloha-service"
database.url = ${?DATABASE_URL}
database.password = ${?DATABASE_PASSWORD}
service.api_key = ${?SERVICE_API_KEY}
```

生产部署应通过 Secret 管理器、容器编排平台或 CI/CD Secret 注入 `DATABASE_PASSWORD`、`SERVICE_API_KEY` 等值；不得把真实凭据写进 HOCON、Dockerfile、Notebook、日志或 Git 历史。`ENV_PROFILE` 可以用于选择入口文件，但不能把所有部署配置硬编码为若干不可组合的大文件；当需要选择具体文件时，优先使用 `FILES_CONFIG`，并保证文件本身不含秘密。

### IV. 后备服务（Backing Services）——将其视为附加资源

**12-Factor 要求。** 数据库、缓存、消息队列、SMTP、对象存储、指标和外部 API 都是通过网络访问的后备服务。应用代码不应区分本地服务和第三方托管服务，只应通过配置中的 URL、资源句柄和凭据访问它们；资源应可在不修改代码的情况下连接、替换或解绑。[5]

**Aloha 的落地方式。** `aloha.db` 已为 PostgreSQL、MySQL、SQLite、MongoDB、Redis、Elasticsearch、DuckDB、Oracle、Kafka 等资源提供统一或半统一的接入模块，`aloha.encrypt.vault` 可用于密码或密钥的安全解析。应用应把每个资源定义为独立配置项，例如 `DATABASE_URL`、`REDIS_URL`、`KAFKA_BOOTSTRAP_SERVERS`，并由连接工厂根据资源句柄建立连接。代码不得写死主机名、端口、用户名或“本地开发专用”分支；本地、staging 和生产应尽量使用相同类型及兼容版本的服务。

### V. 构建、发布、运行（Build, Release, Run）——严格分离三个阶段

**12-Factor 要求。** 构建阶段将代码和依赖转换成可执行 bundle；发布阶段把该 bundle 与当前部署配置组合成不可变 release；运行阶段只启动指定 release。每个 release 应有唯一 ID，且不能原地修改；回滚应通过选择旧 release 完成。[6]

**Aloha 的落地方式。** 推荐将 `src/app-demo.Dockerfile` 的多阶段镜像流程作为参考：builder 阶段复制源码、安装构建依赖并执行 `aloha compile`（若需要）；runtime 阶段只复制构建产物并安装声明的运行依赖。CI 应按如下顺序工作：

```text
Git commit → build/test/scan → push immutable image:<commit-or-version>
          → release: inject env/Secret and select image digest
          → run: start the image without editing it
```

镜像应使用不可变 tag 或 digest；不要在容器启动时执行 `git pull`、`pip install`、编译源码或改写发布文件。配置变化应创建新的 release 记录，即使镜像未变化；代码变化必须产生新的镜像。Docker build args 可用于构建参数，但不应承载秘密，因为它们可能进入构建历史。

### VI. 进程（Processes）——以无状态进程运行

**12-Factor 要求。** 进程应无状态、共享无关。内存或本地文件系统只能作为短暂的单事务缓存；需要持久化的数据必须写入数据库、对象存储、队列或其他后备服务。不能依赖 sticky session 或某个进程的本地缓存。[7]

**Aloha 的落地方式。** 使用 `src/main.py` 或 `aloha start` 作为明确的进程入口，将 HTTP 服务、worker 和定时任务拆成可独立扩缩容的 process type。请求会话、任务状态、上传文件和业务结果应写入 Redis、数据库或对象存储；容器的 `logs/` 不应成为业务数据存储。`aloha.db` 的连接模块和服务模块可帮助把外部状态放到附加资源中，但应用仍须避免模块全局可变状态、跨请求临时文件和本地 session。

### VII. 端口绑定（Port Binding）——通过端口提供服务

**12-Factor 要求。** 应用作为自包含服务，通过端口绑定提供 HTTP 或其他协议，不依赖运行时注入的外部 Web 服务器。端口应可由环境配置，服务应监听容器可达的地址。[8]

**Aloha 的落地方式。** 应用入口从 `PORT` 或项目约定的 `PORT_SVC` 读取端口，并监听 `0.0.0.0`；Dockerfile 使用 `EXPOSE` 表达默认端口，部署平台负责真正的端口映射。`src/app-demo.Dockerfile` 已提供 `PORT_SVC`、`EXPOSE` 和 HTTP `HEALTHCHECK` 的示例。应用不要把开发机 `localhost` 作为生产监听地址，也不要要求生产环境必须预装 Nginx/Apache 才能启动；反向代理、TLS 和网关可作为平台层能力。

### VIII. 并发（Concurrency）——通过进程模型扩展

**12-Factor 要求。** 进程是一级资源；不同工作负载用不同 process type 表达，容量通过增加进程数量横向扩展。进程不应自行 daemonize 或写 PID 文件，而应交给操作系统或平台进程管理器。[9]

**Aloha 的落地方式。** 将 web API、异步 worker、批处理和管理命令分别定义为独立启动命令，并在 Docker Compose、Kubernetes 或其他平台中分别设置副本数、资源限制和滚动策略。可在单进程内部使用线程或异步模型，但不能把单个进程的垂直扩展当作唯一扩展方案。容器中的前台进程应保持为 PID 1 的主服务或由明确的进程管理器启动，不应使用 `tail -f` 作为生产服务入口；`src/dev-demo.Dockerfile` 中的 `tail -f /dev/null` 仅适合开发容器保持存活。

### IX. 易处理性（Disposability）——快速启动和优雅停止

**12-Factor 要求。** 进程应可随时启动和停止，启动尽量快速，并在收到 `SIGTERM` 时停止接收新请求、完成当前工作后退出。worker 应能安全归还未完成任务；同时还要能承受突然终止。[10]

**Aloha 的落地方式。** 启动时只加载必要配置、建立连接池并快速开始服务；不要在启动时执行不可控的长任务或隐式迁移。HTTP 服务应注册 `SIGTERM` 处理逻辑并关闭监听器、连接池和线程；worker 应使用可重试、幂等或事务化的任务处理，并让队列在断连时重新投递任务。Docker `HEALTHCHECK` 只用于发现服务状态，不能替代优雅停止。部署平台应设置合理的 termination grace period，并验证强制杀进程后的恢复行为。

### X. 开发、预发布、生产一致性（Dev/Prod Parity）——尽量保持一致

**12-Factor 要求。** 应缩短代码到生产的时间差、开发者与运维者之间的人员差，并尽量消除工具和后备服务差异。开发、staging 和 production 应使用相同类型及兼容版本的数据库、队列、缓存和运行时。[11]

**Aloha 的落地方式。** 使用 `tool/cicd/` 的脚本和 Docker Compose 启动容器化开发环境；开发、CI 和生产复用相同的 Python 版本、依赖清单、入口命令和 Docker 构建流程。HOCON 的 `include` 用于组织配置结构，环境变量用于注入部署差异。开发环境可以降低资源规模，但不应把 SQLite、内存缓存或 mock 队列作为唯一测试路径；应在 CI 中运行真实或兼容的 PostgreSQL、Redis、Kafka 等服务集成测试，并对本地镜像和生产镜像执行相同的启动检查。

### XI. 日志（Logs）——将日志视为事件流

**12-Factor 要求。** 应用只产生按时间排序的事件流，不负责日志文件的路由、保留和归档。进程应将未缓冲日志写到 `stdout`/`stderr`，由执行环境统一采集、聚合、检索和告警。[12]

**Aloha 的落地方式。** `aloha.logger` 提供统一 logger、日志级别配置和多进程安全的文件 handler；在 12-Factor 生产部署中，推荐配置控制台 handler，让应用日志输出到标准输出，由 Docker、Kubernetes、Fluent Bit 或云日志服务负责采集。若因合规要求保留文件 handler，应将其视为平台或 sidecar 的临时能力，不让业务依赖本地日志文件，也不把 `logs/` 挂载卷当作跨实例共享状态。日志应包含时间、级别、服务名、release ID、request/correlation ID，并避免打印凭据、Token、密码和个人敏感信息。

### XII. 管理进程（Admin Processes）——以一次性进程运行管理任务

**12-Factor 要求。** 数据库迁移、REPL、数据修复和一次性脚本应作为 one-off process 运行，并使用与常驻进程完全相同的代码、依赖、release 和配置。[13]

**Aloha 的落地方式。** 将迁移、重建索引、数据修复和诊断脚本提交到代码库，并为每项任务定义明确的 CLI 入口；通过同一个镜像 digest、同一组环境变量和同一依赖环境执行。例如，管理任务应在生产 release 容器内调用 `python -m your_app.admin.migrate` 或项目定义的 `aloha` 子命令，而不是在宿主机临时安装一套依赖后运行。任务必须可审计、幂等或可安全重试，并在执行前后记录 release、操作者和影响范围。

## 三、推荐的 Aloha 目录与发布约定

```text
my-aloha-service/
├── src/
│   ├── my_app/                 # 业务包和 process type 入口
│   ├── resource/config/
│   │   ├── main.conf           # 非秘密配置结构
│   │   └── database.conf        # 可 include 的模块配置
│   ├── pyproject.toml           # 应用依赖、测试和入口
│   └── Dockerfile               # build/run 镜像定义
├── tests/                      # 单元、集成和启动检查
├── tool/cicd/                  # 本地与 CI/CD 脚本
├── doc/                        # 用户、开发和运维文档
└── .github/workflows/          # 构建、测试、扫描和发布
```

推荐发布命令应满足“相同代码、显式依赖、不可变镜像、运行时注入配置”的原则。示例命令如下，具体入口以应用自身的 `pyproject.toml` 和 Dockerfile 为准：

```bash
# 本地验证
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest

# 构建不可变镜像
export RELEASE_ID="$(git rev-parse --short=12 HEAD)"
docker build -f src/Dockerfile -t registry.example/my-aloha-service:"$RELEASE_ID" .
docker push registry.example/my-aloha-service:"$RELEASE_ID"

# 运行时仅注入配置，不在容器内改代码或安装依赖
docker run --rm \
  -e ENV_PROFILE=PRD \
  -e FILES_CONFIG=main.conf,database.conf \
  -e DATABASE_URL \
  -e DATABASE_PASSWORD \
  -p 8080:8080 \
  registry.example/my-aloha-service:"$RELEASE_ID"
```

## 四、上线前验收清单

| 检查项 | 通过条件 |
| --- | --- |
| 代码库 | 所有应用源码和构建定义来自一个 Git 代码库；部署可追溯到 commit |
| 依赖 | `pyproject.toml` 显式声明依赖；构建环境与运行环境隔离且可复现 |
| 配置 | 凭据不在仓库、镜像和日志中；部署差异由环境变量/Secret 注入 |
| 后备服务 | 数据库、缓存、队列和外部 API 通过资源句柄连接，可替换而无需改代码 |
| 构建发布运行 | 构建、发布、运行分离；镜像和 release 不原地修改；支持回滚 |
| 进程与并发 | 进程无状态；web/worker/admin 入口分离；副本可横向增加 |
| 端口与健康 | 监听 `0.0.0.0`；端口可配置；健康检查不依赖宿主机内部路径 |
| 停止与恢复 | `SIGTERM` 可优雅停止；任务幂等或可重试；突然退出后不会丢失持久状态 |
| 开发生产一致性 | 使用同一运行时、依赖和主要后备服务类型；集成测试覆盖真实连接方式 |
| 日志 | 生产日志输出 `stdout/stderr`；平台统一采集；不写入敏感信息 |
| 管理进程 | 迁移和修复任务随应用代码发布，并使用相同镜像、配置和依赖运行 |

## 参考资料

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
