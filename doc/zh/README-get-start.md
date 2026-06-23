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

1. **定义 API 处理程序**：通过继承 `aloha.service.api.v0` 中的 `APIHandler` 来创建你的 API 处理程序。例如，在 `src/app_common/api/api_multipart.py` 中：

```python
from aloha.logger import LOG
from aloha.service.api.v0 import APIHandler

class MultipartHandler(APIHandler):
    def response(self):
        LOG.info("Handling multipart request")
        return {"status": "success"}

default_handlers = [
    (r"/api_internal/multipart", MultipartHandler),
]
```

2. **配置应用程序**：在 `src/resource/config/main.conf` 中定义你的应用程序配置。指定要加载的模块：

```hocon
service {
    modules = [
        "app_common.api.api_multipart"
    ]
}
```

3. **启动应用程序**：使用 `aloha.service.app` 中的 `Application` 类来启动你的服务。例如，在 `src/app_common/main.py` 中：

```python
def main():
    from aloha.service.app import Application
    app = Application()
    app.start()
```

你可以使用提供的 `main.py` 脚本运行应用程序：

```bash
python3 src/main.py app_common.main
```

[:octicons-mark-github-16: 前往模板项目](https://github.com/LabNow-ai/aloha-python/tree/main/src){ .md-button }
