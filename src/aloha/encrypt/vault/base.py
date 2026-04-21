import abc
from urllib.parse import quote_plus as urlquote


class BaseVault(abc.ABC):
    """
    Abstract base class for password vault implementations.

    Defines the interface for password vaults that can decrypt passwords.
    """

    @abc.abstractmethod
    def decrypt_password(self, *args, **kwargs):
        """
        Decrypt a password.

        :param args: Additional arguments
        :param kwargs: Additional keyword arguments, should contain 'password'
        :return: Decrypted password
        """
        return kwargs.get("password")

    def get_password(self, password, *args, **kwargs):
        """
        Get a password, optionally URL-encoded.

        :param password: Password or dict containing password
        :param args: Additional arguments
        :param kwargs: Additional keyword arguments, can include 'url_encode'
        :return: Password, optionally URL-encoded
        """
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
    """
    Dummy vault implementation that returns passwords as-is.

    No actual encryption/decryption is performed.
    """

    def decrypt_password(self, *args, **kwargs):
        """
        Return password without decryption.

        :param args: Additional arguments
        :param kwargs: Additional keyword arguments, should contain 'password'
        :return: Original password
        """
        return kwargs.get("password")


def main():
    """
    Test function for DummyVault.
    """
    vault = DummyVault()
    ret = vault.get_password(None, url_quote=True)
    # print(ret)
    return ret
