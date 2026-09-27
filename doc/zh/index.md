# Aloha：Python 微服务工具库与项目模板

**Aloha 是一个开源 Python 工具库和微服务项目模板，帮助开发者构建可容器化部署的服务。** `aloha` 包集成了 HOCON 配置、结构化日志、数据库操作、加密工具、FastAPI/Uvicorn 服务辅助组件和测试支持。

你可以将 `aloha` 安装到现有 Python 项目中，也可以使用 `aloha-python` 仓库作为新微服务的 Docker 开发起点。

[![PyPI 版本](https://img.shields.io/pypi/v/aloha)](https://pypi.org/project/aloha/)
[![构建状态](https://img.shields.io/github/actions/workflow/status/LabNow-ai/aloha-python/build.yml?branch=main)](https://github.com/LabNow-ai/aloha-python/actions)
[![许可证](https://img.shields.io/github/license/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/blob/main/LICENSE)

## Aloha 提供什么

- **HOCON 配置**：加载模块化配置文件，并通过环境变量选择运行配置 profile。
- **面向服务的日志**：将 plain 或 JSON 日志输出到控制台和按日轮转的文件，并包含进程及主机元数据。
- **数据库连接**：提供 PostgreSQL、MySQL、SQLite、DuckDB、MongoDB、Redis、Elasticsearch、Oracle 和 Kafka 等数据库或服务的操作工具。
- **安全工具**：AES、RSA、JWT、哈希及密码保险库集成。
- **Python Web 服务**：FastAPI/Uvicorn 应用辅助组件和可复用 HTTP 服务组件。
- **测试与构建工具**：测试辅助工具，以及可选的 Cython 命令，用于将指定模块构建为本地扩展模块。
- **容器化项目模板**：示例应用、Dockerfile、Docker Compose 开发环境和 CI/CD 脚本。

## 安装 Python 包

Aloha 支持 Python 3.10 及以上版本。使用 pip 安装基础包：

```bash
python -m pip install aloha
```

可选集成通过 extras 分组；只安装项目需要的依赖即可：

```bash
python -m pip install "aloha[service]"  # FastAPI 和 Uvicorn
python -m pip install "aloha[db]"       # 数据库集成
python -m pip install "aloha[all]"      # 所有可选集成和工具
```

更多 extras 和最小使用示例见[安装与快速开始](README-get-start.md)。

## 选择使用方式

### 在现有 Python 项目中使用 Aloha

安装 Python 包，使用 HOCON 配置应用，然后导入所需模块：

```python
from aloha.logger import LOG

LOG.info("Service is ready")
```

全局 logger 从 HOCON 的 `deploy` 配置读取日志级别、文件格式和控制台格式。详情参阅[配置指南](README-config.md)和[日志 API 参考](api/logging.md)。

### 从微服务模板开始

克隆仓库并启动开发容器：

```bash
git clone https://github.com/LabNow-ai/aloha-python.git
cd aloha-python
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

进入容器后运行示例服务和测试：

```bash
cd /workspace/src
python3 main.py app_common.main
pytest ./
```

`src/app_common/` 中的应用是可供改造的示例。完整步骤和目录说明参见[快速开始指南](README-get-start.md)。

## 文档导航

- [安装与快速开始](README-get-start.md)
- [配置与 HOCON profile](README-config.md)
- [CLI 命令](README-cli.md)
- [12-Factor 应用指南](README-12factor.md)
- [开发与 Docker 指南](README-develop.md)
- [API 参考](api/index.md)

## 项目与社区

- [GitHub 源码仓库](https://github.com/LabNow-ai/aloha-python)
- [PyPI Python 包](https://pypi.org/project/aloha/)
- [报告问题或提出功能建议](https://github.com/LabNow-ai/aloha-python/issues)
