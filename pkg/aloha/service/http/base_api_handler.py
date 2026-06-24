"""Base FastAPI dependencies and request helpers for aloha services."""

import asyncio
import json
import logging
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request, Response

from ...logger import LOG


class AbstractApiHandler(ABC):
    """Shared request parsing and response helpers for JSON APIs.

    This is a base class that provides utility methods for API handlers.
    Subclasses should inherit from this and implement the response() method.
    """

    LOG = LOG
    MAP_ERROR_INFO: dict = {"BAD_REQUEST": {"code": "5101", "message": ["Bad request: fail to parse body as JSON object!"]}}

    def __init__(self):
        """Initialize request state used by subclasses."""
        self.api_args: Optional[tuple] = None
        self.api_kwargs: Optional[dict] = None
        self._request: Optional[Request] = None
        self._response: Optional[Response] = None

    def response(self, *args, **kwargs) -> dict:
        """Subclasses must implement the business response."""
        raise NotImplementedError()

    @property
    def request_header_content_type(self) -> str:
        """Return the request content type with a JSON default."""
        if self._request is None:
            return "application/json; charset=utf-8"
        return self._request.headers.get("Content-Type", "application/json; charset=utf-8")

    @property
    def request_id(self) -> str:
        """Return or create a request identifier for tracing."""
        if self._request is None:
            return datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        request_id = self._request.headers.get("Request-ID")
        if request_id is None:
            request_id = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return request_id

    @property
    def request_body(self) -> Optional[dict]:
        """Parse the request body as JSON or multipart form data."""
        content_type: str = self.request_header_content_type

        if self._request is None:
            return {}

        # For multipart/form-data, use request_param logic
        if content_type.startswith("multipart/form-data"):
            return self.request_param

        try:
            body = asyncio.get_event_loop().run_until_complete(self._request.body())
            body_str = body.decode("utf-8")
            if body_str:
                return json.loads(body_str)
            return {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self.MAP_ERROR_INFO["BAD_REQUEST"]

    @property
    def request_param(self) -> dict:
        """Parse query/body arguments into a JSON-friendly dict."""
        ret: dict = {}
        if self._request is None:
            return ret

        # Parse query parameters
        for k, v in self._request.query_params.items():
            try:
                value = json.loads(v)
            except json.JSONDecodeError:
                value = v
            ret[k] = value

        return ret

    def get_request_files(self) -> Dict[str, list]:
        """Get uploaded files from multipart form data."""
        if self._request is None:
            return {}
        return self._request._form

    def finish(self, data: Any, status_code: int = 200) -> Response:
        """Create a JSON response with proper content type."""
        if isinstance(data, dict):
            content = json.dumps(data, ensure_ascii=False, default=str, separators=(",", ":"))
        elif isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, ensure_ascii=False, default=str, separators=(",", ":"))
        return Response(content=content, status_code=status_code, media_type="application/json")

    def set_header(self, key: str, value: str) -> None:
        """Set a response header (no-op in base class, overridden in FastAPI route)."""
        pass

    def set_status(self, status_code: int, reason: str = None) -> None:
        """Set the response status code (no-op in base class)."""
        pass

    async def _handle_request(self, request: Request, *args, **kwargs) -> Response:
        """Process the request and return a response."""
        self._request = request
        self.api_args = args
        self.api_kwargs = kwargs

        try:
            result = self.response(*args, **kwargs)
            if isinstance(result, (dict, list)):
                return self.finish(result)
            return result
        except Exception as e:
            if self.LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            msgs = ["An internal error has occurred!", repr(e)]
            return self.finish({"code": 5201, "message": msgs}, status_code=500)


def create_handler_route(handler_class):
    """Create a FastAPI route wrapper for a handler class."""

    class HandlerRoute(APIRouter):
        async def _execute_handler(self, request: Request, **kwargs) -> Response:
            handler = handler_class()
            return await handler._handle_request(request, **kwargs)

    return HandlerRoute
