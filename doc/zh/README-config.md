# 配置说明

## 操作系统环境变量

### `ENV_PROFILE`

*默认值*：`None`（未定义）。

用于指定当前进程运行环境，例如 `DEV | STG | PRD`。
通常用于决定 `${DIR_CONFIG}` 下哪个配置文件作为入口配置。

如果该变量已定义，`aloha` 会优先查找 `main-${ENV_PROFILE}.conf`；否则使用 `main.conf`。

### `ENTRYPOINT`

*默认值*：`None`（未定义）。

使用 `aloha start` 启动服务/进程时，指定入口 **Python 模块**。
它等价于执行 `aloha start ${ENTRYPOINT}`。

指定的 **Python 模块必须**包含 `main()` 函数。

### `APP_MODULE`

*默认值*：`default`。

用于定义应用模块名。该值会映射到配置项 `APP_MODULE`，并作为日志文件名前缀。

### `DIR_LOG`

*默认值*：`logs`。

用于定义日志文件存储目录。

### `DIR_RESOURCE`

*默认值*：当前工作目录下的 `resource`。

用于定义资源目录。该目录会作为 `aloha.config.paths.get_resource_dir()` 的根目录。

### `DIR_CONFIG`

*默认值*：`${DIR_RESOURCE}/config`。

用于定义配置文件目录。

### `FILES_CONFIG`

*默认值*：`None`（未定义）。

可选项。用于定义以英文逗号分隔的配置文件列表。
如果该变量存在，则会忽略 `ENV_PROFILE`。
