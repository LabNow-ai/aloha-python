"""Kafka connection helpers."""

import json
import typing
from dataclasses import dataclass

import confluent_kafka as kafka
import confluent_kafka.admin as kafka_admin

from ..logger import LOG

__all__ = ("KafkaOperator", "ConsumedMessage")

LOG.debug("Version of confluent_kafka client = %s" % kafka.__version__)


@dataclass
class ConsumedMessage:
    """Represents a message consumed from Kafka."""

    topic: str
    partition: int
    offset: int
    key: str | bytes | None
    value: str | bytes | None
    headers: list[tuple[str, str | bytes]] | None = None


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
    """Create Kafka admin, producer, and consumer clients."""

    def __init__(self, kafka_config):
        """
        Parameter reference: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md

        :param kafka_config:
        host = [
            {host: kafka_server_1, port: 9092}
        ]
        """
        self._config = json.loads(json.dumps(kafka_config, ensure_ascii=False))  # deep copy

        if "host" in kafka_config:
            self._config = {
                "bootstrap.servers": ",".join(["{host}:{port}".format(**i) for i in kafka_config.pop("host")]),
            }
        LOG.debug("Kafka connection info: " + str(self._config))
        self._producer = None
        self._consumer = None

    def admin_client(self, *args, **kwargs):
        """Return a configured Kafka AdminClient."""
        config_admin = {**self._config}
        a = kafka_admin.AdminClient(config_admin)
        return a

    def create_topic(self, topic: str, num_partitions=3, replication_factor=1, *args, **kwargs):
        """Create a Kafka topic and wait for the broker response."""
        """Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability."""
        a = self.admin_client()
        new_topic = kafka_admin.NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)

        # Call create_topics to asynchronously create topics. A dict of <topic,future> is returned.
        fs = a.create_topics([new_topic])

        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                LOG.info("Topic {} created".format(topic))
            except Exception as e:
                LOG.error("Failed to create topic {}: {}".format(topic, e))
                return False
            finally:
                if hasattr(a, "close"):
                    a.close()

        return True

    def producer(self) -> kafka.Producer:
        """Return a configured Kafka Producer."""
        if self._producer is None:
            config_producer = {**self._config}
            self._producer = kafka.Producer(config_producer)
        return self._producer

    def producer_deliver(
        self, topic: str, generator: typing.Iterator[typing.Any], func_callback: callable = None, *args, **kwargs
    ):
        """Stream messages from an iterator into a Kafka topic."""
        # func_callback should be a function that takes two arguments: err and msg
        p = self.producer()

        def delivery_report(err, msg):
            """Called once for each message produced to indicate delivery result. Triggered by poll() or flush()."""
            if err is not None:
                LOG.error("Kafka msg delivery failed: {}".format(err))
            else:
                LOG.debug("Kafka msg delivered to {} [{}]".format(msg.topic(), msg.partition()))

        if func_callback is None:
            func_callback = delivery_report

        for data in generator:  # some data from the generator
            # Trigger any available delivery report callbacks from previous produce() calls
            p.poll(0)

            value, key, headers = _unpack_message(data)
            if isinstance(value, str):
                value = value.encode("utf-8")
            prepared_headers = _prepare_headers(headers)

            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            p.produce(topic, value=value, key=key, headers=prepared_headers, callback=func_callback)

        # Wait for any outstanding messages to be delivered and delivery report callbacks to be triggered.
        p.flush()

    def consumer_generator(
        self, topics_subscribe: list, group_id: str | None = None, poll_timeout: float = 1.0, *args, **kwargs
    ) -> typing.Iterator[ConsumedMessage]:
        """Yield decoded messages from the subscribed Kafka topics."""
        config_consumer = {"auto.offset.reset": "earliest", "enable.auto.commit": False, **self._config}
        if group_id is not None:
            config_consumer["group.id"] = group_id

        # Merge extra config passed via kwargs (convert snake_case to dot.case for confluent_kafka)
        for k, v in kwargs.items():
            k_dot = k.replace("_", ".")
            config_consumer[k_dot] = v

        c = kafka.Consumer(config_consumer)
        self._consumer = c

        c.subscribe(topics_subscribe)
        try:
            while True:
                msg = c.poll(poll_timeout)

                if msg is None:
                    continue
                elif msg.error():
                    code = msg.error().code()
                    if code == kafka.KafkaError._PARTITION_EOF:
                        pass
                    LOG.error("Kafka consumer: {}".format(msg.error()))
                    continue

                val = msg.value()
                if val is not None:
                    try:
                        val = val.decode("utf-8")
                    except Exception:
                        pass

                key = msg.key()
                if key is not None:
                    try:
                        key = key.decode("utf-8")
                    except Exception:
                        pass

                raw_headers = msg.headers()
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
                    topic=msg.topic(),
                    partition=msg.partition(),
                    offset=msg.offset(),
                    key=key,
                    value=val,
                    headers=headers,
                )
                LOG.debug("Received message: {}".format(consumed_msg))
                yield consumed_msg
        finally:
            c.close()
            self._consumer = None

    def commit(self, *args, **kwargs):
        """Commit offsets for the current consumer."""
        if self._consumer is not None:
            self._consumer.commit(*args, **kwargs)

    def close(self):
        """Close all Kafka clients."""
        if self._producer is not None:
            self._producer.flush()
            self._producer = None
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
