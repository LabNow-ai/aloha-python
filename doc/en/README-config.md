# Configurations

## OS environment variables

### `ENV_PROFILE`

*Default value*: `None` (not defined).

Define the environment profile for the current process, such as `DEV | STG | PRD`.
This is usually used to decide which config file in `${DIR_CONFIG}` should be used as the entrypoint config.

If this environment variable is defined, `aloha` will first search for `main-${ENV_PROFILE}.conf`; otherwise it uses `main.conf`.

### `ENTRYPOINT`

*Default value*: `None` (not defined).

Define the entrypoint **Python module** when using `aloha start` to start a service/process.
It is equivalent to `aloha start ${ENTRYPOINT}`.

The specified **Python module must** contain a `main()` function.

### `APP_MODULE`

*Default value*: `default`.

Define the application module name. It is mapped to config variable `APP_MODULE` and used as the prefix for log files.

### `DIR_LOG`

*Default value*: `logs`.

Define where log files are stored.

### `DIR_RESOURCE`

*Default value*: `resource` under the current working directory.

Define the resource folder. It will be used as the root directory by `aloha.config.paths.get_resource_dir()`.

### `DIR_CONFIG`

*Default value*: `${DIR_RESOURCE}/config`.

Define where to find configuration files.

### `FILES_CONFIG`

*Default value*: `None` (not defined).

Optional. Define a comma-separated list of config files to load.
If this variable is set, `ENV_PROFILE` is ignored.
