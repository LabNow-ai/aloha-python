# Database Operators Module (`aloha.db`)

The `aloha.db` subpackage provides operators to connect and perform queries across databases, including PostgreSQL, MySQL, SQLite, Redis, DuckDB, MongoDB, Elasticsearch, and Kafka.

## 1. Password Vault Integration (`aloha.db.base`)

Connection configurations securely resolve passwords through `PasswordVault` (supporting standard text, vault servers, or custom integrations).

```python
from aloha.db.base import PasswordVault

# Resolves vault config to extract a password string
vault = PasswordVault.get_vault(cfg_db.get("vault_type"), cfg_db.get("vault_config"))
password = vault.get_password(cfg_db.get("password"))
```

---

## 2. PostgreSQL Operator (`aloha.db.postgres`)

Creates and manages an SQLalchemy connection pool backed by `psycopg`.

### Key Classes

- `PostgresOperator(cfg_db: dict, **kwargs)`
  - Methods:
    - `execute_query(sql: str, *args, **kwargs) -> CursorResult`: Executes a raw SQL command inside a connection context block.
  - Properties:
    - `connection`: Returns the SQLAlchemy `Engine` instance.
    - `connection_str -> str`: Returns a connection string with credentials hidden or resolved.

### Usage Example

```python
from aloha.db.postgres import PostgresOperator
from aloha.settings import SETTINGS

cfg_db = SETTINGS.config.get("db_postgres")
postgres_op = PostgresOperator(cfg_db)

# Run raw SQL
result = postgres_op.execute_query("SELECT NOW();")
for row in result:
    print(row)
```
