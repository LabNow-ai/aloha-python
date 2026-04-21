from .config import hocon, paths


class Settings:
    """
    Global settings management class for aloha.

    Manages configuration loading and provides access to common directories.
    """

    def __init__(self):
        self._config = None

    @property
    def resource_dir(self):
        """
        Get the resource directory path.

        :return: Resource directory path
        """
        return paths.get_resource_dir()

    @property
    def config_dir(self):
        """
        Get the configuration directory path.

        :return: Config directory path
        """
        return paths.get_config_dir()

    @property
    def config(self):
        """
        Get the global configuration object.

        Lazily loads configuration from HOCON files on first access.

        :return: Configuration object
        """
        if self._config is None:
            config_files = paths.get_config_files()  # by default, use the `main.conf` file in the config_dir
            self._config = hocon.load_config_from_hocon_files(config_files, base_dir=paths.get_config_dir())

        return self._config

    def __getitem__(self, item):
        """
        Get a configuration value by key.

        :param item: Configuration key
        :return: Configuration value
        """
        return self.config[item]


SETTINGS = Settings()
