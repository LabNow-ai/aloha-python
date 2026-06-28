"""
Async Oracle DB connection helpers.
"""

import oracledb
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("OracledbOperator",)

LOG.debug("oracledb (async) version = %s" % oracledb.__version__)


class OracledbOperator:
    """Create and use an async SQLAlchemy-backed Oracle connection."""

    def __init__(self, db_config, **kwargs):
        """Build an async Oracle connection pool from the provided config."""
        """example of db_config:
        {
            "host": "192.168.1.100",
            "port": 1521,
            "user": "PT_INDEX",
            "password": "vault_key_or_plain",
            "service_name": "orcl",   # 推荐使用 service_name
            "sid": "orcl",            # 或使用 sid
            "vault_type": "...",
            "vault_config": {...},
            "lib_dir": "/opt/oracle/instantclient"  # optional, use THICK mode if defined.
        }
        """

        password_vault = PasswordVault.get_vault_sync(db_config.get("vault_type"), db_config.get("vault_config"))
        self._config = {
            "host": db_config["host"],
            "port": db_config["port"],
            "user": db_config["user"],
            "password": password_vault.get_password(db_config.get("password")),
        }

        if "lib_dir" in db_config:
            try:
                oracledb.init_oracle_client(lib_dir=db_config["lib_dir"])
                LOG.info("Oracle client initialized in THICK mode from: %s" % db_config["lib_dir"])
            except Exception as e:
                LOG.warning(f"Warning: {e}")
                raise RuntimeError(f"Failed to initialize Oracle client: {e}")

        service_name = db_config.get("service_name")
        sid = db_config.get("sid")

        if service_name:
            dsn = oracledb.makedsn(db_config["host"], db_config["port"], service_name=service_name)
        elif sid:
            dsn = oracledb.makedsn(db_config["host"], db_config["port"], sid=sid)
        else:
            raise ValueError("Oracle config must specify service_name or sid")

        self._config["dsn"] = dsn
        try:
            self.engine: AsyncEngine = create_async_engine(
                "oracle+oracledb://{user}:{password}@".format(**self._config),
                connect_args={"dsn": dsn},
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                **kwargs,
            )
            msg = "OracleDB (async) connected: {host}:{port}".format(**self._config)
            print(msg)
        except Exception as e:
            LOG.error(e)
            raise RuntimeError("Failed to connect to OracleDB (async)")

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
        return "oracle://{user}@{host}:{port} (async)".format(**self._config)

    async def close(self):
        """Close the async engine and all connections."""
        await self.engine.dispose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()