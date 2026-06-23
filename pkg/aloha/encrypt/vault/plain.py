"""AES-backed password vault helpers."""

import pyhocon

from ...encrypt.aes import AesEncryptor
from .base import BaseVault


def _is_empty_str(s):
    """Return True when the value should be treated as empty."""
    return s is None or isinstance(s, pyhocon.config_tree.NoneValue) or s == "None" or s == ""


class AesVault(AesEncryptor, BaseVault):
    """Password vault that stores encrypted secrets with AES."""

    def __init__(self, key: str | None = None):
        """Initialize the vault with an optional AES key."""
        super().__init__(key)

    def decrypt_password(self, pwd):
        """Decrypt the stored password and return plain text."""
        if _is_empty_str(pwd):
            return None
        return self.decrypt(pwd)


def main():
    """Small self-test for the AES vault."""
    vault = AesVault()
    pwd = vault.get_password(None, url_quote=True)
    # print(pwd)
    return pwd
