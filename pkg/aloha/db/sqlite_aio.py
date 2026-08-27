"""
Async SQLite connection helpers.
"""

import sqlite3

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("SqliteOperator",)


class SqliteOperator:
    """Create and use an async SQLAlchemy-backed SQLite connection."""

    def __init__(self, db_config, **kwargs):
        """Build an async SQLite or SQLCipher engine from the provided config."""
        self._connection_pattern = "sqlite+aiosqlite://{dbname}"
        dbname = db_config.get("dbname", "")
        if len(dbname) > 0:
            dbname = "/%s" % dbname
        self._config = {"dbname": dbname}

        if "password" in db_config:
            try:
                import sqlcipher3
            except ImportError:
                raise RuntimeError("Python package required for encrypted sqlite3: sqlcipher3-binary")
            LOG.debug("Version of sqlcipher3 = %s" % sqlcipher3.sqlite_version)
            password_vault = PasswordVault.get_vault_sync(db_config.get("vault_type"), db_config.get("vault_config"))
            password = password_vault.get_password(db_config.get("password", None))
            self._config["password"] = password
            self._connection_pattern = "sqlite+pysqlcipher://:{password}@/{dbname}"
        else:
            LOG.debug("Version of sqlite = %s" % sqlite3.sqlite_version)

        try:
            self.engine: AsyncEngine = create_async_engine(self._connection_pattern.format(**self._config), **kwargs)
            LOG.debug("Sqlite (async) connected: %s" % self.connection_str)
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError("Failed to connect to sqlite (async)")

    @property
    def connection(self):
        return self.engine

    async def execute_query(self, sql, *args, **kwargs):
        """Execute a SQL statement asynchronously and return the cursor result."""
        async with self.engine.connect() as conn:
            cur = await conn.execute(text(sql), *args, **kwargs)
            return cur

    async def execute_query_scalars(self, sql, *args, **kwargs):
        """Execute a SQL statement and return all scalar results."""
        async with self.engine.connect() as conn:
            cur = await conn.stream_scalars(text(sql), *args, **kwargs)
            async for row in cur:
                yield row

    @property
    def connection_str(self) -> str:
        """Return the SQLAlchemy connection URL used by the engine."""
        return self._connection_pattern.format(**self._config)

    async def close(self):
        """Close the async engine and all connections."""
        await self.engine.dispose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()