"""
Async MongoDB connection helpers.
"""

import ipaddress
import json

from motor.motor_asyncio import AsyncIOMotorClient

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("MongoOperator",)


def _is_ip_addr(s):
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False


_conn = {}


def MongoOperator(config):
    """
    Return a cached async MongoDB operation wrapper for the given config.
    
    Note: This function returns the same async operator class (no caching needed for async).
    The caching behavior is preserved for API compatibility but the underlying operations are async.
    """
    db_name = config.get("db_name")
    collection_name = config.get("collection_name")

    _config = {k: v for k, v in config.items() if v is not None}
    key = "%s:%s:%s" % (json.dumps(_config, sort_keys=True, ensure_ascii=False), db_name or "", collection_name or "")

    if key not in _conn:
        try:
            _conn[key] = _MongoDBOperation(_config, db_name=db_name, collection_name=collection_name)
        except Exception as e:
            LOG.exception(e)
            return
    return _conn[key]


class _MongoDBOperation:
    """Async MongoDB collection helper built on top of motor (async pymongo)."""

    def __init__(self, config, db_name=None, collection_name=None):
        """Create an async MongoClient and optionally bind a default collection."""
        self.db_name, self.collection_name = db_name, collection_name

        host = config["host"]

        if config.get("port") is None and isinstance(host, list):
            hosts = ["{host}:{port}".format(**h) for h in host]
        else:
            hosts = ["{host}:{port}".format(host=host, port=config.get("port", 27017))]

        replicaSet = config.get("replicaSet")
        if replicaSet is None and not _is_ip_addr(hosts[0].split(":")[0]):
            replicaSet = hosts[0].split(".")[0]

        password_vault = PasswordVault.get_vault_sync(config.get("vault_type"), config.get("vault_config"))
        _config = {
            "host": "mongodb://%s" % ",".join(hosts),
            "port": config.get("port"),
            "replicaSet": replicaSet,
            "username": config["username"],
            "password": password_vault.get_password(config.get("password")),
            "maxPoolSize": config.get("maxPoolSize"),
            "authSource": config.get("authSource", db_name),
        }
        msg = {k: ("***" if k == "password" else v) for k, v in _config.items()}
        LOG.debug(msg)

        try:
            self.conn: AsyncIOMotorClient = AsyncIOMotorClient(**_config)

            self.db = self.conn[db_name]
            if self.collection_name is not None:
                self.collection = self.db[self.collection_name]
        except Exception as e:
            LOG.exception(e)

    async def set_collection(self, collection_name):
        """Switch the active collection after verifying it exists."""
        if collection_name not in await self.db.list_collection_names():
            raise Exception("Collection[%s] does not exist in [%s]" % (self.collection_name, self.db_name))
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]
        return True

    async def check_and_get_collection(self, collection_name=None, raise_if_not_exists=True):
        """Return the active collection, switching it when requested."""
        self.db = self.conn[self.db_name]

        if self.collection_name is not None:
            self.collection = self.db[self.collection_name]

        if collection_name is not None and collection_name != self.collection_name:
            if self.collection_name not in await self.db.list_collection_names():
                if raise_if_not_exists:
                    raise Exception("Collection [%s] does not exist in [%s]" % (self.collection_name, self.db_name))
                else:
                    pass

            self.collection_name = collection_name
            self.collection = self.db[self.collection_name]

        return self.collection

    async def insert(self, doc_or_docs, check_keys=False, collection_name=None):
        """Insert a single document or a list of documents asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.insert_many(doc_or_docs, check_keys=check_keys) if isinstance(doc_or_docs, list) else await collection.insert_one(doc_or_docs)
        except Exception as e:
            LOG.exception(e)

    async def insert_many(self, docs, collection_name=None):
        """Insert many documents at once asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.insert_many(docs)
        except Exception as e:
            LOG.exception(e)

    async def insert_one(self, doc, collection_name=None):
        """Insert one document asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.insert_one(doc)
        except Exception as e:
            LOG.exception(e)

    async def delete_many(self, field_filter, collection_name=None):
        """Delete all documents matching the filter asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.delete_many(filter=field_filter)
        except Exception as e:
            LOG.exception(e)

    async def delete_one(self, field_filter, collection_name=None):
        """Delete one document matching the filter asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.delete_one(filter=field_filter)
        except Exception as e:
            LOG.exception(e)

    async def update_one(
        self,
        field_filter,
        update,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        array_filters=None,
        session=None,
        collection_name=None,
    ):
        """Update one document and return whether the update succeeded."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            await collection.update_one(
                filter=field_filter,
                update=update,
                upsert=upsert,
                bypass_document_validation=bypass_document_validation,
                collation=collation,
                array_filters=array_filters,
                session=session,
            )
            return True
        except Exception as e:
            LOG.exception(e)
            return False

    async def update_many(
        self,
        field_filter,
        update,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        array_filters=None,
        session=None,
        collection_name=None,
    ):
        """Update many documents matching the filter asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.update_many(
                filter=field_filter,
                update=update,
                upsert=upsert,
                bypass_document_validation=bypass_document_validation,
                collation=collation,
                array_filters=array_filters,
                session=session,
            )
        except Exception as e:
            LOG.exception(e)

    async def query(self, field_filter=None, sort=None, limit=40, skip=0, collection_name=None):
        """Query documents with optional sorting, limit, and skip asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            if sort:
                cursor = collection.find(field_filter or {}).sort(sort).skip(skip).limit(limit)
            else:
                cursor = collection.find(field_filter or {}).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            LOG.exception(e)

    async def find_many(self, field_filter=None, projection=None, collection_name=None, *args, **kwargs):
        """Return a cursor for a MongoDB query asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            cursor = collection.find(field_filter or {}, projection, *args, **kwargs)
            return await cursor.to_list(length=None)
        except Exception as e:
            LOG.exception(e)

    async def find_one(self, field_filter=None, projection=None, collection_name=None, *args, **kwargs):
        """Return a single matching MongoDB document asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.find_one(field_filter or {}, projection, *args, **kwargs)
        except Exception as e:
            LOG.exception(e)

    async def count(self, field_filter=None, collection_name=None):
        """Count documents matching the filter asynchronously."""
        try:
            collection = await self.check_and_get_collection(collection_name)
            return await collection.count_documents(field_filter or {})
        except Exception as e:
            LOG.exception(e)

    async def check_connected(self):
        """Check if the connection is still active."""
        try:
            await self.conn.admin.command("ping")
        except Exception:
            raise NameError("MongoDB: not connected")

    async def close(self):
        """Close the MongoDB connection."""
        if self.conn:
            self.conn.close()