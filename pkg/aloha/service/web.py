"""FastAPI web application assembly for aloha services."""

import logging
import os
import re
from typing import Any, List, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from ..logger import LOG
from ..logger.logger import setup_logger
from ..settings import SETTINGS

setup_logger(
    logging.getLogger("uvicorn.access"),
    formatter_str="A> %(asctime)s> %(message)s",
    module="access_%s" % (SETTINGS.config.get("APP_MODULE") or os.environ.get("APP_MODULE", "default")),
)


def _load_routes(name: str) -> List[Tuple[str, Any]]:
    """Load routes from a service module.

    Returns list of (url_pattern, handler_class) tuples.
    """
    mod = __import__(name, fromlist=["default_handlers"])
    routes = []
    seen = set()
    for url, handler in mod.default_handlers:
        if not url.startswith("/"):
            url = "/" + url
        # Deduplicate routes
        key = (url, handler)
        if key not in seen:
            seen.add(key)
            routes.append((url, handler))
    return routes


class FastAPIApplication:
    """FastAPI application that loads routes from configured service modules."""

    def __init__(self, config: dict = None, **kwargs):
        """Create the FastAPI application and its routes."""
        self.config = config or {}
        self.app = FastAPI(title="Aloha Service", version="1.0.0", **kwargs)
        self._setup_default_handler()
        self._setup_routes()

    def _setup_default_handler(self):
        """Register a custom default 404 handler when configured."""
        handler_class = self.config.get("default_handler_class")
        if not handler_class:
            return

        @self.app.exception_handler(404)
        async def _default_404_handler(request: Request, exc: Exception):
            handler = handler_class(request=request)
            if hasattr(handler, "handle") and callable(handler.handle):
                return await handler.handle(request)
            if hasattr(handler, "__call__") and callable(handler):
                return await handler(request)
            if hasattr(handler, "response") and callable(handler.response):
                return await handler.response()
            return JSONResponse(
                {"code": 404, "message": ["Not Found"], "data": None},
                status_code=404,
            )

    def _setup_routes(self):
        """Setup routes from configured service modules."""
        settings = self.config.get("service", {})
        modules = settings.get("modules", [])

        for m in modules:
            routes = _load_routes(m)
            for url, handler_class in routes:
                self._register_handler(url, handler_class)
                s_log_msg = "Loaded API module %-50s" % url
                if LOG.level < logging.INFO:
                    s_log_msg += "\t from class %s" % str(handler_class)
                LOG.info(s_log_msg)

    def _register_handler(self, url: str, handler_class):
        """Register a handler class as FastAPI routes based on its methods."""
        has_get = hasattr(handler_class, "get") and callable(getattr(handler_class, "get"))
        has_post = hasattr(handler_class, "post") and callable(getattr(handler_class, "post"))

        # Determine path pattern for FastAPI
        fastapi_url, path_params = self._convert_url_pattern(url)

        # Store path_params in closure for use in handlers
        _has_path_params = path_params
        _original_url = url

        # Register POST handler if handler class has post method
        if has_post:

            async def post_handler(request: Request):
                kwargs = {}
                handler = handler_class()
                handler._request = request

                # Extract path params from URL
                if _has_path_params:
                    match_path = self._match_path(_original_url, str(request.url.path))
                    if match_path:
                        kwargs.update(match_path)

                try:
                    body = await request.json()
                except Exception:
                    body = {}

                kwargs.update(body)

                try:
                    result = await handler.post(**kwargs)
                    # If handler returns a Response object, return it directly
                    if isinstance(result, Response):
                        return result
                    # Otherwise, wrap in standard response format
                    resp = dict(code=5200, message=["success"])
                    if isinstance(result, dict):
                        resp["data"] = result.get("data", result)
                    else:
                        resp["data"] = result
                    return JSONResponse(resp)
                except Exception as e:
                    if handler.LOG.level == logging.DEBUG:
                        handler.LOG.error(e, exc_info=True)
                    return JSONResponse({"code": 5201, "message": [repr(e)]}, status_code=500)

            self.app.post(fastapi_url)(post_handler)

        # Register GET handler if handler class has get method
        if has_get:

            async def get_handler(request: Request):
                kwargs = {}
                handler = handler_class()
                handler._request = request

                # Extract path params from URL
                if _has_path_params:
                    match_path = self._match_path(_original_url, str(request.url.path))
                    if match_path:
                        kwargs.update(match_path)

                kwargs.update(dict(request.query_params))

                try:
                    result = await handler.get(**kwargs)
                    # If handler returns a Response object, return it directly
                    if isinstance(result, Response):
                        return result
                    # Otherwise, wrap in standard response format
                    resp = dict(code=5200, message=["success"])
                    if isinstance(result, dict):
                        resp["data"] = result.get("data", result)
                    else:
                        resp["data"] = result
                    return JSONResponse(resp)
                except Exception as e:
                    if handler.LOG.level == logging.DEBUG:
                        handler.LOG.error(e, exc_info=True)
                    return JSONResponse({"code": 5201, "message": [repr(e)]}, status_code=500)

            self.app.get(fastapi_url)(get_handler)

        # Default: register a POST handler using response() method
        if not has_post and not has_get:

            async def default_handler(request: Request):
                kwargs = {}
                handler = handler_class()
                handler._request = request

                # Extract path params from URL
                if _has_path_params:
                    match_path = self._match_path(_original_url, str(request.url.path))
                    if match_path:
                        kwargs.update(match_path)

                try:
                    body = await request.json()
                except Exception:
                    body = {}

                kwargs.update(body)

                resp = dict(code=5200, message=["success"])
                try:
                    result = handler.response(**kwargs)
                    resp["data"] = result
                except Exception as e:
                    if handler.LOG.level == logging.DEBUG:
                        handler.LOG.error(e, exc_info=True)
                    return JSONResponse({"code": 5201, "message": [repr(e)]}, status_code=500)

                return JSONResponse(resp)

            self.app.post(fastapi_url)(default_handler)

    def _convert_url_pattern(self, tornado_pattern: str) -> Tuple[str, bool]:
        """Convert Tornado URL pattern to FastAPI pattern.

        Tornado: /api/common/sys_info/(.*)
        FastAPI: /api/common/sys_info/{path_param}
        """
        has_capture = "(.*)" in tornado_pattern
        fastapi_pattern = tornado_pattern.replace("(.*)", "{path_param:path}")
        return fastapi_pattern, has_capture

    def _match_path(self, tornado_pattern: str, path: str) -> dict:
        """Match a path against a Tornado pattern and extract params."""
        # Convert Tornado pattern to regex
        pattern = tornado_pattern
        pattern = pattern.replace("(.*)", r"(?P<path_param>.*)")
        pattern = "^" + pattern + "$"

        match = re.match(pattern, path)
        if match:
            return match.groupdict()
        return {}

    def get_port(self) -> int:
        """Get the configured port."""
        service_settings = self.config.get("service", {})
        port = service_settings.get("port") or int(os.environ.get("PORT_SVC", 8000))
        port = int(os.environ.get("PORT", port))
        return port

    def get_workers(self) -> int:
        """Get the configured number of workers."""
        service_settings = self.config.get("service", {})
        return int(service_settings.get("num_process") or 1)


# Backward compatibility alias
WebApplication = FastAPIApplication
