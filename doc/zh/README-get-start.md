# Aloha 快速开始

本指南介绍两种使用 Aloha 的方式：

1. 在现有应用中安装和使用 `aloha` Python 工具库。
2. 将 `aloha-python` 仓库作为基于 Docker 的微服务模板。

## 1. 安装 Python 工具库

Aloha 支持 Python 3.10 及以上版本。安装基础包：

```bash
python -m pip install aloha
```

按需安装可选能力：

```bash
python -m pip install "aloha[service]"  # FastAPI 和 Uvicorn 支持
python -m pip install "aloha[db]"       # 数据库集成
python -m pip install "aloha[all]"      # 所有可选依赖
```

其他 extras 包括：`aio` 异步数据库驱动、`build` Cython 编译、`stream` Kafka 客户端、`data` 和 `report` 数据处理与报表工具，以及用于开发的 `test` 和 `docs`。

验证安装：

```bash
aloha info
```

## 2. 在应用中使用 Aloha

只需导入应用所需模块。例如，从 `aloha.logger` 导入共享 logger：

```python
from aloha.logger import LOG

LOG.info("Application started")
```

如需使用 HOCON 配置，可指定资源配置目录并通过 `SETTINGS` 读取：

```python
from aloha.settings import SETTINGS

config_settings = SETTINGS.config
```

默认情况下，Aloha 会相对于当前工作目录从 `resource/config/` 查找配置。可以通过 `PROFILE_ENV`、`FILES_CONFIG`、`DIR_RESOURCE` 和 `DIR_CONFIG` 选择配置 profile 与配置文件位置。详情见[配置指南](README-config.md)。

`aloha start` 可以运行包含 `main()` 函数的应用模块：

```bash
aloha start your_package.main
```

## 3. 从微服务模板开始

克隆仓库并进入项目目录：

```bash
git clone https://github.com/LabNow-ai/aloha-python.git
cd aloha-python
```

启动并进入容器化开发环境：

```bash
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

在容器 Shell 中运行 FastAPI/Uvicorn 示例服务和测试：

```bash
cd /workspace/src
python3 main.py app_common.main
pytest ./
```

示例应用位于 `src/app_common/`；服务配置和 profile 位于 `src/resource/config/`。可以基于这些示例添加自己的业务逻辑。容器命令见[开发指南](README-develop.md)，HOCON 配置见[配置指南](README-config.md)。

## 4. 构建生产镜像

在仓库根目录执行以下命令，构建示例 Docker 镜像：

```bash
source tool/tool.sh
build_image app_common latest src/app-demo.Dockerfile
```

Docker 构建过程可以使用 Cython 编译指定的应用模块。详情见[CLI 指南](README-cli.md)和[编译参考](../skills/aloha_python/references/compile.md)。

## 后续阅读

- 浏览 [API 参考](api/index.md)。
- 了解[结构化日志](api/logging.md)、[数据库集成](api/db.md)和 [HOCON 配置](README-config.md)。
- 查看 [12-Factor 应用指南](README-12factor.md)，了解部署实践。
