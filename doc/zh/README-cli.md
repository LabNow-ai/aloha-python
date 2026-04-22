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

在某些场景下，你可能希望发布可运行的 Python 项目，但不直接分发原始 `.py` 源码。这个命令会把大部分 Python 模块编译为扩展库文件（Linux/macOS 上通常是 `.so`），从而提升源码保护能力，也减少实现细节的直接可读性。

Aloha 通过 `Cython` 完成这个流程：

```bash
aloha compile --base=./app --dist=./build --keep='main.py'
```

它的执行逻辑如下：

1. 扫描 `--base` 指定的源码目录。
2. 跳过隐藏目录、输出目录、被排除路径、`.pyc` 文件和 `.pyx` 文件。
3. 将非 Python 文件原样复制到目标目录。
4. 将普通的 `.py` 模块编译为扩展模块。
5. 将 `--keep` 指定的文件保留为普通 Python 文件，不参与编译。
6. 将最终产物移动到 `--dist`，并清理中间生成的 Cython 文件。

需要注意：

- `__init__.py` 会被当作普通 Python 文件复制，不会编译。
- 所有的作为python submodule的文件夹中，必须包含`__init__.py`文件，否则该submodule模块下的.py文件会编译后会被放置到根目录下。
- `--keep` 指定的文件不会被编译。
- 使用前需要先安装 `Cython`。
- 该命令会先在 `/tmp/build/<项目名>` 下生成临时构建目录，再把结果移动到 `--dist`。

可用参数：

- `--base`：待构建源码的根目录
- `--dist`：二进制产物目录（默认值为 `build`）
- `--exclude`：需要排除的文件/目录，参数后可直接跟一个或多个路径
- `--keep`：保留为源码、不转为动态库的文件，参数后可直接跟一个或多个路径
