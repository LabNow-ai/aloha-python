from typing import ClassVar

from ..encrypt import vault
from ..logger import LOG
from ..settings import SETTINGS


class PasswordVault:
    """
    Password vault manager that provides access to password vault implementations.

    Caches vault instances for performance.
    """

    _dict_cache_vault: ClassVar[dict] = {}

    @staticmethod
    def get_vault(vault_type: str | None = None, vault_config: dict | None = None, **kwargs) -> vault.BaseVault:
        """
        Get a password vault instance.

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
        LOG.debug("Using password vault: %s", encryption_method)  # nosemgrep

        cache_key = f"{encryption_method}:{vault_config!s}"
        if cache_key not in PasswordVault._dict_cache_vault:
            if encryption_method in ("plain", "aes") or encryption_method is True:
                v = vault.AesVault(**(vault_config or {}))
            elif encryption_method == "cyberark":
                config_cyberark = vault_config or SETTINGS.config.get("CYBERARK_CONFIG")
                if config_cyberark is None:
                    raise RuntimeError("Missing [CYBERARK_CONFIG] in config!")
                v = vault.CyberArkVault(**config_cyberark)
            else:
                msg = f"Using plain password vault as unknown value of PASSWORD_ENCRYPTION={encryption_method} in config."
                LOG.info(msg)  # nosemgrep
                v = vault.DummyVault(**(vault_config or {}))
            PasswordVault._dict_cache_vault[cache_key] = v

        return PasswordVault._dict_cache_vault[cache_key]


def main():
    """
    Command-line tool to decrypt passwords from config.

    Usage: python -m aloha.db.base <config_key>
    """
    import sys

    config_key = sys.argv[-1]
    LOG.debug(f"Getting pwd for deploy key [deploy.{config_key}]")
    try:
        db_config = SETTINGS.config["deploy"][config_key]
        password_vault = PasswordVault.get_vault()
        p = password_vault.get_password(db_config.get("password"))
        LOG.debug(f"Decrypted PWD: {p}")
    except KeyError:
        LOG.error(f"Please make sure config key [deploy.{config_key}] exists!")
