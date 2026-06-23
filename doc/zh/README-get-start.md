# 快速开始

## 第一步：安装 Python 包

```title="安装 aloha 及全部扩展依赖"
pip install aloha[all]
```

## 第二步：把本仓库当作 boilerplate 使用

本仓库是一个基于 `aloha` 的样板/模板项目。
它提供了一个即用的应用程序布局、开发脚本和容器化工具，让你无需从头搭建项目骨架，即可开始构建。

### 这个模板提供了什么

- 基于 Docker 和 Docker Compose 的容器化开发环境
- 预装好的 Python 运行环境和项目依赖
- 可直接扩展的应用入口
- 适合持续开发的常见目录结构：源码、文档、Notebook、工具脚本

### 推荐使用方式

1. 克隆本仓库。
2. 检查启动应用程序的结构。
3. 需要可复现开发环境时，使用 `tool/cicd/` 里的脚本启动开发容器。
4. 在模板结构上放入你自己的业务代码，并逐步扩展。

### 启动开发环境

如果你想直接使用完整的 boilerplate 开发环境，可以启动容器化 DEV 环境：

```bash
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

其中 `up` 命令用于创建或启动开发容器，`enter` 命令用于进入容器内部的交互式 Shell。

### 项目结构

这个模板围绕几个常见目录组织：

- `doc/`：文档源文件。你可以在这里放置你的项目文档。
- `src/`：应用程序代码和入口。这是你的业务逻辑所在。它包含一个演示应用程序 (`app_common`)，展示了如何使用 `aloha`。
- `tool/`：开发和 CI/CD 相关的脚本和 Docker 资源。

### 如何在你的项目中使用 `aloha` 包

`src/` 目录包含一个演示应用程序，展示了如何使用 `aloha` 包。以下是如何在常规 Python 项目开发中导入和使用 `aloha` 的简要概述：

1. **导入 `aloha` 模块**：为你的应用程序逻辑导入必要的 `aloha` 模块。例如，`aloha.logger` 用于日志记录，`aloha.config` 用于配置，或 `aloha.db` 用于数据库交互。

2. **配置你的应用程序**：在 `src/resource/config/main.conf` 中定义你的应用程序配置。

3. **实现你的应用程序逻辑**：使用导入的 `aloha` 模块编写你的 Python 代码。

4. **运行你的应用程序**：你可以使用提供的 `main.py` 脚本运行应用程序：

```bash
python3 src/main.py your_module.main
```

此命令指示 `src/main.py` 查找并执行你指定模块（例如 `your_module.main`）中的 `main()` 函数。

## HOCON 配置

`aloha` 使用 HOCON (Human-Optimized Config Object Notation) 格式作为其配置文件。这允许分层、模块化和人类可读的配置。

### 配置文件位置

默认情况下，`aloha` 会在 `src/resource/config/` 目录中查找配置文件。主配置文件是 `main.conf`。

### 模块化配置

HOCON 支持包含其他配置文件，这对于模块化你的设置非常有用（例如，分离开发、预发布和生产环境的配置）。

**`main.conf` 示例：**

```hocon
include "deploy-DEV.conf"

app_name = "MyAlohaApp"

server {
    host = "0.0.0.0"
    port = 8080
}

database {
    type = "postgresql"
    connection_string = "${?DB_CONNECTION_STRING}" # 环境变量覆盖
}
```

在此示例中：
- `include "deploy-DEV.conf"` 引入了来自另一个文件的设置，允许进行特定于环境的覆盖。
- `app_name` 和 `server` 定义了应用程序特定的设置。
- `database.connection_string = "${?DB_CONNECTION_STRING}"` 演示了如何使用环境变量覆盖配置值，使其适用于不同的部署环境。

### 在代码中访问配置

你可以通过 `aloha.settings.SETTINGS.config` 在你的 Python 代码中访问配置值：

```python
from aloha.settings import SETTINGS

app_name = SETTINGS.config.get("app_name")
server_port = SETTINGS.config.get("server.port")

print(f"Application Name: {app_name}")
print(f"Server Port: {server_port}")
```

这种方法确保了你的应用程序可配置并适应各种部署场景。

[:octicons-mark-github-16: 前往模板项目](https://github.com/LabNow-ai/aloha-python/tree/main/src){ .md-button }
