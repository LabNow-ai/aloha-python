"""Service application bootstrap utilities."""

__all__ = ('Application',)

import asyncio

from ..logger import LOG

try:
    import uvloop
    from tornado.platform.asyncio import AsyncIOMainLoop

    LOG.info('Using uvloop == %s for service event loop...' % uvloop.__version__)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    AsyncIOMainLoop().install()
except ImportError:
    LOG.info('[uvloop] NOT installed, fallback to asyncio loop! Consider `pip install uvloop`!')

from tornado.options import options

from ..settings import SETTINGS
from .web import WebApplication


class Application:
    """Bootstrap and run an aloha web service."""

    def __init__(self, *args, **kwargs):
        """Create the service application wrapper."""
        options['log_file_prefix'] = 'access.log'
        settings = dict(SETTINGS.config)
        self.web_app = WebApplication(settings)

    def start(self):
        """Start the web app and run the asyncio event loop."""
        try:
            self.web_app.start()
            event_loop = asyncio.get_event_loop()
            if event_loop.is_running():
                # notice: the event loop MUST NOT be initialized before web_app starts (as it may fork process)
                # ref: https://github.com/tornadoweb/tornado/issues/2426#issuecomment-400895086
                raise RuntimeError('Event loop already running before WebApp starts!')
            else:
                event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise e
        finally:
            pass

    def stop(self):
        """Stop the event loop if it is currently running."""
        event_loop = asyncio.get_event_loop()
        if event_loop.is_running():
            event_loop.stop()
