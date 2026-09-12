# Configurations

## OS environment variables

### `PROFILE_ENV`

*Default value*: `None` (not defined).

Define the environment profile for the current process, such as `DEV | STG | PRD`.
This is usually used to decide which config file in `${DIR_CONFIG}` should be used as the entrypoint config.

If this environment variable is defined, `aloha` will first search for `main-${PROFILE_ENV}.conf`; otherwise it uses `main.conf`.

> [!NOTE]
> **Backward Compatibility & Deprecation Notice**:
> If `PROFILE_ENV` is not defined or has no value, `aloha` falls back to reading the legacy `ENV_PROFILE` environment variable. If `ENV_PROFILE` is present, a `DeprecationWarning` will be emitted. `ENV_PROFILE` is deprecated and support will be removed in a future release. Please migrate to `PROFILE_ENV`.

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
If this variable is set, `PROFILE_ENV` (and legacy `ENV_PROFILE`) is ignored.
