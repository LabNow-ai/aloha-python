"""Password vault abstraction used by database and service helpers."""

import abc
from urllib.parse import quote_plus as urlquote


class BaseVault(abc.ABC):
    """Abstract base class for password vault implementations."""

    @abc.abstractmethod
    def decrypt_password(self, *args, **kwargs):
        """Decrypt a password and return the plain-text value."""
        return kwargs.get("password")

    def get_password(self, password, *args, **kwargs):
        """Return a password, optionally URL-encoded."""
        kwargs.update(password if isinstance(password, dict) else {"password": password})
        url_quote = kwargs.get("url_encode", True)

        pwd = self.decrypt_password(*args, **kwargs)
        if pwd is None:
            return None

        if url_quote:
            return urlquote(pwd)
        else:
            return pwd


class DummyVault(BaseVault):
    """Vault implementation that returns passwords unchanged."""

    def decrypt_password(self, *args, **kwargs):
        """Return the original password without decryption."""
        return kwargs.get("password")


def main():
    """Small self-test for the dummy vault."""
    vault = DummyVault()
    ret = vault.get_password(None, url_quote=True)
    # print(ret)
    return ret
