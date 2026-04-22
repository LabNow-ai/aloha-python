"""CyberArk-based password vault helpers."""

import hashlib
from binascii import a2b_hex
from urllib.parse import quote_plus as urlquote

import requests
from Crypto.Cipher import AES
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from ...encrypt.aes import AesEncryptor
from ...logger import LOG
from .base import BaseVault

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
if hasattr(requests.packages.urllib3.util.ssl_, "DEFAULT_CIPHERS"):
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGHT:!DH:!aNULL"


class CyberArkVault(BaseVault, AesEncryptor):
    """Fetch and decrypt passwords from a CyberArk-compatible endpoint."""

    _cached: dict = {}

    def __init__(self, url: str, app_id: str, key: str | None = None, safe: str = "AIM_ELIS_LAS", folder: str = "root"):
        """Initialize the vault with the CyberArk endpoint and credentials."""
        super().__init__(key)
        self.key, self.url, self.app_id, self.safe, self.folder = key, url, app_id, safe, folder

    @staticmethod
    def get_sign(appid, keyvalue):
        """Generate the CyberArk request signature."""
        hash_string = appid + "&" + keyvalue
        sha256 = hashlib.sha256()
        sha256.update(hash_string.encode("utf8"))
        return sha256.hexdigest()

    def decrypt_password(self, text):
        """Decrypt the AES-encrypted password returned by CyberArk."""
        if text is None:
            return None

        cryptor = AES.new(self.key_aes, AES.MODE_ECB)
        s = cryptor.decrypt(a2b_hex(text.encode()))
        s = s[0 : -s[-1]]
        return s.decode()

    def get_cyberark_password(self, object: str | None = None, **kwargs):
        """Request and decrypt a password from the CyberArk endpoint."""
        assert isinstance(object, str)
        kwargs.update({"object": object})

        app_id = kwargs.get("app_id", self.app_id)
        data = {
            "appId": app_id,
            "safe": kwargs.get("safe", self.safe),
            "folder": kwargs.get("folder", self.folder),
            "object": kwargs.get("object", object),
            "sign": self.get_sign(app_id, self.key),
        }

        retry = 5
        while retry:
            try:
                LOG.debug("POST CyberArk: %s with data: %s", self.url, data)
                resp = requests.post(
                    self.url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    # verify=False,
                )
                tmp = resp.json()
                if resp.status_code == 200 and int(tmp["code"]) == 200:
                    LOG.debug("Got data from CyberArk: %s", tmp)
                    return self.decrypt_password(tmp["password"])
                else:
                    raise RuntimeError(resp.text)
            except Exception as e:
                retry -= 1
                if retry == 0:
                    raise e
                else:
                    LOG.error("CyberArk request error: {}".format(e))
        return None

    def get_password(self, object=None, **kwargs):
        """Return a cached CyberArk password, optionally URL-encoded."""
        key_for_cache = "{app_id};{safe};{folder};{key};{object}".format(
            app_id=self.app_id, safe=self.safe, folder=self.folder, key=self.key, object=object
        )
        if key_for_cache not in self._cached:
            kwargs.update(object if isinstance(object, dict) else {"object": object})
            url_quote = kwargs.get("url_encode", True)

            pwd = self.get_cyberark_password(**kwargs)
            if url_quote:  # quote/escape password by default
                pwd = urlquote(pwd)
            self._cached[key_for_cache] = pwd
        else:
            LOG.debug("Using cached CyberArk key: %s" % key_for_cache)

        return self._cached[key_for_cache]


def main():
    """Small self-test scaffold for the CyberArk vault."""
    cfg_cyberark = dict(
        url="https://localhost/pidms/rest/pwd/getPassword",  # to fill properly
        app_id="",
        safe="",
        folder="root",
        key="",
    )
    # from ...settings import SETTINGS
    # cfg_cyberark = SETTINGS.config['CYBERARK_CONFIG']
    vault = CyberArkVault(**cfg_cyberark)
    pwd = vault.get_password({"object": "PG_"})
    assert pwd is not None
    # print(pwd)
