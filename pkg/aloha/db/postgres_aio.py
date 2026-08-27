"""
Async PostgreSQL connection helpers.
"""

import asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("PostgresOperator",)

LOG.debug("postgres_aio: using asyncpg for async PostgreSQL support")


class PostgresOperator:
    """Create and use an async SQLAlchemy-backed PostgreSQL connection."""

    def __init__(self, db_config, **kwargs):
        """Build an async PostgreSQL connection pool from the database config."""
        password_vault = PasswordVault.get_vault_sync(db_config.get("vault_type"), db_config.get("vault_config"))
        self._config = {
            "host": db_config["host"],
            "port": db_config["port"],
            "user": db_config["user"],
            "password": password_vault.get_password(db_config.get("password")),
            "dbname": db_config["dbname"],
        }
        connect_args = {}
        if "schema" in db_config:
            connect_args["options"] = "-csearch_path={}".format(db_config["schema"])

        try:
            self.engine: AsyncEngine = create_async_engine(
                "postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}".format(**self._config),
                connect_args=connect_args,
                client_encoding="utf8",
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                **kwargs,
            )
            LOG.debug("PostgresSQL (async) connected: {host}:{port}/{dbname}".format(**self._config))
        except Exception as e:
            LOG.error(e)
            raise RuntimeError("Failed to connect to PostgresSQL (async)")

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
        return "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(**self._config)

    async def close(self):
        """Close the async engine and all connections."""
        await self.engine.dispose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


async def create_pool(db_config, **kwargs) -> asyncpg.Pool:
    """
    Create an asyncpg connection pool directly.

    Args:
        db_config: Database configuration dict with host, port, user, password, dbname
        **kwargs: Additional asyncpg pool arguments

    Returns:
        asyncpg.Pool instance
    """
    password_vault = PasswordVault.get_vault_sync(db_config.get("vault_type"), db_config.get("vault_config"))
    password = password_vault.get_password(db_config.get("password"))

    pool = await asyncpg.create_pool(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=password,
        database=db_config["dbname"],
        min_size=kwargs.pop("min_size", 5),
        max_size=kwargs.pop("max_size", 20),
        **kwargs,
    )
    return pool