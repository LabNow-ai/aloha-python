# 开发文档

## 使用 Docker 对源码进行实时调试

```bash
# 先进入项目根目录（该目录包含 `src`），然后执行：
docker run -it \
  -v $(pwd):/root/app/ \
  -w /root/app/src \
  --name="app-$(whoami)" \
  -p 8080:80 \
  quay.io/labnow/base:latest bash

python -m aloha.script.start app_common.debug
```

## 构建 Docker 镜像

```bash
source tool/tool.sh
build_image app_common latest tool/app.Dockerfile
```

## 开发文档

```bash
mkdocs serve -f mkdocs.yml -a 0.0.0.0:80
```
