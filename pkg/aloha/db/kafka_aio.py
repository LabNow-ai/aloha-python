"""Async Kafka connection helpers."""

import inspect
import json
import typing
from dataclasses import dataclass

import aiokafka as kafka
import aiokafka.admin as kafka_admin

from ..logger import LOG

__all__ = ("KafkaOperator", "ConsumedMessage")

LOG.debug("kafka_aio: using aiokafka for async Kafka support")


@dataclass
class ConsumedMessage:
    """Represents a message consumed from Kafka."""

    topic: str
    partition: int
    offset: int
    key: str | bytes | None
    value: str | bytes | None
    headers: list[tuple[str, str | bytes]] | None = None


class DummyMessage:
    def __init__(self, topic: str, partition: int):
        self._topic = topic
        self._partition = partition

    def topic(self) -> str:
        return self._topic

    def partition(self) -> int:
        return self._partition


def _unpack_message(data: typing.Any) -> typing.Tuple[typing.Any, typing.Any, typing.Any]:
    """Unpack data into (value, key, headers)."""
    if isinstance(data, dict):
        value = data.get("value")
        key = data.get("key")
        headers = data.get("headers")
    elif hasattr(data, "value"):
        value = data.value
        key = getattr(data, "key", None)
        headers = getattr(data, "headers", None)
    else:
        value = data
        key = None
        headers = None
    return value, key, headers


def _prepare_headers(headers: typing.Any) -> typing.List[typing.Tuple[str, bytes]] | None:
    if not headers:
        return None
    if isinstance(headers, dict):
        headers = list(headers.items())
    processed = []
    for k, v in headers:
        if isinstance(v, str):
            v = v.encode("utf-8")
        elif v is None:
            v = b""
        processed.append((k, v))
    return processed


class KafkaOperator:
    """Create async Kafka admin, producer, and consumer clients."""

    def __init__(self, kafka_config):
        """
        Parameter reference: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md

        :param kafka_config:
        host = [
            {host: kafka_server_1, port: 9092}
        ]
        """
        self._config = json.loads(json.dumps(kafka_config, ensure_ascii=False))

        if "host" in kafka_config:
            self._config = {
                "bootstrap_servers": ",".join(["{host}:{port}".format(**i) for i in kafka_config.pop("host")]),
            }
        LOG.debug("Kafka (async) connection info: " + str(self._config))

        self._admin_client = None
        self._producer = None
        self._consumer = None

    async def admin_client(self, *args, **kwargs) -> kafka_admin.AIOKafkaAdminClient:
        """Return a configured async Kafka AdminClient."""
        if self._admin_client is None:
            self._admin_client = kafka_admin.AIOKafkaAdminClient(bootstrap_servers=self._config.get("bootstrap_servers"))
            await self._admin_client.start()
        return self._admin_client

    async def create_topic(self, topic: str, num_partitions=3, replication_factor=1, *args, **kwargs):
        """Create a Kafka topic and wait for the broker response asynchronously."""
        admin = await self.admin_client()
        try:
            new_topic = kafka_admin.NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
            await admin.create_topics([new_topic])
            LOG.info("Topic {} created".format(topic))
            return True
        except Exception as e:
            LOG.error("Failed to create topic {}: {}".format(topic, e))
            return False

    async def producer(self) -> kafka.AIOKafkaProducer:
        """Return a configured async Kafka Producer."""
        if self._producer is None:
            self._producer = kafka.AIOKafkaProducer(
                bootstrap_servers=self._config.get("bootstrap_servers"),
                value_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
                key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
            )
            await self._producer.start()
        return self._producer

    async def producer_deliver(
        self, topic: str, generator: typing.AsyncIterator[typing.Any], func_callback=None, *args, **kwargs
    ):
        """Stream messages from an async iterator into a Kafka topic."""
        producer = await self.producer()

        if func_callback is None:

            async def delivery_report(err, msg):
                """Called once for each message produced to indicate delivery result."""
                if err is not None:
                    LOG.error("Kafka msg delivery failed: {}".format(err))
                else:
                    LOG.debug("Kafka msg delivered to {} [{}]".format(msg.topic(), msg.partition()))

            func_callback = delivery_report

        async for data in generator:
            value, key, headers = _unpack_message(data)
            prepared_headers = _prepare_headers(headers)
            try:
                metadata = await producer.send_and_wait(
                    topic,
                    value=value,
                    key=key,
                    headers=prepared_headers,
                )
                if func_callback is not None:
                    if inspect.iscoroutinefunction(func_callback):
                        await func_callback(None, DummyMessage(topic, metadata.partition))
                    else:
                        func_callback(None, DummyMessage(topic, metadata.partition))
            except Exception as e:
                if func_callback is not None:
                    if inspect.iscoroutinefunction(func_callback):
                        await func_callback(e, None)
                    else:
                        func_callback(e, None)
                else:
                    LOG.error("Kafka msg delivery failed: {}".format(e))

    async def consumer_generator(
        self, topics_subscribe: list, group_id: str | None = None, poll_timeout: float = 1.0, *args, **kwargs
    ) -> typing.AsyncIterator[ConsumedMessage]:
        """Yield decoded messages from the subscribed Kafka topics asynchronously."""
        # Enable manual commit by default (At-least-once)
        kwargs.setdefault("enable_auto_commit", False)

        consumer = kafka.AIOKafkaConsumer(
            *topics_subscribe,
            bootstrap_servers=self._config.get("bootstrap_servers"),
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: v.decode("utf-8") if v else None,
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            **kwargs,
        )
        self._consumer = consumer
        await consumer.start()
        try:
            async for msg in consumer:
                raw_headers = msg.headers
                headers = None
                if raw_headers:
                    headers = []
                    for k, v in raw_headers:
                        if isinstance(v, bytes):
                            try:
                                v = v.decode("utf-8")
                            except Exception:
                                pass
                        headers.append((k, v))

                consumed_msg = ConsumedMessage(
                    topic=msg.topic,
                    partition=msg.partition,
                    offset=msg.offset,
                    key=msg.key,
                    value=msg.value,
                    headers=headers,
                )
                LOG.debug("Received message: {}".format(consumed_msg))
                yield consumed_msg
        finally:
            await consumer.stop()
            self._consumer = None

    async def commit(self, *args, **kwargs):
        """Commit offsets for the current consumer."""
        if self._consumer is not None:
            await self._consumer.commit(*args, **kwargs)

    async def close(self):
        """Close all Kafka clients."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
        if self._admin_client:
            await self._admin_client.close()
            self._admin_client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
