"""Version 0 JSON API helpers for FastAPI.

This module defines the simplest request/response protocol used by aloha:
request bodies are passed directly to the handler method and the response is
serialized as a JSON object with a `code` and `message` field.
"""

import json
import logging
from abc import ABC
from typing import Any, Optional, Dict

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from ..http import AbstractApiClient, AbstractApiHandler
from ..http.base_api_handler import AbstractApiHandler as BaseHandler

__all__ = ("APIHandler", "APICaller", "create_v0_router")


class APIHandler(BaseHandler, ABC):
    """Base handler for v0 JSON endpoints using FastAPI.

    Subclasses implement :meth:`response`, which receives parsed request data
    and returns a Python object that can be JSON-serialized.
    """

    MAP_ERROR_INFO = {"BAD_REQUEST": {"code": "5101", "message": ["Bad request: fail to parse body as JSON object!"]}}

    async def post(self, *args, **kwargs):
        """Parse the request body, call :meth:`response`, and return JSON."""
        req_body = self.request_body

        if req_body is not None:
            kwargs.update(req_body)

        resp = dict(code=5200, message=["success"])
        try:
            result = self.response(*args, **kwargs)
            resp["data"] = result
        except Exception as e:
            if self.LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({"code": 5201, "message": [repr(e)]})

        return self.finish(resp)

    async def get(self, *args, **kwargs):
        """Handle GET request (useful for some v0 endpoints)."""
        kwargs.update(self.request_param)
        resp = dict(code=5200, message=["success"])
        try:
            result = self.response(*args, **kwargs)
            resp["data"] = result
        except Exception as e:
            if self.LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({"code": 5201, "message": [repr(e)]})
        return self.finish(resp)


def create_v0_router(handler_class):
    """Create FastAPI routes for a v0 API handler class.
    
    Args:
        handler_class: A class inheriting from APIHandler
        
    Returns:
        A function that registers routes on a FastAPI app
    """
    from fastapi import APIRoute
    
    async def handle_post(request: Request, **kwargs):
        handler = handler_class()
        handler._request = request
        
        # Get body for POST
        try:
            body = await request.json()
        except:
            body = {}
        
        kwargs.update(body)
        resp = dict(code=5200, message=["success"])
        try:
            result = handler.response(**kwargs)
            resp["data"] = result
        except Exception as e:
            import logging
            if handler.LOG.level == logging.DEBUG:
                handler.LOG.error(e, exc_info=True)
            return JSONResponse({"code": 5201, "message": [repr(e)]}, status_code=500)
        
        return JSONResponse(resp)
    
    async def handle_get(request: Request, **kwargs):
        handler = handler_class()
        handler._request = request
        
        # Get query params for GET
        kwargs.update(dict(request.query_params))
        resp = dict(code=5200, message=["success"])
        try:
            result = handler.response(**kwargs)
            resp["data"] = result
        except Exception as e:
            import logging
            if handler.LOG.level == logging.DEBUG:
                handler.LOG.error(e, exc_info=True)
            return JSONResponse({"code": 5201, "message": [repr(e)]}, status_code=500)
        
        return JSONResponse(resp)
    
    return handle_post, handle_get


class APICaller(AbstractApiClient):
    """Client helper for v0 endpoints.

    The payload is sent as-is, without signature wrapping or token exchange.
    """

    def wrap_request_data(self, data: dict) -> dict:
        """Return the request body unchanged."""
        assert isinstance(data, dict), "Data object must be a dict!"
        return data
