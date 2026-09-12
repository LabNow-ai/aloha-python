# 配置说明

## 操作系统环境变量

### `PROFILE_ENV`

*默认值*：`None`（未定义）。

用于指定当前进程运行环境，例如 `DEV | STG | PRD`。
通常用于决定 `${DIR_CONFIG}` 下哪个配置文件作为入口配置。

如果该变量已定义，`aloha` 会优先查找 `main-${PROFILE_ENV}.conf`；否则使用 `main.conf`。

> [!NOTE]
> **向后兼容与弃用说明**：
> 如果 `PROFILE_ENV` 未定义或无值，`aloha` 会回退读取旧版环境变量 `ENV_PROFILE`。若检测到 `ENV_PROFILE` 有值，系统将输出 `DeprecationWarning` 弃用警告。`ENV_PROFILE` 已被弃用，并且在将来版本中会正式取消支持。请尽快迁移使用 `PROFILE_ENV`。

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
如果该变量存在，则会忽略 `PROFILE_ENV`（及旧版 `ENV_PROFILE`）。
