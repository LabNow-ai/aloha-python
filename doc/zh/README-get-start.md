# 快速开始

## 第一步：安装 Python 包

```title="安装 aloha 及全部扩展依赖"
pip install aloha[all]
```

## 第二步：把本仓库当作 boilerplate 使用

仓库中的 `app/` 目录就是基于 `aloha` 的 boilerplate / 模板项目。
它已经准备好了可直接使用的项目结构、开发脚本和容器化工具，你可以直接在这个骨架上开始开发，而不需要从零搭建工程。

### 这个模板提供了什么

- 基于 Docker 和 Docker Compose 的容器化开发环境
- 预装好的 Python 运行环境和项目依赖
- 可直接扩展的应用入口
- 适合持续开发的常见目录结构：源码、文档、Notebook、工具脚本

### 推荐使用方式

1. 克隆本仓库。
2. 打开 `app/` 目录，查看模板项目的结构。
3. 需要可复现开发环境时，使用 `tool/cicd/` 里的脚本启动开发容器。
4. 在模板结构上放入你自己的业务代码，并逐步扩展。

### 启动开发环境

如果你想直接使用完整的 boilerplate 开发环境，可以启动容器化 DEV 环境：

```bash
./tool/cicd/run-dev.sh up
./tool/cicd/run-dev.sh enter
```

其中 `up` 用于创建或启动开发容器，`enter` 用于进入容器内部的交互式 Shell。

### 项目结构

这个模板围绕几个常见目录组织：

- `app/`：应用代码和入口
- `src/`：`aloha` 库源码
- `doc/`：文档源码
- `notebook/`：用于实验和探索的 Jupyter Notebook
- `tool/`：开发与 CI/CD 相关脚本和 Docker 资源

你可以参考 GitHub 仓库中的 `app` 目录，在自己的项目中开始使用 `aloha`：

[:octicons-mark-github-16: 前往模板项目](https://github.com/LabNow-ai/aloha-python/tree/main/app){ .md-button }
