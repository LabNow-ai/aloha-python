"""PostgreSQL connection helpers."""

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from ..logger import LOG
from .base import PasswordVault

__all__ = ("PostgresOperator",)

LOG.debug("postgres: psycopg version = %s" % psycopg.__version__)


class PostgresOperator:
    """Create and use a SQLAlchemy-backed PostgreSQL connection."""

    def __init__(self, db_config, **kwargs):
        """Build a PostgreSQL connection pool from the database config."""
        password_vault = PasswordVault.get_vault(db_config.get("vault_type"), db_config.get("vault_config"))
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
            self.engine = create_engine(
                "postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}".format(**self._config),
                connect_args=connect_args,
                client_encoding="utf8",
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                **kwargs,
            )
            LOG.debug("PostgresSQL connected: {host}:{port}/{dbname}".format(**self._config))
        except Exception as e:
            LOG.error(e)
            raise RuntimeError("Failed to connect to PostgresSQL")

    @property
    def connection(self):
        return self.engine

    def execute_query(self, sql, *args, **kwargs):
        """Execute a SQL statement and return the cursor result."""
        with self.engine.connect() as conn:
            cur = conn.execute(text(sql), *args, **kwargs)
            return cur

    @property
    def connection_str(self) -> str:
        """Return a human-readable connection string."""
        return "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(**self._config)
