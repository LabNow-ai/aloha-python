# Development Docs

## Live debug source code with Docker

```bash
# First, cd to project root (which includes `src`), then run:
docker run -it \
  -v $(pwd):/root/app/ \
  -w /root/app/src \
  --name="app-$(whoami)" \
  -p 8080:80 \
  quay.io/labnow/base:latest bash

python -m aloha.script.start app_common.debug
```

## Build Docker image

```bash
source tool/tool.sh
build_image app_common latest tool/app.Dockerfile
```

## Develop docs

```bash
mkdocs serve -f mkdocs.yml -a 0.0.0.0:3000
```
