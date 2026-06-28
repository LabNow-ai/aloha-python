"""
aloha.db package - Database and middleware connection helpers.

Sync modules (blocking):
    from aloha.db import PostgresOperator, MySqlOperator, RedisOperator, ...
    from aloha.db.postgres import PostgresOperator
    from aloha.db.mysql import MySqlOperator
    from aloha.db.redis import RedisOperator
    from aloha.db.mongo import MongoOperator
    from aloha.db.elasticsearch import ElasticSearchOperator
    from aloha.db.kafka import KafkaOperator
    from aloha.db.sqlite import SqliteOperator
    from aloha.db.duckdb import DuckOperator
    from aloha.db.oracle import OracledbOperator

Async modules (non-blocking):
    from aloha.db import PostgresOperator as PostgresOperatorAio, ...
    from aloha.db.postgres_aio import PostgresOperator
    from aloha.db.mysql_aio import MySqlOperator
    from aloha.db.redis_aio import RedisOperator
    from aloha.db.mongo_aio import MongoOperator
    from aloha.db.elasticsearch_aio import ElasticSearchOperator
    from aloha.db.kafka_aio import KafkaOperator
    from aloha.db.sqlite_aio import SqliteOperator
    from aloha.db.duckdb_aio import DuckOperator
    from aloha.db.oracle_aio import OracledbOperator

Base utilities:
    from aloha.db.base import PasswordVault
    from aloha.db.base_aio import PasswordVault  # async version

Usage example (sync):
    from aloha.db.postgres import PostgresOperator

    op = PostgresOperator(db_config)
    result = op.execute_query("SELECT * FROM users")
    for row in result:
        print(row)

Usage example (async):
    from aloha.db.postgres_aio import PostgresOperator

    async def main():
        op = PostgresOperator(db_config)
        result = await op.execute_query("SELECT * FROM users")
        async for row in op.execute_query_scalars("SELECT * FROM users"):
            print(row)
        await op.close()

    import asyncio
    asyncio.run(main())
"""

# Sync modules
from .base import PasswordVault
from .postgres import PostgresOperator
from .mysql import MySqlOperator
from .redis import RedisOperator
from .mongo import MongoOperator
from .elasticsearch import ElasticSearchOperator
from .kafka import KafkaOperator
from .sqlite import SqliteOperator
from .duckdb import DuckOperator
from .oracle import OracledbOperator

# Async modules (importable as aliases for easy switching)
from .base_aio import PasswordVault as PasswordVaultAio
from .postgres_aio import PostgresOperator as PostgresOperatorAio
from .mysql_aio import MySqlOperator as MySqlOperatorAio
from .redis_aio import RedisOperator as RedisOperatorAio
from .mongo_aio import MongoOperator as MongoOperatorAio
from .elasticsearch_aio import ElasticSearchOperator as ElasticSearchOperatorAio
from .kafka_aio import KafkaOperator as KafkaOperatorAio
from .sqlite_aio import SqliteOperator as SqliteOperatorAio
from .duckdb_aio import DuckOperator as DuckOperatorAio
from .oracle_aio import OracledbOperator as OracledbOperatorAio

__all__ = (
    # Sync operators
    "PostgresOperator",
    "MySqlOperator",
    "RedisOperator",
    "MongoOperator",
    "ElasticSearchOperator",
    "KafkaOperator",
    "SqliteOperator",
    "DuckOperator",
    "OracledbOperator",
    "PasswordVault",
    # Async operators (aliased)
    "PostgresOperatorAio",
    "MySqlOperatorAio",
    "RedisOperatorAio",
    "MongoOperatorAio",
    "ElasticSearchOperatorAio",
    "KafkaOperatorAio",
    "SqliteOperatorAio",
    "DuckOperatorAio",
    "OracledbOperatorAio",
    "PasswordVaultAio",
)