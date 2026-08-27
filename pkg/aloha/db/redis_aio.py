"""
Async Redis connection helpers.
"""

import redis.asyncio as redis
from packaging import version

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("RedisOperator",)


class RedisOperator:
    """Create async Redis connections with version-checked redis-py."""

    def __init__(self, config):
        """Normalize Redis connection settings and build connection metadata."""
        self._check_redis_version()

        password_vault = PasswordVault.get_vault_sync(config.get("vault_type"), config.get("vault_config"))
        _config = {
            "host": config["host"],
            "port": config.get("port", "6379"),
            "password": password_vault.get_password(config.get("password", None)),
            "decode_responses": config.get("decode_responses", True),
            "retry_on_timeout": True,
            "max_connections": config.get("max_connections", 1000),
            "socket_timeout": 3,
            "socket_connect_timeout": 1,
        }
        if "db" in config:
            _config["db"] = config["db"]
        self._config = _config

        self._pool = None

    @staticmethod
    def _check_redis_version() -> bool:
        """Ensure a redis-py version new enough for the helpers is installed."""
        ver_min = version.parse("4.1.0")
        valid = False
        try:
            ver_cur = version.parse(redis.__version__)
            if ver_cur >= ver_min:
                valid = True
                LOG.debug("Using redis (async) version = %s" % redis.__version__)
        except Exception as e:
            LOG.error("Failed to obtain redis version!")
            LOG.error(str(e))

        if not valid:
            msg = "Invalid version of `redis-py`, version >4.1.0 required for async support!"
            LOG.fatal(msg)
            raise ImportError(msg)

        return valid

    @property
    def connection_generic(self):
        """Return a standard async Redis client."""
        LOG.debug("AsyncRedis connection info: {host}:{port}".format(**self._config))

        if self._pool is None:
            self._pool = redis.ConnectionPool()
        return redis.Redis(connection_pool=self._pool, **self._config)

    @property
    def connection_cluster(self):
        """Return an async Redis Cluster client."""
        LOG.debug("AsyncRedisCluster connection info: {host}:{port}".format(**self._config))
        return redis.RedisCluster(**self._config)

    async def close(self):
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.disconnect()
            self._pool = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()