"""
Async MySQL connection helpers.
"""

import aiomysql
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("MySqlOperator",)

LOG.debug("mysql_aio: using aiomysql for async MySQL support")


class MySqlOperator:
    """Create and use an async SQLAlchemy-backed MySQL connection."""

    def __init__(self, db_config, **kwargs):
        """Build an async connection pool from the provided database config."""
        password_vault = PasswordVault.get_vault_sync(db_config.get("vault_type"), db_config.get("vault_config"))
        self._config = {
            "host": db_config["host"],
            "port": db_config["port"],
            "user": db_config["user"],
            "password": password_vault.get_password(db_config["password"]),
            "dbname": db_config["dbname"],
        }

        try:
            self.engine: AsyncEngine = create_async_engine(
                "mysql+aiomysql://{user}:{password}@{host}:{port}/{dbname}".format(**self._config),
                pool_size=50,
                pool_recycle=500,
                pool_pre_ping=True,
                **kwargs,
            )
            LOG.debug("MySQL (async) connected: {host}:{port}/{dbname}".format(**self._config))
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError("Failed to connect to MySQL (async)")

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
        """Return a human-readable connection string."""
        return "mysql://{user}:{password}@{host}:{port}/{dbname}".format(**self._config)

    async def close(self):
        """Close the async engine and all connections."""
        await self.engine.dispose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


async def create_pool(db_config, **kwargs) -> aiomysql.Pool:
    """
    Create an aiomysql connection pool directly.

    Args:
        db_config: Database configuration dict with host, port, user, password, dbname
        **kwargs: Additional aiomysql pool arguments

    Returns:
        aiomysql.Pool instance
    """
    password_vault = PasswordVault.get_vault_sync(db_config.get("vault_type"), db_config.get("vault_config"))
    password = password_vault.get_password(db_config["password"])

    pool = await aiomysql.create_pool(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=password,
        db=db_config["dbname"],
        minsize=kwargs.pop("minsize", 5),
        maxsize=kwargs.pop("maxsize", 50),
        **kwargs,
    )
    return pool