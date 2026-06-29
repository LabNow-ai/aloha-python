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

try:
    from .postgres import PostgresOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .mysql import MySqlOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .redis import RedisOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .mongo import MongoOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .elasticsearch import ElasticSearchOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .kafka import KafkaOperator, ConsumedMessage
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .sqlite import SqliteOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .duckdb import DuckOperator
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .oracle import OracledbOperator
except (ImportError, ModuleNotFoundError):
    pass


# Async modules (importable as aliases for easy switching)
from .base_aio import PasswordVault as PasswordVaultAio

try:
    from .postgres_aio import PostgresOperator as PostgresOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .mysql_aio import MySqlOperator as MySqlOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .redis_aio import RedisOperator as RedisOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .mongo_aio import MongoOperator as MongoOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .elasticsearch_aio import ElasticSearchOperator as ElasticSearchOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .kafka_aio import KafkaOperator as KafkaOperatorAio, ConsumedMessage as ConsumedMessageAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .sqlite_aio import SqliteOperator as SqliteOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .duckdb_aio import DuckOperator as DuckOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .oracle_aio import OracledbOperator as OracledbOperatorAio
except (ImportError, ModuleNotFoundError):
    pass

__all__ = (
    # Sync operators
    "PostgresOperator",
    "MySqlOperator",
    "RedisOperator",
    "MongoOperator",
    "ElasticSearchOperator",
    "KafkaOperator",
    "ConsumedMessage",
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
    "ConsumedMessageAio",
    "SqliteOperatorAio",
    "DuckOperatorAio",
    "OracledbOperatorAio",
    "PasswordVaultAio",
)