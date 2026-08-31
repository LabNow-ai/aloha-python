import json
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx2

from ...logger import LOG

try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json import JSONDecodeError


class OpenApiClient:
    """Simple HTTP client that acquires and caches an access token."""

    retry_method_whitelist = frozenset(["GET", "POST"])
    retry_status_forcelist = frozenset({413, 429, 503, 502, 504})

    def __init__(self, url_oauth_get_token: str, client_id: str, client_secret: str, grant_type: str = "client_credentials"):
        """Store OAuth-style client credentials and token endpoint."""
        self.url_oauth_get_token = url_oauth_get_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type

        self.expires_at = None
        self.access_token = None

    @classmethod
    def get_request_session(cls, total_retries: int = 10, *args, **kwargs) -> httpx2.Client:
        """Create an httpx2 client; retry policy is applied by ``_request``."""
        return httpx2.Client(*args, **kwargs)

    @classmethod
    def _request(cls, method: str, url: str, total_retries: int = 10, **kwargs):
        """Send a request with the former urllib3 retry policy."""
        if method.upper() not in cls.retry_method_whitelist:
            return cls.get_request_session().request(method, url, **kwargs)

        last_error = None
        for attempt in range(total_retries + 1):
            client = cls.get_request_session()
            try:
                response = client.request(method, url, **kwargs)
                if response.status_code not in cls.retry_status_forcelist or attempt == total_retries:
                    return response
            except httpx2.HTTPError as error:
                last_error = error
                if attempt == total_retries:
                    raise
            finally:
                client.close()
            time.sleep(0.1 * (2**attempt))

        if last_error is not None:
            raise last_error
        raise RuntimeError("HTTP request failed without a response")

    def get_access_token(self) -> str:
        """Fetch or refresh the cached access token."""
        now = datetime.now()

        if self.expires_at is None or self.expires_at > now:
            try:
                resp = self._request(
                    "POST",
                    self.url_oauth_get_token,
                    timeout=5,
                    json={"client_id": self.client_id, "client_secret": self.client_secret, "grant_type": self.grant_type},
                )

                data = resp.json()["data"]
                if data is None or "access_token" not in data:
                    raise RuntimeError("Fail to fetch OpenAPI token with result: %s" % resp.text)

                self.access_token = data["access_token"]

                expires_in = int(data["expires_in"])
                self.expires_at = datetime.now() + timedelta(minutes=expires_in - 1)
            except Exception as e:
                msg = "Exception acquiring ESG access token from [%s]: %s" % (self.url_oauth_get_token, str(e))
                LOG.error(msg)

        return self.access_token

    def _get_request_url(self, url: str):
        """Attach access token and request id to the target URL."""
        request_url = "{url}?access_token={access_token}&request_id={request_id}".format(
            url=url, access_token=self.get_access_token(), request_id=datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        )
        return request_url

    @staticmethod
    def _get_data_from_esg_response(resp) -> Optional[dict]:
        """Parse a JSON response and unwrap legacy ESG payloads."""
        try:
            return resp.json()
        except (json.JSONDecodeError, JSONDecodeError):  # simplejson may provide its own JSONDecodeError
            try:
                content = resp.text.replace('"data":"', '"data":').replace('}"}', "}}")
                data = json.loads(content)
                return data.get("data", {})
            except json.JSONDecodeError:
                msg = "Cannot parse ESG response: %s" % resp.text
                raise ValueError(msg)

    def post(self, url_api: str, body: dict, headers: dict = None, timeout: int = 5):
        """Send a POST request to the remote API."""
        url = self._get_request_url(url_api)
        LOG.debug("Calling ESG POST: %s" % url)
        try:
            resp = self._request("POST", url, headers=headers, json=body, timeout=timeout)
            return self._get_data_from_esg_response(resp)
        except Exception as e:
            LOG.error("Error calling ESG API POST [%s]: %s" % (url, str(e)))

    def get(self, url_api: str, body: dict, headers: dict = None, timeout: int = 5):
        """Send a GET request to the remote API."""
        url = self._get_request_url(url_api)
        LOG.debug("Calling ESG GET: %s" % url)
        try:
            resp = self._request("GET", url, headers=headers, json=body, timeout=timeout)
            return self._get_data_from_esg_response(resp)
        except Exception as e:
            LOG.error("Error calling ESG API GET [%s]: %s" % (url, str(e)))
