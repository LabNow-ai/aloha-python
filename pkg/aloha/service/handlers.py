"""Default HTTP handlers for aloha services."""

from fastapi import Request
from fastapi.responses import JSONResponse


class DefaultHandler404:
    """Default 404 response handler for FastAPI services."""

    def __init__(self, request: Request | None = None, **kwargs):
        self.request = request
        self._request = request

    async def handle(self, request: Request | None = None):
        """Return a JSON response for unmatched routes."""
        _request = request or self.request
        del _request
        return JSONResponse(
            {"code": 404, "message": ["Not Found"], "data": None},
            status_code=404,
        )
