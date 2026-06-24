"""FastAPI middleware and dependencies with permissive CORS defaults."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class CORSResponse(JSONResponse):
    """JSON response with permissive CORS headers for simple APIs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        await super().__call__(scope, receive, send)


def add_cors_headers(response: Response) -> None:
    """Add permissive CORS headers to a response."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "1000"
    response.headers["Content-Type"] = "application/json; charset=UTF-8"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = (
        "authorization, Authorization, Content-Type,"
        "Access-Control-Allow-Origin, Access-Control-Allow-Headers,"
        "X-Requested-By, Access-Control-Allow-Methods"
    )


class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware that adds permissive CORS headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        add_cors_headers(response)
        return response
