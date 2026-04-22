"""MySQL connection helpers."""

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from ..logger import LOG
from .base import PasswordVault

__all__ = ("MySqlOperator",)

LOG.debug("Version of pymysql = %s" % pymysql.__version__)


class MySqlOperator:
    """Create and use a SQLAlchemy-backed MySQL connection."""

    def __init__(self, db_config, **kwargs):
        """Build a connection pool from the provided database config."""
        password_vault = PasswordVault.get_vault(db_config.get("vault_type"), db_config.get("vault_config"))
        self._config = {
            "host": db_config["host"],
            "port": db_config["port"],
            "user": db_config["user"],
            "password": password_vault.get_password(db_config["password"]),
            "dbname": db_config["dbname"],
        }

        try:
            self.db = create_engine(
                "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}".format(**self._config),
                pool_size=50,
                pool_recycle=500,
                pool_pre_ping=True,
                **kwargs,
            )
            LOG.debug("MySQL connected: {host}:{port}/{dbname}".format(**self._config))
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError("Failed to connect to MySQL")

    @property
    def connection(self):
        return self.db

    def execute_query(self, sql, *args, **kwargs):
        """Execute a SQL statement and return the cursor result."""
        with self.db.connect() as conn:
            cur = conn.execute(text(sql), *args, **kwargs)
            return cur

    @property
    def connection_str(self) -> str:
        """Return a human-readable connection string."""
        return "mysql://{user}:{password}@{host}:{port}/{dbname}".format(**self._config)
