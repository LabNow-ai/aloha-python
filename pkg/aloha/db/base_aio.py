"""
Async password vault manager for async database operations.
"""

from ..encrypt import vault
from ..logger import LOG
from ..settings import SETTINGS


class PasswordVault:
    """
    Async password vault manager that provides access to password vault implementations.

    Caches vault instances for performance.
    """

    _dict_cache_vault = {}

    @staticmethod
    async def get_vault(vault_type: str | None = None, vault_config: dict | None = None, **kwargs) -> vault.BaseVault:
        """
        Get a password vault instance (async version).

        Supports multiple vault types:
        - 'plain' or 'aes': AES-based vault (default fallback)
        - 'cyberark': CyberArk vault
        - Other/None: Dummy vault (plain text)

        :param vault_type: Type of vault to use (overrides config)
        :param vault_config: Vault configuration dictionary
        :param args: Additional arguments
        :param kwargs: Additional keyword arguments
        :return: Vault instance implementing BaseVault interface
        :raises RuntimeError: If CyberArk vault is requested but config is missing
        """
        encryption_method = vault_type or SETTINGS.config.get("PASSWORD_ENCRYPTION")
        LOG.debug("Using password vault (async): %s", encryption_method)

        cache_key = "%s:%s" % (encryption_method, str(vault_config))
        if cache_key not in PasswordVault._dict_cache_vault:
            if encryption_method in ("plain", "aes") or encryption_method is True:
                v = vault.AesVault(**(vault_config or {}))
            elif encryption_method == "cyberark":
                config_cyberark = vault_config or SETTINGS.config.get("CYBERARK_CONFIG")
                if config_cyberark is None:
                    raise RuntimeError("Missing [CYBERARK_CONFIG] in config!")
                v = vault.CyberArkVault(**config_cyberark)
            else:
                msg = "Using plain password vault as unknown value of PASSWORD_ENCRYPTION=%s in config." % encryption_method
                LOG.info(msg)
                v = vault.DummyVault(**(vault_config or {}))
            PasswordVault._dict_cache_vault[cache_key] = v

        return PasswordVault._dict_cache_vault[cache_key]

    @staticmethod
    def get_vault_sync(vault_type: str | None = None, vault_config: dict | None = None, **kwargs) -> vault.BaseVault:
        """
        Get a password vault instance (sync version for backward compatibility).

        :param vault_type: Type of vault to use (overrides config)
        :param vault_config: Vault configuration dictionary
        :param args: Additional arguments
        :param kwargs: Additional keyword arguments
        :return: Vault instance implementing BaseVault interface
        """
        encryption_method = vault_type or SETTINGS.config.get("PASSWORD_ENCRYPTION")
        LOG.debug("Using password vault (sync): %s", encryption_method)

        cache_key = "%s:%s" % (encryption_method, str(vault_config))
        if cache_key not in PasswordVault._dict_cache_vault:
            if encryption_method in ("plain", "aes") or encryption_method is True:
                v = vault.AesVault(**(vault_config or {}))
            elif encryption_method == "cyberark":
                config_cyberark = vault_config or SETTINGS.config.get("CYBERARK_CONFIG")
                if config_cyberark is None:
                    raise RuntimeError("Missing [CYBERARK_CONFIG] in config!")
                v = vault.CyberArkVault(**config_cyberark)
            else:
                msg = "Using plain password vault as unknown value of PASSWORD_ENCRYPTION=%s in config." % encryption_method
                LOG.info(msg)
                v = vault.DummyVault(**(vault_config or {}))
            PasswordVault._dict_cache_vault[cache_key] = v

        return PasswordVault._dict_cache_vault[cache_key]