"""
Async Kafka connection helpers.
"""

import json
import typing

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, AIOKafkaAdminClient
from aiokafka.admin import NewTopic

from ..logger import LOG

__all__ = ("KafkaOperator",)

LOG.debug("kafka_aio: using aiokafka for async Kafka support")


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

    async def admin_client(self, *args, **kwargs) -> AIOKafkaAdminClient:
        """Return a configured async Kafka AdminClient."""
        admin = AIOKafkaAdminClient(bootstrap_servers=self._config.get("bootstrap_servers"))
        await admin.start()
        return admin

    async def create_topic(self, topic: str, num_partitions=3, replication_factor=1, *args, **kwargs):
        """Create a Kafka topic and wait for the broker response asynchronously."""
        admin = await self.admin_client()
        try:
            new_topic = NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
            await admin.create_topics([new_topic])
            LOG.info("Topic {} created".format(topic))
            return True
        except Exception as e:
            LOG.error("Failed to create topic {}: {}".format(topic, e))
            return False
        finally:
            await admin.close()

    async def producer(self) -> AIOKafkaProducer:
        """Return a configured async Kafka Producer."""
        producer = AIOKafkaProducer(
            bootstrap_servers=self._config.get("bootstrap_servers"),
            value_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
        )
        await producer.start()
        return producer

    async def producer_deliver(self, topic: str, generator: typing.AsyncIterator[str], func_callback=None, *args, **kwargs):
        """Stream messages from an async iterator into a Kafka topic."""
        producer = await self.producer()
        try:
            if func_callback is None:
                async def delivery_report(err, msg):
                    """Called once for each message produced to indicate delivery result."""
                    if err is not None:
                        LOG.error("Kafka msg delivery failed: {}".format(err))
                    else:
                        LOG.debug("Kafka msg delivered to {} [{}]".format(msg.topic(), msg.partition()))

                func_callback = delivery_report

            async for data in generator:
                await producer.send_and_wait(topic, data, callback=func_callback)

        finally:
            await producer.stop()

    async def consumer_generator(
        self, topics_subscribe: list, group_id: str | None = None, poll_timeout: float = 1.0, *args, **kwargs
    ) -> typing.AsyncIterator[str]:
        """Yield decoded messages from the subscribed Kafka topics asynchronously."""
        consumer = AIOKafkaConsumer(
            *topics_subscribe,
            bootstrap_servers=self._config.get("bootstrap_servers"),
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: v.decode("utf-8") if v else None,
        )
        await consumer.start()
        try:
            async for msg in consumer:
                if msg.value() is not None:
                    LOG.debug("Received message: {}".format(msg.value()))
                    yield msg.value()
        finally:
            await consumer.stop()

    async def close(self):
        """Close all Kafka clients."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
        if self._admin_client:
            await self._admin_client.close()
            self._admin_client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()