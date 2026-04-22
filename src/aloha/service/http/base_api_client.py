"""Base HTTP client helpers for aloha API clients."""

import uuid
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter, Retry

from ...logger import LOG
from ...settings import SETTINGS


class AbstractApiClient(ABC):
    """Common client behavior for aloha HTTP APIs."""

    LOG = LOG
    RETRY_METHOD_WHITELIST: frozenset = frozenset(['GET', 'POST'])
    RETRY_STATUS_FORCELIST: frozenset = frozenset({413, 429, 503, 502, 504})
    config = SETTINGS.config

    def __init__(self, url_endpoint: str = None, *args, **kwargs):
        """Store the endpoint used by the client."""
        self.url_endpoint = url_endpoint or ''
        LOG.debug('API Caller URL endpoint set to: %s' % self.url_endpoint)

    @classmethod
    def get_request_session(cls, total_retries: int = 3, *args, **kwargs) -> requests.Session:
        """Create a requests session with retry support."""
        session = requests.Session()
        # https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry.DEFAULT_ALLOWED_METHODS
        retries = Retry(
            total=total_retries, backoff_factor=0.1, method_whitelist=cls.RETRY_METHOD_WHITELIST, status_forcelist=cls.RETRY_STATUS_FORCELIST
        )
        for prefix in ('http://', 'https://'):
            session.mount(prefix, HTTPAdapter(max_retries=retries))
        return session

    def get_headers(self, *args, **kwargs) -> dict:
        """Build the default request headers used by aloha clients."""
        headers = {
            'Content-Type': 'application/json',
            'Request-ID': str(uuid.uuid1()),
        }
        return headers

    @abstractmethod
    def wrap_request_data(self, data: dict) -> dict:
        """Transform the request payload before sending it."""
        assert isinstance(data, dict), "Data object must be a dict!"
        raise NotImplementedError()
        # return data

    def call(self, api_url: str, data: dict = None, timeout=5, **kwargs):
        """Call a remote API and return the parsed JSON response."""
        body = data or dict()
        body.update(kwargs)
        payload = self.wrap_request_data(data=body)
        LOG.debug('Calling api: %s' % api_url)
        session = self.get_request_session()
        resp = session.post(
            urljoin(self.url_endpoint, api_url), json=payload, timeout=timeout, headers=self.get_headers()
        )

        try:
            ret = resp.json()
        except Exception as e:
            LOG.error(str(e))
            raise RuntimeError(resp.text)

        return ret
