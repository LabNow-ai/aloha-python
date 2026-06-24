# 开发文档

## 快速启动开发环境

本项目提供了一个使用 Docker 和 Docker Compose 的容器化开发环境。它设置了一个完整的开发工作区，预装了所有必要的依赖项。

### 启动开发环境

在你的终端中运行此命令：

```bash
./tool/cicd/run-dev.sh up
```

这将构建 Docker 镜像并启动容器。你的本地代码目录将挂载到容器中，实现实时开发。

### 进入开发容器

环境运行后，执行：

```bash
./tool/cicd/run-dev.sh enter
```

你将连接到正在运行的容器，并获得一个 bash shell。

### 管理环境

`run-dev.sh` 脚本提供了几个命令来管理你的开发环境：

| 命令                          | 描述                                 |
| -------------------------------- | ------------------------------------------- |
| `./tool/cicd/run-dev.sh up`      | 启动或创建开发环境 |
| `./tool/cicd/run-dev.sh restart` | 重启正在运行的容器               |
| `./tool/cicd/run-dev.sh logs`    | 查看并跟踪容器日志              |
| `./tool/cicd/run-dev.sh enter`   | 访问容器的 bash shell           |
| `./tool/cicd/run-dev.sh down`    | 停止并移除容器               |

## 使用 Docker 实时调试源代码

如果你更喜欢运行单个容器进行调试：

```bash
# 首先，cd 到项目根目录（包含 `src`），然后运行：
docker run -it \
  -v $(pwd):/root/app/ \
  -w /root/app/src \
  --name="app-$(whoami)" \
  -p 8080:80 \
  quay.io/labnow/base:latest bash

python3 main.py app_common.debug
```

## 构建 Docker 镜像

```bash
source tool/tool.sh
build_image app_common latest tool/app-demo.Dockerfile
```

## 开发文档

```bash
mkdocs serve -f mkdocs.yml -a 0.0.0.0:3000
```
