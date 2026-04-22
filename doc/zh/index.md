# 介绍

Aloha！感谢你关注这个 Python 包。

[![License](https://img.shields.io/github/license/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/LabNow-ai/aloha-python/build.yml?branch=main)](https://github.com/LabNow-ai/aloha-python/actions)
[![Join the Gitter Chat](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/LabNow-ai/)
[![PyPI version](https://img.shields.io/pypi/v/aloha)](https://pypi.python.org/pypi/aloha/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/aloha)](https://pepy.tech/badge/aloha/)
[![Code Activity](https://img.shields.io/github/commit-activity/m/LabNow-ai/aloha-python)](https://github.com/LabNow-ai/aloha-python/pulse)
[![Recent Code Update](https://img.shields.io/github/last-commit/LabNow-ai/aloha-python.svg)](https://github.com/LabNow-ai/aloha-python/stargazers)

如果这个项目对你有帮助，欢迎给我们点一个 STAR，或支持我们的开发工作！[![GitHub Stars](https://img.shields.io/github/stars/LabNow-ai/aloha-python.svg?label=Stars&style=social)](https://github.com/LabNow-ai/aloha-python/stargazers)

`aloha` 是一个用于构建 Python 微服务的通用工具包，封装了常见组件与能力，例如：

- 快速创建 RESTful API 并启动服务
- 日志工具
- 环境、配置文件与资源文件管理
- 连接常见数据库
- 运行环境检测与监控

## 安装

```title="安装 aloha 及扩展依赖"
pip install aloha[all]
```

请注意，包名后的 `[all]` 表示额外依赖集合，用于启用更多能力。

可选扩展包括：

- `all`：包含下面所有扩展
- `service`：构建 RESTful API 所需依赖（`aloha` 基于 Tornado）
- `build`：将 Python 代码编译为二进制文件，便于源码保护
- `db`：连接常见数据库，如 MySQL / PostgreSQL / Redis
- `stream`：基于 `confluent_kafka` 处理流式数据
- `data`：使用 `pandas` 等库进行数据处理或数据科学任务
- `report`：将数据或报告导出为 Excel 文件
- `test`：单元测试工具
- `docs`：文档构建工具
