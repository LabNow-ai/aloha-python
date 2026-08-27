"""
Async Elasticsearch connection helpers.
"""

import json
import re

from elasticsearch import AsyncElasticsearch

from ..logger import LOG
from .base_aio import PasswordVault

__all__ = ("ElasticSearchOperator",)


def _mask_hosts(hosts):
    if isinstance(hosts, list):
        return [_mask_hosts(h) for h in hosts]
    if isinstance(hosts, dict):
        return {k: ("***" if k in ("password", "http_auth") else _mask_hosts(v)) for k, v in hosts.items()}
    if isinstance(hosts, str):
        return re.sub(r"([^:/]+://)?([^:/]+):([^@]+)@", r"\1\2:***@", hosts)
    return hosts


class ElasticSearchOperator:
    """Create and use an async Elasticsearch client with optional index helpers."""

    def __init__(self, config, index_config=None):
        """Build the async client and optionally load the index configuration."""
        self.es_config = config

        password_vault = PasswordVault.get_vault_sync(config.get("vault_type"), config.get("vault_config"))
        username = config.get("username")
        password = password_vault.get_password(config.get("password"))

        hosts = config.get("host", "localhost")
        masked_hosts = _mask_hosts(hosts)
        LOG.debug("ElasticSearch (async) connection info: " + str(masked_hosts))

        self._config = {
            "http_auth": (username, password) if username is not None and password is not None else None,
            "hosts": hosts,
            "timeout": config.get("timeout", 0.1),
            "max_retries": config.get("max_retries", 3),
            "retry_on_timeout": config.get("retry_on_timeout", True),
        }

        self.index_config = index_config
        self.index_name = self.es_config.get("index_name")
        self.index_type = self.es_config.get("index_type")

        self.es: AsyncElasticsearch = AsyncElasticsearch(**self._config)

        if index_config is not None:
            self.index_config = self._load_config(index_config)

    @staticmethod
    def _load_config(config):
        """Load an index configuration from a dict or JSON file."""
        if isinstance(config, dict):
            return config

        elif isinstance(config, str) and ".json" in config:
            with open(config, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config

        else:
            raise ValueError("Invalid ES config data type")

    async def put_mapping(self, index_name=None, index_type=None, index_config: dict | None = None):
        """Apply a mapping definition to the current index asynchronously."""
        return await self.es.indices.put_mapping(
            index=index_name or self.index_name,
            doc_type=index_type or self.index_type,
            body=index_config["mappings"][index_type or self.index_type],
        )

    async def build_index(self, index_name=None, index_config=None, raise_if_exist=False):
        """Create the index if it does not already exist asynchronously."""
        if not await self.es.indices.exists(index=index_name or self.index_name):
            res = await self.es.indices.create(index=index_name or self.index_name, body=index_config or self.index_config)
            return res
        else:
            msg = "Index [%s] already exits" % self.index_name
            if raise_if_exist:
                raise RuntimeError(msg)
            else:
                LOG.info(msg)
                return False

    async def search(self, query, index_name=None, index_type=None):
        """Execute a search query asynchronously."""
        return await self.es.search(index=index_name or self.index_name, doc_type=index_type or self.index_type, body=query)

    async def msearch(self, body):
        """Execute a multi-search request asynchronously."""
        return await self.es.msearch(body=body)

    async def insert(self, doc, index_name=None, index_type=None, id=None):
        """Insert or replace a document asynchronously."""
        return await self.es.index(index=index_name or self.index_name, doc_type=index_type or self.index_type, id=id, body=doc)

    async def delete(self, index_name=None, index_type=None, id=None):
        """Delete a document by ID asynchronously."""
        return await self.es.delete(index=index_name or self.index_name, doc_type=index_type or self.index_type, id=id)

    async def exists(self, index_name=None):
        """Check if an index exists asynchronously."""
        return await self.es.indices.exists(index=index_name or self.index_name)

    async def close(self):
        """Close the Elasticsearch client."""
        await self.es.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()