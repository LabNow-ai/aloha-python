from typing import Any

from attrdict import AttrDict

from .config import hocon, paths


class Settings:
    """
    Global settings management class for the Aloha package.

    This class manages the lazy loading of HOCON configuration files, environment
    profile resolution, and provides access to project resource and configuration directories.

    Attributes:
        _config (Any | None): Internal storage for the parsed configuration.
    """

    def __init__(self, config: Any | None = None):
        """
        Initialize the Settings manager.

        :param config: Optional pre-loaded configuration dictionary, list, or None.
                       If provided, it is parsed and loaded immediately.
        """
        if config is None:
            self._config = None
        else:
            self.load_settings(config)

    @property
    def dir_resource(self):
        """
        Get the absolute path of the resource directory.

        Resolves dynamically based on the `DIR_RESOURCE` environment variable,
        falling back to the default 'resource' directory in the current working directory.

        :return: Absolute path to the resource directory.
        """
        return paths.get_resource_dir()

    @property
    def dir_config(self):
        """
        Get the absolute path of the configuration directory.

        Resolves dynamically based on the `DIR_CONFIG` environment variable,
        falling back to the 'config' subdirectory under the resource directory.

        :return: Absolute path to the configuration directory.
        """
        return paths.get_config_dir()

    def load_settings(self, config: Any) -> Any:
        """
        Recursively load and transform configuration values.

        Converts raw dictionaries into `AttrDict` objects to support attribute-style
        dot notation access, and recursively processes lists and nested values.

        :param config: The configuration data to load (dict or list).
        :return: The converted configuration object (AttrDict or list).
        :raises ValueError: If the configuration data type is unsupported.
        """
        if isinstance(config, dict):
            self._config = AttrDict({key: self.load_settings(value) for key, value in config.items()})
        elif isinstance(config, list):
            self._config = [self.load_settings(value) for value in config]
        else:
            raise ValueError("Unsupported config type: %s" % str(type(config)))
        return self._config

    @property
    def config(self):
        """
        Get the global configuration object.

        Lazily loads and parses configuration files on first access. It resolves active
        HOCON configuration files based on the `FILES_CONFIG` or `ENV_PROFILE` environment
        variables, falls back to `main.conf` if not specified, and merges them into an `AttrDict`.

        :return: Merged global configuration settings as an AttrDict.
        """
        if self._config is None:
            config_files = paths.get_config_files()  # by default, use the `main.conf` file in the config_dir
            self._config = hocon.load_config_from_hocon_files(config_files, base_dir=paths.get_config_dir())

        return self._config

    def __getitem__(self, item):
        """
        Get a configuration value using dictionary key lookup syntax.

        Allows retrieving configurations using `SETTINGS[key]`.

        :param item: The configuration key to look up.
        :return: The resolved configuration value.
        """
        return self.config[item]


SETTINGS = Settings()
