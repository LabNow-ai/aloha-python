"""Plain Tornado handler with permissive CORS defaults."""

from typing import Optional, Awaitable

from tornado import web


class PlainHttpHandler(web.RequestHandler):
    """Minimal handler that exposes JSON-friendly CORS headers."""

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """Accept streamed body chunks without additional processing."""
        pass

    def set_default_headers(self):
        """Enable permissive cross-origin access for simple APIs."""
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header(
            'Access-Control-Allow-Headers',
            'authorization, Authorization, Content-Type,'
            'Access-Control-Allow-Origin, Access-Control-Allow-Headers,'
            'X-Requested-By, Access-Control-Allow-Methods'
        )
