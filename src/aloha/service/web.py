"""Tornado web application assembly for aloha services."""

import logging
import os

from tornado import httpserver, web
from tornado.routing import HostMatches

from ..logger import LOG
from ..logger.logger import setup_logger
from ..settings import SETTINGS

setup_logger(
    logging.getLogger("tornado.access"),
    formatter_str="A> %(asctime)s> %(message)s",
    module="access_%s" % (SETTINGS.config.get("APP_MODULE") or os.environ.get("APP_MODULE", "default")),
)


def _load_handlers(name):
    """Load `(URL pattern, handler)` tuples from a service module."""
    mod = __import__(name, fromlist=["default_handlers"])
    handlers = []
    for url, handler in mod.default_handlers:
        if not url.startswith("/"):
            url = "/" + url
        handlers.append((url, handler))
    return handlers


class WebApplication(web.Application):
    """Tornado application that loads handlers from configured service modules."""

    def __init__(self, config: dict, *args, **kwargs):
        """Create the application and its HTTP server."""
        handlers = self.init_handlers(config)
        super().__init__(handlers=handlers, **config)
        self.http_server = httpserver.HTTPServer(self)

    @staticmethod
    def init_handlers(config: dict):
        """Collect and normalize all handlers from configured service modules."""
        settings = config.get("service", {})
        modules = settings.get("modules", [])
        handlers = []
        for m in modules:
            _handlers = _load_handlers(m)
            for h in _handlers:
                (url, class_handler) = h
                handlers.append(h)
                s_log_msg = "Loaded API module %-50s" % url
                if LOG.level < logging.INFO:  # more verbose information
                    s_log_msg += "\t from class %s" % str(class_handler)
                LOG.info(s_log_msg)

        return [(HostMatches("(.*)"), handlers)]

    def start(self):
        """Bind the configured port and start the HTTP server."""
        service_settings = self.settings.get("service", {})

        port = service_settings.get("port") or int(os.environ.get("PORT_SVC", 80))
        port = os.environ.get("port", port)  # if overwrite port in param

        num_process = int(service_settings.get("num_process") or 0)
        LOG.info("Starting service with [%s] process at port [%s]...", num_process or "undefined", port)
        self.http_server.bind(port)
        self.http_server.start(num_processes=num_process)
