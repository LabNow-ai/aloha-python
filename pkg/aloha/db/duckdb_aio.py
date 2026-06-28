"""
Async DuckDB connection helpers.
"""

from pathlib import Path

import duckdb
import duckdb_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text

from aloha.logger import LOG

__all__ = ("DuckOperator",)

LOG.debug("duckdb_aio version = %s, duckdb_engine = %s (async)", (duckdb.__version__, duckdb_engine.__version__))


class DuckOperator:
    """Create and use an async DuckDB connection through SQLAlchemy."""

    def __init__(self, db_config, **kwargs):
        """Build an async DuckDB engine, creating the database file if necessary."""
        """db_config example:
        {
            "path": "/path/to/db.duckdb",     # file path of duckdb, use ":memory:" for in-memory mode
            "schema": "sales",                # optional, 'main' by default
            "read_only": True,                # optional, False by default, (will set to False if in in-memory mode)
            "config": {"memory_limit": "500mb"}, # optional, duckdb connection configs
        }
        """
        self._config = {
            "path": db_config.get("path", ":memory:"),
            "schema": db_config.get("schema", "main"),
            "read_only": bool(db_config.get("read_only", False)),
            "config": db_config.get("config", {}),
            "auto_commit": db_config.get("auto_commit", True),
        }

        if not self._config["path"] or self._config["path"] == ":memory:":
            self._config["path"] = ":memory:"

            if self._config["read_only"]:
                LOG.warning("In-memory database cannot be read-only. Setting read_only=False.")
                self._config["read_only"] = False

        else:
            self._prepare_database()

        try:
            str_connection = f"duckdb+aioduckdb:///{self._config['path']}"
            self.engine: AsyncEngine = create_async_engine(
                str_connection,
                connect_args={"read_only": self._config["read_only"], "config": self._config["config"]},
                **kwargs,
            )

            LOG.debug("DuckDB (async) connected: {path} [schema={schema}, read_only={read_only}]".format(**self._config))
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError("Failed to connect to DuckDB (async)")

    def _prepare_database(self):
        """Prepare the database file and its parent directory."""
        path = self._config["path"]
        path_obj = Path(path)

        parent_dir = path_obj.parent
        if not parent_dir.exists():
            if self._config["read_only"]:
                raise RuntimeError(f"Directory '{parent_dir}' does not exist and read_only=True")
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                LOG.debug(f"Created directory: {parent_dir}")
            except Exception as e:
                raise RuntimeError(f"Failed to create directory '{parent_dir}': {e}")

        if not path_obj.exists():
            if self._config["read_only"]:
                raise RuntimeError(f"DuckDB file '{path}' does not exist and read_only=True")
            try:
                LOG.debug(f"Database file not found, creating: {path}")
                duckdb.connect(path).close()
            except Exception as e:
                raise RuntimeError(f"Failed to create database file '{path}': {e}")

    @property
    def connection(self):
        return self.engine

    @property
    def conn(self):
        """Alias for connection property."""
        return self.engine

    async def execute_query(self, sql, *args, **kwargs):
        """Execute a SQL statement asynchronously and return the cursor result."""
        async with self.engine.connect() as conn:
            cur = await conn.execute(text(sql), *args, **kwargs)
            if self._config.get("auto_commit", True):
                await conn.commit()
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
        return f"duckdb:///{self._config['path']} [schema={self._config['schema']}, read_only={self._config['read_only']}] (async)"

    async def close(self):
        """Close the async engine and all connections."""
        await self.engine.dispose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()