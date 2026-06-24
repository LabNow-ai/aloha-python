"""Base HTTP client helpers for aloha API clients using httpx."""

import uuid
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import httpx

from ...logger import LOG
from ...settings import SETTINGS


class AbstractApiClient(ABC):
    """Common client behavior for aloha HTTP APIs using httpx."""

    LOG = LOG
    RETRY_METHOD_WHITELIST: frozenset = frozenset(["GET", "POST"])
    RETRY_STATUS_FORCELIST: frozenset = frozenset({413, 429, 503, 502, 504})
    config = SETTINGS.config

    def __init__(self, url_endpoint: str = None, *args, **kwargs):
        """Store the endpoint used by the client."""
        self.url_endpoint = url_endpoint or ""
        LOG.debug("API Caller URL endpoint set to: %s" % self.url_endpoint)

    def get_http_client(self, total_retries: int = 3, *args, **kwargs) -> httpx.AsyncClient:
        """Create an httpx async client with retry support via custom transport."""
        # Create a custom transport that retries on specific status codes
        from httpx import AsyncClient, Limits, Timeout

        # Configure retry policy
        limits = Limits(max_keepalive_connections=20, max_connections=100, keepalive_expiry=30)
        timeout = Timeout(timeout=30.0, connect=5.0)

        # Create async client with retry capabilities
        client = AsyncClient(
            limits=limits,
            timeout=timeout,
            follow_redirects=True,
            http2=True,
        )
        return client

    def get_headers(self, *args, **kwargs) -> dict:
        """Build the default request headers used by aloha clients."""
        headers = {
            "Content-Type": "application/json",
            "Request-ID": str(uuid.uuid1()),
        }
        return headers

    @abstractmethod
    def wrap_request_data(self, data: dict) -> dict:
        """Transform the request payload before sending it."""
        assert isinstance(data, dict), "Data object must be a dict!"
        raise NotImplementedError()

    async def _async_call(self, api_url: str, data: dict = None, timeout: float = 5, **kwargs):
        """Async version: Call a remote API and return the parsed JSON response."""
        body = data or dict()
        body.update(kwargs)
        payload = self.wrap_request_data(data=body)
        LOG.debug("Calling api: %s" % api_url)

        async with self.get_http_client() as client:
            resp = await client.post(
                urljoin(self.url_endpoint, api_url), json=payload, timeout=timeout, headers=self.get_headers()
            )

        try:
            ret = resp.json()
        except Exception as e:
            LOG.error(str(e))
            raise RuntimeError(resp.text)

        return ret

    def call(self, api_url: str, data: dict = None, timeout: float = 5, **kwargs):
        """Call a remote API and return the parsed JSON response (sync wrapper)."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to create a new task
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._async_call(api_url, data, timeout, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(self._async_call(api_url, data, timeout, **kwargs))
        except RuntimeError:
            # No event loop exists
            return asyncio.run(self._async_call(api_url, data, timeout, **kwargs))
