"""Version 0 JSON API helpers.

This module defines the simplest request/response protocol used by aloha:
request bodies are passed directly to the handler method and the response is
serialized as a JSON object with a `code` and `message` field.
"""

import json
import logging
from abc import ABC

from ..http import AbstractApiClient, AbstractApiHandler

__all__ = ("APIHandler", "APICaller")


class APIHandler(AbstractApiHandler, ABC):
    """Base Tornado handler for v0 JSON endpoints.

    Subclasses implement :meth:`response`, which receives parsed request data
    and returns a Python object that can be JSON-serialized.
    """

    MAP_ERROR_INFO = {"BAD_REQUEST": {"code": "5101", "message": ["Bad request: fail to parse body as JSON object!"]}}

    async def post(self, *args, **kwargs):
        """Parse the request body, call :meth:`response`, and return JSON."""
        req_body = self.request_body

        if req_body is not None:  # body_arguments
            kwargs.update(req_body)

        resp = dict(code=5200, message=["success"])
        try:
            result = self.response(*args, **kwargs)  # this call may throw TypeError when argument missing
            resp["data"] = result
        except Exception as e:
            if self.LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({"code": 5201, "message": [repr(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(",", ":"))
        return self.finish(resp)


class APICaller(AbstractApiClient):
    """Client helper for v0 endpoints.

    The payload is sent as-is, without signature wrapping or token exchange.
    """

    def wrap_request_data(self, data: dict) -> dict:
        """Return the request body unchanged."""
        assert isinstance(data, dict), "Data object must be a dict!"
        return data
