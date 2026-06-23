"""Service application bootstrap utilities for FastAPI."""

import asyncio
import logging
import uvicorn

from ..logger import LOG

try:
    import uvloop
    LOG.info("Using uvloop == %s for service event loop..." % uvloop.__version__)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    LOG.info("[uvloop] NOT installed, fallback to asyncio loop! Consider `pip install uvloop`!")

from ..settings import SETTINGS
from .web import FastAPIApplication

__all__ = ("Application",)


class Application:
    """Bootstrap and run an aloha FastAPI web service."""

    def __init__(self, *args, **kwargs):
        """Create the service application wrapper."""
        settings = dict(SETTINGS.config)
        self.web_app = FastAPIApplication(settings)
        self._server = None

    def start(self):
        """Start the FastAPI app using uvicorn."""
        port = self.web_app.get_port()
        workers = self.web_app.get_workers()
        
        LOG.info("Starting FastAPI service at port [%s] with [%s] workers...", port, workers)
        
        try:
            # Configure uvicorn
            config = uvicorn.Config(
                app=self.web_app.app,
                host="0.0.0.0",
                port=port,
                workers=workers,
                log_level="info",
                access_log=True,
            )
            self._server = uvicorn.Server(config)
            
            # Run with uvloop if available
            try:
                import uvloop
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            except ImportError:
                pass
            
            asyncio.run(self._server.serve())
        except KeyboardInterrupt:
            LOG.info("Service interrupted by user")
        except Exception as e:
            LOG.error("Service error: %s", str(e))
            raise e

    def stop(self):
        """Stop the server if it is currently running."""
        if self._server is not None:
            self._server.should_exit = True
