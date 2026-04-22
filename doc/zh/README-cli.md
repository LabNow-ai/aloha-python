# 常用任务

## 检查 aloha 是否安装成功

```bash
aloha info
```

该命令会输出包版本等信息。

## 从主入口函数启动模块

```bash
aloha start package_name.module_name
# 例如: aloha start app_common.debug
```

注意：`module_name` **必须**包含名为 `main()` 的函数。

## 将 Python 代码编译为二进制

在某些场景下，你可能需要把 Python 源码编译为二进制库，以保护源码。

Aloha 支持通过 `Cython` 进行构建：

```bash
aloha compile --base=./app --dist=./build --keep='main.py'
```

可用参数：

- `--base`：待构建源码的根目录
- `--dist`：二进制产物目录（默认值为 `build`）
- `--exclude`：需要排除的文件/目录（可多次传入）
- `--keep`：保留为源码、不转为动态库的文件（可多次传入）
