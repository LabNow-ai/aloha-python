"""Version 2 token-based JSON API helpers for FastAPI.

Version 2 uses an access token in the request header and a request-id header
for tracing. It keeps the same request/response shape as the earlier API
generations while adding header-based authentication.
"""

import json
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from ...encrypt import jwt
from ...logger import LOG
from ...settings import SETTINGS
from ..http import AbstractApiClient
from ..http.base_api_handler import AbstractApiHandler as BaseHandler

__all__ = ("APIHandler", "APICaller", "create_v2_router", "verify_v2_token")


class APIHandler(BaseHandler, ABC):
    """Token-authenticated API handler for v2 endpoints."""

    async def prepare(self) -> Optional[Response]:
        """Validate the access token before handling the request."""
        access_token = self._request.headers.get("Access-Token")
        if access_token is None:
            return self.finish({"msg": "Invalid Access-Token in request header!"})
        else:
            secret_key = SETTINGS.config["APP_SECRET_KEY"]
            options = {"verify_exp": False}
            access_token = jwt.decode(secret_key, access_token, options=options)
            if not isinstance(access_token, dict):
                self.LOG.error("Invalid Access-Token found in request for [%s]: %s" % (str(self._request.url), access_token))
                return self.finish({"msg": access_token})
        return None

    async def post(self, *args, **kwargs):
        """Handle POST requests with JSON request bodies."""
        body_arguments = self.request_body
        kwargs.update(body_arguments)
        try:
            if self.LOG.level == logging.DEBUG:
                s_kwargs = json.dumps(kwargs, ensure_ascii=False)
                self.LOG.debug("POST Request [%s]: %s" % (self.request_id, s_kwargs[:1000]))
            self.api_args, self.api_kwargs = args or (), kwargs or {}
            resp = self.response(*self.api_args, **self.api_kwargs)
        except Exception as e:
            self.LOG.error(e, exc_info=True)
            self.LOG.info("POST Request [%s]: %s" % (self.request_id, self._request._body))
            return self.finish({"status": "error", "message": [str(e)]})

        return self.finish(resp)

    async def get(self, *args, **kwargs):
        """Handle GET requests with query-string arguments."""
        query_arguments = self.request_param
        kwargs.update(query_arguments)
        try:
            self.LOG.debug("GET Request [%s]: %s" % (self.request_id, kwargs))
            self.api_args, self.api_kwargs = args or (), kwargs or {}
            resp = self.response(*self.api_args, **self.api_kwargs)
        except Exception as e:
            self.LOG.error(e, exc_info=True)
            self.LOG.info("GET Request [%s]: %s" % (self.request_id, kwargs))
            return self.finish({"status": "error", "message": ["An internal error has occurred!"]})

        return self.finish(resp)


def verify_v2_token(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency to verify v2 access token.

    Returns the decoded token payload if valid, otherwise raises HTTPException.
    """

    access_token = request.headers.get("Access-Token")
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access-Token in request header!")

    secret_key = SETTINGS.config.get("APP_SECRET_KEY")
    if not secret_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="APP_SECRET_KEY not configured!")

    options = {"verify_exp": False}
    try:
        payload = jwt.decode(secret_key, access_token, options=options)
        if not isinstance(payload, dict):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access-Token!")
        return payload
    except Exception as e:
        LOG.error(str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access-Token!")


def create_v2_router(handler_class):
    """Create FastAPI routes for a v2 API handler class with JWT token validation.

    Args:
        handler_class: A class inheriting from APIHandler

    Returns:
        Tuple of (handle_post, handle_get) functions for the routes
    """

    async def handle_post(request: Request, token_payload: Dict = Depends(verify_v2_token)):
        handler = handler_class()
        handler._request = request

        try:
            body = await request.json()
        except Exception:
            body = {}

        kwargs = body
        try:
            if handler.LOG.level == logging.DEBUG:
                s_kwargs = json.dumps(kwargs, ensure_ascii=False)
                handler.LOG.debug("POST Request [%s]: %s" % (handler.request_id, s_kwargs[:1000]))

            resp = handler.response(**kwargs)
        except Exception as e:
            handler.LOG.error(e, exc_info=True)
            msgs = ["An internal error has occurred.", str(e)]
            return JSONResponse({"status": "error", "message": msgs}, status_code=500)

        return handler.finish(resp)

    async def handle_get(request: Request, token_payload: Dict = Depends(verify_v2_token)):
        handler = handler_class()
        handler._request = request

        kwargs = dict(request.query_params)
        try:
            handler.LOG.debug("GET Request [%s]: %s" % (handler.request_id, kwargs))
            resp = handler.response(**kwargs)
        except Exception as e:
            handler.LOG.error(e, exc_info=True)
            msgs = ["An internal error has occurred.", repr(e)]
            return JSONResponse({"status": "error", "message": msgs}, status_code=500)

        return handler.finish(resp)

    return handle_post, handle_get


class APICaller(AbstractApiClient):
    """Client helper that adds v2 access-token headers automatically."""

    APP_ID_KEYS = AbstractApiClient.config.get("APP_ID_KEYS", {})
    APP_SECRET_KEY = AbstractApiClient.config.get("APP_SECRET_KEY")

    def wrap_request_data(self, data: dict) -> dict:
        """Return the request body unchanged."""
        assert isinstance(data, dict), "Data object must be a dict!"
        return data

    def get_headers(self, app_id: str = None, app_key: str = None) -> dict:
        """Build the HTTP headers expected by v2 handlers."""
        if app_id is None:
            app_id = list(self.APP_ID_KEYS.keys())[0]

        expire_time = datetime.now() + timedelta(days=1)

        access_token = jwt.encode(secret_key=self.APP_SECRET_KEY, payload={"exp": int(expire_time.timestamp()), "aid": app_id})

        headers = super().get_headers()
        headers.update({"Access-Token": access_token})
        return headers
